# 🌍 Travel Agent AI - Project Guide

> Built with Gemini API | Your personal AI travel companion

## 📋 Project Overview

**Travel Agent AI** is an intelligent chatbot that helps you find cheap flights, compare routes, and plan travel itineraries. It uses Google's Gemini API to understand your travel needs and provide smart recommendations.

**Why this project?**
- Learn AI/LLM concepts through real-world application
- Build a portfolio piece that solves an actual problem
- Understand how agents work with external APIs
- Practice Python + API integration

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

- [ ] Research flight APIs (Skyscanner, Amadeus, Kiwi, etc.)
- [ ] Choose a flight API to integrate
- [ ] Add functions to fetch flight data
- [ ] Integrate flight data into agent responses
- [ ] Test with real search queries

**What you'll build:** Agent that can actually find cheap flights based on user queries

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

### APIs to Consider (Phase 2)
- **Skyscanner API** — Flight search
- **Amadeus API** — Airline data
- **Kiwi API** — Flight comparisons
- **Google Flights API** — Price tracking

### Phase 2 Preview
Once basic agent works, you'll integrate actual flight data:
```python
def search_flights(origin, destination, date):
    # Call flight API
    # Return results
    # Let agent analyze and recommend
```

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

## 💡 Pro Tips

1. **Start simple, iterate** — Get Phase 1 working before adding complexity
2. **Read error messages carefully** — They tell you exactly what's wrong
3. **Test frequently** — Run your code after small changes
4. **Use print statements** — Debug by printing values at key points
5. **Keep a learning journal** — Note what you learn each day
6. **Ask questions** — When stuck, break the problem down

---

## 🎯 Success Criteria

Your project is successful when:
- ✅ Agent responds naturally to travel questions
- ✅ Maintains conversation context
- ✅ API integrates without errors
- ✅ Code is well-organized and documented
- ✅ You understand every line of code you wrote

---

## 📞 Getting Help

**Stuck?**
1. Read the error message carefully
2. Check the relevant documentation
3. Print variables to understand what's happening
4. Break the problem into smaller pieces
5. Ask for help with specific errors, not vague problems

---

## 🚀 Ready to Start?

Open VS Code, create your project structure, and let's build something awesome! 

**Next steps:**
1. Create project directory
2. Set up virtual environment
3. Install dependencies
4. Create `.env` file with your API key
5. Start with `config.py` and `agent.py`

Good luck, bro! You got this! 💪

---

*Last Updated: October 2025*
*Built with ❤️ by Shenks*