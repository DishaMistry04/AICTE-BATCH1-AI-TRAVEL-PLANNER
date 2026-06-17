import os
from datetime import date
import base64

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from fpdf import FPDF


load_dotenv()
st.set_page_config(page_title="AI Travel Planner", page_icon="travelicon.jpg", layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash") 
else:
    model = None

def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


bg_image = get_base64("travelbg_dark.jpg")


st.markdown(f"""
<style>

.stApp {{
    background-image: url("data:image/png;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

div[data-testid="stVerticalBlock"] {{
    background: transparent !important;
}}

div[data-testid="stAppViewContainer"] {{
    background: transparent !important;
}}

div[data-testid="stForm"] {{
    background: transparent !important;
}}

.title {{
    text-align:center;
    font-size:38px;
    font-weight:800;
    color:white;
    padding:15px;
    border-radius:15px;
}}

/* WIDGET LABEL FONT SIZE */
[data-testid="stWidgetLabel"] p {{
    font-size: 19px !important;
    font-weight: 600 !important;
}}

.header {{
    display: flex;
    align-items: center;
    gap: 25px;
}}

.title {{
    display:flex;
    align-items:center;
    justify-content:center;
    gap:25px;

    font-size:38px;
    font-weight:800;
    color:white;

    padding:15px;
    border-radius:15px;

    background:transparent;
    backdrop-filter:none;

    height:70px;
}}

.title img {{
    width:70px;
    height:60px;
    border-radius:12px;
}}

.title span {{
    transform: translateY(10px);
}}

/* Trip Duration info box text */
div[data-testid="stAlert"] p {{
    color: white !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}}

</style>

""", unsafe_allow_html=True)

st.markdown(f"""
<div class="title">

<img src="data:image/jpg;base64,{get_base64('travelicon.png')}">

<span>AI TRAVEL PLANNER</span>

</div>
""", unsafe_allow_html=True)

destination = st.text_input("Destination", "Goa")
starting_city = st.text_input("Starting City", "Mumbai")

trip_type = st.selectbox(
    "Trip Type",
    ["Solo", "Couple", "Family", "Friends Group", "Business"]
)

religion = st.selectbox(
    "Religion (for religious places preference)",
    ["Any", "Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Other"]
)

col_date1, col_date2 = st.columns(2)

with col_date1:
    start_date = st.date_input("Start Date", min_value=date.today())

with col_date2:
    end_date = st.date_input("End Date", min_value=start_date)

days = (end_date - start_date).days + 1
st.info(f"Trip Duration: {days} Days")

col1, col2, col3 = st.columns(3)

with col1:
    adults = st.number_input("Adults", 1, 20, 2)

with col2:
    children = st.number_input("Children", 0, 10, 0)

with col3:
    seniors = st.number_input("Senior Citizens", 0, 10, 0)

budget = st.number_input("Budget (₹)", 1000, 1000000, 30000)

interests = st.multiselect(
    "Interests",
    [
        "Food", "Adventure", "History", "Nightlife", "Beaches",
        "Shopping", "Nature", "Photography", "Wildlife",
        "Religious Places", "Local Experiences"
    ]
)

other_interest = st.text_input("Other Interests (Optional)")

col4, col5 = st.columns(2)

with col4:
    travel_by = st.selectbox("Travel By", ["Flight", "Train", "Bus", "Car", "Any"])

with col5:
    food_preference = st.selectbox(
        "Food Preference",
        ["Veg", "Non-Veg", "Jain", "Vegan", "No Preference"]
    )

hotel_preference = st.selectbox(
    "Hotel Preference",
    ["Budget Hotel", "3 Star", "4 Star", "5 Star", "Resort", "Homestay", "Any"]
)

medical_conditions = st.text_area("Medical Conditions (Optional)")

if st.button("Generate Plan "):
    if not api_key:
        st.error("GEMINI_API_KEY not found in Streamlit Secrets")
    else:
        with st.spinner("Generating your travel plan..."):
            prompt = f"""
        You are an expert AI travel planner. Create a personalized travel plan based ONLY on the user's inputs.

        USER TRAVEL DETAILS:

        Destination: {destination}
        Starting City: {starting_city}

        Travel Dates:
        Start Date: {start_date}
        End Date: {end_date}
        Total Days: {days}

        Travelers:
        Adults: {adults}
        Children: {children}
        Senior Citizens: {seniors}

        Budget:
        Total Budget: ₹{budget}

        Travel Preferences:
        Travel Mode Selected: {travel_by}
        Food Preference: {food_preference}
        Hotel Preference: {hotel_preference}

        Trip Type:
        {trip_type}

        Interests:
        {", ".join(interests)}

        Other Interests:
        {other_interest}

        Religion Preference:
        {religion}

        Medical Conditions:
        {medical_conditions}


        IMPORTANT INSTRUCTIONS:

        1. WEATHER:
        - Do NOT give general seasonal weather information.
        - Give weather prediction/information specifically for the selected travel dates.
        - Mention expected temperature range, rainfall possibility, humidity, and what clothes/items to pack.
        - Explain if the selected dates are good or not for visiting.

        Example:
        "During 15 March - 20 March, Nagpur usually experiences temperatures around 25-38°C..."


        2. TRAVEL OPTIONS:
        - Recommend travel ONLY according to the selected travel mode.

        If user selected Train:
        Show:
        - Suitable trains/routes
        - Approx journey time
        - Estimated ticket cost
        - Advantages/disadvantages

        If user selected Flight:
        Show:
        - Suitable flights
        - Airport details
        - Flight duration
        - Approx airfare
        - Advantages/disadvantages

        If user selected Bus:
        Show:
        - Bus type
        - Duration
        - Approx fare
        - Comfort level

        If user selected Car:
        Show:
        - Distance
        - Driving time
        - Fuel/toll estimate
        - Route suggestions


        3. BUDGET:
        Make a realistic budget breakdown:
        - Travel cost
        - Hotel cost
        - Food cost
        - Activities
        - Shopping
        - Emergency buffer

        Check whether the plan fits within ₹{budget}.


        4. DAY-WISE ITINERARY:
        Create a plan according to:
        - Exact number of days ({days})
        - User interests
        - Trip type
        - Age group of travelers

        Include:
        Morning:
        Afternoon:
        Evening:


        5. FOOD:
        Suggest food places and famous local dishes according to:
        {food_preference}


        6. HOTELS:
        Suggest hotels according to:
        {hotel_preference}

        Mention:
        - Area/location
        - Approx price range
        - Why suitable


        7. SHOPPING:
        Suggest:
        - Famous markets
        - Local products
        - Approx prices


        8. IMPORTANT TRAVEL TIPS:

        Provide destination-specific travel advice that is practical, realistic, and useful for the traveler.

        Include:

        * Safety precautions and personal security tips
        * Best times of the day to visit major attractions
        * Local transport guidance (metro, bus, taxi, auto, rideshare, etc.)
        * Important items to carry based on weather and activities
        * Bargaining/negotiation tips for local markets and street shopping
        * Common tourist scams, overcharging practices, and how to avoid them
        * Local customs, etiquette, and cultural expectations
        * Religious and cultural guidelines visitors should respect
        * Appropriate dress code recommendations where applicable
        * Cash vs digital payment acceptance and ATM availability
        * Emergency contacts, hospitals, and medical assistance information
        * Areas, neighborhoods, or situations tourists should avoid (if any)
        * Peak crowd hours and strategies to avoid long queues
        * Weather-related precautions for the selected travel dates
        * Mobile network coverage, internet availability, and SIM card suggestions
        * Useful local language phrases with English meanings
        * Tipping practices and service charge expectations
        * Photography restrictions at religious, cultural, or government locations
        * Food and drinking water safety recommendations
        * Solo traveler, family, senior citizen, and child-specific advice when relevant
        * Festival, holiday, or local event information occurring during the selected travel dates

        Make all tips specific to the destination, travel dates, trip type, age group, and traveler preferences. Avoid generic advice.

        FORMAT:
        Use clear headings, bullet points and tables where useful.
        Make the answer personalized, not generic.
        """
            response = model.generate_content(prompt)
            result = response.text
            
            st.markdown("## Travel Plan")
            st.markdown(result)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Times", size=11)

            clean_result = result.replace("₹", "Rs.")
            clean_result = clean_result.replace("✈️", "")
            clean_result = clean_result.replace("🌍", "")
            clean_result = clean_result.replace("##", "")
            clean_result = clean_result.replace("**", "")

            for line in clean_result.split("\n"):
                pdf.multi_cell(0, 7, line)

            pdf_bytes = pdf.output(dest="S").encode("latin-1")

            st.download_button(
                label="Download Travel Plan as PDF",
                data=pdf_bytes,
                file_name="travel_plan.pdf",
                mime="application/pdf"
            )
