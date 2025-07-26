# Hallucination Guardrail System

A DeepSeek-powered guardrail system that evaluates and filters agent responses to prevent hallucinations and ensure accurate, safe customer service.

## 🚀 **New Default Configuration**

**Important:** As of v2.0, guardrails are **disabled by default** for optimal performance (8-20s responses). They are now an **opt-in feature** for when you need maximum accuracy and safety validation.

| Mode | Guardrails | Response Time | Use Case |
|------|------------|---------------|----------|
| **Performance (Default)** | ❌ Disabled | 8-20s | Production, user-facing |
| **Enhanced (Opt-in)** | ✅ Enabled | 25-45s | Demos, research, safety-critical |

## Overview

The guardrail system uses DeepSeek's chat model to evaluate responses from the parts agent before they're sent to users. It can:

- **Detect hallucinations**: Identify false or impossible claims about parts, pricing, or procedures
- **Check safety compliance**: Ensure installation instructions are safe and appropriate  
- **Validate scope adherence**: Confirm responses stay within refrigerator/dishwasher parts domain
- **Apply appropriate actions**: Allow, warn, block, or log responses based on evaluation

## Quick Start

### 1. Default Usage (Guardrails Disabled)

**No setup required!** The system now runs without guardrails by default for fast responses:

```bash
# Backend with performance mode (default)
uvicorn main:app --reload
# Expected response time: 8-20 seconds
```

### 2. Enable Guardrails (Opt-in)

**Option A: Use Enhanced Startup Script**
```bash
./start_enhanced.sh
# Automatically enables guardrails + multi-agent + advanced features
```

**Option B: Manual Configuration**
```bash
# Required for guardrails
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Enable guardrails
GUARDRAIL_ENABLED=true
GUARDRAIL_PRESET=balanced
GUARDRAIL_THRESHOLD=0.7

# Start server
uvicorn main:app --reload
```

### 3. Environment Variable Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GUARDRAIL_ENABLED` | **`false`** | **New default** - disabled for speed |
| `GUARDRAIL_PRESET` | `balanced` | Preset when enabled |
| `GUARDRAIL_THRESHOLD` | `0.7` | Confidence threshold |
| `DEEPSEEK_API_KEY` | - | Required when guardrails enabled |

### 4. When to Enable Guardrails

**Enable guardrails when you need:**
- 🛡️ **Safety-critical applications** - Medical, industrial, or high-risk domains
- 🎯 **Maximum accuracy** - Research, demos, or proof-of-concept work  
- 🔍 **Response validation** - Compliance, audit, or regulatory requirements
- 🧪 **AI behavior analysis** - Studying model outputs and failure modes

**Keep guardrails disabled (default) when you need:**
- ⚡ **Fast responses** - User-facing applications, production chat
- 💰 **Cost efficiency** - High-volume deployments  
- 🎯 **Simple queries** - Basic part lookup, compatibility checks
- 📱 **Mobile applications** - Where latency matters most

### 5. Test the System (When Guardrails Enabled)

```bash
# Run all test cases
cd backend
python tests/test_guardrail_examples.py

# Test a specific scenario
python tests/test_guardrail_examples.py --test "Impossible Part Number"

# Test live chat with guardrail protection
python test_live_guardrail.py

# Interactive chat session with guardrail
python test_live_guardrail.py --interactive

# View configuration help
python config/guardrail_config.py
```

### 6. Monitor in Production

The guardrail logs all evaluations and actions. Check your application logs for:

```
INFO - Guardrail WARNED on response: {"confidence": 0.8, "action": "warn", ...}
WARNING - Guardrail BLOCKED response: {"confidence": 0.9, "action": "block", ...}
```

## Configuration

> **Note:** Guardrails are **disabled by default** in v2.0. Set `GUARDRAIL_ENABLED=true` to use these configuration options.

### Presets

Choose a preset that matches your risk tolerance:

| Preset | Threshold | Description | Use Case |
|--------|-----------|-------------|----------|
| `strict` | 0.5 | Aggressive detection, blocks questionable responses | High-risk domains, new deployments |
| `balanced` | 0.7 | Blocks clear hallucinations, warns on concerns | **Default** - Production ready |
| `lenient` | 0.85 | Only warns on high-confidence issues | Established systems, low false-positive tolerance |
| `monitoring_only` | 0.3 | Logs everything but doesn't block/warn | Analysis and tuning phase |

### Fine-Tuning

Override preset settings with specific environment variables:

```bash
# Core Settings
GUARDRAIL_ENABLED=false                   # NEW DEFAULT: disabled for performance
GUARDRAIL_PRESET=balanced                 # Choose preset (when enabled)
GUARDRAIL_THRESHOLD=0.7                   # Confidence threshold (0.0-1.0)

# Action Control  
GUARDRAIL_BLOCK_HIGH=true                 # Block high-confidence hallucinations
GUARDRAIL_WARN_MEDIUM=true                # Warn on medium-confidence issues
GUARDRAIL_LOG_ALL=false                   # Log all evaluations

# Performance
GUARDRAIL_TIMEOUT=8.0                     # Max evaluation time (seconds)
DEEPSEEK_GUARDRAIL_MODEL=deepseek-chat    # Evaluation model
```

## How It Works

### 1. Response Evaluation

The guardrail evaluates responses across multiple criteria:

- **Part Accuracy**: Are part numbers realistic and properly formatted?
- **Compatibility Claims**: Are compatibility statements appropriately qualified?
- **Safety Instructions**: Are safety instructions accurate and complete?
- **Pricing Claims**: Are price ranges reasonable for appliance parts?
- **Installation Steps**: Are installation steps logical and safe?
- **Scope Adherence**: Does response stay within refrigerator/dishwasher parts?

