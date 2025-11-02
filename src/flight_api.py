"""
Flight API module - Handles Amadeus API integration for flight search

This module provides functions to search flights, parse results, and format
them for display in the travel agent.
"""

import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests # type: ignore

try:
    from amadeus import Client, ResponseError # type: ignore
except ImportError:
    Client = None
    ResponseError = None

from config import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET, AMADEUS_CONFIGURED

# Get logger for this module
logger = logging.getLogger(__name__)

# Cache for exchange rates (to avoid repeated API calls)
_exchange_rate_cache: Dict[str, float] = {}
_airline_name_cache: Dict[str, str] = {}
_airlines_db: Optional[Dict[str, list]] = None  # Will load OpenFlights data
_airports_db: Optional[Dict[str, str]] = None  # Will load OpenFlights airport country mapping

# Mapping for common airline codes that Amadeus uses (not standard IATA)
# These come from actual flight search results
_AMADEUS_CARRIER_CODES = {
    "OD": "Malindo Air",  # Malaysian carrier
    "ID": "Batik Air",    # Indonesian carrier (Batik Air using ID code in Amadeus)
    "Z2": "Zip Air",      # Japanese LCC
    "SJ": "Sriwijaya Air", # Indonesian carrier
    "JT": "Lion Air",     # Indonesian carrier (Lion Mentari)
    "SL": "Thai Lion Air",  # Thai carrier (using ICAO code)
}


def _load_airlines_database() -> Dict[str, list]:
    """
    Load airline database from OpenFlights CSV file

    Format: Airline ID,Name,IATA,ICAO,Callsign,Country,Active
    Index by both IATA (2-letter like 'GA') and ICAO (3-letter like 'GIA')

    Returns dictionary with structure:
    {
        "GA": [  # IATA code
            {"name": "Garuda Indonesia", "country": "Indonesia", "iata": "GA", "icao": "GIA"},
            ...
        ],
        "GIA": [  # ICAO code (also indexed)
            {"name": "Garuda Indonesia", "country": "Indonesia", "iata": "GA", "icao": "GIA"},
            ...
        ]
    }

    Returns:
        Dictionary mapping both IATA and ICAO codes to list of airline info dicts
    """
    global _airlines_db

    if _airlines_db is not None:
        return _airlines_db

    _airlines_db = {}

    try:
        import os
        import csv

        # Path to airlines database
        db_path = os.path.join(os.path.dirname(__file__), "..", "data", "airlines.dat")

        if not os.path.exists(db_path):
            logger.warning(f"Airlines database not found at {db_path}")
            return _airlines_db

        with open(db_path, "r", encoding="utf-8") as f:
            # Use CSV reader to properly handle quoted fields
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 7:
                    continue

                try:
                    # Extract fields
                    # Format: [0]=ID, [1]=Name, [2]=IATA, [3]=ICAO, [4]=Callsign, [5]=Country, [6]=Active
                    airline_id = row[0].strip()
                    airline_name = row[1].strip()
                    iata_code = row[2].strip()
                    icao_code = row[3].strip()
                    callsign = row[4].strip()
                    country = row[5].strip()
                    active = row[6].strip()

                    # Skip if no IATA and ICAO codes, or if they're NULL markers
                    if (not iata_code or iata_code == "\\N") and (not icao_code or icao_code == "\\N"):
                        continue

                    # Create airline info dict
                    airline_info = {
                        "id": airline_id,
                        "name": airline_name,
                        "iata": iata_code if iata_code != "\\N" else None,
                        "icao": icao_code if icao_code != "\\N" else None,
                        "callsign": callsign if callsign != "\\N" else None,
                        "country": country if country != "\\N" else None,
                        "active": active == "Y",
                    }

                    # Index by IATA code if available
                    if iata_code and iata_code != "\\N":
                        if iata_code not in _airlines_db:
                            _airlines_db[iata_code] = []
                        _airlines_db[iata_code].append(airline_info)

                    # Also index by ICAO code if available and different from IATA
                    if icao_code and icao_code != "\\N" and icao_code != iata_code:
                        if icao_code not in _airlines_db:
                            _airlines_db[icao_code] = []
                        _airlines_db[icao_code].append(airline_info)

                except (IndexError, ValueError) as e:
                    continue

        logger.info(
            f"Loaded airlines from OpenFlights database: {len(_airlines_db)} unique codes (IATA + ICAO)"
        )
        return _airlines_db

    except Exception as e:
        logger.error(f"Error loading airlines database: {e}", exc_info=True)
        _airlines_db = {}
        return _airlines_db


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


