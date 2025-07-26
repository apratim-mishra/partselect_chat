from typing import Dict, Any, List
import json
from datetime import datetime
import logging
from .base_agent import BaseAgent
import os
from dotenv import load_dotenv
from openai import OpenAI

from .tools import (
    search_parts, 
    check_compatibility, 
    get_installation_guide,
    get_troubleshooting_guide,
    get_part_details
)
from utils.prompts import PARTS_AGENT_SYSTEM_PROMPT
from .hallucination_guardrail import HallucinationGuardrail, GuardrailAction
from .multi_agent_system import MultiAgentOrchestrator
from .partselect_web_tools import (
    search_partselect_web,
    get_partselect_url,
    validate_model_number,
    get_popular_models,
    get_part_categories,
    get_brands
)

# Add logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PartsAgent(BaseAgent):
    """Agent specialized in refrigerator and dishwasher parts"""
    
    def __init__(self):
        # Try Deepseek first, fallback to GPT-4
        load_dotenv()
        
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if deepseek_key:
            model = "deepseek-chat"
            super().__init__(name="PartSelect Assistant", model=model)
            self.client = OpenAI(
                api_key=deepseek_key,
                base_url="https://api.deepseek.com"
            )
            logger.info("Using DeepSeek API.")
        elif openai_key:
            model = "gpt-4o-mini"
            super().__init__(name="PartSelect Assistant", model=model)
            self.client = OpenAI(api_key=openai_key)
            logger.info("Using OpenAI API as a fallback.")
        else:
            raise ValueError("API key not found. Please set either DEEPSEEK_API_KEY or OPENAI_API_KEY in your .env file.")
        
        # Initialize hallucination guardrail (only if DeepSeek key is available)
        self.guardrail = None
        if deepseek_key:
            try:
                # Configure guardrail settings
                guardrail_threshold = float(os.getenv("GUARDRAIL_THRESHOLD", "0.7"))
                guardrail_enabled = os.getenv("GUARDRAIL_ENABLED", "false").lower() == "true"  # Default to false for better performance
                
                if guardrail_enabled:
                    self.guardrail = HallucinationGuardrail(
                        api_key=deepseek_key,
                        threshold=guardrail_threshold,
                        action=GuardrailAction.WARN  # Default to warn
                    )
                    logger.info("Hallucination guardrail initialized.")
                else:
                    logger.info("Hallucination guardrail disabled by configuration.")
            except Exception as e:
                logger.warning(f"Failed to initialize guardrail: {str(e)}. Continuing without guardrail.")
                self.guardrail = None
        else:
            logger.info("Guardrail not available - DeepSeek API key required.")
        
        # Initialize multi-agent orchestrator for advanced query handling
        try:
            use_multi_agent = os.getenv("USE_MULTI_AGENT", "false").lower() == "true"  # Default to false for better performance
            if use_multi_agent and deepseek_key:
                self.multi_agent_orchestrator = MultiAgentOrchestrator(self.client, self.model)
                logger.info("Multi-agent orchestrator initialized.")
            else:
                self.multi_agent_orchestrator = None
                logger.info("Multi-agent orchestrator disabled for better performance.")
        except Exception as e:
            logger.warning(f"Failed to initialize multi-agent orchestrator: {str(e)}")
            self.multi_agent_orchestrator = None

    def get_system_prompt(self) -> str:
        return PARTS_AGENT_SYSTEM_PROMPT
    
    def get_tools(self) -> List[Dict]:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_parts",
                    "description": "Search for refrigerator or dishwasher parts by keyword, model number, or part number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (part name, number, or model)"
                            },
                            "appliance_type": {
                                "type": "string",
                                "enum": ["refrigerator", "dishwasher", "both"],
                                "description": "Type of appliance",
                                "default": "both"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_partselect_web",
                    "description": "Search PartSelect website for parts, models, brands, and categories",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for PartSelect website"
                            },
                            "appliance_type": {
                                "type": "string",
                                "enum": ["refrigerator", "dishwasher", "both"],
                                "description": "Type of appliance",
                                "default": "both"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_model_number",
                    "description": "Validate if a model number exists and get its PartSelect page",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string",
                                "description": "Model number to validate"
                            },
                            "appliance_type": {
                                "type": "string",
                                "enum": ["refrigerator", "dishwasher"],
                                "description": "Type of appliance (optional)"
                            }
                        },
                        "required": ["model"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_popular_models",
                    "description": "Get popular models for a specific appliance type",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "appliance_type": {
                                "type": "string",
                                "enum": ["refrigerator", "dishwasher"],
                                "description": "Type of appliance"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of models to return (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["appliance_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_part_categories",
                    "description": "Get available part categories for an appliance type",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "appliance_type": {
                                "type": "string",
                                "enum": ["refrigerator", "dishwasher"],
                                "description": "Type of appliance"
                            }
                        },
                        "required": ["appliance_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_brands",
                    "description": "Get available brands, optionally filtered by appliance type",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "appliance_type": {
                                "type": "string",
                                "enum": ["refrigerator", "dishwasher"],
                                "description": "Type of appliance (optional)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "check_compatibility",
                    "description": "Check if a part is compatible with a specific appliance model",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "part_number": {
                                "type": "string",
                                "description": "Part number to check"
                            },
                            "model_number": {
                                "type": "string", 
                                "description": "Appliance model number"
                            }
                        },
                        "required": ["part_number", "model_number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_installation_guide",
                    "description": "Get installation instructions for a specific part",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "part_number": {
                                "type": "string",
                                "description": "Part number"
                            }
                        },
                        "required": ["part_number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_troubleshooting_guide", 
                    "description": "Get troubleshooting guide for common appliance issues",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "issue": {
                                "type": "string",
                                "description": "Description of the issue"
                            },
                            "appliance_type": {
                                "type": "string",
                                "enum": ["refrigerator", "dishwasher"],
                                "description": "Type of appliance"
                            }
                        },
                        "required": ["issue", "appliance_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_part_details",
                    "description": "Get detailed information about a specific part",
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "part_number": {
                                "type": "string",
                                "description": "Part number"
                            }
                        },
                        "required": ["part_number"]
                    }
                }
            }
        ]
        
        return tools
    
    async def _execute_tool(self, function_name: str, function_args: Dict) -> Any:
        """Execute the appropriate tool function with error handling and guardrail validation"""
        try:
            logger.info(f"Executing tool: {function_name} with args: {function_args}")
            
            # Execute the tool function with proper parameter filtering
            if function_name == "search_parts":
                # Filter to only expected parameters
                filtered_args = {k: v for k, v in function_args.items() if k in ['query', 'appliance_type']}
                result = await search_parts(**filtered_args)
            elif function_name == "search_partselect_web":
                # Filter to only expected parameters
                filtered_args = {k: v for k, v in function_args.items() if k in ['query', 'appliance_type']}
                result = await search_partselect_web(**filtered_args)
            elif function_name == "validate_model_number":
                # Filter to only expected parameters
                filtered_args = {k: v for k, v in function_args.items() if k in ['model', 'appliance_type']}
                result = await validate_model_number(**filtered_args)
            elif function_name == "get_popular_models":
                # Filter to only expected parameters
                filtered_args = {k: v for k, v in function_args.items() if k in ['appliance_type', 'limit']}
                result = await get_popular_models(**filtered_args)
            elif function_name == "get_part_categories":
                # Filter to only expected parameters
                filtered_args = {k: v for k, v in function_args.items() if k in ['appliance_type']}
                result = await get_part_categories(**filtered_args)
            elif function_name == "get_brands":
                # Filter to only expected parameters
                filtered_args = {k: v for k, v in function_args.items() if k in ['appliance_type']}
                result = await get_brands(**filtered_args)
            elif function_name == "check_compatibility":
                # Filter to only expected parameters
                filtered_args = {k: v for k, v in function_args.items() if k in ['part_number', 'model_number']}
                result = await check_compatibility(**filtered_args)
            elif function_name == "get_installation_guide":
                # Filter to only expected parameters
                filtered_args = {k: v for k, v in function_args.items() if k in ['part_number']}
                result = await get_installation_guide(**filtered_args)
            elif function_name == "get_troubleshooting_guide":
                # Filter to only expected parameters
                filtered_args = {k: v for k, v in function_args.items() if k in ['issue', 'appliance_type']}
                result = await get_troubleshooting_guide(**filtered_args)
            elif function_name == "get_part_details":
                # Filter to only expected parameters
                filtered_args = {k: v for k, v in function_args.items() if k in ['part_number']}
                result = await get_part_details(**filtered_args)
            else:
                error_msg = f"Unknown function: {function_name}"
                logger.warning(error_msg)
                return {"error": error_msg}
            
            # Track tool usage in context if available
            if hasattr(self, '_current_context') and self._current_context:
                self._current_context["tools_used"].append(function_name)
                
                # Extract parts from tool results for context
                if function_name in ["search_parts", "get_part_details"] and result.get("found"):
                    if function_name == "search_parts":
                        parts = result.get("results", [])
                        for part in parts[:5]:  # Limit to 5 parts
                            if part.get("part_number"):
                                self._current_context["parts_found"].append(part["part_number"])
                    elif function_name == "get_part_details":
                        if result.get("part_number"):
                            self._current_context["parts_found"].append(result["part_number"])
            
            # Apply guardrail validation to tool results if enabled
            if self.guardrail and result and not result.get("error"):
                try:
                    result = await self._validate_tool_result(function_name, function_args, result)
                except Exception as e:
                    logger.warning(f"Tool result validation failed for {function_name}: {str(e)}")
                    # Continue with original result if validation fails
            
            return result
                
        except Exception as e:
            error_msg = f"Error executing {function_name}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    async def process_message(self, message: str, conversation_id: str) -> Dict[str, Any]:
        """Override to add scope checking and hallucination guardrail"""
        try:
            # Validate inputs
            if not message or not message.strip():
                return {
                    "message": "Message cannot be empty",
                    "timestamp": datetime.now().isoformat(),
                    "agent": self.name,
                    "error": True
                }
            
            # Check if message is in scope
            if not self._is_in_scope(message):
                return {
                    "message": "I'm sorry, but I can only help with refrigerator and dishwasher parts. For other appliances like ovens, microwaves, or washing machines, please visit our main website or contact our general support team.",
                    "timestamp": datetime.now().isoformat(),
                    "agent": self.name,
                    "out_of_scope": True
                }
            
            # Check for performance mode (bypass enhanced features for speed)
            performance_mode = os.getenv("PERFORMANCE_MODE", "true").lower() == "true"  # Default to true for best user experience
            if performance_mode:
                logger.info("Performance mode enabled - using fast processing")
                return await super().process_message(message, conversation_id)
            
            # Store conversation context for guardrail evaluation
            conversation_context = {
                "conversation_history": self.conversations.get(conversation_id, []),
                "tools_used": [],
                "parts_found": []
            }
            
            # Track tool usage during processing
            self._current_context = conversation_context
            
            # Use multi-agent orchestrator for complex queries if available (with timeout)
            if self.multi_agent_orchestrator:
                try:
                    logger.info("Using multi-agent orchestrator for query processing")
                    # Add timeout to multi-agent processing
                    import asyncio
                    final_response = await asyncio.wait_for(
                        self.multi_agent_orchestrator.process_query(message, conversation_context),
                        timeout=15.0  # 15 second timeout for multi-agent processing
                    )
                    
                    # Convert structured response to expected format
                    response = {
                        "message": final_response.message,
                        "timestamp": datetime.now().isoformat(),
                        "agent": self.name,
                        "query_type": final_response.response_type.value if final_response.response_type else "general_info",
                        "appliance_type": final_response.appliance_type.value if final_response.appliance_type else "both",
                        "confidence_level": final_response.confidence_level.value if final_response.confidence_level else "medium",
                        "partselect_links": final_response.partselect_links or [],
                        "recommended_actions": final_response.recommended_actions or [],
                        "key_information": final_response.key_information or {},
                        "multi_agent_used": True,
                        "disclaimer": final_response.disclaimer
                    }
                    
                    # Add to conversation history
                    self.conversations[conversation_id].append({
                        "role": "assistant",
                        "content": response["message"]
                    })
                    
                except (Exception, asyncio.TimeoutError) as e:
                    logger.warning(f"Multi-agent orchestrator failed: {str(e)}. Falling back to standard processing.")
                    # Fall back to standard processing
                    response = await super().process_message(message, conversation_id)
            else:
                # Process normally if in scope (standard single-agent mode)
                response = await super().process_message(message, conversation_id)
            
            # Apply hallucination guardrail if enabled and response is successful
            if (self.guardrail and 
                not response.get("error", False) and 
                not response.get("out_of_scope", False)):
                
                try:
                    # Collect additional context from the response
                    self._update_context_from_response(conversation_context, response)
                    
                    # Evaluate response for hallucinations with timeout
                    import asyncio
                    guardrail_result = await asyncio.wait_for(
                        self.guardrail.evaluate_response(
                            user_query=message,
                            assistant_response=response["message"],
                            context=conversation_context
                        ),
                        timeout=8.0  # 8 second timeout for guardrail evaluation
                    )
                    
                    # Apply guardrail action
                    response = self._apply_guardrail_action(response, guardrail_result, message)
                    
                    # Log guardrail results for monitoring
                    self._log_guardrail_result(message, response["message"], guardrail_result)
                    
                except (Exception, asyncio.TimeoutError) as e:
                    logger.warning(f"Guardrail evaluation failed: {str(e)}. Proceeding without guardrail.")
            
            # Clear context tracking
            self._current_context = None
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}")
            return {
                "message": error_msg,
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
                "error": True
            }
    
    def _is_in_scope(self, message: str) -> bool:
        """Enhanced scope checking with better keyword matching"""
        if not message:
            return True  # Let the base agent handle empty messages
            
        # Keywords that indicate the query is IN SCOPE (positive indicators)
        in_scope_keywords = [
            "refrigerator", "fridge", "dishwasher", "dish washer", 
            "ice maker", "freezer", "cooling", "chiller"
        ]
        
        # Keywords that indicate the query is OUT OF SCOPE (negative indicators)
        out_of_scope_keywords = [
            "oven", "stove", "range", "microwave", "washer", "washing machine", 
            "dryer", "air conditioner", "ac", "heater", "furnace", "vacuum", 
            "blender", "toaster", "coffee maker", "grill", "cooktop"
        ]
        
        message_lower = message.lower().strip()
        
        # If it explicitly mentions in-scope appliances, allow it
        for keyword in in_scope_keywords:
            if keyword in message_lower:
                return True
        
        # Check for out-of-scope appliances
        for keyword in out_of_scope_keywords:
            if keyword in message_lower:
                return False
        
        # If no clear indicators, assume it might be related to our domain
        # This prevents false negatives for general parts questions
        return True
    
    async def _validate_tool_result(self, function_name: str, function_args: Dict, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool results for potential hallucinations or inconsistencies"""
        try:
            # Create a summary of the tool result for evaluation
            result_summary = self._summarize_tool_result(function_name, function_args, result)
            
            # Quick evaluation focused on tool data quality
            tool_evaluation = await self.guardrail.evaluate_response(
                user_query=f"Tool: {function_name} with args: {function_args}",
                assistant_response=result_summary,
                context={
                    "tool_name": function_name,
                    "tool_args": function_args,
                    "is_tool_result": True
                }
            )
            
            # If tool result seems problematic, sanitize it
            if tool_evaluation.confidence_score > 0.8 and tool_evaluation.is_hallucination:
                logger.warning(f"Tool result flagged as potentially hallucinated: {function_name}")
                
                # Add warning to result
                if isinstance(result, dict):
                    result["guardrail_warning"] = "Tool result may contain inaccurate information"
                    result["guardrail_confidence"] = tool_evaluation.confidence_score
            
            return result
            
        except Exception as e:
            logger.warning(f"Tool result validation failed: {str(e)}")
            return result

    def _summarize_tool_result(self, function_name: str, function_args: Dict, result: Dict[str, Any]) -> str:
        """Create a summary of tool result for guardrail evaluation"""
        try:
            if function_name == "search_parts":
                if result.get("found"):
                    parts = result.get("results", [])
                    return f"Found {len(parts)} parts: " + ", ".join([
                        f"{p.get('part_number', 'Unknown')} ({p.get('name', 'Unknown')}) - ${p.get('price', 'Unknown')}"
                        for p in parts[:3]
                    ])
                else:
                    return "No parts found for search query"
            
            elif function_name == "check_compatibility":
                compatible = result.get("compatible", False)
                part_num = result.get("part_number", "Unknown")
                model_num = result.get("model_number", "Unknown")
                return f"Part {part_num} is {'compatible' if compatible else 'not compatible'} with model {model_num}"
            
            elif function_name == "get_installation_guide":
                if result.get("found"):
                    steps = result.get("steps", [])
                    time_est = result.get("time_estimate", "Unknown")
                    return f"Installation guide for {result.get('part_name', 'part')} - {len(steps)} steps, estimated time: {time_est}"
                else:
                    return "No installation guide found"
            
            elif function_name == "get_troubleshooting_guide":
                if result.get("found"):
                    causes = result.get("possible_causes", [])
                    solutions = result.get("solutions", [])
                    return f"Troubleshooting for {result.get('issue', 'unknown issue')} - {len(causes)} possible causes, {len(solutions)} solutions"
                else:
                    return f"No troubleshooting guide found for {result.get('issue', 'unknown issue')}"
            
            elif function_name == "get_part_details":
                if result.get("found"):
                    return f"Part details for {result.get('part_number', 'Unknown')}: {result.get('name', 'Unknown')} - ${result.get('price', 'Unknown')}"
                else:
                    return f"No details found for part {result.get('part_number', 'Unknown')}"
            
            return str(result)[:200]  # Fallback to truncated string representation
            
        except Exception as e:
            logger.warning(f"Failed to summarize tool result: {str(e)}")
            return str(result)[:100]

    def _update_context_from_response(self, context: Dict[str, Any], response: Dict[str, Any]) -> None:
        """Update context with information extracted from the response"""
        try:
            response_message = response.get("message", "")
            
            # Extract part numbers mentioned in response (simple pattern matching)
            import re
            part_numbers = re.findall(r'\b[A-Z0-9]{6,12}\b', response_message)
            if part_numbers:
                context["parts_found"] = part_numbers[:5]  # Limit to first 5
                
        except Exception as e:
            logger.warning(f"Failed to update context from response: {str(e)}")

    def _apply_guardrail_action(self, response: Dict[str, Any], guardrail_result, original_query: str) -> Dict[str, Any]:
        """Apply the appropriate action based on guardrail evaluation"""
        
        if self.guardrail.should_block_response(guardrail_result):
            # Replace response with safe fallback
            fallback_message = self.guardrail.get_fallback_response(original_query, guardrail_result)
            
            response["message"] = fallback_message
            response["guardrail_blocked"] = True
            response["guardrail_reasons"] = guardrail_result.reasons
            
        elif self.guardrail.should_warn_user(guardrail_result):
            # Append warning to existing response
            warning = self.guardrail.get_warning_message(guardrail_result)
            response["message"] += warning
            response["guardrail_warning"] = True
            response["guardrail_reasons"] = guardrail_result.reasons
        
        # Always add guardrail metadata for logging/debugging
        response["guardrail_evaluated"] = True
        response["guardrail_confidence"] = guardrail_result.confidence_score
        response["guardrail_action"] = guardrail_result.action.value
        
        return response

    def _log_guardrail_result(self, query: str, response: str, result) -> None:
        """Log guardrail evaluation results for monitoring"""
        
        log_data = {
            "query_preview": query[:100] + "..." if len(query) > 100 else query,
            "response_preview": response[:100] + "..." if len(response) > 100 else response,
            "is_hallucination": result.is_hallucination,
            "confidence": result.confidence_score,
            "action": result.action.value,
            "reasons": result.reasons[:3],  # Limit for brevity
            "severity": result.details.get("severity", "unknown")
        }
        
        if result.action == GuardrailAction.BLOCK:
            logger.warning(f"Guardrail BLOCKED response: {json.dumps(log_data)}")
        elif result.action == GuardrailAction.WARN:
            logger.info(f"Guardrail WARNED on response: {json.dumps(log_data)}")
        else:
            logger.debug(f"Guardrail evaluated response: {json.dumps(log_data)}")

    # Add missing helper method
    def _get_timestamp(self) -> str:
        return datetime.now().isoformat()