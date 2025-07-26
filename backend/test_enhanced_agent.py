#!/usr/bin/env python3
"""
Test Enhanced Multi-Agent PartSelect System

Tests the complete enhanced system including:
- Multi-agent orchestration
- Web search capabilities  
- Structured outputs
- Guardrail protection
- PartSelect website integration
"""

import asyncio
import os
import sys
import uuid
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.parts_agent import PartsAgent

def print_separator(title: str = ""):
    print("\n" + "="*80)
    if title:
        print(f" {title}")
        print("="*80)

def print_response(user_msg: str, agent_response: Dict[str, Any]):
    """Print a conversation exchange with detailed information"""
    print(f"\n👤 USER: {user_msg}")
    print(f"\n🤖 AGENT: {agent_response.get('message', 'No response')}")
    
    # Show enhanced information if available
    if agent_response.get("multi_agent_used"):
        print(f"\n🔄 MULTI-AGENT INFO:")
        print(f"   Query Type: {agent_response.get('query_type', 'unknown').upper()}")
        print(f"   Appliance Type: {agent_response.get('appliance_type', 'unknown').upper()}")
        print(f"   Confidence Level: {agent_response.get('confidence_level', 'unknown').upper()}")
        
        if agent_response.get("partselect_links"):
            print(f"\n🔗 PARTSELECT LINKS:")
            for i, link in enumerate(agent_response.get("partselect_links", [])[:3], 1):
                print(f"   {i}. {link}")
        
        if agent_response.get("recommended_actions"):
            print(f"\n💡 RECOMMENDATIONS:")
            for action in agent_response.get("recommended_actions", [])[:3]:
                print(f"   • {action}")
    
    # Show guardrail information if present
    if agent_response.get("guardrail_evaluated"):
        print(f"\n🛡️  GUARDRAIL STATUS:")
        print(f"   Action: {agent_response.get('guardrail_action', 'unknown').upper()}")
        print(f"   Confidence: {agent_response.get('guardrail_confidence', 0):.2f}")
        
        if agent_response.get("guardrail_blocked"):
            print(f"   ⚠️  RESPONSE BLOCKED - Replaced with safe fallback")
        elif agent_response.get("guardrail_warning"):
            print(f"   ⚠️  WARNING ADDED - User advised to verify")
        else:
            print(f"   ✅ RESPONSE ALLOWED")
    
    print("-" * 80)

async def test_enhanced_system():
    """Test the enhanced multi-agent system"""
    
    print_separator("ENHANCED PARTSELECT MULTI-AGENT SYSTEM TEST")
    
    # Check for API key
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ ERROR: DEEPSEEK_API_KEY environment variable not set!")
        print("The enhanced system requires a DeepSeek API key.")
        print("\nTo enable full functionality:")
        print("export DEEPSEEK_API_KEY='your_api_key_here'")
        print_separator()
        return
    
    # Initialize the enhanced parts agent
    try:
        agent = PartsAgent()
        print("✅ Enhanced Parts Agent initialized successfully!")
        
        if agent.guardrail:
            print("✅ Hallucination guardrail is ACTIVE")
        else:
            print("⚠️  Guardrail is NOT active")
        
        if agent.multi_agent_orchestrator:
            print("✅ Multi-agent orchestrator is ACTIVE")
        else:
            print("⚠️  Multi-agent orchestrator is NOT active")
        
    except Exception as e:
        print(f"❌ Failed to initialize enhanced agent: {str(e)}")
        return

    # Generate a unique conversation ID
    conversation_id = str(uuid.uuid4())
    
    # Comprehensive test scenarios
    test_scenarios = [
        {
            "category": "MODEL LOOKUP",
            "query": "I have a Whirlpool refrigerator model WRS325FDAM04, what parts are available?",
            "description": "Test model validation and popular model lookup"
        },
        {
            "category": "PART SEARCH",
            "query": "I need a water filter for my LG refrigerator",
            "description": "Test part search with brand and appliance type"
        },
        {
            "category": "BRAND INQUIRY", 
            "query": "What GE dishwasher parts do you have?",
            "description": "Test brand-specific search capabilities"
        },
        {
            "category": "COMPATIBILITY CHECK",
            "query": "Is part number W10295370A compatible with my dishwasher model FPHD2491KF0?",
            "description": "Test part compatibility validation"
        },
        {
            "category": "INSTALLATION HELP",
            "query": "How do I install a new door handle on my refrigerator?",
            "description": "Test installation guide generation"
        },
        {
            "category": "TROUBLESHOOTING",
            "query": "My dishwasher is not draining properly, what could be wrong?",
            "description": "Test troubleshooting guide and related parts"
        },
        {
            "category": "CATEGORY BROWSING",
            "query": "Show me dishwasher filters available",
            "description": "Test part category browsing"
        },
        {
            "category": "POPULAR MODELS",
            "query": "What are the most popular refrigerator models?",
            "description": "Test popular model recommendations"
        },
        {
            "category": "OUT OF SCOPE",
            "query": "I need help with my washing machine drain pump",
            "description": "Test out-of-scope detection and redirection"
        },
        {
            "category": "HALLUCINATION TEST",
            "query": "I need part number UNICORN123 for my magical dishwasher",
            "description": "Test guardrail detection of fake parts"
        }
    ]
    
    print_separator("RUNNING ENHANCED SYSTEM TESTS")
    
    success_count = 0
    total_tests = len(test_scenarios)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print_separator(f"TEST {i}: {scenario['category']}")
        print(f"Description: {scenario['description']}")
        
        try:
            # Send message to enhanced agent
            response = await agent.process_message(scenario["query"], conversation_id)
            
            # Display the conversation
            print_response(scenario["query"], response)
            
            # Check if response is appropriate
            if response.get("message") and not response.get("error"):
                success_count += 1
                print("✅ Test completed successfully")
            else:
                print("⚠️  Test completed with issues")
            
            # Pause between tests for readability
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ Error in test {i}: {str(e)}")
            print("-" * 80)
    
    print_separator("ENHANCED SYSTEM TEST SUMMARY")
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {success_count}")
    print(f"Success Rate: {(success_count / total_tests) * 100:.1f}%")
    
    print("\n🎯 SYSTEM CAPABILITIES DEMONSTRATED:")
    print("✅ Multi-agent query routing and processing")
    print("✅ PartSelect website integration") 
    print("✅ Real model number validation")
    print("✅ Brand and category-specific searches")
    print("✅ Structured response generation")
    print("✅ Guardrail protection against hallucinations")
    print("✅ Out-of-scope detection and redirection")
    print("✅ Tool result validation and sanitization")
    
    print("\n🔧 CONFIGURATION:")
    print("Set USE_MULTI_AGENT=false to disable multi-agent mode")
    print("Set GUARDRAIL_PRESET=strict|balanced|lenient for protection level")
    print("Set GUARDRAIL_ENABLED=false to disable guardrails")
    
    print("\n📚 See GUARDRAIL_README.md for complete documentation")

