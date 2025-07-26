from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    timestamp: str
    agent: str
    error: Optional[bool] = False
    out_of_scope: Optional[bool] = False
    
class Part(BaseModel):
    part_number: str
    name: str
    description: str
    price: float
    appliance_type: str
    in_stock: bool = True
    image_url: Optional[str] = None
    
class CompatibilityCheck(BaseModel):
    model_config = {"protected_namespaces": ()}
    part_number: str
    appliance_model: str  # Changed from model_number to avoid conflict
    compatible: bool
    reason: str
    
class InstallationGuide(BaseModel):
    part_number: str
    part_name: str
    difficulty: str
    time_estimate: str
    tools_required: List[str]
    steps: List[str]
    safety_warning: str
    video_url: Optional[str] = None

class TroubleshootingGuide(BaseModel):
    issue: str
    appliance_type: str
    possible_causes: List[str]
    solutions: List[str]
    related_parts: List[str]
    difficulty: str
    when_to_call_professional: str