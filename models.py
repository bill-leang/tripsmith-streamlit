"""
Data models for the travel itinerary tool.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime, date

@dataclass
class Flight:
    """Flight information model."""
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration: str
    price: float
    currency: str = "USD"
    flight_number: Optional[str] = None
    stops: int = 0

@dataclass
class Hotel:
    """Hotel information model."""
    name: str
    address: str
    city: str
    country: str
    price_per_night: float
    currency: str = "USD"
    rating: Optional[float] = None
    amenities: List[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    booking_url: Optional[str] = None

@dataclass
class PointOfInterest:
    """Point of Interest model."""
    name: str
    description: str
    category: str
    address: str
    city: str
    country: str
    rating: Optional[float] = None
    price_range: Optional[str] = None
    opening_hours: Optional[str] = None
    website: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None

@dataclass
class DayItinerary:
    """Daily itinerary model."""
    date: date
    city: str
    activities: List[Dict[str, Any]]
    meals: List[Dict[str, Any]]
    accommodation: Optional[Hotel] = None
    transportation: List[Dict[str, Any]] = None

@dataclass
class TravelItinerary:
    """Complete travel itinerary model."""
    destination: str
    start_date: date
    end_date: date
    duration_days: int
    budget: float
    currency: str = "USD"
    travelers: int = 1
    days: List[DayItinerary] = None
    flights: List[Flight] = None
    hotels: List[Hotel] = None
    points_of_interest: List[PointOfInterest] = None
    
    def __post_init__(self):
        if self.days is None:
            self.days = []
        if self.flights is None:
            self.flights = []
        if self.hotels is None:
            self.hotels = []
        if self.points_of_interest is None:
            self.points_of_interest = []

