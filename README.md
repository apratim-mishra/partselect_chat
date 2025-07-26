# PartSelect Chat Agent

A modern, AI-powered chat assistant for PartSelect, specializing in refrigerator and dishwasher parts assistance with a professional UI and an advanced, multi-agent backend.

## 🚀 **Performance-First Design**

**New in v2.0:** Performance mode is now the **default configuration**! Get fast 8-20 second responses out of the box with optional enhanced features when needed.

| Mode | Response Time | Features | How to Run |
|------|---------------|----------|-------|
| **Performance (Default)** | 8-20s | Fast single-agent chat + all tools | `./start_server.sh` |
| **Enhanced (Opt-in)** | 25-45s | Multi-agent system + Guardrails | `./start_enhanced.sh` |

## ✨ Features

### 🔍 **Core Functionality**
- **Smart Part Search**: Find parts by name, number, or model from a local DB and simulated web search.
- **Compatibility Verification**: Check if parts work with specific appliance models.
- **Interactive Installation Guides**: Step-by-step instructions.
- **Intelligent Troubleshooting**: AI-powered diagnostic help for common issues.
- **Detailed Part Information**: Get specifications, pricing, and availability.
- **Scope Management**: Politely deflects questions about appliances other than refrigerators and dishwashers.

### 🎨 **Enhanced Chat Experience**
- **Rich Text Formatting**: Supports headers, lists, bolding, and italics.
- **Part Number Highlighting**: Automatically detects and styles part numbers for readability.
- **Price Display**: Formats pricing information for clarity.
- **Mobile-Responsive Design**: Fully optimized for all screen sizes.
- **Real-time Communication**: WebSocket support for instant, bidirectional chat.

### 🤖 **AI-Powered Intelligence**
- **Dual-Mode Operation**: Choose between a fast single-agent system or a powerful multi-agent system.
- **Function Calling**: Dynamic tool usage based on user intent.
- **Multi-Model Support**: Defaults to DeepSeek, with a fallback to OpenAI.
- **Hallucination Guardrail**: (Enhanced Mode) Validates AI responses against known data to prevent fabricated information.
- **Multi-Agent System**: (Enhanced Mode) A sophisticated architecture with a `TriagingAgent` that routes queries to specialized agents for superior handling of complex questions.
- **Web Search Simulation**: Tools that mimic searching a real parts website to find models, brands, and categories.

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**
- **FastAPI**: Modern, high-performance web framework.
- **Uvicorn**: ASGI server for production deployment.
- **OpenAI/DeepSeek API**: For LLM-based reasoning.
- **WebSockets**: For real-time communication.
- **Pydantic**: For robust data validation and settings management.
- **Tenacity**: For resilient API calls with retry logic.

### Frontend
- **React 18**
- **CSS3**: Advanced styling for a professional look and feel.
- **Axios**: HTTP client for API communication.
- **WebSocket API**: Native browser API for real-time chat.

## 📋 Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- A `.env` file with a `DEEPSEEK_API_KEY` (recommended) or `OPENAI_API_KEY`.

### 🐍 Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv mypythonenv
    source mypythonenv/bin/activate  # On Windows: mypythonenv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r ../requirements.txt
    ```

4.  **Configure environment variables:**
    Create a `.env` file in the **project root** (`instalily/.env`):
    ```env
    # Recommended: Get a free key from deepseek.com
    DEEPSEEK_API_KEY="your_deepseek_api_key"
    
    # Fallback option
    OPENAI_API_KEY="your_openai_api_key"
    ```

5.  **Start the backend server:**

    **Option A: Performance Mode (Default - Recommended for most uses)**
    ```bash
    # Use the startup script for convenience
    ./start_server.sh
    ```
    - ⚡ **Response Time:** 8-20 seconds
    - ✅ **Best for:** Production use, user-facing applications.
    - 🎯 **Features:** Fast chat, all 10 tools available via single-agent logic.

    **Option B: Enhanced Mode (Advanced Features)**
    ```bash
    # Use the enhanced startup script
    ./start_enhanced.sh
    ```
    - 🛡️ **Response Time:** 25-45 seconds
    - 🧠 **Best for:** Demos, research, and handling complex queries with maximum accuracy.
    - 🔬 **Features:** Multi-agent routing, hallucination guardrails, and advanced validation.

    ✅ The backend will be available at `http://localhost:8000`.

