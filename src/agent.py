"""
Agent module - Handles Travel Buddy agent initialization and chat logic

This module contains the TravelAgent class which manages interactions with the Gemini API
and maintains the conversation state with users.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List

from config import (
    TRAVEL_PERSONA,
    EXIT_COMMANDS,
    MAX_INPUT_LENGTH,
    ERROR_EMPTY_INPUT,
    ERROR_INPUT_TOO_LONG,
    AMADEUS_CONFIGURED,
)
from llm import UniversalLLM, create_llm
from flight_api import (
    search_flights,
    format_flight_results,
    format_flight_error,
    detect_flight_request,
    extract_flight_details_from_response,
)
from destination_data import (
    recommend_destinations,
    format_destination_recommendation,
    detect_travel_preferences,
)
from smart_detection import (
    LocationDetector,
    DateRangeSuggester,
    PackageGenerator,
    detect_travel_intentions,
)
from intelligent_date_generator import IntelligentDateGenerator

# Get logger for this module
logger = logging.getLogger(__name__)


class ConversationMessage:
    """
    Represents a single message in the conversation history.

    This helps track the flow of the conversation and could be useful for:
    - Debugging user interactions
    - Analyzing conversation patterns
    - Providing context to the LLM in future iterations
    """

    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """
        Initialize a conversation message.

        Args:
            role: Either 'user' or 'assistant'
            content: The actual message text
            timestamp: When the message was sent (defaults to now)
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.role}: {self.content[:50]}..."

    def to_dict(self) -> Dict:
        """Convert to dict for LLM history"""
        return {"role": self.role, "content": self.content}


