#!/bin/bash

# PartSelect Agent - Server Startup Script
# Performance mode is now the default! Use start_enhanced.sh for full features.

echo "🚀 Starting PartSelect Agent Server (Performance Mode - Default)"
echo "=============================================================="

# Performance mode is now default - no need to set these explicitly
# But we'll set them for clarity and to override any existing env vars
export PERFORMANCE_MODE=true
export GUARDRAIL_ENABLED=false
export USE_MULTI_AGENT=false
export LOG_LEVEL=INFO

# Check if DeepSeek API key is set
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️  WARNING: DEEPSEEK_API_KEY not set"
    echo "Some features may not work without an API key"
fi

echo "📊 Performance Configuration:"
echo "- PERFORMANCE_MODE: $PERFORMANCE_MODE"
echo "- GUARDRAIL_ENABLED: $GUARDRAIL_ENABLED"
echo "- USE_MULTI_AGENT: $USE_MULTI_AGENT"
echo "- LOG_LEVEL: $LOG_LEVEL"
echo ""

echo "🌐 Starting server on http://localhost:8000"
echo "📝 API documentation: http://localhost:8000/docs"
echo "❤️  Health check: http://localhost:8000/health"
echo ""
echo "💡 For even faster responses, ensure frontend sets timeout > 30s"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload 