"""
Multi-Agent System for PartSelect
Implements routing, handoffs, and parallel execution based on important_info.md techniques
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from openai import OpenAI
import re

from .structured_outputs import *
from .partselect_web_tools import *
from .tools import search_parts, check_compatibility, get_installation_guide, get_troubleshooting_guide, get_part_details

logger = logging.getLogger(__name__)

class BaseSpecializedAgent:
    """Base class for specialized agents"""
    
    def __init__(self, name: str, client: OpenAI, model: str = "deepseek-chat"):
        self.name = name
        self.client = client
        self.model = model
        
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process a query and return structured response"""
        raise NotImplementedError

class TriagingAgent(BaseSpecializedAgent):
    """Routes queries to appropriate agents based on classification"""
    
    def __init__(self, client: OpenAI, model: str = "deepseek-chat"):
        super().__init__("TriagingAgent", client, model)
        
    def get_system_prompt(self) -> str:
        return """You are a Triaging Agent for PartSelect, a parts e-commerce website. Your role is to analyze user queries and classify them for routing to specialized agents.

You must classify queries into one of these types:
- part_search: User wants to find specific parts
- model_lookup: User wants information about a specific model
- compatibility_check: User wants to check if a part fits their model  
- installation_guide: User needs installation instructions
- troubleshooting: User has an appliance problem to diagnose
- brand_inquiry: User asking about specific brands
- general_info: General questions about appliances/parts
- out_of_scope: Questions outside refrigerator/dishwasher domain

Extract entities like:
- Model numbers (format: alphanumeric 6-15 characters)
- Part names/types (filters, handles, motors, etc.)
- Brand names (GE, Whirlpool, LG, etc.)
- Appliance types (refrigerator, dishwasher)

Determine urgency and confidence levels. Always explain your reasoning.

RESPOND WITH VALID JSON IN THIS EXACT FORMAT:
{
  "query_type": "part_search|model_lookup|compatibility_check|installation_guide|troubleshooting|brand_inquiry|general_info|out_of_scope",
  "appliance_type": "refrigerator|dishwasher|both",
  "urgency": "low|medium|high|emergency",
  "confidence": "low|medium|high|very_high",
  "requires_model_number": true|false,
  "extracted_entities": {
    "model_number": "string or null",
    "brand": "string or null",
    "part_category": "string or null"
  },
  "reasoning": "explanation for classification"
}"""

    async def classify_query(self, query: str, context: Dict[str, Any] = None) -> QueryClassification:
        """Classify user query for routing"""
        try:
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": f"Classify this query: '{query}'"}
            ]
            
            # Use regular completion with JSON mode (DeepSeek doesn't support structured outputs)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages + [{"role": "system", "content": "Respond with valid JSON matching the QueryClassification schema."}],
                temperature=0.1
            )
            
            # Parse the JSON response manually
            try:
                import json
                response_content = response.choices[0].message.content
                # Remove markdown code blocks if present
                if "```json" in response_content:
                    response_content = response_content.split("```json")[1].split("```")[0].strip()
                elif "```" in response_content:
                    response_content = response_content.split("```")[1].split("```")[0].strip()
                
                classification_data = json.loads(response_content)
                return QueryClassification(**classification_data)
            except Exception as parse_error:
                logger.warning(f"Failed to parse classification JSON: {parse_error}")
                # Create a basic fallback classification
                appliance_type = ApplianceType.BOTH
                query_lower = query.lower()
                if "refrigerator" in query_lower or "fridge" in query_lower:
                    appliance_type = ApplianceType.REFRIGERATOR
                elif "dishwasher" in query_lower:
                    appliance_type = ApplianceType.DISHWASHER
                
                return QueryClassification(
                    query_type=QueryType.GENERAL_INFO,
                    appliance_type=appliance_type,
                    urgency=UrgencyLevel.LOW,
                    confidence=ConfidenceLevel.MEDIUM,
                    requires_model_number=False,
                    extracted_entities={},
                    reasoning="Fallback classification due to parsing error"
                )
            
        except Exception as e:
            logger.error(f"Error classifying query: {str(e)}")
            # Fallback classification
            return QueryClassification(
                query_type=QueryType.GENERAL_INFO,
                appliance_type=ApplianceType.BOTH,
                urgency=UrgencyLevel.LOW,
                confidence=ConfidenceLevel.LOW,
                requires_model_number=False,
                extracted_entities={},
                reasoning="Error in classification, using fallback"
            )
    
    async def route_query(self, classification: QueryClassification) -> AgentRouting:
        """Determine which agents should handle the query"""
        routing_map = {
            QueryType.PART_SEARCH: {
                "primary": "ProductSearchAgent",
                "secondary": ["WebSearchAgent"],
                "parallel": False
            },
            QueryType.MODEL_LOOKUP: {
                "primary": "ModelLookupAgent", 
                "secondary": ["ProductSearchAgent"],
                "parallel": False
            },
            QueryType.COMPATIBILITY_CHECK: {
                "primary": "ProductSearchAgent",
                "secondary": ["WebSearchAgent"],
                "parallel": False
            },
            QueryType.INSTALLATION_GUIDE: {
                "primary": "WebSearchAgent",
                "secondary": ["ProductSearchAgent"],
                "parallel": False
            },
            QueryType.TROUBLESHOOTING: {
                "primary": "WebSearchAgent",
                "secondary": ["ProductSearchAgent"],
                "parallel": False
            },
            QueryType.BRAND_INQUIRY: {
                "primary": "WebSearchAgent",
                "secondary": ["ProductSearchAgent"],
                "parallel": True
            },
            QueryType.GENERAL_INFO: {
                "primary": "WebSearchAgent",
                "secondary": [],
                "parallel": False
            },
            QueryType.OUT_OF_SCOPE: {
                "primary": "OutOfScopeAgent",
                "secondary": [],
                "parallel": False
            }
        }
        
        route_config = routing_map.get(classification.query_type, routing_map[QueryType.GENERAL_INFO])
        
        return AgentRouting(
            primary_agent=route_config["primary"],
            secondary_agents=route_config["secondary"],
            parallel_execution=route_config["parallel"],
            routing_reason=f"Query classified as {classification.query_type.value} with {classification.confidence.value} confidence"
        )

