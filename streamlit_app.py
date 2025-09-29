"""
Streamlit web application for the travel itinerary tool.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json
from typing import Dict, Any

from config import Config
from api_clients import TravelDataFetcher
from llm_service import ItineraryGenerator
from models import TravelItinerary

# Page configuration
st.set_page_config(
    page_title="Travel Itinerary Generator",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .itinerary-day {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .activity-item {
        background-color: white;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .meal-item {
        background-color: #fff3cd;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
        border-left: 3px solid #ffc107;
    }
    .transport-item {
        background-color: #d1ecf1;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
        border-left: 3px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'itinerary' not in st.session_state:
        st.session_state.itinerary = None
    if 'travel_data' not in st.session_state:
        st.session_state.travel_data = None
    if 'generation_in_progress' not in st.session_state:
        st.session_state.generation_in_progress = False

def validate_api_keys():
    """Validate that all required API keys are present."""
    try:
        Config.validate_required_keys()
        return True
    except ValueError as e:
        st.error(f"❌ Configuration Error: {e}")
        st.info("""
        To fix this:
        1. Copy `env_example.txt` to `.env`
        2. Fill in your actual API keys in the `.env` file
        3. Make sure `.env` is in your `.gitignore`
        """)
        return False

def display_header():
    """Display the main header."""
    st.markdown('<h1 class="main-header">✈️ Travel Itinerary Generator</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #666; margin-bottom: 2rem;">
        Create personalized travel itineraries using AI and real-time data from multiple sources
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display the sidebar with input form."""
    st.sidebar.header("🗺️ Trip Details")
    
    # Destination
    destination = st.sidebar.text_input(
        "Destination City/Country",
        placeholder="e.g., Paris, France",
        help="Enter the city or country you want to visit"
    )
    
    # Origin (optional)
    origin = st.sidebar.text_input(
        "Origin City (Optional)",
        placeholder="e.g., New York, USA",
        help="Enter your departure city for flight search"
    )
    
    # Date inputs
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=date.today() + timedelta(days=30),
            min_value=date.today()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=date.today() + timedelta(days=37),
            min_value=date.today() + timedelta(days=1)
        )
    
    # Validate dates
    if end_date <= start_date:
        st.sidebar.error("End date must be after start date")
        return None
    
    # Budget and travelers
    budget = st.sidebar.number_input(
        "Budget (USD)",
        min_value=100,
        max_value=50000,
        value=2000,
        step=100
    )
    
    travelers = st.sidebar.number_input(
        "Number of Travelers",
        min_value=1,
        max_value=10,
        value=1
    )
    
    # Preferences
    st.sidebar.header("🎯 Preferences")
    
    interests = st.sidebar.multiselect(
        "Interests",
        ["Culture", "Nature", "Food", "History", "Adventure", "Relaxation", "Nightlife", "Shopping"],
        default=["Culture", "Food"]
    )
    
    travel_style = st.sidebar.selectbox(
        "Travel Style",
        ["Budget", "Mid-range", "Luxury", "Backpacker", "Family-friendly"]
    )
    
    activity_level = st.sidebar.selectbox(
        "Activity Level",
        ["Relaxed", "Moderate", "Active", "Very Active"]
    )
    
    food_preferences = st.sidebar.multiselect(
        "Food Preferences",
        ["Local Cuisine", "International", "Vegetarian", "Vegan", "Fine Dining", "Street Food"],
        default=["Local Cuisine"]
    )
    
    return {
        'destination': destination,
        'origin': origin,
        'start_date': start_date.strftime("%Y-%m-%d"),
        'end_date': end_date.strftime("%Y-%m-%d"),
        'budget': budget,
        'travelers': travelers,
        'interests': interests,
        'travel_style': travel_style,
        'activity_level': activity_level,
        'food_preferences': food_preferences
    }