def get_exchange_rate(from_currency: str, to_currency: str = "IDR") -> Optional[float]:
    """
    Get exchange rate from one currency to another using exchangerate-api.com

    Args:
        from_currency: Source currency code (e.g., 'EUR')
        to_currency: Target currency code (default: 'IDR')

    Returns:
        Exchange rate as float, or None if API call fails
    """
    cache_key = f"{from_currency}_{to_currency}"

    # Check cache first
    if cache_key in _exchange_rate_cache:
        logger.debug(f"Using cached exchange rate: {cache_key}")
        return _exchange_rate_cache[cache_key]

    try:
        # Using free exchangerate-api.com (no API key required)
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        if to_currency in data.get("rates", {}):
            rate = data["rates"][to_currency]
            _exchange_rate_cache[cache_key] = rate
            logger.info(f"Exchange rate {from_currency} to {to_currency}: {rate}")
            return rate
        else:
            logger.warning(f"Currency {to_currency} not found in exchange rates")
            return None

    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to fetch exchange rate: {e}")
        # Fallback to cached or approximate rate
        return None
    except Exception as e:
        logger.error(f"Error getting exchange rate: {e}", exc_info=True)
        return None


def _load_airports_database() -> Dict[str, str]:
    """
    Load airport database from OpenFlights CSV file

    Format: Airport ID,Name,City,Country,IATA,ICAO,Latitude,Longitude,Altitude,Timezone,DST,Timezone DB,Type,Source

    Returns dictionary mapping IATA codes to countries:
    {
        "JKT": "Indonesia",
        "CGK": "Indonesia",
        "DPS": "Indonesia",
        ...
    }

    Returns:
        Dictionary mapping IATA codes to country names
    """
    global _airports_db

    if _airports_db is not None:
        return _airports_db

    _airports_db = {}

    try:
        import os
        import csv

        # Path to airports database
        db_path = os.path.join(os.path.dirname(__file__), "..", "data", "airports.dat")

        if not os.path.exists(db_path):
            logger.warning(f"Airports database not found at {db_path}")
            return _airports_db

        with open(db_path, "r", encoding="utf-8") as f:
            # Use CSV reader to properly handle quoted fields
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 5:
                    continue

                try:
                    # Format: ID,Name,City,Country,IATA,ICAO,...
                    # Fields: [0]=ID, [1]=Name, [2]=City, [3]=Country, [4]=IATA, [5]=ICAO, ...
                    iata_code = row[4].strip()
                    country = row[3].strip()

                    # Skip if no IATA code or if it's empty
                    if not iata_code or iata_code == "\\N":
                        continue

                    # Map IATA code to country
                    _airports_db[iata_code] = country

                except (IndexError, ValueError):
                    continue

        logger.info(f"Loaded {len(_airports_db)} airports from OpenFlights database")
        return _airports_db

    except Exception as e:
        logger.error(f"Error loading airports database: {e}", exc_info=True)
        _airports_db = {}
        return _airports_db


def _get_country_from_airport(airport_code: str) -> Optional[str]:
    """
    Get country name from airport code using OpenFlights database

    Args:
        airport_code: IATA airport code (e.g., 'CGK', 'BKK', 'SIN')

    Returns:
        Country name or None if unknown
    """
    if not airport_code:
        return None

    airport_code = airport_code.strip().upper()

    try:
        airports_db = _load_airports_database()
        country = airports_db.get(airport_code)
        if country:
            logger.debug(f"Found {airport_code} -> {country}")
            return country
    except Exception as e:
        logger.warning(f"Error looking up airport {airport_code}: {e}")

    logger.debug(f"Could not find country for airport code: {airport_code}")
    return None


