# 🌍 Budget Travel Agent API

> Universal AI-powered travel assistant with multi-LLM support

## 📋 Project Overview

**Budget Travel Agent** is an intelligent travel assistant that helps users find budget-friendly flights, destinations, and create complete travel packages. Built with universal LLM support - works with Gemini, GLM, OpenAI, and more!

**Why this project?**
- 🌍 **Global Reach**: Auto-detects user location worldwide
- 💰 **Budget-Focused**: Specializes in affordable travel options
- 🤖 **Universal LLM**: Switch between AI providers easily
- 🎯 **Smart Features**: Complete trip suggestions with flights + destinations
- 🔧 **Production Ready**: Optimized for scale with caching and RAG

## ✨ Key Features

- **🗺️ Global Location Detection**: Auto-detect from IP (50+ cities worldwide)
- **💡 Smart Recommendations**: AI-curated destinations with cost breakdowns
- **✈️ Complete Packages**: Flight + destination suggestions with per-person pricing
- **📅 Dynamic Dates**: Smart weekend recommendations (2-month range)
- **🔄 Multi-LLM Support**: Gemini, GLM, OpenAI, custom providers
- **⚡ Token Optimized**: RAG implementation for 60% cost reduction
- **🎨 UI Ready**: Separate frontend/backend architecture

---

## 🎯 Learning Objectives

By the end of this project, you'll understand:

- ✅ How to set up and use LLM APIs (Gemini)
- ✅ System prompts and AI personas
- ✅ Building conversational agents
- ✅ Integrating external APIs (flight data)
- ✅ Environment variables and secure API key management
- ✅ Error handling and debugging
- ✅ Structuring Python projects professionally

---

## 🚀 Project Phases

### Phase 1: Foundation (Week 1)
**Goal:** Get the basic agent working

- [x] Set up project structure
- [x] Configure environment variables (.env file)
- [x] Initialize Gemini API client
- [x] Create agent with travel persona
- [x] Build chat loop (user input → AI response)
- [x] Test with sample conversations [not using Test Case Scenario]

**What you'll build:** A chatbot that acts like a travel advisor and responds to travel questions

---

### Phase 2: Data Integration (Week 2)
**Goal:** Add real flight data

- [x] Research flight APIs (Skyscanner, Amadeus, Kiwi, etc.)
- [x] Choose a flight API to integrate (Amadeus API)
- [x] Add functions to fetch flight data
- [x] Integrate flight data into agent responses
- [ ] Test and refine with real search queries

**What you'll build:** Agent that can actually find cheap flights based on user queries

**Phase 2 Completed Tasks:**
✅ Created `src/flight_api.py` with Amadeus SDK integration
✅ Implemented `search_flights()` function for flight data retrieval
✅ Implemented `format_flight_results()` function for user-friendly display
✅ Added `search_and_format_flights()` method to TravelAgent class
✅ Updated system prompt to inform agent about flight search capability
✅ Configured Amadeus API credentials in `.env`
✅ Added Windows UTF-8 encoding fix for emoji support

---

### Phase 3: Intelligence & Features (Week 3+)
**Goal:** Make it smarter and more useful

- [ ] Add price comparison logic
- [ ] Build itinerary suggestions
- [ ] Add alert functionality (track price drops)
- [ ] Improve error handling
- [ ] Add logging for debugging

**What you'll build:** A fully functional travel planning assistant

---

## 💻 Project Structure