class TravelAgent:
    """
    Budget Travel Buddy AI Agent - Universal LLM Support

    This class handles:
    - Universal LLM initialization (Gemini, GLM, OpenAI, etc.)
    - Sending messages and receiving responses
    - Input validation
    - Conversation history tracking
    - Error handling with specific exception types
    """

    def __init__(self, provider: str = None, model: str = None) -> None:
        """
        Initialize Travel Agent with universal LLM support.

        Args:
            provider: LLM provider (gemini, glm, openai, custom)
            model: Specific model to use
        """
        # Initialize universal LLM
        self.llm = create_llm(provider=provider, model=model)
        self.conversation_history: List[ConversationMessage] = []

        # Log provider info
        provider_info = self.llm.get_provider_info()
        logger.info(f"Initialized TravelAgent with {provider_info['provider']} ({provider_info['model']})")
        logger.info("TravelAgent initialized successfully")

    def _build_history_for_llm(self) -> List[Dict]:
        """Build conversation history for LLM"""
        # Get last 10 messages to avoid token limits
        recent_messages = self.conversation_history[-10:]
        return [msg.to_dict() for msg in recent_messages]

    def send_message(self, user_input: str) -> Optional[str]:
        """
        Kirim pesan ke Travel Buddy dan dapatkan respons.

        This method:
        - Sends the user's message to the configured LLM
        - Detects if it's a flight search request
        - Automatically searches flights if detected
        - Stores both user and assistant messages in history
        - Handles specific exception types appropriately
        - Returns None if any error occurs

        Args:
            user_input: The user's message to the Travel Buddy

        Returns:
            The assistant's response (possibly with flight results), or None if an error occurred
        """
        try:
            logger.debug(f"Sending message: {user_input[:100]}...")

            # Build conversation history
            history = self._build_history_for_llm()

            # Send message to LLM
            response = self.llm.chat(
                message=user_input,
                system_prompt=TRAVEL_PERSONA,
                history=history
            )
            response_text = response

            # Auto-suggest complete trip if user asks generally
            complete_trip_suggestion = self.auto_suggest_complete_trip(user_input)
            if complete_trip_suggestion:
                response_text += complete_trip_suggestion
                logger.info("Complete trip suggestions appended to response")

            # Check if this is a flight request
            elif detect_flight_request(user_input) or detect_flight_request(response_text):
                logger.info("Flight request detected, attempting to extract flight details...")

                # Try to extract flight parameters from response
                flight_details = extract_flight_details_from_response(response_text)

                if flight_details:
                    logger.info(
                        f"Extracted flight details: {flight_details['origin']} -> "
                        f"{flight_details['destination']} on {flight_details['date']}"
                    )

                    # Search for flights
                    flight_results = self.search_and_format_flights(
                        flight_details["origin"],
                        flight_details["destination"],
                        flight_details["date"],
                    )

                    # Append flight results to response
                    response_text += "\n\n" + flight_results
                    logger.info("Flight search results appended to response")
                else:
                    logger.warning(
                        "Flight request detected but could not extract complete details (origin, destination, date)"
                    )
                    # Add helpful message to response
                    response_text += (
                        "\n\n⚠️ **Note:** Untuk mencari penerbangan, saya butuh informasi:\n"
                        "- **Asal** (misal: Jakarta/JKT)\n"
                        "- **Tujuan** (misal: Penang/PEN)\n"
                        "- **Tanggal keberangkatan** (format: YYYY-MM-DD atau \"15 Desember 2025\")\n\n"
                        "Bisa ulangi request dengan info lengkap? Terima kasih! 😊"
                    )

            # Check if user is asking for destination recommendations
            elif self.detect_destination_request(user_input, response_text):
                logger.info("Destination recommendation request detected")

                # Detect preferences from user input
                preferences = detect_travel_preferences(user_input)

                # If no specific preferences detected, suggest exploring
                if not preferences:
                    response_text += (
                        "\n\n💡 **Tip**: Biar kasih rekomendasi yang pas, sebutin:\n"
                        "- Tipe liburan (pantai, gunung, budaya, kota)\n"
                        "- Budget (hemat, 1jutaan, 2jutaan)\n"
                        "- Preferensi (dalam/luar negeri)\n\n"
                        "Contoh: 'Mau pantai yang budget-friendly'\n"
                        "Aku kasih rekomendasi spesifik deh! 😊"
                    )
                else:
                    # Generate recommendations based on detected preferences
                    destination_recommendations = self.generate_destination_recommendations(preferences)
                    response_text += destination_recommendations
                    logger.info("Destination recommendations appended to response")

            # Store in conversation history
            self.conversation_history.append(ConversationMessage("user", user_input))
            self.conversation_history.append(
                ConversationMessage("assistant", response_text)
            )

            logger.info(f"Received response ({len(response_text)} chars)")
            return response_text

        except Exception as e:
            # Log with full traceback for debugging
            logger.error(f"Error sending message: {e}", exc_info=True)
            return None

    def should_exit(self, user_input: str) -> bool:
        """
        Cek apakah pengguna ingin keluar.

        Checks if the user input matches any of the exit commands
        defined in config.py

        Args:
            user_input: The user's input string

        Returns:
            True if user wants to exit, False otherwise
        """
        should_exit = user_input.lower() in EXIT_COMMANDS
        if should_exit:
            logger.info(f"Exit command detected: {user_input}")
        return should_exit

    def is_valid_input(self, user_input: str) -> bool:
        """
        Validasi input pengguna dengan multiple checks.

        Validates:
        - Input is not empty or just whitespace
        - Input doesn't exceed maximum length (prevents prompt injection)

        Args:
            user_input: The user's input string

        Returns:
            True if input is valid, False otherwise
        """
        stripped = user_input.strip()

        # Check for empty input
        if not stripped:
            logger.warning("Empty input received")
            print(f"❌ {ERROR_EMPTY_INPUT}")
            return False

        # Check for excessive length (security: prevent prompt injection)
        if len(stripped) > MAX_INPUT_LENGTH:
            logger.warning(
                f"Input too long: {len(stripped)} chars (max: {MAX_INPUT_LENGTH})"
            )
            print(f"❌ {ERROR_INPUT_TOO_LONG}")
            return False

        return True

    def get_conversation_history(self) -> list:
        """
        Dapatkan riwayat percakapan.

        This can be useful for:
        - Debugging conversation flow
        - Analyzing user behavior
        - Implementing features like "show chat history"

        Returns:
            List of ConversationMessage objects in chronological order
        """
        return self.conversation_history.copy()

    def clear_history(self) -> None:
        """
        Bersihkan riwayat percakapan.

        This could be useful if you want to start a new conversation
        without reinitializing the agent.
        """
        self.conversation_history.clear()
        logger.info("Conversation history cleared")

    def detect_destination_request(self, user_input: str, response_text: str) -> bool:
        """
        Detect if user is asking for destination recommendations

        Args:
            user_input: User's message
            response_text: AI's response

        Returns:
            True if destination recommendation is requested
        """
        destination_keywords = [
            'destinasi', 'rekomendasi', 'kemana', 'mana ya', 'liburan',
            'jalan-jalan', 'trip', 'wisata', 'tempat wisata', 'kunjungan',
            'bantuin pilih', 'saranin', 'kasih ide'
        ]

        # Check if any destination keyword appears
        text_to_check = (user_input + " " + response_text).lower()
        return any(keyword in text_to_check for keyword in destination_keywords)

    def generate_destination_recommendations(self, preferences: Dict) -> str:
        """
        Generate destination recommendations based on detected preferences

        Args:
            preferences: Dictionary of detected preferences

        Returns:
            Formatted destination recommendations
        """
        logger.info(f"Generating destination recommendations with preferences: {preferences}")

        # Get recommendations from destination database
        recommended_destinations = recommend_destinations(
            budget=preferences.get('budget'),
            travel_types=preferences.get('travel_types'),
            region=preferences.get('region'),
            max_results=4
        )

        # Format the recommendations
        formatted_recommendations = format_destination_recommendation(recommended_destinations)

        return formatted_recommendations

    def auto_suggest_complete_trip(self, user_input: str) -> Optional[str]:
        """
        Auto-suggest complete travel packages when user asks for general travel

        Args:
            user_input: User's message

        Returns:
            Formatted complete trip suggestions or None if not applicable
        """
        # Check if user wants a complete trip suggestion
        intentions = detect_travel_intentions(user_input)

        if not intentions.get("wants_complete_trip"):
            return None

        logger.info("Auto-suggesting complete travel package")

        # Detect origin from conversation context
        conversation_texts = [msg.content for msg in self.conversation_history[-3:]]
        origin = LocationDetector.detect_origin(user_input, conversation_texts)

        if not origin:
            # Default to Jakarta if no origin detected
            origin = LocationDetector.INDONESIAN_CITIES["jakarta"]

        # Detect travel preferences
        preferences = detect_travel_preferences(user_input)
        travel_type = preferences.get('travel_types', [])[0].value if preferences.get('travel_types') else None
        budget_category = "budget" if preferences.get('budget') else "affordable"

        # NEW: Detect if user mentioned a specific destination
        from destination_lookup import DestinationDatabase
        detected_destination = DestinationDatabase.detect_destination(user_input)

        # Suggest destinations (now with destination detection, deduplicate)
        suggested_dests = LocationDetector.suggest_destinations(
            origin['code'],
            travel_type,
            budget_category,
            detected_destination.name if detected_destination else None
        )

        # Deduplicate destinations based on airport code
        seen_codes = set()
        destinations = []
        for dest in suggested_dests:
            if dest.get("code") not in seen_codes:
                destinations.append(dest)
                seen_codes.add(dest.get("code"))

        # Get date ranges for next 6 months (now with price optimization)
        date_ranges = DateRangeSuggester.get_date_ranges(months_ahead=6)

        # Generate complete packages with intelligent date generation
        packages = PackageGenerator.generate_packages(
            origin,
            destinations,
            date_ranges,
            budget_category,
            user_input,
            detected_destination.name if detected_destination else None
        )

        # Add price optimization tips if international destination detected
        if detected_destination and detected_destination.region != "domestic":
            packages.insert(0, {
                "name": detected_destination.name,
                "origin": origin["full_name"],
                "origin_code": origin["code"],
                "destination": f"{detected_destination.name} ({detected_destination.airport_codes[0] if detected_destination.airport_codes else 'N/A'})",
                "destination_code": detected_destination.airport_codes[0] if detected_destination.airport_codes else "N/A",
                "tip": f"💡 {detected_destination.name} Best Times: {', '.join(detected_destination.best_seasons)} | Currency: {detected_destination.currency}"
            })

        # Generate intelligent date suggestions if user wants flexibility
        intelligent_dates = ""
        if any(keyword in user_input.lower() for keyword in ["bebas", "murah", "fleksibel", "kapan saja"]):
            date_generator = IntelligentDateGenerator()
            smart_suggestions = date_generator.generate_dates_from_keywords(
                user_input,
                detected_destination.name if detected_destination else None,
                origin.get("name")
            )
            if smart_suggestions:
                intelligent_dates = date_generator.format_suggestions(smart_suggestions)

        # Format the suggestions
        flight_suggestions = PackageGenerator.format_package_suggestion(packages)
        return flight_suggestions + intelligent_dates

    def search_and_format_flights(
        self, origin: str, destination: str, departure_date: str
    ) -> str:
        """
        Search for flights and return formatted results.

        This method integrates with the Amadeus API to search for real flight data.

        Args:
            origin: IATA code or city name (e.g., 'JKT' for Jakarta)
            destination: IATA code or city name (e.g., 'DPS' for Bali)
            departure_date: Date in YYYY-MM-DD format

        Returns:
            Formatted flight results or error message
        """
        if not AMADEUS_CONFIGURED:
            logger.warning("Amadeus API not configured")
            return "⚠️ Flight search is not available. Please configure Amadeus API credentials."

        logger.info(
            f"Flight search requested: {origin} -> {destination} on {departure_date}"
        )

        result = search_flights(origin, destination, departure_date)

        if result["success"]:
            formatted = format_flight_results(result["data"])
            logger.info(f"Flight search successful, found {len(result['data'])} flights")
            return formatted
        else:
            formatted_error = format_flight_error(result["error"])
            logger.error(f"Flight search failed: {result['error']}")
            return formatted_error
