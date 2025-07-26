#!/bin/bash

# PartSelect Agent - Enhanced Server Startup Script
# This script enables all advanced features (slower but more intelligent)

echo "🛡️  Starting PartSelect Agent Server (Enhanced Mode)"
echo "================================================="

# Enable all enhanced features
export PERFORMANCE_MODE=false
export GUARDRAIL_ENABLED=true
export USE_MULTI_AGENT=true
export GUARDRAIL_PRESET=balanced
export LOG_LEVEL=INFO

# Check if DeepSeek API key is set
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️  WARNING: DEEPSEEK_API_KEY not set"
    echo "Enhanced features require an API key"
fi

echo "🛡️  Enhanced Configuration:"
echo "- PERFORMANCE_MODE: $PERFORMANCE_MODE"
echo "- GUARDRAIL_ENABLED: $GUARDRAIL_ENABLED"
echo "- USE_MULTI_AGENT: $USE_MULTI_AGENT"
echo "- GUARDRAIL_PRESET: $GUARDRAIL_PRESET"
echo ""

echo "🌐 Starting server on http://localhost:8000"
echo "📝 API documentation: http://localhost:8000/docs"
echo "❤️  Health check: http://localhost:8000/health"
echo ""
echo "🛡️  Enhanced Features Enabled:"
echo "   ✅ Multi-agent query routing"
echo "   ✅ Hallucination guardrails"
echo "   ✅ Advanced tool validation"
echo "   ✅ PartSelect website integration"
echo ""
echo "⏱️  Expected Response Times: 25-45 seconds"
echo "💡 For faster responses, use ./start_server.sh instead"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload 