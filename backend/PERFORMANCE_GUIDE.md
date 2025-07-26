# PartSelect Agent Performance Guide

## Performance Mode is Now Default!

**Good news:** Performance mode is now the **default configuration**! You'll get fast 8-20 second responses out of the box.

Simply run:
```bash
uvicorn main:app --reload
# or
./start_server.sh
```

**No configuration needed** - fast responses are now the default!

## Performance Modes

### 🚀 Performance Mode (Default - Recommended for Production)
```bash
# No configuration needed - this is now the default!
uvicorn main:app --reload
# or use the startup script
./start_server.sh
```
**Expected Response Time:** 8-20 seconds
**Features:** Fast chat, tool calling, part search
**Status:** ✅ **Now the default configuration**

### ⚡ Balanced Mode (Good Performance + Some Protection)
```bash
export PERFORMANCE_MODE=false
export GUARDRAIL_ENABLED=true
export GUARDRAIL_PRESET=lenient       # Fast guardrail evaluation
export USE_MULTI_AGENT=false
```
**Expected Response Time:** 8-15 seconds  
**Features:** Chat + Guardrail protection

### 🛡️ Enhanced Mode (Full Features - Opt-in)
```bash
# Use the enhanced startup script
./start_enhanced.sh
# or set manually
export PERFORMANCE_MODE=false
export GUARDRAIL_ENABLED=true
export USE_MULTI_AGENT=true
uvicorn main:app --reload
```
**Expected Response Time:** 25-45 seconds
**Features:** Multi-agent routing + advanced guardrails + validation
**Best for:** AI research, demonstrations, maximum accuracy

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `PERFORMANCE_MODE` | `true` | **NEW DEFAULT** - Fast responses (8-20s) |
| `GUARDRAIL_ENABLED` | `false` | **NEW DEFAULT** - Disabled for speed |
| `GUARDRAIL_PRESET` | `balanced` | `strict\|balanced\|lenient\|monitoring_only` |
| `GUARDRAIL_THRESHOLD` | `0.7` | Confidence threshold (0.0-1.0) |
| `USE_MULTI_AGENT` | `false` | Enable multi-agent query routing |
| `DEEPSEEK_API_KEY` | - | Required for enhanced features |

## Troubleshooting Performance Issues

### Frontend Timeout (30s)
**Symptoms:** "Request timed out. Please try again."
**Solution:** Enable performance mode:
```bash
export PERFORMANCE_MODE=true
```

### Still Slow in Performance Mode
**Possible Causes:**
1. **Slow API connection:** Check internet connectivity to DeepSeek API
2. **Complex queries:** Tool-calling queries (installation, compatibility) take longer
3. **Rate limiting:** DeepSeek API may be rate-limited

**Solutions:**
```bash
# Disable guardrails completely
export GUARDRAIL_ENABLED=false

# Reduce API timeout (faster failures)
export AGENT_TIMEOUT=15
```

### Backend Errors
**Check logs for:**
- API key issues
- Import errors
- Network connectivity

## Performance Test

Run the performance test to verify your configuration:

```bash
cd backend
python test_performance.py
```

This will test both enhanced and performance modes and show you the speed difference.

## Production Recommendations

### For High-Traffic Production
```bash
export PERFORMANCE_MODE=true
export GUARDRAIL_ENABLED=false
export USE_MULTI_AGENT=false
export LOG_LEVEL=WARNING
```

### For Development/Testing
```bash
export PERFORMANCE_MODE=false
export GUARDRAIL_ENABLED=true
export GUARDRAIL_PRESET=lenient
export USE_MULTI_AGENT=false
export LOG_LEVEL=DEBUG
```

### For Demo/Showcase
```bash
export PERFORMANCE_MODE=false
export GUARDRAIL_ENABLED=true
export GUARDRAIL_PRESET=balanced
export USE_MULTI_AGENT=true
export LOG_LEVEL=INFO
```

## Feature Trade-offs

| Feature | Speed Impact | Benefit |
|---------|-------------|---------|
| **Performance Mode** | +300% faster | Simple, reliable responses |
| **Guardrails** | -50% slower | Prevents hallucinations |
| **Multi-Agent** | -75% slower | Better query understanding |
| **Web Search** | -25% slower | Real PartSelect integration |
| **Tool Validation** | -10% slower | Data quality checks |

## Monitoring Response Times

The system logs response times. Look for these patterns:

```
✅ Response time: 8.55 seconds          # Good for production
⚠️  Response time: 25.30 seconds        # Consider optimization
❌ Timeout after 30.00 seconds          # Enable performance mode
```

## Advanced Configuration

### Custom Timeouts
```bash
export AGENT_TIMEOUT=20                 # Total processing timeout
export GUARDRAIL_TIMEOUT=8              # Guardrail evaluation timeout  
export MULTI_AGENT_TIMEOUT=15           # Multi-agent timeout
```

### API Optimization
```bash
export DEEPSEEK_API_TIMEOUT=10          # API request timeout
export MAX_RETRIES=2                    # Reduce retry attempts
```

## Common Configurations

### E-commerce Production Site
```bash
export PERFORMANCE_MODE=true
export GUARDRAIL_ENABLED=false
# Priority: Speed over advanced features
```

### Customer Support Demo
```bash
export PERFORMANCE_MODE=false
export GUARDRAIL_ENABLED=true
export GUARDRAIL_PRESET=balanced
export USE_MULTI_AGENT=false
# Priority: Show guardrail protection
```

### AI Research/Testing
```bash
export PERFORMANCE_MODE=false
export GUARDRAIL_ENABLED=true
export GUARDRAIL_PRESET=strict
export USE_MULTI_AGENT=true
# Priority: All features enabled
``` 