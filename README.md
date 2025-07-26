# PartSelect Chat Agent

A modern, AI-powered chat assistant for PartSelect, specializing in refrigerator and dishwasher parts assistance with professional UI design and intelligent tool integration.

## 🚀 **Performance-First Design**

**New in v2.0:** Performance mode is now the **default configuration**! Get fast 8-20 second responses out of the box with optional enhanced features when needed.

| Mode | Response Time | Features | Usage |
|------|---------------|----------|-------|
| **Performance (Default)** | 8-20s | Fast chat + tools | `uvicorn main:app --reload` |
| **Enhanced (Opt-in)** | 25-45s | All advanced features | `./start_enhanced.sh` |

## ✨ Features

### 🔍 **Core Functionality**
- **Smart Part Search**: Find refrigerator and dishwasher parts by name, number, or model
- **Compatibility Verification**: Check if parts work with specific appliance models
- **Interactive Installation Guides**: Step-by-step instructions with visual formatting
- **Intelligent Troubleshooting**: AI-powered diagnostic help for common appliance issues
- **Smart Scope Management**: Automatically redirects non-refrigerator/dishwasher queries
- **Detailed Part Information**: Comprehensive specifications, pricing, and availability

### 🎨 **Enhanced Chat Experience**
- **Rich Text Formatting**: Supports headers, numbered lists, bullet points, and emphasis
- **Professional Message Layout**: Clean, responsive message bubbles with proper spacing
- **Part Number Highlighting**: Automatic detection and highlighting of part numbers
- **Price Display**: Enhanced formatting for pricing information
- **Mobile-Responsive Design**: Optimized for all screen sizes
- **Real-time Communication**: WebSocket support for instant responses
- **Accessibility Features**: ARIA labels, screen reader support, and keyboard navigation

### 🤖 **AI-Powered Intelligence**
- **Function Calling**: Dynamic tool usage based on user intent
- **Context Awareness**: Maintains conversation history for better responses
- **Error Recovery**: Intelligent retry logic with exponential backoff
- **Multi-Model Support**: DeepSeek API with OpenAI fallback
- **Structured Responses**: Automatically formatted output for better readability
- **Performance-First**: Fast responses (8-20s) enabled by default
- **Optional Advanced Features**: Guardrails & multi-agent system available when needed

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**: Core runtime environment
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Uvicorn**: ASGI server for production-ready deployment
- **OpenAI/DeepSeek API**: AI model integration with function calling
- **WebSockets**: Real-time bidirectional communication
- **Pydantic**: Data validation and serialization
- **Tenacity**: Robust retry logic for API calls

### Frontend
- **React 18**: Modern component-based UI library
- **CSS3**: Advanced styling with custom properties and responsive design
- **Axios**: HTTP client for API communication
- **WebSocket API**: Real-time chat functionality

## 📋 Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- DeepSeek API key (recommended) or OpenAI API key

### 🐍 Backend Setup

1. **Navigate to the backend directory:**
```bash
cd backend
```

2. **Create and activate virtual environment:**
```bash
python -m venv mypythonenv
source mypythonenv/bin/activate  # On Windows: mypythonenv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r ../requirements.txt
```

4. **Configure environment variables:**
Create a `.env` file in the project root:
```env
DEEPSEEK_API_KEY=your_deepseek_api_key  # Recommended
OPENAI_API_KEY=your_openai_api_key      # Fallback option
```

5. **Start the backend server:**

**Option A: Performance Mode (Default - Recommended)**
```bash
uvicorn main:app --reload --port 8000
# or use the startup script
./start_server.sh
```
- ⚡ **Response Time:** 8-20 seconds
- ✅ **Best for:** Production use, user-facing applications
- 🎯 **Features:** Fast chat, tool calling, part search

**Option B: Enhanced Mode (Advanced Features)**
```bash
./start_enhanced.sh
# or set manually
export PERFORMANCE_MODE=false
export GUARDRAIL_ENABLED=true
export USE_MULTI_AGENT=true
uvicorn main:app --reload --port 8000
```
- 🛡️ **Response Time:** 25-45 seconds
- 🧠 **Best for:** Demos, research, maximum accuracy  
- 🔬 **Features:** Multi-agent routing + guardrails + advanced validation

✅ Backend available at `http://localhost:8000`

### ⚛️ Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm start
```
✅ Frontend available at `http://localhost:3000`

## 🎯 Usage Examples

Open `http://localhost:3000` and try these example queries:

### 📦 **Part Installation**
```
"How can I install part PS11752778?"
```
*AI will use the `get_installation_guide` tool to provide: difficulty level, time estimate, tools required, and step-by-step instructions*

### 🔧 **Compatibility Check**
```
"Is part WPW10082853 compatible with WDT780SAEM1?"
```
*AI will use the `check_compatibility` tool to show: compatibility status, alternative parts, and model-specific notes*

### 🛠️ **Troubleshooting**
```
"My ice maker isn't working"
```
*AI will use the `get_troubleshooting_guide` tool to provide: diagnostic questions, common causes, and solution steps*

### 🔍 **Part Search**
```
"Find water filters for Whirlpool fridge"
```
*AI will use the `search_parts` tool to show: compatible filters, specifications, and installation guides*

### 📋 **Part Details**
```
"What's the price of part PS11752778?"
```
*AI will use the `get_part_details` tool to provide: pricing, specifications, availability, and warranty information*

## ⚙️ Configuration & Environment Variables

### 🚀 **Default Configuration (Performance Mode)**
No configuration needed! The system now defaults to fast responses:

```bash
# Default values (no env vars required)
PERFORMANCE_MODE=true          # Fast processing (8-20s responses)
GUARDRAIL_ENABLED=false        # No guardrail delays
USE_MULTI_AGENT=false          # Single agent for speed
```

### 🛡️ **Enhanced Mode Configuration**
For advanced features, set these environment variables:

```bash
# Enhanced mode (slower but more intelligent)
PERFORMANCE_MODE=false         # Full processing
GUARDRAIL_ENABLED=true         # Enable hallucination detection
USE_MULTI_AGENT=true           # Multi-agent query routing
GUARDRAIL_PRESET=balanced      # strict|balanced|lenient|monitoring_only
GUARDRAIL_THRESHOLD=0.7        # Confidence threshold (0.0-1.0)
```

### 🎯 **Quick Start Commands**

| Goal | Command | Expected Time |
|------|---------|---------------|
| **Fast responses (default)** | `uvicorn main:app --reload` | 8-20 seconds |
| **All features enabled** | `./start_enhanced.sh` | 25-45 seconds |
| **Custom configuration** | Set env vars + `uvicorn main:app --reload` | Varies |

## 📁 Project Structure

```
instalily/
├── backend/
│   ├── main.py                 # FastAPI application with REST and WebSocket APIs
│   ├── agents/
│   │   ├── __init__.py         # Clean module exports
│   │   ├── base_agent.py       # Abstract base class with AI integration
│   │   ├── parts_agent.py      # PartSelect-specific agent implementation
│   │   └── tools.py            # Function calling tools (5 core functions)
│   ├── data/
│   │   └── parts_database.json # Comprehensive mock parts database
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models for type safety
│   └── utils/
│       ├── __init__.py
│       └── prompts.py          # Optimized system prompts
├── frontend/
│   ├── src/
│   │   ├── App.js              # Main React application
│   │   ├── index.css           # Global styles and CSS reset
│   │   ├── components/
│   │   │   ├── ChatInterface.js    # Chat UI with WebSocket integration
│   │   │   ├── Message.js          # Advanced message formatting component
│   │   │   └── ProductCard.js      # Product display component
│   │   └── styles/
│   │       └── App.css         # Professional styling with design system
│   ├── package.json            # React dependencies
│   └── public/
│       └── index.html          # HTML template
├── mypythonenv/               # Python virtual environment
├── requirements.txt           # Python dependencies (streamlined)
├── .env                      # Environment configuration
└── README.md
```

