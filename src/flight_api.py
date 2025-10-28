"""
Flight API module - Handles Amadeus API integration for flight search

This module provides functions to search flights, parse results, and format
them for display in the travel agent.
"""

import logging
from typing import Dict, Any, Optional

try:
    from amadeus import Client, ResponseError
except ImportError:
    Client = None
    ResponseError = None

from config import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET, AMADEUS_CONFIGURED

# Get logger for this module
logger = logging.getLogger(__name__)


class AmadeusClient:
    """Wrapper for Amadeus API client"""

    def __init__(self):
        """Initialize Amadeus client with credentials from environment"""
        if not AMADEUS_CONFIGURED:
            logger.warning(
                "Amadeus API not configured. Set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET in .env"
            )
            self.client = None
            return

        if Client is None:
            logger.error("amadeus package not installed. Run: pip install amadeus")
            self.client = None
            return

        try:
            self.client = Client(
                client_id=AMADEUS_CLIENT_ID, client_secret=AMADEUS_CLIENT_SECRET
            )
            logger.info("Amadeus client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Amadeus client: {e}", exc_info=True)
            self.client = None

    def is_ready(self) -> bool:
        """Check if client is ready to use"""
        return self.client is not None


def search_flights(
    origin: str, destination: str, departure_date: str, adults: int = 1
) -> Dict[str, Any]:
    """
    Search for flights using Amadeus API

    Args:
        origin: IATA code (e.g., 'JKT' for Jakarta) or city name
        destination: IATA code (e.g., 'DPS' for Denpasar/Bali) or city name
        departure_date: Date in YYYY-MM-DD format
        adults: Number of adult passengers (default: 1)

    Returns:
        Dictionary with flight data or error message:
        {
            "success": bool,
            "data": list of flights or None,
            "error": error message if failed
        }
    """
    amadeus = AmadeusClient()

    if not amadeus.is_ready():
        return {
            "success": False,
            "data": None,
            "error": "Amadeus API not configured. Please check your .env file.",
        }

    try:
        # Normalize input to IATA codes (convert to uppercase)
        origin = origin.upper().strip()
        destination = destination.upper().strip()

        logger.info(
            f"Searching flights from {origin} to {destination} on {departure_date}"
        )

        # Call Amadeus Flight Offers Search API
        response = amadeus.client.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=adults,
        )

        # Check if response has data
        if not response.data:
            logger.warning(
                f"No flights found for {origin}-{destination} on {departure_date}"
            )
            return {"success": True, "data": [], "error": None}

        logger.info(f"Found {len(response.data)} flight offers")
        return {"success": True, "data": response.data, "error": None}

    except ResponseError as error:
        logger.error(f"Amadeus API error: {error}", exc_info=True)
        error_message = str(error)

        # Parse common error messages
        if "not a valid" in error_message.lower() or "invalid" in error_message.lower():
            return {
                "success": False,
                "data": None,
                "error": f"Invalid airport code. Please use valid IATA codes (e.g., JKT, DPS, SIN, BKK)",
            }
        elif "unauthorized" in error_message.lower():
            return {
                "success": False,
                "data": None,
                "error": "Amadeus authentication failed. Check your API credentials.",
            }
        else:
            return {
                "success": False,
                "data": None,
                "error": f"Flight search failed: {error_message}",
            }

    except Exception as e:
        logger.error(f"Unexpected error during flight search: {e}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "error": f"Flight search failed: {str(e)}",
        }


def format_flight_results(flight_data: list) -> str:
    """
    Format flight search results for display

    Args:
        flight_data: Raw flight data from Amadeus API

    Returns:
        Formatted string with flight information
    """
    if not flight_data:
        return "No flights found for this route."

    formatted = "✈️ **Flight Options:**\n\n"

    # Show top 5 results
    for i, flight in enumerate(flight_data[:5], 1):
        try:
            # Extract price
            price = flight.get("price", {})
            total_price = price.get("grandTotal", "N/A")
            currency = price.get("currency", "")

            # Extract itineraries (journey segments)
            itineraries = flight.get("itineraries", [])

            if not itineraries:
                continue

            # Get first leg of journey
            first_leg = itineraries[0]
            segments = first_leg.get("segments", [])

            if not segments:
                continue

            # Get departure and arrival info
            first_segment = segments[0]
            last_segment = segments[-1]

            departure = first_segment.get("departure", {})
            arrival = last_segment.get("arrival", {})

            departure_time = departure.get("at", "N/A")
            arrival_time = arrival.get("at", "N/A")

            # Get airline info if available
            airline = first_segment.get("operating", {})
            airline_code = airline.get("carrierCode", "")

            # Calculate duration
            duration = first_leg.get("duration", "")

            # Format output
            formatted += f"**Option {i}:**\n"
            formatted += f"  💰 Price: {currency} {total_price}\n"
            formatted += f"  ✈️  Departs: {departure_time}\n"
            formatted += f"  🛬 Arrives: {arrival_time}\n"

            if duration:
                formatted += f"  ⏱️  Duration: {duration}\n"

            if airline_code:
                formatted += f"  🔤 Airline: {airline_code}\n"

            formatted += f"  📍 Stops: {len(segments) - 1}\n\n"

        except (KeyError, TypeError) as e:
            logger.warning(f"Error parsing flight data: {e}")
            continue

    if formatted == "✈️ **Flight Options:**\n\n":
        return "Could not parse flight results. Please try again."

    return formatted


def format_flight_error(error: str) -> str:
    """
    Format error message for display

    Args:
        error: Error message from flight search

    Returns:
        Formatted error message
    """
    return f"❌ Flight search error: {error}\n"


def extract_flight_details_from_query(user_query: str) -> Optional[Dict[str, str]]:
    """
    Try to extract flight details from user query

    This is a simple heuristic-based approach. In production, you might use NLP.

    Args:
        user_query: User's message

    Returns:
        Dictionary with 'origin', 'destination', 'date' or None if unable to extract
    """
    # This is a placeholder for future NLP-based extraction
    # For now, we'll rely on the agent to ask clarifying questions

    logger.debug(f"Analyzing query for flight details: {user_query}")
    return None
