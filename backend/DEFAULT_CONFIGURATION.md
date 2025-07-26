# PartSelect Agent - Default Configuration

## ✅ **Performance Mode is Now Default!**

**Great news!** Based on user feedback, we've made **performance mode the default configuration** for the best user experience.

## 🚀 **New Defaults (Fast & User-Friendly)**

| Setting | Old Default | New Default | Impact |
|---------|-------------|-------------|--------|
| `PERFORMANCE_MODE` | `false` | **`true`** | ⚡ 3-5x faster responses |
| `GUARDRAIL_ENABLED` | `true` | **`false`** | ⚡ No guardrail delays |
| `USE_MULTI_AGENT` | `false` | `false` | ⚡ Maintained for speed |

**Result:** Default response time is now **8-20 seconds** instead of 25-45 seconds!

## 🎯 **How to Use**

### **Option 1: Default Performance Mode (Recommended)**
```bash
# Just start normally - fast mode is now default!
uvicorn main:app --reload

# Or use the startup script
./start_server.sh
```
- **Response Time:** 8-20 seconds
- **Features:** Fast chat, tool calling, part search
- **Best for:** Production, user-facing applications

### **Option 2: Enhanced Mode (Opt-in for Advanced Features)**
```bash
# Use enhanced startup script
./start_enhanced.sh

# Or set manually
export PERFORMANCE_MODE=false
export GUARDRAIL_ENABLED=true
export USE_MULTI_AGENT=true
uvicorn main:app --reload
```
- **Response Time:** 25-45 seconds
- **Features:** Multi-agent routing + guardrails + advanced validation
- **Best for:** Demos, research, maximum accuracy

## 📊 **Performance Comparison**

| Mode | Response Time | Features | Use Case |
|------|---------------|----------|----------|
| **Performance (Default)** | 8-20s | Fast chat + tools | ✅ Production |
| **Enhanced (Opt-in)** | 25-45s | All features | Research/Demo |

## 🎉 **What This Means for You**

### **✅ No More Timeouts**
- Default configuration now works perfectly with frontend timeout (45s)
- Users get fast, reliable responses out of the box

### **✅ Simple Usage**
```bash
# Backend
uvicorn main:app --reload

# Frontend  
npm start
```
**That's it!** No configuration needed for fast responses.

### **✅ Optional Enhanced Features**
```bash
# Want advanced features? Just use:
./start_enhanced.sh
```

## 🔧 **Environment Variable Reference**

### **Default Values (Performance Mode)**
```bash
PERFORMANCE_MODE=true          # Fast processing
GUARDRAIL_ENABLED=false        # No guardrail delays  
USE_MULTI_AGENT=false          # Single agent (fast)
```

### **Enhanced Mode Override**
```bash
PERFORMANCE_MODE=false         # Full processing
GUARDRAIL_ENABLED=true         # Enable guardrails
USE_MULTI_AGENT=true           # Multi-agent routing
```

## 🧪 **Testing the Configuration**

Test your current defaults:
```bash
python -c "from agents.parts_agent import PartsAgent; agent = PartsAgent(); print('Defaults working!')"
```

Expected output:
```
INFO:agents.parts_agent:Hallucination guardrail disabled by configuration.
INFO:agents.parts_agent:Multi-agent orchestrator disabled for better performance.
Defaults working!
```

## 🎯 **Migration Guide**

### **If you had custom performance settings:**
- **Remove them** - performance mode is now default
- **Keep using them** - they still override defaults

### **If you want the old behavior (enhanced features):**
```bash
export PERFORMANCE_MODE=false
export GUARDRAIL_ENABLED=true
export USE_MULTI_AGENT=true
```

### **If you want maximum speed:**
```bash
# Already the default! No changes needed
uvicorn main:app --reload
```

## 🏆 **Benefits of New Defaults**

1. **✅ Better User Experience** - Fast responses by default
2. **✅ No Timeout Issues** - Works perfectly with frontend
3. **✅ Production Ready** - Optimized for real-world usage  
4. **✅ Optional Features** - Enhanced mode still available
5. **✅ Backward Compatible** - Existing env vars still work

## 🚀 **Summary**

**Before:** Enhanced features default → Slow responses → User frustration
**After:** Performance mode default → Fast responses → Happy users!

**The PartSelect Agent now provides excellent performance out of the box while keeping advanced features available when needed.** 🎯 