class ProductSearchAgent(BaseSpecializedAgent):
    """Specialized agent for product/parts search"""
    
    def __init__(self, client: OpenAI, model: str = "deepseek-chat"):
        super().__init__("ProductSearchAgent", client, model)
    
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Search for parts based on query"""
        try:
            classification = context.get("classification") if context else None
            
            # Extract search criteria from query and classification
            criteria = await self._extract_search_criteria(query, classification)
            
            # Search using multiple methods
            search_results = []
            partselect_links = []
            
            # 1. Search local database
            db_results = await search_parts(
                criteria.search_query, 
                criteria.appliance_type.value if criteria.appliance_type != ApplianceType.BOTH else "both"
            )
            
            if db_results.get("found"):
                for part in db_results.get("results", []):
                    search_results.append(PartInfo(
                        part_number=part.get("part_number", ""),
                        name=part.get("name", ""),
                        description=part.get("description", ""),
                        price=part.get("price", 0.0),
                        brand="Unknown",  # DB doesn't have brand info
                        appliance_type=ApplianceType(part.get("appliance_type", "both")),
                        in_stock=part.get("in_stock", True),
                        image_url=part.get("image_url"),
                        partselect_url=None,
                        oem_compatible=True
                    ))
            
            # 2. Search PartSelect web
            web_results = await search_partselect_web(
                criteria.search_query,
                criteria.appliance_type.value if criteria.appliance_type != ApplianceType.BOTH else "both"
            )
            
            if web_results.get("found"):
                for result in web_results.get("results", []):
                    partselect_links.append(result["url"])
            
            # Create structured result
            result = PartSearchResult(
                found=len(search_results) > 0 or len(partselect_links) > 0,
                count=len(search_results),
                parts=search_results[:10],  # Limit results
                search_criteria=criteria,
                suggestions=self._generate_suggestions(criteria, search_results),
                related_categories=self._get_related_categories(criteria.appliance_type)
            )
            
            # Generate response message
            message = self._format_search_response(result, partselect_links)
            
            return AgentResponse(
                agent_name=self.name,
                success=result.found,
                message=message,
                data=result.dict(),
                confidence=ConfidenceLevel.HIGH if result.found else ConfidenceLevel.LOW,
                suggestions=result.suggestions,
                partselect_links=partselect_links,
                requires_followup=not result.found,
                followup_questions=self._generate_followup_questions(criteria) if not result.found else []
            )
            
        except Exception as e:
            logger.error(f"Error in ProductSearchAgent: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=f"I encountered an error while searching for parts: {str(e)}",
                confidence=ConfidenceLevel.LOW,
                requires_followup=True,
                followup_questions=["Could you provide more specific details about the part you're looking for?"]
            )
    
    async def _extract_search_criteria(self, query: str, classification: QueryClassification = None) -> PartSearchCriteria:
        """Extract search criteria from query"""
        # Use classification if available
        if classification:
            appliance_type = classification.appliance_type
            entities = classification.extracted_entities
        else:
            # Basic extraction
            appliance_type = ApplianceType.BOTH
            entities = {}
            
            if "refrigerator" in query.lower() or "fridge" in query.lower():
                appliance_type = ApplianceType.REFRIGERATOR
            elif "dishwasher" in query.lower():
                appliance_type = ApplianceType.DISHWASHER
        
        return PartSearchCriteria(
            search_query=query,
            appliance_type=appliance_type,
            brand=entities.get("brand"),
            model_number=entities.get("model_number"),
            part_category=entities.get("part_category")
        )
    
    def _generate_suggestions(self, criteria: PartSearchCriteria, results: List[PartInfo]) -> List[str]:
        """Generate search suggestions"""
        suggestions = []
        
        if not results:
            if criteria.appliance_type == ApplianceType.BOTH:
                suggestions.append("Try specifying whether you need refrigerator or dishwasher parts")
            
            suggestions.append("Provide your appliance model number for better results")
            suggestions.append("Try searching for the part category (e.g., 'filters', 'handles', 'motors')")
        
        return suggestions
    
    def _get_related_categories(self, appliance_type: ApplianceType) -> List[str]:
        """Get related part categories"""
        if appliance_type == ApplianceType.REFRIGERATOR:
            return ["Filters", "Handles", "Shelves", "Ice Makers", "Motors"][:5]
        elif appliance_type == ApplianceType.DISHWASHER:
            return ["Racks", "Filters", "Spray Arms", "Pumps", "Latches"][:5]
        else:
            return ["Filters", "Handles", "Motors", "Pumps", "Racks"][:5]
    
    def _format_search_response(self, result: PartSearchResult, partselect_links: List[str]) -> str:
        """Format the search response message"""
        if not result.found:
            return f"I couldn't find specific parts matching '{result.search_criteria.search_query}'. {' '.join(result.suggestions)}"
        
        message = f"I found {result.count} parts for your search:\n\n"
        
        for i, part in enumerate(result.parts[:3], 1):  # Show top 3
            message += f"{i}. **{part.name}** (Part #{part.part_number})\n"
            message += f"   - Price: ${part.price:.2f}\n"
            message += f"   - {part.description}\n"
            message += f"   - {'In Stock' if part.in_stock else 'Out of Stock'}\n\n"
        
        if partselect_links:
            message += "**Relevant PartSelect Pages:**\n"
            for i, link in enumerate(partselect_links[:3], 1):
                message += f"{i}. {link}\n"
        
        return message
    
    def _generate_followup_questions(self, criteria: PartSearchCriteria) -> List[str]:
        """Generate follow-up questions"""
        questions = []
        
        if not criteria.model_number:
            questions.append("What's the model number of your appliance?")
        
        if not criteria.part_category:
            questions.append("What type of part are you looking for (e.g., filter, handle, motor)?")
        
        if criteria.appliance_type == ApplianceType.BOTH:
            questions.append("Is this for a refrigerator or dishwasher?")
        
        return questions

class ModelLookupAgent(BaseSpecializedAgent):
    """Specialized agent for model number lookup and validation"""
    
    def __init__(self, client: OpenAI, model: str = "deepseek-chat"):
        super().__init__("ModelLookupAgent", client, model)
    
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Look up model information"""
        try:
            # Extract model number from query
            model_numbers = self._extract_model_numbers(query)
            
            if not model_numbers:
                return AgentResponse(
                    agent_name=self.name,
                    success=False,
                    message="I couldn't find a valid model number in your query. Could you please provide the model number?",
                    confidence=ConfidenceLevel.LOW,
                    requires_followup=True,
                    followup_questions=["What's the model number of your appliance?"]
                )
            
            # Validate each model number
            results = []
            partselect_links = []
            
            for model in model_numbers:
                validation = await validate_model_number(model)
                
                if validation.get("valid"):
                    appliance_type = validation.get("appliance_type", "unknown")
                    
                    model_info = ModelValidation(
                        is_valid=True,
                        model_number=validation["model"],
                        appliance_type=ApplianceType(appliance_type) if appliance_type in ["refrigerator", "dishwasher"] else ApplianceType.BOTH,
                        confidence=ConfidenceLevel(validation.get("confidence", "medium")),
                        partselect_url=validation.get("url"),
                        validation_notes=validation.get("notes", [])
                    )
                    
                    results.append(model_info)
                    if validation.get("url"):
                        partselect_links.append(validation["url"])
            
            # Get popular models if validation successful
            similar_models = []
            if results:
                main_result = results[0]
                if main_result.appliance_type != ApplianceType.BOTH:
                    popular_result = await get_popular_models(main_result.appliance_type.value, limit=5)
                    if popular_result.get("found"):
                        for model_data in popular_result.get("models", []):
                            similar_models.append(PopularModel(
                                model_number=model_data["model"],
                                appliance_type=ApplianceType(model_data["appliance_type"]),
                                partselect_url=model_data["url"]
                            ))
            
            # Create response
            if results:
                main_result = results[0]
                message = f"✅ **Model {main_result.model_number}** is a valid {main_result.appliance_type.value} model.\n\n"
                message += f"**PartSelect Page:** {main_result.partselect_url}\n\n"
                
                if similar_models:
                    message += "**Similar Popular Models:**\n"
                    for model in similar_models[:3]:
                        message += f"- {model.model_number}\n"
                
                return AgentResponse(
                    agent_name=self.name,
                    success=True,
                    message=message,
                    data={"model_info": main_result.dict(), "similar_models": [m.dict() for m in similar_models]},
                    confidence=main_result.confidence,
                    partselect_links=partselect_links,
                    suggestions=["You can now search for parts for this model", "Check installation guides for specific parts"]
                )
            else:
                return AgentResponse(
                    agent_name=self.name,
                    success=False,
                    message="I couldn't validate the model number you provided. Please double-check the model number.",
                    confidence=ConfidenceLevel.LOW,
                    requires_followup=True,
                    followup_questions=["Could you verify the model number?", "Where did you find this model number on your appliance?"]
                )
                
        except Exception as e:
            logger.error(f"Error in ModelLookupAgent: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=f"I encountered an error while looking up the model: {str(e)}",
                confidence=ConfidenceLevel.LOW
            )
    
    def _extract_model_numbers(self, query: str) -> List[str]:
        """Extract potential model numbers from query"""
        # Look for patterns that look like model numbers
        patterns = [
            r'\b[A-Z]{2,}[0-9]{3,}[A-Z0-9]*\b',  # Letters followed by numbers
            r'\b[0-9]{3,}[A-Z]{2,}[A-Z0-9]*\b',  # Numbers followed by letters
            r'\b[A-Z0-9]{6,15}\b'  # General alphanumeric 6-15 chars
        ]
        
        models = []
        for pattern in patterns:
            matches = re.findall(pattern, query.upper())
            models.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_models = []
        for model in models:
            if model not in seen:
                seen.add(model)
                unique_models.append(model)
        
        return unique_models

class WebSearchAgent(BaseSpecializedAgent):
    """Specialized agent for web search on PartSelect"""
    
    def __init__(self, client: OpenAI, model: str = "deepseek-chat"):
        super().__init__("WebSearchAgent", client, model)
    
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Perform web search and return results"""
        try:
            classification = context.get("classification") if context else None
            appliance_type = "both"
            
            if classification:
                appliance_type = classification.appliance_type.value
            
            # Perform web search
            search_results = await search_partselect_web(query, appliance_type)
            
            if search_results.get("found"):
                message = f"I found {search_results['count']} relevant results on PartSelect:\n\n"
                
                partselect_links = []
                for i, result in enumerate(search_results.get("results", [])[:5], 1):
                    message += f"{i}. **{result['title']}**\n"
                    message += f"   {result['snippet']}\n"
                    message += f"   🔗 {result['url']}\n\n"
                    partselect_links.append(result["url"])
                
                return AgentResponse(
                    agent_name=self.name,
                    success=True,
                    message=message,
                    data=search_results,
                    confidence=ConfidenceLevel.HIGH,
                    partselect_links=partselect_links,
                    suggestions=["Click the links above to browse parts", "Use model numbers for more specific results"]
                )
            else:
                return AgentResponse(
                    agent_name=self.name,
                    success=False,
                    message="I couldn't find specific results for your query on PartSelect. Try using different search terms.",
                    confidence=ConfidenceLevel.LOW,
                    requires_followup=True,
                    followup_questions=["Could you provide more details about what you're looking for?"]
                )
                
        except Exception as e:
            logger.error(f"Error in WebSearchAgent: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=f"I encountered an error during web search: {str(e)}",
                confidence=ConfidenceLevel.LOW
            )

class MultiAgentOrchestrator:
    """Main orchestrator for the multi-agent system"""
    
    def __init__(self, client: OpenAI, model: str = "deepseek-chat"):
        self.client = client
        self.model = model
        
        # Initialize specialized agents
        self.triaging_agent = TriagingAgent(client, model)
        self.product_search_agent = ProductSearchAgent(client, model)
        self.model_lookup_agent = ModelLookupAgent(client, model)
        self.web_search_agent = WebSearchAgent(client, model)
        
        # Agent registry
        self.agents = {
            "TriagingAgent": self.triaging_agent,
            "ProductSearchAgent": self.product_search_agent,
            "ModelLookupAgent": self.model_lookup_agent,
            "WebSearchAgent": self.web_search_agent
        }
    
    async def process_query(self, query: str, conversation_context: Dict[str, Any] = None) -> FinalResponse:
        """Process a user query through the multi-agent system"""
        try:
            # Step 1: Classify and route the query
            classification = await self.triaging_agent.classify_query(query, conversation_context)
            routing = await self.triaging_agent.route_query(classification)
            
            # Step 2: Prepare context for agents
            agent_context = {
                "classification": classification,
                "routing": routing,
                "conversation_context": conversation_context or {}
            }
            
            # Step 3: Execute primary agent
            primary_agent = self.agents.get(routing.primary_agent)
            if not primary_agent:
                raise ValueError(f"Unknown primary agent: {routing.primary_agent}")
            
            primary_response = await primary_agent.process(query, agent_context)
            
            # Step 4: Execute secondary agents if needed
            secondary_responses = []
            if routing.secondary_agents and not primary_response.success:
                if routing.parallel_execution:
                    # Parallel execution
                    tasks = []
                    for agent_name in routing.secondary_agents:
                        agent = self.agents.get(agent_name)
                        if agent:
                            tasks.append(agent.process(query, agent_context))
                    
                    if tasks:
                        secondary_responses = await asyncio.gather(*tasks, return_exceptions=True)
                        # Filter out exceptions
                        secondary_responses = [r for r in secondary_responses if isinstance(r, AgentResponse)]
                else:
                    # Sequential execution
                    for agent_name in routing.secondary_agents:
                        agent = self.agents.get(agent_name)
                        if agent:
                            response = await agent.process(query, agent_context)
                            secondary_responses.append(response)
                            if response.success:
                                break  # Stop if we get a successful response
            
            # Step 5: Consolidate responses
            final_response = self._consolidate_responses(
                query, classification, primary_response, secondary_responses
            )
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error in MultiAgentOrchestrator: {str(e)}")
            return FinalResponse(
                message=f"I encountered an error processing your request: {str(e)}",
                response_type=QueryType.GENERAL_INFO,
                confidence_level=ConfidenceLevel.LOW,
                followup_needed=True
            )
    
    def _consolidate_responses(self, 
                             query: str, 
                             classification: QueryClassification,
                             primary_response: AgentResponse, 
                             secondary_responses: List[AgentResponse]) -> FinalResponse:
        """Consolidate multiple agent responses into final response"""
        
        # Use primary response as base
        if primary_response.success:
            main_response = primary_response
        else:
            # Try to find a successful secondary response
            main_response = None
            for response in secondary_responses:
                if response.success:
                    main_response = response
                    break
            
            # If no successful response, use primary
            if not main_response:
                main_response = primary_response
        
        # Collect all PartSelect links
        all_links = set(main_response.partselect_links)
        for response in secondary_responses:
            all_links.update(response.partselect_links)
        
        # Collect all suggestions
        all_suggestions = list(main_response.suggestions)
        for response in secondary_responses:
            all_suggestions.extend(response.suggestions)
        
        # Remove duplicates while preserving order
        seen_suggestions = set()
        unique_suggestions = []
        for suggestion in all_suggestions:
            if suggestion not in seen_suggestions:
                seen_suggestions.add(suggestion)
                unique_suggestions.append(suggestion)
        
        return FinalResponse(
            message=main_response.message,
            response_type=classification.query_type,
            appliance_type=classification.appliance_type,
            key_information=main_response.data or {},
            recommended_actions=unique_suggestions,
            partselect_links=list(all_links),
            confidence_level=main_response.confidence,
            followup_needed=main_response.requires_followup,
            disclaimer="Please verify part compatibility and follow safety guidelines when working with appliances."
        ) 