def display_itinerary(itinerary: TravelItinerary):
    """Display the generated itinerary."""
    st.markdown('<h2 class="section-header">📅 Your Travel Itinerary</h2>', unsafe_allow_html=True)
    
    # Summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Destination", itinerary.destination)
    with col2:
        st.metric("Duration", f"{itinerary.duration_days} days")
    with col3:
        st.metric("Travelers", itinerary.travelers)
    with col4:
        st.metric("Budget", f"${itinerary.budget:,.0f}")
    
    # Flight Information
    if itinerary.flights:
        st.markdown("**✈️ Flight Options**")
        for i, flight in enumerate(itinerary.flights, 1):
            st.markdown(f"""
            <div class="activity-item">
                <strong>Option {i}: {flight.airline} {flight.flight_number}</strong><br>
                <strong>Route:</strong> {flight.departure_airport} → {flight.arrival_airport}<br>
                <strong>Departure:</strong> {flight.departure_time}<br>
                <strong>Arrival:</strong> {flight.arrival_time}<br>
                <strong>Duration:</strong> {flight.duration}<br>
                <small>💰 ${flight.price:.2f} | Stops: {flight.stops}</small>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")
    
    # Hotel Information
    if itinerary.hotels:
        st.markdown("**🏨 Hotel Options**")
        for i, hotel in enumerate(itinerary.hotels, 1):
            st.markdown(f"""
            <div class="activity-item">
                <strong>Option {i}: {hotel.name}</strong><br>
                <strong>Address:</strong> {hotel.address}<br>
                <strong>Location:</strong> {hotel.city}, {hotel.country}<br>
                <strong>Rating:</strong> ⭐ {hotel.rating}/5<br>
                <small>💰 ${hotel.price_per_night:.2f}/night | Amenities: {', '.join(hotel.amenities[:3])}</small>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")
    
    # Daily itinerary
    for i, day in enumerate(itinerary.days, 1):
        st.markdown(f"""
        <div class="itinerary-day">
            <h3>Day {i} - {day.date.strftime('%A, %B %d, %Y')}</h3>
            <p><strong>📍 {day.city}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Activities
        if day.activities:
            st.markdown("**🎯 Activities**")
            for activity in day.activities:
                st.markdown(f"""
                <div class="activity-item">
                    <strong>{activity.get('time', '')} - {activity.get('activity', '')}</strong><br>
                    {activity.get('description', '')}<br>
                    <small>⏱️ {activity.get('duration', '')} | 💰 ${activity.get('cost', 0):.2f} | 📍 {activity.get('location', '')}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Meals
        if day.meals:
            st.markdown("**🍽️ Meals**")
            for meal in day.meals:
                st.markdown(f"""
                <div class="meal-item">
                    <strong>{meal.get('time', '')} - {meal.get('meal', '')}</strong><br>
                    <strong>{meal.get('restaurant', '')}</strong><br>
                    {meal.get('description', '')}<br>
                    <small>💰 ${meal.get('cost', 0):.2f} | 📍 {meal.get('location', '')}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Transportation
        if day.transportation:
            st.markdown("**🚗 Transportation**")
            for transport in day.transportation:
                st.markdown(f"""
                <div class="transport-item">
                    <strong>{transport.get('from', '')} → {transport.get('to', '')}</strong><br>
                    {transport.get('method', '')}<br>
                    <small>⏱️ {transport.get('duration', '')} | 💰 ${transport.get('cost', 0):.2f}</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")

def display_data_analysis(travel_data: Dict[str, Any]):
    """Display analysis of the fetched travel data."""
    st.markdown('<h2 class="section-header">📊 Travel Data Analysis</h2>', unsafe_allow_html=True)
    
    # Flights analysis
    if travel_data.get('flights'):
        st.markdown("**✈️ Flight Options**")
        flights_df = pd.DataFrame(travel_data['flights'])
        if not flights_df.empty:
            st.dataframe(flights_df.head(10))
            
            # Flight price distribution (if available)
            if 'price' in flights_df.columns:
                fig = px.histogram(flights_df, x='price', title='Flight Price Distribution')
                st.plotly_chart(fig, use_container_width=True)
    
    # Hotels analysis
    if travel_data.get('hotels'):
        st.markdown("**🏨 Hotel Options**")
        hotels_df = pd.DataFrame(travel_data['hotels'])
        if not hotels_df.empty:
            st.dataframe(hotels_df.head(10))
    
    # POIs analysis
    if travel_data.get('pois'):
        st.markdown("**🎯 Points of Interest**")
        pois_df = pd.DataFrame(travel_data['pois'])
        if not pois_df.empty:
            st.dataframe(pois_df.head(15))

def main():
    """Main application function."""
    initialize_session_state()
    
    # Validate API keys
    if not validate_api_keys():
        return
    
    # Display header
    display_header()
    
    # Display sidebar and get inputs
    inputs = display_sidebar()
    if not inputs:
        return
    
    # Generate itinerary button
    if st.sidebar.button("🚀 Generate Itinerary", type="primary", use_container_width=True):
        if not inputs['destination']:
            st.error("Please enter a destination")
            return
        
        st.session_state.generation_in_progress = True
        
        with st.spinner("🔄 Generating your personalized itinerary..."):
            try:
                # Fetch travel data
                data_fetcher = TravelDataFetcher()
                travel_data = data_fetcher.get_comprehensive_data(
                    destination=inputs['destination'],
                    start_date=inputs['start_date'],
                    end_date=inputs['end_date'],
                    origin=inputs['origin'] if inputs['origin'] else None,
                    budget=inputs['budget']
                )
                st.session_state.travel_data = travel_data
                
                # Generate itinerary
                itinerary_generator = ItineraryGenerator()
                preferences = {
                    'interests': inputs['interests'],
                    'travel_style': inputs['travel_style'],
                    'activity_level': inputs['activity_level'],
                    'food_preferences': inputs['food_preferences']
                }
                
                itinerary = itinerary_generator.generate_itinerary(
                    destination=inputs['destination'],
                    start_date=inputs['start_date'],
                    end_date=inputs['end_date'],
                    budget=inputs['budget'],
                    travelers=inputs['travelers'],
                    preferences=preferences,
                    travel_data=travel_data
                )
                
                st.session_state.itinerary = itinerary
                st.session_state.generation_in_progress = False
                
                st.success("✅ Itinerary generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating itinerary: {e}")
                st.session_state.generation_in_progress = False
    
    # Display results
    if st.session_state.itinerary:
        display_itinerary(st.session_state.itinerary)
        
        # Export options
        st.markdown('<h2 class="section-header">📤 Export Options</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📄 Export as JSON"):
                itinerary_dict = {
                    'destination': st.session_state.itinerary.destination,
                    'start_date': st.session_state.itinerary.start_date.isoformat(),
                    'end_date': st.session_state.itinerary.end_date.isoformat(),
                    'budget': st.session_state.itinerary.budget,
                    'travelers': st.session_state.itinerary.travelers,
                    'days': [
                        {
                            'date': day.date.isoformat(),
                            'city': day.city,
                            'activities': day.activities,
                            'meals': day.meals,
                            'transportation': day.transportation
                        }
                        for day in st.session_state.itinerary.days
                    ]
                }
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(itinerary_dict, indent=2),
                    file_name=f"itinerary_{st.session_state.itinerary.destination}_{st.session_state.itinerary.start_date}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📊 Show Data Analysis"):
                if st.session_state.travel_data:
                    display_data_analysis(st.session_state.travel_data)
        
        with col3:
            if st.button("🔄 Generate New Itinerary"):
                st.session_state.itinerary = None
                st.session_state.travel_data = None
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>Built with ❤️ using Streamlit, OpenAI, and travel APIs</p>
        <p>Make sure to set up your API keys in the .env file to use all features</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