def get_airline_name(airline_code: str, origin: Optional[str] = None, destination: Optional[str] = None) -> str:
    """
    Get full airline name from airline code with context-aware selection

    Strategy:
    1. Cache (fast)
    2. Amadeus API (has carrier codes like OD, ID that OpenFlights doesn't have)
    3. OpenFlights database (fallback for standard IATA codes)
    4. Match by destination country if needed
    5. Return code itself as final fallback

    Args:
        airline_code: Airline code (e.g., 'GA', 'OD', 'ID')
        origin: Origin airport code (e.g., 'JKT') for context
        destination: Destination airport code (e.g., 'BKK') for context

    Returns:
        Airline name or the code itself if not found
    """
    if not airline_code:
        return "Unknown Airline"

    airline_code = airline_code.strip().upper()

    # Create cache key including context
    cache_key = f"{airline_code}_{origin}_{destination}"

    # Check cache first
    if cache_key in _airline_name_cache:
        return _airline_name_cache[cache_key]

    # Check Amadeus carrier codes mapping (these are not in OpenFlights)
    if airline_code in _AMADEUS_CARRIER_CODES:
        name = _AMADEUS_CARRIER_CODES[airline_code]
        _airline_name_cache[cache_key] = name
        logger.debug(f"Found {airline_code} in Amadeus carrier codes: {name}")
        return name

    # Try Amadeus API as backup (if configured)
    try:
        if AMADEUS_CONFIGURED and Client:
            amadeus = AmadeusClient()
            if amadeus.is_ready():
                response = amadeus.client.reference_data.airlines.get(
                    airlineCode=airline_code
                )
                if response.data:
                    name = response.data[0].get("businessName", airline_code)
                    _airline_name_cache[cache_key] = name
                    logger.info(f"Got airline name from Amadeus: {airline_code} -> {name}")
                    return name
    except Exception as e:
        logger.debug(f"Failed to get airline name from Amadeus: {e}")

    # Fallback: Try OpenFlights database with context-aware selection
    try:
        airlines_db = _load_airlines_database()
        if airline_code in airlines_db:
            airline_list = airlines_db[airline_code]

            # If only one airline, return it
            if len(airline_list) == 1:
                name = airline_list[0]["name"]
                _airline_name_cache[cache_key] = name
                logger.debug(f"Found {airline_code} in OpenFlights DB: {name}")
                return name

            # Multiple airlines with same code - use context to pick best match
            origin_country = _get_country_from_airport(origin) if origin else None
            dest_country = _get_country_from_airport(destination) if destination else None

            logger.debug(
                f"Multiple airlines found for {airline_code}: {[a['name'] for a in airline_list]}, "
                f"origin_country={origin_country}, dest_country={dest_country}"
            )

            # Priority 1: Active airlines from origin/destination countries
            relevant_countries = {origin_country, dest_country}
            relevant_countries.discard(None)

            for airline in airline_list:
                # Check if country is valid (not empty, not placeholder values)
                country = airline.get("country", "")
                is_valid_country = country and country not in ["", "N/A", None] and len(country) > 2

                if airline["active"] and is_valid_country and country in relevant_countries:
                    name = airline["name"]
                    _airline_name_cache[cache_key] = name
                    logger.debug(
                        f"Found {airline_code} in OpenFlights DB (active + context match): {name} ({country})"
                    )
                    return name

            # Priority 2: Any active airline (even without country match)
            for airline in airline_list:
                if airline["active"]:
                    name = airline["name"]
                    _airline_name_cache[cache_key] = name
                    logger.debug(f"Found {airline_code} in OpenFlights DB (active): {name}")
                    return name

            # Priority 3: Match by country only
            for airline in airline_list:
                country = airline.get("country", "")
                is_valid_country = country and country not in ["", "N/A", None] and len(country) > 2
                if is_valid_country and country in relevant_countries:
                    name = airline["name"]
                    _airline_name_cache[cache_key] = name
                    logger.debug(
                        f"Found {airline_code} in OpenFlights DB (context match): {name} ({country})"
                    )
                    return name

            # Fallback: First in list
            name = airline_list[0]["name"]
            _airline_name_cache[cache_key] = name
            logger.debug(
                f"Found {airline_code} in OpenFlights DB (first match): {name}"
            )
            return name

    except Exception as e:
        logger.warning(f"Error looking up airline in OpenFlights DB: {e}")

    # Final fallback: return the code itself
    logger.debug(f"Could not find airline name for code: {airline_code}")
    _airline_name_cache[cache_key] = airline_code
    return airline_code


