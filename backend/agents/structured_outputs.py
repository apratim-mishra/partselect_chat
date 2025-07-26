"""
Structured Outputs for PartSelect Multi-Agent System
Using Pydantic models for guaranteed schema adherence
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Literal
from enum import Enum

class ApplianceType(str, Enum):
    """Supported appliance types"""
    REFRIGERATOR = "refrigerator"
    DISHWASHER = "dishwasher"
    BOTH = "both"

class QueryType(str, Enum):
    """Types of user queries"""
    PART_SEARCH = "part_search"
    MODEL_LOOKUP = "model_lookup"
    COMPATIBILITY_CHECK = "compatibility_check"
    INSTALLATION_GUIDE = "installation_guide"
    TROUBLESHOOTING = "troubleshooting"
    BRAND_INQUIRY = "brand_inquiry"
    GENERAL_INFO = "general_info"
    OUT_OF_SCOPE = "out_of_scope"

class UrgencyLevel(str, Enum):
    """Query urgency levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"

class ConfidenceLevel(str, Enum):
    """Confidence levels for responses"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

# === ROUTING/TRIAGING MODELS ===

class QueryClassification(BaseModel):
    """Classification result for incoming user queries"""
    query_type: QueryType = Field(description="The primary type of query")
    appliance_type: ApplianceType = Field(description="Target appliance type")
    urgency: UrgencyLevel = Field(description="Urgency level of the query")
    confidence: ConfidenceLevel = Field(description="Confidence in classification")
    requires_model_number: bool = Field(description="Whether model number is needed")
    extracted_entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted entities like model numbers, part names, brands"
    )
    reasoning: str = Field(description="Explanation for the classification")

class AgentRouting(BaseModel):
    """Routing decision for agent selection"""
    primary_agent: str = Field(description="Primary agent to handle the query")
    secondary_agents: List[str] = Field(
        default_factory=list,
        description="Additional agents that may be needed"
    )
    parallel_execution: bool = Field(
        default=False,
        description="Whether agents should run in parallel"
    )
    routing_reason: str = Field(description="Reason for this routing decision")

# === PRODUCT SEARCH MODELS ===

class PartSearchCriteria(BaseModel):
    """Criteria for searching parts"""
    model_config = ConfigDict(protected_namespaces=())
    
    search_query: str = Field(description="Main search query")
    appliance_type: ApplianceType = Field(description="Type of appliance")
    brand: Optional[str] = Field(None, description="Specific brand if mentioned")
    model_number: Optional[str] = Field(None, description="Model number if provided")
    part_category: Optional[str] = Field(None, description="Specific part category")
    price_range: Optional[Dict[str, float]] = Field(None, description="Price range filter")

class PartInfo(BaseModel):
    """Information about a single part"""
    part_number: str = Field(description="Part number")
    name: str = Field(description="Part name")
    description: str = Field(description="Part description")
    price: float = Field(description="Part price")
    brand: str = Field(description="Brand name")
    appliance_type: ApplianceType = Field(description="Compatible appliance type")
    in_stock: bool = Field(description="Stock availability")
    image_url: Optional[str] = Field(None, description="Product image URL")
    partselect_url: Optional[str] = Field(None, description="PartSelect page URL")
    oem_compatible: bool = Field(default=True, description="OEM compatibility")

class PartSearchResult(BaseModel):
    """Result of part search operation"""
    found: bool = Field(description="Whether parts were found")
    count: int = Field(description="Number of parts found")
    parts: List[PartInfo] = Field(description="List of found parts")
    search_criteria: PartSearchCriteria = Field(description="Original search criteria")
    suggestions: List[str] = Field(
        default_factory=list,
        description="Alternative search suggestions"
    )
    related_categories: List[str] = Field(
        default_factory=list,
        description="Related part categories"
    )

# === MODEL LOOKUP MODELS ===

class ModelValidation(BaseModel):
    """Model number validation result"""
    model_config = ConfigDict(protected_namespaces=())
    
    is_valid: bool = Field(description="Whether model number is valid")
    model_number: str = Field(description="Validated model number")
    appliance_type: ApplianceType = Field(description="Detected appliance type")
    brand: Optional[str] = Field(None, description="Detected brand")
    confidence: ConfidenceLevel = Field(description="Validation confidence")
    partselect_url: Optional[str] = Field(None, description="PartSelect model page URL")
    validation_notes: List[str] = Field(
        default_factory=list,
        description="Notes about validation"
    )

class PopularModel(BaseModel):
    """Information about a popular model"""
    model_config = ConfigDict(protected_namespaces=())
    
    model_number: str = Field(description="Model number")
    appliance_type: ApplianceType = Field(description="Appliance type")
    brand: Optional[str] = Field(None, description="Brand name")
    description: Optional[str] = Field(None, description="Model description")
    partselect_url: str = Field(description="PartSelect page URL")
    popularity_rank: Optional[int] = Field(None, description="Popularity ranking")

class ModelLookupResult(BaseModel):
    """Result of model lookup operation"""
    model_config = ConfigDict(protected_namespaces=())
    
    found: bool = Field(description="Whether model was found")
    model_info: Optional[ModelValidation] = Field(None, description="Model information")
    similar_models: List[PopularModel] = Field(
        default_factory=list,
        description="Similar or related models"
    )
    common_parts: List[str] = Field(
        default_factory=list,
        description="Common parts for this model"
    )

# === COMPATIBILITY MODELS ===

class CompatibilityCheck(BaseModel):
    """Part compatibility check"""
    model_config = ConfigDict(protected_namespaces=())
    
    part_number: str = Field(description="Part number to check")
    model_number: str = Field(description="Model to check against")
    is_compatible: bool = Field(description="Compatibility result")
    confidence: ConfidenceLevel = Field(description="Confidence in result")
    compatibility_notes: List[str] = Field(
        default_factory=list,
        description="Notes about compatibility"
    )
    alternative_parts: List[str] = Field(
        default_factory=list,
        description="Alternative compatible parts"
    )

# === INSTALLATION GUIDE MODELS ===

class InstallationStep(BaseModel):
    """Single installation step"""
    step_number: int = Field(description="Step sequence number")
    title: str = Field(description="Step title")
    description: str = Field(description="Detailed step description")
    tools_needed: List[str] = Field(
        default_factory=list,
        description="Tools needed for this step"
    )
    safety_warnings: List[str] = Field(
        default_factory=list,
        description="Safety warnings for this step"
    )
    estimated_time: Optional[str] = Field(None, description="Estimated time for step")
    difficulty: Optional[str] = Field(None, description="Difficulty level")

class InstallationGuide(BaseModel):
    """Complete installation guide"""
    part_number: str = Field(description="Part number")
    part_name: str = Field(description="Part name")
    appliance_type: ApplianceType = Field(description="Appliance type")
    overall_difficulty: str = Field(description="Overall difficulty rating")
    total_time: str = Field(description="Total estimated time")
    tools_required: List[str] = Field(description="All tools needed")
    safety_precautions: List[str] = Field(description="Important safety notes")
    preparation_steps: List[str] = Field(
        default_factory=list,
        description="Preparation before starting"
    )
    installation_steps: List[InstallationStep] = Field(description="Installation steps")
    testing_steps: List[str] = Field(
        default_factory=list,
        description="Steps to test the installation"
    )
    video_url: Optional[str] = Field(None, description="Installation video URL")
    professional_recommendation: bool = Field(
        default=False,
        description="Whether professional installation is recommended"
    )

# === TROUBLESHOOTING MODELS ===

class TroubleshootingStep(BaseModel):
    """Single troubleshooting step"""
    step_number: int = Field(description="Step sequence number")
    action: str = Field(description="Action to take")
    expected_result: str = Field(description="What should happen")
    if_successful: Optional[str] = Field(None, description="Next step if successful")
    if_unsuccessful: Optional[str] = Field(None, description="Next step if unsuccessful")
    safety_notes: List[str] = Field(
        default_factory=list,
        description="Safety considerations"
    )

class TroubleshootingGuide(BaseModel):
    """Complete troubleshooting guide"""
    issue_description: str = Field(description="Description of the issue")
    appliance_type: ApplianceType = Field(description="Appliance type")
    possible_causes: List[str] = Field(description="Possible causes of the issue")
    difficulty_level: str = Field(description="Troubleshooting difficulty")
    estimated_time: str = Field(description="Estimated time to resolve")
    tools_needed: List[str] = Field(
        default_factory=list,
        description="Tools that might be needed"
    )
    troubleshooting_steps: List[TroubleshootingStep] = Field(
        description="Step-by-step troubleshooting"
    )
    related_parts: List[str] = Field(
        default_factory=list,
        description="Parts that might need replacement"
    )
    when_to_call_professional: str = Field(
        description="When to seek professional help"
    )

# === WEB SEARCH MODELS ===

class WebSearchResult(BaseModel):
    """Single web search result"""
    title: str = Field(description="Page title")
    url: str = Field(description="Page URL")
    snippet: str = Field(description="Page snippet/description")
    result_type: str = Field(description="Type of result (model, part, brand, etc.)")
    relevance_score: Optional[float] = Field(None, description="Relevance score")

class WebSearchResults(BaseModel):
    """Web search results collection"""
    query: str = Field(description="Original search query")
    found: bool = Field(description="Whether results were found")
    count: int = Field(description="Number of results")
    results: List[WebSearchResult] = Field(description="Search results")
    search_suggestions: List[str] = Field(
        default_factory=list,
        description="Alternative search suggestions"
    )

# === RESPONSE MODELS ===

class AgentResponse(BaseModel):
    """Standard response from any agent"""
    agent_name: str = Field(description="Name of the responding agent")
    success: bool = Field(description="Whether the operation was successful")
    message: str = Field(description="Human-readable response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Structured response data")
    confidence: ConfidenceLevel = Field(description="Confidence in the response")
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for next steps"
    )
    partselect_links: List[str] = Field(
        default_factory=list,
        description="Relevant PartSelect URLs"
    )
    requires_followup: bool = Field(
        default=False,
        description="Whether follow-up questions are needed"
    )
    followup_questions: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up questions"
    )

class FinalResponse(BaseModel):
    """Final consolidated response to user"""
    message: str = Field(description="Main response message")
    response_type: QueryType = Field(description="Type of response")
    appliance_type: Optional[ApplianceType] = Field(None, description="Relevant appliance type")
    key_information: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key structured information"
    )
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Recommended next actions"
    )
    partselect_links: List[str] = Field(
        default_factory=list,
        description="Relevant PartSelect links"
    )
    confidence_level: ConfidenceLevel = Field(description="Overall confidence")
    disclaimer: Optional[str] = Field(None, description="Important disclaimers")
    followup_needed: bool = Field(default=False, description="Whether follow-up is needed")

# === TOOL CALLING MODELS ===

class ToolCall(BaseModel):
    """Represents a tool call with structured parameters"""
    tool_name: str = Field(description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(description="Tool parameters")
    reason: str = Field(description="Reason for calling this tool")

class ToolResult(BaseModel):
    """Result from a tool execution"""
    tool_name: str = Field(description="Name of the executed tool")
    success: bool = Field(description="Whether tool execution was successful")
    result: Dict[str, Any] = Field(description="Tool execution result")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")

# === MULTI-AGENT COORDINATION MODELS ===

class AgentHandoff(BaseModel):
    """Represents handoff between agents"""
    from_agent: str = Field(description="Source agent")
    to_agent: str = Field(description="Target agent")
    context: Dict[str, Any] = Field(description="Context to pass along")
    reason: str = Field(description="Reason for handoff")
    priority: str = Field(default="normal", description="Handoff priority")

class ParallelExecution(BaseModel):
    """Configuration for parallel agent execution"""
    agents: List[str] = Field(description="Agents to run in parallel")
    shared_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Shared context for all agents"
    )
    consolidation_strategy: str = Field(
        default="merge",
        description="How to consolidate results"
    )
    timeout_seconds: int = Field(default=30, description="Execution timeout") 