## 🔌 API Endpoints

| Method | Endpoint | Description | Response Format |
|--------|----------|-------------|----------------|
| `GET` | `/` | API health check | `{"message": "PartSelect Chat Agent API"}` |
| `POST` | `/chat` | Send chat message (REST) | `ChatResponse` object |
| `WS` | `/ws/{client_id}` | WebSocket for real-time chat | JSON messages |
| `GET` | `/health` | Detailed health status | `{"status": "healthy"}` |

### Chat API Schema
```json
// Request
{
  "message": "How can I install part PS11752778?",
  "conversation_id": "user_session_123"
}

// Response
{
  "message": "Here are the installation instructions...",
  "timestamp": "2024-01-15T10:30:00",
  "agent": "PartSelect Assistant"
}
```

## 🛠️ Available Tools

The AI agent has access to 5 specialized tools:

| Tool | Function | Purpose |
|------|----------|---------|
| **search_parts** | `search_parts(query, appliance_type)` | Find parts by keyword, model, or part number |
| **check_compatibility** | `check_compatibility(part_number, model_number)` | Verify part compatibility with appliance models |
| **get_installation_guide** | `get_installation_guide(part_number)` | Get step-by-step installation instructions |
| **get_troubleshooting_guide** | `get_troubleshooting_guide(issue, appliance_type)` | Diagnostic help for appliance problems |
| **get_part_details** | `get_part_details(part_number)` | Comprehensive part information and specifications |

## 🎨 Message Formatting Features

The chat interface automatically formats AI responses with:

- **📋 Headers**: `### Installation Steps` → Styled section headers with underlines
- **📝 Numbered Lists**: `1. Step one` → Circular numbered badges with proper spacing
- **• Bullet Points**: `* Important note` → Clean bullet formatting with consistent margins
- **🔧 Part Numbers**: `PS11752778` → Highlighted with gradient background and monospace font
- **💰 Pricing**: `$45.99` → Green highlighted prices for easy identification
- **📊 Key-Value Pairs**: `Difficulty: Easy` → Structured info rows with left borders
- **✨ Text Emphasis**: `**bold**` and `*italic*` → Proper HTML formatting
- **⚠️ Error States**: Clear error indicators with appropriate styling

## 🏗️ Architecture Overview

### Agent Framework
```
BaseAgent (Abstract)
    ↓
PartsAgent (Concrete)
    ↓
Tools Integration (5 functions)
    ↓
Mock Database (JSON)
```

### Key Components

1. **BaseAgent**: Abstract class providing:
   - OpenAI/DeepSeek API integration
   - Function calling orchestration
   - Conversation management
   - Error handling with retry logic
   - Tool execution framework

2. **PartsAgent**: Concrete implementation with:
   - PartSelect-specific system prompts
   - Scope checking (refrigerator/dishwasher only)
   - Tool definitions and mappings
   - Enhanced error messages

3. **Tools Module**: Core functions for:
   - Part searching with fuzzy matching
   - Compatibility verification
   - Installation guide generation
   - Troubleshooting assistance
   - Detailed part information

## 🚀 Extending the System

### Adding New Appliance Types

1. **Update Database**: Modify `backend/data/parts_database.json` with new appliance data
2. **Scope Logic**: Update `_is_in_scope()` method in `PartsAgent`
3. **System Prompts**: Enhance prompts in `backend/utils/prompts.py`
4. **Tool Enums**: Add new appliance types to tool parameter definitions

### Adding New Tools/Functions

1. **Tool Functions**: Create new async functions in `backend/agents/tools.py`
2. **Tool Definitions**: Add tool schemas to `get_tools()` in `PartsAgent`
3. **Tool Execution**: Update `_execute_tool()` method to handle new functions
4. **Frontend Support**: Add UI components for new tool response formats

### Database Integration