def format_duration(duration_str: str) -> str:
    """
    Convert ISO 8601 duration format to human-readable format

    Args:
        duration_str: Duration in ISO format (e.g., 'PT1H50M', 'PT10H', 'P1DT2H30M')

    Returns:
        Human-readable duration (e.g., '1h 50m', '10h', '1d 2h 30m')
    """
    if not duration_str:
        return "N/A"

    try:
        # Parse ISO 8601 duration
        # Format: P[n]Y[n]M[n]DT[n]H[n]M[n]S
        pattern = r"P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?"
        match = re.match(pattern, duration_str)

        if not match:
            return duration_str  # Return as-is if can't parse

        years, months, days, hours, minutes, seconds = match.groups()

        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds:
            parts.append(f"{seconds}s")

        return " ".join(parts) if parts else "N/A"

    except Exception as e:
        logger.warning(f"Error parsing duration {duration_str}: {e}")
        return duration_str


def get_airline_name_safe(airline_code: str, origin: Optional[str] = None, destination: Optional[str] = None) -> str:
    """
    Safe wrapper for get_airline_name with better error handling

    Args:
        airline_code: IATA airline code
        origin: Origin airport code for context
        destination: Destination airport code for context

    Returns:
        Airline name or user-friendly fallback
    """
    if not airline_code or airline_code.strip() == "":
        return "Unknown Airline"

    name = get_airline_name(airline_code, origin, destination)
    if name == airline_code:  # If still same as code, format it nicely
        return f"Airline {airline_code.upper()}"

    return name