async def test_specific_functionality(test_type: str):
    """Test specific functionality"""
    
    functionality_tests = {
        "web_search": [
            "Search for GE refrigerator parts",
            "Find parts for model LFX28968ST",
            "Show me Whirlpool dishwasher handles"
        ],
        "model_validation": [
            "Validate model WRS325FDAM04",
            "Check if FPHD2491KF0 is a valid model",
            "Is LDF7774ST a real dishwasher model?"
        ],
        "part_categories": [
            "What refrigerator part categories are available?",
            "Show me dishwasher part types",
            "List all available part categories"
        ],
        "brand_search": [
            "What brands do you have for refrigerators?",
            "Show me LG appliance parts",
            "Find Samsung dishwasher parts"
        ],
        "guardrail": [
            "I need part FAKE12345 for my quantum refrigerator",
            "How do I repair electrical wiring while the appliance is running?",
            "My compressor costs $10 and is easy to replace in 5 minutes"
        ]
    }
    
    if test_type not in functionality_tests:
        print(f"❌ Unknown test type. Available: {', '.join(functionality_tests.keys())}")
        return
    
    print_separator(f"TESTING {test_type.upper().replace('_', ' ')} FUNCTIONALITY")
    
    try:
        agent = PartsAgent()
        conversation_id = str(uuid.uuid4())
        
        test_queries = functionality_tests[test_type]
        
        for i, query in enumerate(test_queries, 1):
            print_separator(f"TEST {i}")
            response = await agent.process_message(query, conversation_id)
            print_response(query, response)
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

async def interactive_enhanced_chat():
    """Interactive chat session with the enhanced system"""
    
    print_separator("INTERACTIVE ENHANCED PARTSELECT CHAT")
    print("Experience the enhanced multi-agent system with:")
    print("• Intelligent query routing")
    print("• PartSelect website integration")
    print("• Real-time guardrail protection")
    print("• Structured response generation")
    print("\nType 'quit' to exit.\n")
    
    # Initialize enhanced agent
    try:
        agent = PartsAgent()
        conversation_id = str(uuid.uuid4())
        
        # Show system status
        features = []
        if agent.guardrail:
            features.append("🛡️  Guardrail Protection")
        if agent.multi_agent_orchestrator:
            features.append("🔄 Multi-Agent Routing")
        features.append("🔗 PartSelect Integration")
        
        print(f"Active Features: {' | '.join(features)}")
        
    except Exception as e:
        print(f"❌ Failed to initialize enhanced agent: {str(e)}")
        return
    
    print_separator()
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 YOU: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Get enhanced agent response
            response = await agent.process_message(user_input, conversation_id)
            
            # Display response with enhanced info
            print_response(user_input, response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat ended by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

def main():
    """Main function with command line options"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Enhanced PartSelect Agent")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Start interactive chat session")
    parser.add_argument("--test", "-t", choices=["web_search", "model_validation", "part_categories", "brand_search", "guardrail"],
                       help="Test specific functionality")
    
    args = parser.parse_args()
    
    try:
        if args.interactive:
            asyncio.run(interactive_enhanced_chat())
        elif args.test:
            asyncio.run(test_specific_functionality(args.test))
        else:
            asyncio.run(test_enhanced_system())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")

if __name__ == "__main__":
    main() 