### 2. Action Determination

Based on confidence score and severity:

```python
if confidence >= 0.8 and severity == "high":
    action = BLOCK
elif confidence >= threshold or recommendation == "block":  
    action = BLOCK if severity in ["high", "medium"] else WARN
elif confidence >= 0.3 or recommendation == "warn":
    action = WARN
else:
    action = ALLOW
```

### 3. Response Modification

- **ALLOW**: Response sent unchanged
- **WARN**: Adds warning message: "⚠️ Please verify this information..."
- **BLOCK**: Replaces with safe fallback asking for more details
- **LOG**: Records evaluation but doesn't modify response

## Integration

The guardrail is deeply integrated into the `PartsAgent` at multiple levels:

### 1. Response-Level Protection
```python
# In PartsAgent.process_message()
response = await super().process_message(message, conversation_id)

if self.guardrail and not response.get("error"):
    guardrail_result = await self.guardrail.evaluate_response(
        user_query=message,
        assistant_response=response["message"],
        context=conversation_context
    )
    response = self._apply_guardrail_action(response, guardrail_result, message)
```

### 2. Tool-Level Validation
```python
# In PartsAgent._execute_tool()
result = await search_parts(**function_args)

if self.guardrail and result and not result.get("error"):
    result = await self._validate_tool_result(function_name, function_args, result)
```

### 3. Data-Level Sanitization
```python
# In tools.py functions
if not validate_part_number(part_number):
    logger.warning(f"Skipping part with invalid part number: {part_number}")
    continue

if not validate_price(price):
    logger.warning(f"Skipping part with invalid price: {price}")
    continue
```

Response includes guardrail metadata:

```json
{
    "message": "Response text...",
    "guardrail_evaluated": true,
    "guardrail_confidence": 0.3,
    "guardrail_action": "allow",
    "guardrail_warning": false,
    "guardrail_blocked": false
}
```

## Test Cases

The system includes comprehensive test cases covering:

1. **Valid Part Recommendation** - Should allow accurate, helpful responses
2. **Impossible Part Number** - Should block clearly hallucinated parts  
3. **Unrealistic Price Claim** - Should warn on dangerous misinformation
4. **Out of Scope Response** - Should block off-topic responses
5. **Unsafe Installation Advice** - Should block dangerous instructions
6. **Qualified Uncertain Response** - Should allow appropriately cautious responses
7. **Minor Inaccuracy** - Should allow responses with acceptable variations
8. **Vague but Safe Response** - Should allow cautious, information-seeking responses

Run tests to validate the system:

```bash
python tests/test_guardrail_examples.py
```

## Performance Considerations

- **Latency**: Adds ~1-3 seconds per response (configurable timeout)
- **Cost**: Each evaluation costs ~$0.002-0.005 (DeepSeek pricing)
- **Reliability**: Falls back gracefully if evaluation fails
- **Scalability**: Can be disabled per environment or request

## Monitoring and Debugging

### Log Levels

- **DEBUG**: All evaluations with full details
- **INFO**: Warnings and notable events  
- **WARNING**: Blocked responses and errors
- **ERROR**: System failures

### Metrics to Track

- Evaluation success rate
- Action distribution (allow/warn/block/log)
- Average confidence scores
- Response time impact
- False positive/negative rates

### Debugging Tools

```bash
# Test specific scenarios
python tests/test_guardrail_examples.py --test "Test Name"

# View configuration
python config/guardrail_config.py

# Enable debug logging
export LOG_LEVEL=DEBUG
```

## Troubleshooting

### Common Issues

**Guardrail not initializing**
- Check `DEEPSEEK_API_KEY` is set
- Verify API key has sufficient credits
- Check network connectivity to `api.deepseek.com`

**Too many false positives**
- Increase `GUARDRAIL_THRESHOLD` (try 0.8-0.9)
- Switch to `lenient` preset
- Review log details for common patterns

**Too many false negatives**  
- Decrease `GUARDRAIL_THRESHOLD` (try 0.5-0.6)
- Switch to `strict` preset
- Add domain-specific test cases

**High latency**
- Reduce `GUARDRAIL_TIMEOUT`
- Consider `monitoring_only` mode for analysis
- Implement async processing for non-critical paths

### Getting Help

1. Check logs for detailed error messages
2. Run test cases to isolate issues  
3. Review configuration with `python config/guardrail_config.py`
4. Test individual components with the test scripts

## API Reference

### HallucinationGuardrail

Main guardrail class for evaluating responses.

```python
guardrail = HallucinationGuardrail(
    api_key="your_key",
    threshold=0.7,
    action=GuardrailAction.WARN
)

result = await guardrail.evaluate_response(
    user_query="User's question",
    assistant_response="Agent's response", 
    context={"tools_used": [...], "parts_found": [...]}
)
```

### GuardrailResult

Evaluation result containing action and reasoning.

```python
@dataclass
class GuardrailResult:
    is_hallucination: bool
    confidence_score: float  # 0-1
    reasons: List[str]
    action: GuardrailAction
    details: Dict[str, Any]
```

### GuardrailAction

Actions the system can take.

```python
class GuardrailAction(Enum):
    ALLOW = "allow"      # Send response unchanged
    WARN = "warn"        # Add warning message
    BLOCK = "block"      # Replace with fallback
    LOG = "log"          # Record but don't modify
``` 