```
travel-agent-ai/
│
├── .env
├── .gitignore               # Ignore sensitive files
├── requirements.txt         # Python dependencies
│
├── src/
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── agent.py            # Agent logic & chat loop
│   ├── config.py           # Configuration & constants
│   ├── flight_api.py       # Flight API integration
│   └── utils.py            # Helper functions
│
├── data/                    # Store results/logs if needed
│
├── README.md               # This file
└── docs/                   # Additional documentation
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.8+** | Programming language |
| **Gemini API** | LLM for agent intelligence |
| **python-dotenv** | Manage environment variables |
| **google-genai** | Gemini SDK for Python |
| **requests** | HTTP library for API calls |

---

## 📦 Installation & Setup

### Step 1: Create Project Directory
```bash
mkdir travel-agent-ai
cd travel-agent-ai
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install google-genai python-dotenv requests
```

Save to requirements.txt:
```bash
pip freeze > requirements.txt
```

### Step 4: Configure Environment Variables
Create `.env` file in project root:
```
GEMINI_API_KEY=your_api_key_here
```

⚠️ **Important:** Add `.env` to `.gitignore` so you never accidentally commit your API key!

---

## ▶️ How to Run the Application

### Quick Start

**1. Activate Virtual Environment**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**2. Run the Application**
```bash
python src/main.py
```

### What Happens When You Run It

1. **Logging Setup** — Application initializes logging system
2. **Environment Check** — Loads `.env` file and validates `GEMINI_API_KEY`
3. **Gemini Client Init** — Initializes connection to Google Gemini API
4. **Welcome Message** — Displays greeting and instructions
5. **Chat Loop** — Waits for your input and responds with Travel Buddy AI

### Example Interaction

```
╔════════════════════════════════════════════════════════════════════════════╗
║                   🌍 Welcome to Travel Buddy AI 🌍                        ║
║                 Your Personal AI Travel Planning Assistant                 ║
╚════════════════════════════════════════════════════════════════════════════╝

📋 Perintah yang tersedia:
  • Tanya tentang destinasi travel, penerbangan murah, atau itinerary
  • Ketik 'exit', 'keluar', atau 'quit' untuk keluar dari aplikasi

Anda: Saya ingin liburan ke Bali bulan Desember, berapa budget yang dibutuhkan?

Travel Buddy: Liburan ke Bali di Desember adalah ide yang bagus! ...

Anda: exit

Terima kasih sudah menggunakan Travel Buddy! Sampai jumpa! 👋
```

### Exit Commands

The application recognizes these commands to exit:
- `exit`
- `keluar` (Indonesian)
- `quit`

Just type any of these and press Enter to close the application gracefully.

### Troubleshooting

**Problem: `GEMINI_API_KEY not found`**
- Make sure `.env` file exists in the project root
- Verify the line is exactly: `GEMINI_API_KEY=your_actual_api_key`
- Get your API key from: https://makersuite.google.com/app/apikey

**Problem: `ModuleNotFoundError: No module named 'google'`**
```bash
pip install -r requirements.txt
```

**Problem: Virtual environment not activated**
You'll see the environment name in parentheses before your prompt: `(venv) C:\path\>`

---

## 📝 Phase 2: Integrating Flight Data

### Setup Instructions

#### Step 1: Install Amadeus SDK
```bash
pip install amadeus
pip freeze > requirements.txt
```

#### Step 2: Get Amadeus API Credentials
1. Go to [Amadeus Developer Portal](https://developers.amadeus.com/)
2. Sign up for a free account
3. Create a new app to get your credentials:
   - **Client ID** (API Key)
   - **Client Secret**
4. Save these credentials securely

#### Step 3: Update `.env` File
Add your Amadeus credentials to your `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
AMADEUS_CLIENT_ID=your_amadeus_client_id_here
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret_here
```

**Important:** Never commit your `.env` file to version control!

#### Step 4: Create `flight_api.py`
This module handles all Amadeus API interactions:

```python
"""
Flight API module - Handles Amadeus API integration for flight search

This module provides functions to search flights, parse results, and format
them for display in the travel agent.
"""

from amadeus import Client, ResponseError
from config import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET

def initialize_amadeus_client():
    """Initialize Amadeus API client with credentials from .env"""
    return Client(
        client_id=AMADEUS_CLIENT_ID,
        client_secret=AMADEUS_CLIENT_SECRET
    )