def format_flight_results(flight_data: list) -> str:
    """
    Format flight search results for display

    Converts prices to IDR and shows airline names instead of codes.

    Args:
        flight_data: Raw flight data from Amadeus API

    Returns:
        Formatted string with flight information in IDR with airline names
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
            currency = price.get("currency", "EUR")

            # Convert to IDR if needed
            price_idr = total_price
            if currency != "IDR" and total_price != "N/A":
                try:
                    rate = get_exchange_rate(currency, "IDR")
                    if rate:
                        price_idr = float(total_price) * rate
                        price_idr = f"Rp {price_idr:,.0f}"
                    else:
                        # Fallback if exchange rate fails
                        price_idr = f"{currency} {total_price}"
                except ValueError:
                    price_idr = f"{currency} {total_price}"
            else:
                if price_idr != "N/A":
                    price_idr = f"Rp {float(price_idr):,.0f}"

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

            # Get origin and destination airport codes for context
            # The structure is: {"iataCode": "JKT", "at": "2025-12-20T10:00:00"}
            origin_airport = first_segment.get("departure", {}).get("iataCode", "")
            dest_airport = last_segment.get("arrival", {}).get("iataCode", "")

            # Get airline info and convert code to name (with context)
            airline = first_segment.get("operating", {})
            airline_code = airline.get("carrierCode", "")

            airline_name = get_airline_name_safe(airline_code, origin_airport, dest_airport)

            # Calculate duration (ISO 8601 format)
            duration_iso = first_leg.get("duration", "")
            duration_readable = format_duration(duration_iso)

            # Format output
            formatted += f"**Option {i}:**\n"
            formatted += f"  💰 Price: {price_idr}\n"
            formatted += f"  ✈️  Departs: {departure_time}\n"
            formatted += f"  🛬 Arrives: {arrival_time}\n"
            formatted += f"  ⏱️  Duration: {duration_readable}\n"
            formatted += f"  🔤 Airline: {airline_name}\n"
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


def detect_flight_request(text: str) -> bool:
    """
    Detect if user is asking about flights

    Args:
        text: User input or agent response

    Returns:
        True if flight request detected, False otherwise
    """
    flight_keywords = [
        "penerbangan",
        "flight",
        "flights",
        "tiket",
        "ticket",
        "pesawat",
        "airplane",
        "airport",
        "bandara",
        "dari",
        "ke",
        "tanggal",
        "date",
        "harga",
        "price",
        "murah",
        "cheap",
    ]

    text_lower = text.lower()
    keyword_count = sum(1 for keyword in flight_keywords if keyword in text_lower)

    # Consider it a flight request if at least 2 keywords found
    return keyword_count >= 2


def extract_airport_code(text: str) -> Optional[str]:
    """
    Extract IATA airport code (3 letters) from text

    Args:
        text: Text to search

    Returns:
        Airport code (uppercase) or None
    """
    # Match 3-letter airport codes
    codes = re.findall(r"\b([A-Z]{3})\b", text)
    if codes:
        return codes[0]
    return None


def extract_date_from_text(text: str) -> Optional[str]:
    """
    Extract date in YYYY-MM-DD format from text

    Supports multiple formats:
    - YYYY-MM-DD
    - DD/MM/YYYY or DD-MM-YYYY
    - "15 Desember 2025" (Indonesian)
    - "15 December 2025" (English)
    - Numbers like "2025-12-15" or "15-12-2025"

    Args:
        text: Text to search

    Returns:
        Date string in YYYY-MM-DD format or None
    """
    # Try to match YYYY-MM-DD format (priority 1)
    date_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if date_match:
        year, month, day = date_match.groups()
        return f"{year}-{month}-{day}"

    # Try to match DD/MM/YYYY or DD-MM-YYYY (priority 2)
    date_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", text)
    if date_match:
        day, month, year = date_match.groups()
        try:
            date_obj = datetime(int(year), int(month), int(day))
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # Try to match Indonesian month names (priority 3)
    months_id = {
        "januari": 1,
        "februari": 2,
        "maret": 3,
        "april": 4,
        "mei": 5,
        "juni": 6,
        "juli": 7,
        "agustus": 8,
        "september": 9,
        "oktober": 10,
        "november": 11,
        "desember": 12,
    }

    for month_name, month_num in months_id.items():
        pattern = rf"(\d{{1,2}})\s+{month_name}\s+(\d{{4}})"
        date_match = re.search(pattern, text.lower())
        if date_match:
            day, year = date_match.groups()
            try:
                date_obj = datetime(int(year), month_num, int(day))
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue

    # Try to match English month names (priority 4)
    months_en = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }

    for month_name, month_num in months_en.items():
        pattern = rf"(\d{{1,2}})\s+{month_name}\s+(\d{{4}})"
        date_match = re.search(pattern, text.lower())
        if date_match:
            day, year = date_match.groups()
            try:
                date_obj = datetime(int(year), month_num, int(day))
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue

    return None


def extract_flight_details_from_response(response_text: str) -> Optional[Dict[str, str]]:
    """
    Extract flight details from Gemini response

    This looks for patterns like:
    - Airport codes (JKT, DPS, SIN, etc)
    - Dates (YYYY-MM-DD or DD/MM/YYYY)
    - City names

    Args:
        response_text: Gemini's response

    Returns:
        Dictionary with 'origin', 'destination', 'date' or None
    """
    # Look for airport codes
    codes = re.findall(r"\b([A-Z]{3})\b", response_text)

    # Look for dates
    date = extract_date_from_text(response_text)

    # Simple heuristic: if we found at least 2 codes and a date, it's likely a flight request
    if len(codes) >= 2 and date:
        return {"origin": codes[0], "destination": codes[1], "date": date}

    # If only found 2 codes but no date, might still be valid
    if len(codes) >= 2 and not date:
        logger.warning(f"Found airport codes {codes[0]}, {codes[1]} but no date")
        return None  # Require date for safety

    logger.debug(f"Could not extract complete flight details from response")
    return None
