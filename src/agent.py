"""
Agent module - Handles Travel Buddy agent initialization and chat logic

This module contains the TravelAgent class which manages interactions with the Gemini API
and maintains the conversation state with users.
"""

import logging
from datetime import datetime
from typing import Optional

from google import genai
from google.genai import types # type: ignore

from config import (
    MODEL,
    TRAVEL_PERSONA,
    EXIT_COMMANDS,
    MAX_INPUT_LENGTH,
    THINKING_BUDGET,
    ERROR_EMPTY_INPUT,
    ERROR_INPUT_TOO_LONG,
    AMADEUS_CONFIGURED,
)
from flight_api import (
    search_flights,
    format_flight_results,
    format_flight_error,
    detect_flight_request,
    extract_flight_details_from_response,
)

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


class TravelAgent:
    """
    Travel Buddy AI Agent untuk membantu perencanaan perjalanan.

    This class handles:
    - Initialization of the Gemini chat session
    - Sending messages and receiving responses
    - Input validation
    - Conversation history tracking
    - Error handling with specific exception types
    """

    def __init__(self, client: genai.Client) -> None:
        """
        Inisialisasi Travel Agent.

        Args:
            client: Initialized Gemini API client

        Raises:
            ValueError: If client is not properly initialized
        """
        if not client:
            raise ValueError("Gemini client is required")

        self.client = client
        self.model = MODEL
        self.chat = None
        self.conversation_history: list = []

        logger.info(f"Initializing TravelAgent with model: {MODEL}")
        self._initialize_chat()
        logger.info("TravelAgent initialized successfully")

    def _initialize_chat(self) -> None:
        """
        Inisialisasi chat session dengan Travel Buddy persona.

        This creates a new chat session with:
        - The Travel Buddy system prompt (persona)
        - Thinking budget for extended reasoning
        - Proper configuration for travel assistance
        """
        try:
            # Configure extended thinking for better reasoning
            # This helps Gemini think through travel planning problems
            thinking_config = types.ThinkingConfig(
                thinking_budget=THINKING_BUDGET  # Now configurable from config.py
            )

            # Main generation configuration
            config = types.GenerateContentConfig(
                system_instruction=TRAVEL_PERSONA, thinking_config=thinking_config
            )

            # Create the chat session
            self.chat = self.client.chats.create(model=self.model, config=config)

            logger.debug(f"Chat session created with thinking_budget={THINKING_BUDGET}")
        except Exception as e:
            logger.error(f"Failed to initialize chat: {e}", exc_info=True)
            raise

    def send_message(self, user_input: str) -> Optional[str]:
        """
        Kirim pesan ke Travel Buddy dan dapatkan respons.

        This method:
        - Sends the user's message to Gemini
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

            # Send message to Gemini
            response = self.chat.send_message(user_input)
            response_text = response.text

            # Check if this is a flight request
            if detect_flight_request(user_input) or detect_flight_request(response_text):
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