### ⚛️ Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Start the development server:**
    ```bash
    npm start
    ```
    ✅ The frontend will be available at `http://localhost:3000`.

## 📁 Project Structure

```
instalily/
├── backend/
│   ├── main.py                 # FastAPI app: REST & WebSocket endpoints
│   ├── agents/
│   │   ├── base_agent.py       # Abstract base class for agents
│   │   ├── parts_agent.py      # Main agent logic, tool definitions
│   │   ├── tools.py            # Core tools for local data (search, compat)
│   │   ├── partselect_web_tools.py # Tools for simulating web search
│   │   ├── multi_agent_system.py # Orchestrator for Enhanced Mode
│   │   ├── hallucination_guardrail.py # Validates LLM output
│   │   └── structured_outputs.py # Pydantic models for agent responses
│   ├── data/
│   │   └── parts_database.json # Mock parts database
│   └── utils/
│       └── prompts.py          # System prompts for the LLM
├── frontend/
│   ├── src/
│   │   ├── App.js              # Main React application component
│   │   ├── components/
│   │   │   ├── ChatInterface.js # The main chat UI
│   │   │   └── Message.js      # Component for rendering individual messages
│   │   └── styles/
│   │       └── App.css         # Professional styling and design system
│   ├── package.json
│   └── public/
│       └── index.html
├── .gitignore
├── README.md
└── requirements.txt
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API root, returns a welcome message. |
| `POST` | `/chat` | Send a chat message via REST. |
| `WS` | `/ws/{client_id}` | Establish a real-time chat connection. |
| `GET` | `/health` | Health check endpoint. |

## 🛠️ Available Tools

The agent system has access to 10 specialized tools across two modules:

| Tool | Source File | Purpose |
|------|-------------|---------|
| `search_parts` | `tools.py` | Find parts by keyword, model, or part number from local DB. |
| `check_compatibility` | `tools.py` | Verify part compatibility with appliance models. |
| `get_installation_guide`| `tools.py` | Get step-by-step installation instructions. |
| `get_troubleshooting_guide`| `tools.py` | Diagnostic help for appliance problems. |
| `get_part_details` | `tools.py` | Get all details for a specific part number. |
| `search_partselect_web`| `partselect_web_tools.py`| Simulate searching the PartSelect website. |
| `validate_model_number`| `partselect_web_tools.py`| Check if a model number is valid based on known data. |
| `get_popular_models` | `partselect_web_tools.py`| Get a list of popular appliance models. |
| `get_part_categories` | `partselect_web_tools.py`| Get a list of available part categories. |
| `get_brands` | `partselect_web_tools.py`| Get a list of available appliance brands. |

## 🏗️ Architecture Overview

The system features a dual architecture that can be toggled via environment variables.

### 1. Performance-Mode Architecture (Default)
A straightforward **single-agent system** where the `PartsAgent` directly processes user input, selects from all 10 available tools using the LLM's function-calling ability, and generates a response. It is optimized for speed and efficiency.

### 2. Enhanced-Mode Architecture
A sophisticated **multi-agent system** orchestrated by `MultiAgentOrchestrator`:
1.  **Triage**: A `TriagingAgent` first classifies the user's query and routes it.
2.  **Specialization**: The query is sent to a specialized agent (`ProductSearchAgent`, `ModelLookupAgent`, or `WebSearchAgent`).
3.  **Execution**: The specialized agent executes its task, which may involve calling multiple tools in sequence or parallel.
4.  **Guardrail**: Before sending the final response to the user, the `HallucinationGuardrail` validates it for factual accuracy against the database. This adds a layer of safety and reliability at the cost of increased latency.
