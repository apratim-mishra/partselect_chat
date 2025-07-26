#!/usr/bin/env python3
"""
Test API Endpoint for Frontend Integration

Tests the /chat endpoint directly to verify it works properly with the frontend.
"""

import asyncio
import aiohttp
import json
import time

async def test_chat_api():
    """Test the /chat endpoint"""
    
    base_url = "http://localhost:8000"
    
    # Test queries
    test_cases = [
        {
            "message": "Hello, can you help me?",
            "conversation_id": "test_simple"
        },
        {
            "message": "How can I install part PS11752778?",
            "conversation_id": "test_complex"
        },
        {
            "message": "I need a water filter for my refrigerator",
            "conversation_id": "test_search"
        }
    ]
    
    print("🧪 Testing PartSelect API Endpoint")
    print("="*50)
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint first
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    print("✅ Backend server is running")
                else:
                    print(f"❌ Backend health check failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Cannot connect to backend: {str(e)}")
            print("Make sure the backend server is running on port 8000")
            return
        
        # Test chat endpoint
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: {test_case['message'][:50]}...")
            
            start_time = time.time()
            try:
                async with session.post(
                    f"{base_url}/chat",
                    json=test_case,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Response time: {duration:.2f}s")
                        print(f"Message preview: {data.get('message', '')[:100]}...")
                        
                        if data.get('error'):
                            print(f"⚠️  Error in response: {data.get('message')}")
                        
                        if duration > 25:
                            print(f"⚠️  Response slower than frontend timeout (25s)")
                        elif duration > 15:
                            print(f"⚠️  Response may be slow for users")
                        else:
                            print(f"✅ Good response time for production")
                            
                    else:
                        print(f"❌ HTTP {response.status}: {await response.text()}")
                        
            except asyncio.TimeoutError:
                end_time = time.time()
                duration = end_time - start_time
                print(f"❌ Timeout after {duration:.2f}s")
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                print(f"❌ Error after {duration:.2f}s: {str(e)}")
            
            # Brief pause between tests
            await asyncio.sleep(1)
    
    print("\n" + "="*50)
    print("✅ API endpoint testing complete")
    print("\n💡 If you see timeouts or slow responses:")
    print("1. Make sure PERFORMANCE_MODE=true is set")
    print("2. Set GUARDRAIL_ENABLED=false for fastest responses")
    print("3. Check your internet connection to DeepSeek API")

if __name__ == "__main__":
    asyncio.run(test_chat_api()) 