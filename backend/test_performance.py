#!/usr/bin/env python3
"""
Performance Test for Enhanced PartSelect Agent

Tests response times and timeout handling for the enhanced system.
"""

import asyncio
import time
import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.parts_agent import PartsAgent

async def test_response_time(agent, query, description, conversation_id="test_perf"):
    """Test response time for a specific query"""
    print(f"\n🧪 Testing: {description}")
    print(f"Query: {query}")
    
    start_time = time.time()
    try:
        response = await asyncio.wait_for(
            agent.process_message(query, conversation_id),
            timeout=30.0
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Response time: {duration:.2f} seconds")
        print(f"Message preview: {response.get('message', '')[:100]}...")
        
        if response.get("multi_agent_used"):
            print(f"🔄 Multi-agent system used")
        if response.get("guardrail_evaluated"):
            print(f"🛡️  Guardrail evaluated")
        if response.get("error"):
            print(f"⚠️  Error occurred")
            
        return duration, True
        
    except asyncio.TimeoutError:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ Timeout after {duration:.2f} seconds")
        return duration, False
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ Error after {duration:.2f} seconds: {str(e)}")
        return duration, False

async def main():
    """Run performance tests"""
    
    print("="*80)
    print(" PARTSELECT AGENT PERFORMANCE TEST")
    print("="*80)
    
    # Check API key
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ ERROR: DEEPSEEK_API_KEY environment variable not set!")
        print("Set PERFORMANCE_MODE=true to test without enhanced features")
        return
    
    # Test queries with different complexity levels
    test_queries = [
        {
            "query": "Hello, can you help me?",
            "description": "Simple greeting (should be fast)"
        },
        {
            "query": "I need help with my refrigerator",
            "description": "Basic appliance inquiry"
        },
        {
            "query": "How can I install part PS11752778?",
            "description": "Installation guide request (original timeout query)"
        },
        {
            "query": "Find water filters for Whirlpool fridge model WRS325FDAM04",
            "description": "Complex search with model number"
        },
        {
            "query": "Is part WPW10757757 compatible with my LG refrigerator LFX28968ST?",
            "description": "Compatibility check (complex query)"
        }
    ]
    
    # Test with enhanced features
    print("\n🚀 Testing with Enhanced Features")
    print("-" * 50)
    
    try:
        agent = PartsAgent()
        
        if agent.guardrail:
            print("✅ Guardrail system active")
        else:
            print("⚠️  Guardrail system not active")
            
        if agent.multi_agent_orchestrator:
            print("✅ Multi-agent system active")
        else:
            print("⚠️  Multi-agent system not active")
        
        enhanced_times = []
        enhanced_success = []
        
        for test in test_queries:
            duration, success = await test_response_time(
                agent, test["query"], test["description"]
            )
            enhanced_times.append(duration)
            enhanced_success.append(success)
            
            # Brief pause between tests
            await asyncio.sleep(1)
        
        print(f"\n📊 Enhanced Features Results:")
        print(f"Average response time: {sum(enhanced_times)/len(enhanced_times):.2f} seconds")
        print(f"Success rate: {sum(enhanced_success)}/{len(enhanced_success)} ({(sum(enhanced_success)/len(enhanced_success)*100):.1f}%)")
        
    except Exception as e:
        print(f"❌ Failed to test enhanced features: {str(e)}")
    
    # Test with performance mode
    print("\n⚡ Testing with Performance Mode (PERFORMANCE_MODE=true)")
    print("-" * 60)
    
    # Temporarily set performance mode
    os.environ["PERFORMANCE_MODE"] = "true"
    
    try:
        # Create new agent instance to pick up environment change
        perf_agent = PartsAgent()
        print("✅ Performance mode enabled")
        
        perf_times = []
        perf_success = []
        
        for test in test_queries:
            duration, success = await test_response_time(
                perf_agent, test["query"], test["description"], "test_perf_mode"
            )
            perf_times.append(duration)
            perf_success.append(success)
            
            # Brief pause between tests
            await asyncio.sleep(1)
        
        print(f"\n📊 Performance Mode Results:")
        print(f"Average response time: {sum(perf_times)/len(perf_times):.2f} seconds")
        print(f"Success rate: {sum(perf_success)}/{len(perf_success)} ({(sum(perf_success)/len(perf_success)*100):.1f}%)")
        
        # Compare results
        if enhanced_times and perf_times:
            avg_enhanced = sum(enhanced_times)/len(enhanced_times)
            avg_perf = sum(perf_times)/len(perf_times)
            improvement = ((avg_enhanced - avg_perf) / avg_enhanced) * 100
            
            print(f"\n🏆 Performance Comparison:")
            print(f"Enhanced mode: {avg_enhanced:.2f}s average")
            print(f"Performance mode: {avg_perf:.2f}s average")
            print(f"Speed improvement: {improvement:.1f}%")
    
    except Exception as e:
        print(f"❌ Failed to test performance mode: {str(e)}")
    finally:
        # Reset environment
        if "PERFORMANCE_MODE" in os.environ:
            del os.environ["PERFORMANCE_MODE"]
    
    print("\n" + "="*80)
    print(" PERFORMANCE TEST COMPLETE")
    print("="*80)
    print("\n💡 Recommendations:")
    print("- Set PERFORMANCE_MODE=true for fastest responses")
    print("- Set USE_MULTI_AGENT=false to disable multi-agent processing")
    print("- Set GUARDRAIL_ENABLED=false to disable guardrails if speed is critical")
    print("- Use environment variables to tune performance vs features")

if __name__ == "__main__":
    asyncio.run(main()) 