def search_flights(origin: str, destination: str, departure_date: str) -> dict:
    """
    Search for flights using Amadeus API

    Args:
        origin: IATA code (e.g., 'JKT' for Jakarta)
        destination: IATA code (e.g., 'DPS' for Denpasar/Bali)
        departure_date: Date in YYYY-MM-DD format

    Returns:
        Dictionary with flight data or error message
    """
    try:
        amadeus = initialize_amadeus_client()
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=1
        )
        return {"success": True, "data": response.data}
    except ResponseError as error:
        return {"success": False, "error": str(error)}
    except Exception as e:
        return {"success": False, "error": f"Flight search failed: {str(e)}"}

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
    for i, flight in enumerate(flight_data[:5], 1):  # Show top 5 results
        price = flight.get('price', {}).get('grandTotal', 'N/A')
        itineraries = flight.get('itineraries', [])

        if itineraries:
            first_flight = itineraries[0]['segments'][0]
            departure = first_flight.get('departure', {})
            arrival = first_flight.get('arrival', {})

            formatted += f"{i}. **Price:** ${price}\n"
            formatted += f"   Departs: {departure.get('at', 'N/A')}\n"
            formatted += f"   Arrives: {arrival.get('at', 'N/A')}\n\n"

    return formatted
```

#### Step 5: Update `config.py`
Add Amadeus credentials configuration:

```python
# Add these lines to config.py
import os
from dotenv import load_dotenv

load_dotenv()

AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
```

#### Step 6: Integrate Flight Search into Agent
Modify `agent.py` to include flight search capability:

```python
from flight_api import search_flights, format_flight_results

# Add this method to TravelAgent class
def search_and_format_flights(self, origin: str, destination: str, date: str) -> str:
    """Search flights and return formatted results"""
    result = search_flights(origin, destination, date)
    if result["success"]:
        return format_flight_results(result["data"])
    else:
        return f"Could not search flights: {result['error']}"
```

#### Step 7: Update System Prompt
Enhance the `TRAVEL_PERSONA` in `config.py` to include flight search capability:

```python
TRAVEL_PERSONA = """
You are 'Travel Buddy', a friendly and enthusiastic travel advisor AI...

NEW CAPABILITY: When users ask about flights, you can search real flight data
using the Amadeus API. Always ask for:
- Origin city/airport (IATA code or city name)
- Destination city/airport
- Departure date (in YYYY-MM-DD format)

When you have these details, search for flights and present the results clearly.
"""
```

#### Step 8: Test Your Setup
1. Activate your virtual environment
2. Run the application:
   ```bash
   python src/main.py
   ```
3. Try these test queries:
   - "Find flights from Jakarta to Bali on 2024-12-15"
   - "What are the cheapest flights to Singapore?"
   - "Show me flights from Surabaya to Bangkok next month"

### Troubleshooting Phase 2

| Issue | Solution |
|-------|----------|
| `AMADEUS_CLIENT_ID not found` | Check `.env` file has both AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET |
| `ModuleNotFoundError: amadeus` | Run `pip install amadeus` |
| `401 Unauthorized` | Verify your Amadeus API credentials are correct |
| `No flights found` | Try with valid IATA codes (e.g., JKT, DPS, SIN, BKK) |
| `Rate limit exceeded` | Add delays between requests or upgrade your Amadeus plan |

---

## 📝 Phase 1: Building the Basic Agent

### Main Concepts

**1. System Instruction / Persona**
This tells the AI how to behave. Example:
```
"You are a friendly travel advisor. Help users find cheap flights and plan trips. 
Always ask clarifying questions about their preferences."
```

**2. Chat Loop**
The agent maintains conversation history and responds contextually.

**3. API Client**
Initialize the Gemini API client with your key.

### Code Structure (Phase 1)

**config.py** — Store constants
```python
MODEL = "gemini-2.5-flash"
TRAVEL_PERSONA = """
You are 'Travel Buddy', a friendly and enthusiastic travel advisor AI...
"""
```

**agent.py** — Core agent logic
```python
def run_travel_agent():
    # Initialize client
    # Set up persona
    # Run chat loop
```

**main.py** — Entry point
```python
if __name__ == "__main__":
    run_travel_agent()
