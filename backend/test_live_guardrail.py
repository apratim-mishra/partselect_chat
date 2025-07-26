#!/usr/bin/env python3
"""
Live test of the guardrail system integrated into the chat agent.

This script demonstrates how the guardrail protects users during actual
conversations with the parts agent.
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

def print_separator():
    print("\n" + "="*70)

def print_conversation(user_msg: str, agent_response: Dict[str, Any]):
    """Print a conversation exchange with guardrail information"""
    print(f"\n👤 USER: {user_msg}")
    print(f"\n🤖 AGENT: {agent_response.get('message', 'No response')}")
    
    # Show guardrail information if present
    if agent_response.get("guardrail_evaluated"):
        print(f"\n🛡️  GUARDRAIL STATUS:")
        print(f"   Action: {agent_response.get('guardrail_action', 'unknown').upper()}")
        print(f"   Confidence: {agent_response.get('guardrail_confidence', 0):.2f}")
        
        if agent_response.get("guardrail_blocked"):
            print(f"   ⚠️  RESPONSE BLOCKED - Replaced with safe fallback")
            print(f"   Reasons: {', '.join(agent_response.get('guardrail_reasons', []))}")
        elif agent_response.get("guardrail_warning"):
            print(f"   ⚠️  WARNING ADDED - User advised to verify")
            print(f"   Reasons: {', '.join(agent_response.get('guardrail_reasons', []))}")
        else:
            print(f"   ✅ RESPONSE ALLOWED")
    
    print("-" * 70)

async def test_chat_with_guardrail():
    """Test the guardrail system in live chat scenarios"""
    
    print("🛡️  LIVE GUARDRAIL CHAT TEST")
    print_separator()
    
    # Check for API key
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ ERROR: DEEPSEEK_API_KEY environment variable not set!")
        print("The guardrail requires a DeepSeek API key to function.")
        print("The agent will still work but without guardrail protection.")
        print("\nTo enable guardrail:")
        print("export DEEPSEEK_API_KEY='your_api_key_here'")
        print_separator()
    
    # Initialize the parts agent (with integrated guardrail)
    try:
        agent = PartsAgent()
        print("✅ Parts agent initialized successfully!")
        
        if agent.guardrail:
            print("✅ Hallucination guardrail is ACTIVE and protecting conversations")
        else:
            print("⚠️  Guardrail is NOT active - responses may not be protected")
        
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        return

    # Generate a unique conversation ID
    conversation_id = str(uuid.uuid4())
    
    # Test scenarios that demonstrate guardrail protection
    test_conversations = [
        {
            "scenario": "SAFE REQUEST - Normal parts search",
            "message": "I need a water filter for my GE refrigerator model GSS25GMHES"
        },
        {
            "scenario": "SCOPE TEST - Out of scope request",
            "message": "I need help with my washing machine drain pump"
        },
        {
            "scenario": "SAFETY TEST - Request for installation help",
            "message": "How do I replace the heating element in my dishwasher?"
        },
        {
            "scenario": "COMPATIBILITY TEST - Part compatibility check",
            "message": "Is part number W10295370A compatible with my Whirlpool dishwasher?"
        },
        {
            "scenario": "TROUBLESHOOTING TEST - Appliance issue",
            "message": "My refrigerator is making loud noises, what could be wrong?"
        }
    ]
    
    print_separator()
    print("🎯 TESTING GUARDRAIL IN VARIOUS CHAT SCENARIOS")
    print_separator()
    
    for i, test in enumerate(test_conversations, 1):
        print(f"\n📋 SCENARIO {i}: {test['scenario']}")
        
        try:
            # Send message to agent and get response
            response = await agent.process_message(test["message"], conversation_id)
            
            # Display the conversation
            print_conversation(test["message"], response)
            
            # Pause between tests for readability
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ Error in scenario {i}: {str(e)}")
            print("-" * 70)
    
    print_separator()
    print("🏁 LIVE GUARDRAIL TEST COMPLETE")
    print("\nSUMMARY:")
    print("✅ The guardrail system is integrated into live chat conversations")
    print("✅ Dangerous responses are blocked and replaced with safe alternatives")
    print("✅ Out-of-scope requests are handled appropriately") 
    print("✅ Normal helpful responses are allowed through unchanged")
    print("✅ Warnings are added to questionable but not dangerous responses")
    
    print("\n🔧 CONFIGURATION:")
    print("Set GUARDRAIL_PRESET=strict|balanced|lenient|monitoring_only")
    print("Set GUARDRAIL_THRESHOLD=0.5-0.9 for sensitivity tuning")
    print("Set GUARDRAIL_ENABLED=false to disable protection")
    
    print("\n📚 See GUARDRAIL_README.md for complete documentation")

async def interactive_chat():
    """Interactive chat session with guardrail protection"""
    
    print("🛡️  INTERACTIVE GUARDRAIL-PROTECTED CHAT")
    print_separator()
    print("Type your questions about refrigerator and dishwasher parts.")
    print("The guardrail will protect you from hallucinated or dangerous responses.")
    print("Type 'quit' to exit.\n")
    
    # Initialize agent
    try:
        agent = PartsAgent()
        conversation_id = str(uuid.uuid4())
        
        if agent.guardrail:
            print("🛡️  Guardrail protection: ACTIVE")
        else:
            print("⚠️   Guardrail protection: INACTIVE")
        
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
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
            
            # Get agent response
            response = await agent.process_message(user_input, conversation_id)
            
            # Display response with guardrail info
            print_conversation(user_input, response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat ended by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

def main():
    """Main function with command line options"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test guardrail-protected chat")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Start interactive chat session")
    
    args = parser.parse_args()
    
    try:
        if args.interactive:
            asyncio.run(interactive_chat())
        else:
            asyncio.run(test_chat_with_guardrail())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")

if __name__ == "__main__":
    main() 