1. **Replace Mock Data**: Connect `tools.py` functions to real databases/APIs
2. **Add Caching**: Implement Redis or in-memory caching for performance
3. **Search Enhancement**: Add vector search for semantic part matching
4. **Real-time Updates**: Implement inventory sync and price updates

## 🔧 Development Features

- **🚀 Performance-First Architecture**: 8-20s default responses, enhanced features opt-in
- **🤖 Multi-Provider AI**: DeepSeek primary, OpenAI fallback with automatic switching
- **📊 Comprehensive Mock Data**: 50+ realistic parts with full specifications
- **⚡ WebSocket Support**: Real-time chat with connection management
- **🎯 Function Calling**: Dynamic tool selection based on user intent
- **🔄 Retry Logic**: Exponential backoff for API resilience
- **🛡️ Optional Guardrails**: Hallucination detection when enabled
- **🧠 Multi-Agent System**: Advanced query routing (opt-in)
- **📱 Mobile-First Design**: Responsive UI optimized for all devices
- **♿ Accessibility**: ARIA labels, keyboard navigation, screen reader support

## 🎯 Key Features Implemented

### Backend Excellence
- ✅ **Clean Architecture** with abstract base classes and inheritance
- ✅ **Robust Error Handling** with tenacity retry logic
- ✅ **Type Safety** with Pydantic models and type hints
- ✅ **Comprehensive Logging** for debugging and monitoring
- ✅ **Environment Configuration** with dotenv support
- ✅ **API Documentation** with FastAPI automatic OpenAPI generation

### Frontend Excellence
- ✅ **Professional UI Design** with modern CSS and design tokens
- ✅ **Rich Text Processing** with automatic content formatting
- ✅ **Responsive Layout** optimized for mobile and desktop
- ✅ **Accessibility Features** with ARIA roles and keyboard support
- ✅ **Real-time Communication** with WebSocket integration
- ✅ **Loading States** with typing indicators and smooth animations

### AI Integration
- ✅ **Performance-First Defaults** with 8-20 second response times
- ✅ **Smart Tool Selection** based on user query analysis
- ✅ **Context Management** with conversation history
- ✅ **Scope Validation** to keep conversations on-topic
- ✅ **Structured Responses** with consistent formatting
- ✅ **Error Recovery** with graceful fallback handling
- ✅ **Optional Advanced Features** (guardrails, multi-agent) when needed

## 🔮 Future Enhancement Opportunities

- 🛒 **E-commerce Integration**: Shopping cart and order management
- 🌐 **Multi-language Support**: I18n for global markets
- 👤 **User Accounts**: Personalized chat history and preferences
- 🎤 **Voice Interface**: Speech-to-text and voice responses
- 📊 **Analytics Dashboard**: Usage metrics and performance tracking
- 🔍 **Vector Search**: Semantic similarity for better part matching
- 📸 **Image Recognition**: Visual part identification from photos
- 🔔 **Notifications**: Stock alerts and maintenance reminders
- 🎨 **Theme System**: Dark mode and customizable UI themes
- 📱 **Mobile App**: Native iOS and Android applications

## 🏆 Technical Highlights

This implementation demonstrates:

- **🚀 Performance-First Design**: Default 8-20s responses, 3-5x faster than v1.0
- **🎨 Production-Ready UI**: Professional design with comprehensive formatting
- **🏗️ Scalable Architecture**: Clean separation of concerns with modular design
- **🔧 High Maintainability**: Well-documented code with clear abstractions
- **🎯 Accurate AI Responses**: Leverages realistic mock data for authentic interactions
- **📱 Cross-Platform Compatibility**: Works seamlessly across all modern browsers
- **⚡ Performance Optimized**: Efficient state management and API communication
- **🛡️ Optional Intelligence**: Advanced features available when needed
- **♿ Accessibility Compliant**: Follows WCAG guidelines for inclusive design

---

**Ready to provide exceptional parts assistance!** 🚀

*Built with modern web technologies and AI-powered intelligence.*# partselect_chat