```

---

## 🧠 Agent Design Tips

### What Makes a Good Persona?

✅ **DO:**
- Be specific about the AI's role
- Define boundaries (what it should/shouldn't help with)
- Include tone and style preferences
- Give examples of good responses

❌ **DON'T:**
- Be too vague ("you are helpful")
- Forget to constrain the AI's domain
- Make it overly complicated

### Example Persona for Travel Agent:
```
"You are 'Travel Buddy', an enthusiastic travel advisor AI specializing in 
finding cheap flights and planning amazing trips.

Your personality:
- Friendly and encouraging
- Detail-oriented about prices and dates
- Ask follow-up questions to understand user needs
- Suggest alternatives when prices are high

You help with:
- Finding cheap flights
- Comparing routes
- Suggesting destinations
- Planning itineraries

Decline requests about:
- Restaurant recommendations (outside your scope)
- Weather forecasts (suggest they check weather.com)
- Non-travel topics
```

---

## 🔑 Key Files Explained

### .env (Environment Variables)
```
GEMINI_API_KEY=abc123xyz789
```
Why? Keeps sensitive data out of code. Never commit this file!

### requirements.txt
```
google-genai==0.3.0
python-dotenv==1.0.0
requests==2.31.0
```
Lets others install same dependencies: `pip install -r requirements.txt`

### main.py (Entry Point)
```python
if __name__ == "__main__":
    run_travel_agent()
```
This ensures code only runs when executed directly, not when imported.

---

## 🧪 Testing Your Agent

### Phase 1 Test Cases
Try these conversations with your basic agent:

1. **Simple Query**
   - Input: "I want to go to Bali in December"
   - Expected: Agent asks follow-up questions (budget, dates, etc.)

2. **Budget Question**
   - Input: "What's the cheapest way to get to Tokyo?"
   - Expected: Agent explains factors affecting price

3. **Out of Scope**
   - Input: "Tell me a joke"
   - Expected: Agent politely redirects to travel topics

4. **Multi-turn Conversation**
   - Verify the agent remembers previous context

---

## 🐛 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| `GEMINI_API_KEY not found` | Check `.env` file exists and variable name matches |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `API Rate Limit` | Add delays between requests, check Gemini quota |
| `Agent gives irrelevant answers` | Refine your system prompt/persona |
| `Conversation history lost` | Ensure you're using chat object properly |

---

## 📚 Resources & Next Steps

### Learning Resources
- [Gemini API Docs](https://ai.google.dev/docs)
- [Python Basics](https://www.python.org/about/gettingstarted/)
- [REST APIs Explained](https://restfulapi.net/)
- [Amadeus API Documentation](https://developers.amadeus.com/)

### Next Steps for Phase 2 Refinement

After integration, you should:

1. **Test Flight Searches** with various airports:
   ```
   - Jakarta (JKT) → Bali (DPS)
   - Jakarta (JKT) → Singapore (SIN)
   - Surabaya (SUB) → Bangkok (BKK)
   - Jakarta (JKT) → Tokyo (NRT/HND)
   ```

2. **Improve Agent Integration** - Currently the agent acknowledges flight search requests but doesn't automatically call the API. To fully integrate:
   - Modify `send_message()` to detect flight search requests
   - Automatically extract origin, destination, and date from user input
   - Call `search_and_format_flights()` and append results to agent response

3. **Add Error Handling** for:
   - Invalid airport codes
   - API rate limits
   - Network failures
   - No flights found scenarios

4. **Enhance Flight Display**:
   - Sort by price, duration, or departure time
   - Add return flight options
   - Show passenger preferences (class, baggage, etc.)

### Phase 3 Preview
- Add price comparison logic
- Build itinerary suggestions
- Add price drop alerts
- Improve error handling and logging

---

## 🎓 Learning Checkpoints

**After Phase 1, you should understand:**
- [ ] How to initialize an API client
- [ ] What system prompts do
- [ ] How chat history works
- [ ] How to structure a Python project
- [ ] Environment variable best practices

**After Phase 2, you should understand:**
- [ ] How to make HTTP requests to APIs
- [ ] How to parse API responses
- [ ] How to integrate external data into an agent
- [ ] Error handling for API calls

---
