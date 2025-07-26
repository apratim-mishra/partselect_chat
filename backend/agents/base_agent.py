from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from openai import OpenAI, RateLimitError, APIError
import os
from datetime import datetime
import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Add basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, model: str = "gpt-4o-mini"):
        self.name = name
        self.model = model
        self.client: OpenAI
        self.conversations: Dict[str, List[Dict]] = {}
        self.max_conversation_length = 20  # Prevent runaway context
        self.max_tool_calls = 5 
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Dict]:
        """Return the tools available to this agent"""
        pass
    
    async def process_message(self, message: str, conversation_id: str) -> Dict[str, Any]:
        """Process a user message and return a response"""
        try:
            # Add input validation
            if not message or not message.strip():
                return {
                    "message": "Message cannot be empty",
                    "timestamp": datetime.now().isoformat(),
                    "agent": self.name,
                    "error": True
                }
            
            if not conversation_id:
                return {
                    "message": "Conversation ID is required",
                    "timestamp": datetime.now().isoformat(),
                    "agent": self.name,
                    "error": True
                }
            
            # Initialize conversation if new
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
            
            # Add user message to conversation
            self.conversations[conversation_id].append({
                "role": "user",
                "content": message.strip()  # Strip whitespace
            })
            
            # Manage conversation length
            self._manage_conversation_length(conversation_id)
            
            # Build messages for API call
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ] + self.conversations[conversation_id]
            
            # Get tools for this agent
            tools = self.get_tools()
            
            # Make API call with retry logic
            final_message = await self._make_api_call_with_retry(messages, tools, conversation_id)
            
            # Add assistant response to conversation
            self.conversations[conversation_id].append({
                "role": "assistant",
                "content": final_message or "I understand your request."  # Handle None
            })
            
            return {
                "message": final_message or "I understand your request.",
                "timestamp": datetime.now().isoformat(),
                "agent": self.name
            }
            
        except Exception as e:
            error_message = f"Error processing message: {str(e)}"
            logger.error(f"[{self.name}] {error_message}")  # Add logging
            return {
                "message": error_message,
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
                "error": True
            }
    
    @retry(
        retry=retry_if_exception_type((RateLimitError, APIError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_api_call_with_retry(self, messages: List[Dict], tools: List[Dict], conversation_id: str) -> str:
        """Make API call with retry logic"""
        try:
            if tools:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.7,
                    max_tokens=1500  # Add token limit
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1500
                )
            
            # Handle tool calls if any
            assistant_message = response.choices[0].message
            
            if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                # Limit tool calls to prevent loops
                tool_calls = assistant_message.tool_calls[:self.max_tool_calls]
                
                # Process tool calls
                tool_results = await self._process_tool_calls(tool_calls)
                
                # Add assistant message with tool calls to conversation
                self.conversations[conversation_id].append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [tc.model_dump() for tc in tool_calls]
                })
                
                # Add tool results to conversation
                for tool_result in tool_results:
                    self.conversations[conversation_id].append(tool_result)
                
                # Get final response after tool execution
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": self.get_system_prompt()}] + 
                             self.conversations[conversation_id],
                    temperature=0.7,
                    max_tokens=1500
                )
                
                final_message = final_response.choices[0].message.content
            else:
                final_message = assistant_message.content
            
            return final_message or "I understand your request."
            
        except RateLimitError:
            logger.warning(f"[{self.name}] Rate limit exceeded for conversation {conversation_id}")
            raise
        except APIError as e:
            logger.error(f"[{self.name}] API error for conversation {conversation_id}: {str(e)}")
            raise
    
    async def _process_tool_calls(self, tool_calls) -> List[Dict]:
        """Process tool calls and return results"""
        results = []
        for tool_call in tool_calls:
            try:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute the tool function
                result = await self._execute_tool(function_name, function_args)
                
                results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str)  # Handle non-serializable objects
                })
            except json.JSONDecodeError as e:
                results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": f"Invalid JSON in tool arguments: {str(e)}"})
                })
            except Exception as e:
                results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": f"Tool execution failed: {str(e)}"})
                })
        
        return results
    
    @abstractmethod
    async def _execute_tool(self, function_name: str, function_args: Dict) -> Any:
        """Execute a specific tool function"""
        pass
    
    def _manage_conversation_length(self, conversation_id: str):
        """Prevent conversations from growing too long"""
        if len(self.conversations[conversation_id]) > self.max_conversation_length:
            # Keep last N messages
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_conversation_length:]