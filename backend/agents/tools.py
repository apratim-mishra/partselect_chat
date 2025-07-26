from typing import Dict, List, Any, Optional
import json
import os
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load mock data
def load_mock_data():
    try:

        data_path = Path(__file__).parent.parent / "data" / "parts_database.json"
        with open(data_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading mock data: {str(e)}")
        return None

# Mock database
PARTS_DB = None

def get_parts_db():
    global PARTS_DB
    if PARTS_DB is None:
        PARTS_DB = load_mock_data()
    if PARTS_DB is None:
        raise RuntimeError("Parts database could not be loaded. Check data/parts_database.json file exists and is valid JSON.")
    return PARTS_DB

def validate_part_number(part_number: str) -> bool:
    """Basic validation for part numbers to prevent obviously fake ones"""
    if not part_number or not isinstance(part_number, str):
        return False
    
    # Part numbers should be alphanumeric and reasonable length
    part_number = part_number.strip().upper()
    
    # Check for obviously fake patterns
    fake_patterns = [
        "MAGIC", "UNICORN", "FAKE", "TEST", "QUANTUM", "SPACE", "ALIEN",
        "DRAGON", "WIZARD", "ROBOT", "CYBER", "MATRIX", "INFINITY"
    ]
    
    for pattern in fake_patterns:
        if pattern in part_number:
            return False
    
    # Basic format check - should be 4-15 alphanumeric characters
    if not (4 <= len(part_number) <= 15 and part_number.replace("-", "").isalnum()):
        return False
    
    return True

def validate_price(price: float) -> bool:
    """Basic validation for part prices"""
    if not isinstance(price, (int, float)):
        return False
    
    # Reasonable price range for appliance parts ($1 - $2000)
    return 1.0 <= price <= 2000.0

async def search_parts(query: str, appliance_type: str = "both") -> Dict[str, Any]:
    """Search for parts by keyword, model, or part number"""
    try:

        if not query or not query.strip():
            return {
                "found": False,
                "count": 0,
                "results": [],
                "message": "Search query cannot be empty"
            }
        
        query_lower = query.lower().strip()

        db = get_parts_db()
        results = []
        
        for part in db["parts"]:
            # Filter by appliance type
            # Filter by appliance type
            if appliance_type != "both" and part.get("appliance_type", "").lower() != appliance_type.lower():
                continue
            
            # Enhanced matching - check for exact part number first
            if (query_lower == part.get("part_number", "").lower() or
                query_lower in part.get("part_number", "").lower() or
                query_lower in part.get("name", "").lower() or
                query_lower in part.get("description", "").lower() or
                any(query_lower in model.lower() for model in part.get("compatible_models", []))):
                
                # Validate part data before including in results
                part_number = part.get("part_number", "")
                price = part.get("price", 0)
                
                # Skip parts with invalid data
                if not validate_part_number(part_number):
                    logger.warning(f"Skipping part with invalid part number: {part_number}")
                    continue
                
                if not validate_price(price):
                    logger.warning(f"Skipping part with invalid price: {price} for part {part_number}")
                    continue
                
                results.append({
                    "part_number": part["part_number"],
                    "name": part["name"],
                    "description": part["description"],
                    "price": part["price"],
                    "appliance_type": part["appliance_type"],
                    "image_url": part.get("image_url", ""),
                    "in_stock": part.get("in_stock", True)
                })
        
        return {
            "found": len(results) > 0,
            "count": len(results),
            "results": results[:10]  # Limit to 10 results
        }
    except Exception as e:
        logger.error(f"Error searching parts: {str(e)}")
        return {
            "found": False,
            "count": 0,
            "results": [],
            "error": "Service unavailable"
        }


async def check_compatibility(part_number: str, model_number: str) -> Dict[str, Any]:
    """Check if a part is compatible with a specific model"""
    try:
        db = get_parts_db()

        # Validate inputs
        if not part_number or not model_number:
            return {
                "compatible": False,
                "reason": "Both part number and model number are required",
                "part_number": part_number,
                "model_number": model_number
            }
        
        # Validate part number format
        if not validate_part_number(part_number):
            return {
                "compatible": False,
                "reason": "Invalid part number format",
                "part_number": part_number,
                "model_number": model_number
            }
        
        # Find the part
        part = None
        for p in db["parts"]:
            if p["part_number"].upper() == part_number.upper():
                part = p
                break
        
        if not part:
            return {
                "compatible": False,
                "reason": "Part not found",
                "part_number": part_number,
                "model_number": model_number
            }
        
        # Check compatibility
        model_upper = model_number.upper()
        compatible = any(model_upper == m.upper() for m in part["compatible_models"])
        
        return {
            "compatible": compatible,
            "part_number": part_number,
            "model_number": model_number,
            "part_name": part["name"],
            "compatible_models": part["compatible_models"][:5] if not compatible else [],
            "reason": "Compatible with your model" if compatible else "Not compatible with your model"
        }
    except Exception as e:
        logger.error(f"Error checking compatibility: {str(e)}")
        return {
            "compatible": False,
            "reason": f"Error checking compatibility: {str(e)}",
            "part_number": part_number,
            "model_number": model_number
        }

async def get_installation_guide(part_number: str) -> Dict[str, Any]:
    """Get installation instructions for a part"""
    db = get_parts_db()
    
        # Validate input
    if not part_number:
        return {
            "found": False,
            "part_number": part_number,
            "error": "Part number is required"
        }
    

    # Find the part
    part = None
    for p in db["parts"]:
        if p["part_number"].upper() == part_number.upper():
            part = p
            break
    
    if not part:
        return {
            "found": False,
            "part_number": part_number,
            "error": "Part not found"
        }
    
    # Get installation guide from database or use default
    installation = part.get("installation_guide", db["default_guides"]["installation"].get(part["category"], []))
    
    if not installation:
    # Try to get default guide by category
        category = part.get("category", "general")
        installation = db.get("default_guides", {}).get("installation", {}).get(category, [])
        
        # Final fallback
        if not installation:
            installation = [
                "Refer to your owner's manual for specific instructions",
                "Ensure power is disconnected before beginning installation",
                "Follow all manufacturer safety guidelines"
            ]

    # Add safety checks to installation steps
    safe_installation = []
    for step in installation:
        if isinstance(step, str):
            # Remove dangerous instructions
            step_lower = step.lower()
            if any(danger in step_lower for danger in [
                "while running", "with power on", "live wire", "bare hands", 
                "metal fork", "without unplugging", "skip safety"
            ]):
                logger.warning(f"Skipping potentially dangerous installation step: {step}")
                continue
        safe_installation.append(step)
    
    # Ensure safety warning is always present
    safety_warning = "Always unplug the appliance and turn off power at the circuit breaker before beginning any repair."
    
    return {
            "found": True,
            "part_number": part_number,
            "part_name": part["name"],
            "difficulty": part.get("installation_difficulty", "Medium"),
            "time_estimate": part.get("installation_time", "15-30 minutes"),
            "tools_required": part.get("tools_required", ["Screwdriver", "Pliers"]),
            "steps": safe_installation,
            "safety_warning": safety_warning,
            "video_url": part.get("installation_video_url", "")
        }

async def get_troubleshooting_guide(issue: str, appliance_type: str) -> Dict[str, Any]:
    """Get troubleshooting guide for common issues"""
    db = get_parts_db()
    

        # Validate inputs
    if not issue or not appliance_type:
        return {
            "found": False,
            "issue": issue,
            "appliance_type": appliance_type,
            "error": "Both issue and appliance type are required"
        }
    # Find relevant troubleshooting guides
    guides = db["troubleshooting_guides"].get(appliance_type, [])
    issue_lower = issue.lower()
    
    relevant_guides = []
    for guide in guides:
        # More flexible matching
        keywords = guide.get("keywords", [])
        if any(keyword.lower() in issue_lower for keyword in keywords):
            relevant_guides.append(guide)
    
    # Sort by number of matching keywords (better matches first)
    relevant_guides.sort(
        key=lambda g: sum(1 for k in g.get("keywords", []) if k.lower() in issue_lower),
        reverse=True
    )
    
    if not relevant_guides:
        # Return generic troubleshooting
        return {
            "found": False,
            "issue": issue,
            "appliance_type": appliance_type,
            "general_tips": [
                "Check if the appliance is properly plugged in",
                "Ensure circuit breaker hasn't tripped",
                "Verify water supply (if applicable)",
                "Check for error codes on display",
                "Consult your owner's manual"
            ]
        }
    
    # Return the most relevant guide
    guide = relevant_guides[0]
    return {
        "found": True,
        "issue": guide["issue"],
        "appliance_type": appliance_type,
        "possible_causes": guide["causes"],
        "solutions": guide["solutions"],
        "related_parts": guide.get("related_parts", []),
        "difficulty": guide.get("difficulty", "Medium"),
        "when_to_call_professional": guide.get("professional_help", "If problem persists after trying these solutions")
    }

async def get_part_details(part_number: str) -> Dict[str, Any]:
    """Get detailed information about a specific part"""
    db = get_parts_db()
    
    # Validate input
    if not part_number:
        return {
            "found": False,
            "part_number": part_number,
            "error": "Part number is required"
        }
    
    # Find the part
    part = None
    for p in db.get("parts", []):
        if p.get("part_number", "").upper() == part_number.upper():
            part = p
            break
    
    if not part:
        return {
            "found": False,
            "part_number": part_number,
            "error": f"Part {part_number} not found in our database. Try searching by name or model number."
        }
    
    return {
        "found": True,
        "part_number": part["part_number"],
        "name": part["name"],
        "description": part["description"],
        "category": part["category"],
        "manufacturer": part["manufacturer"],
        "price": part["price"],
        "in_stock": part.get("in_stock", True),
        "appliance_type": part["appliance_type"],
        "compatible_models": part["compatible_models"],
        "specifications": part.get("specifications", {}),
        "warranty": part.get("warranty", "90 days"),
        "oem_part_numbers": part.get("oem_part_numbers", []),
        "image_url": part.get("image_url", ""),
        "reviews_summary": {
            "rating": part.get("rating", 4.5),
            "review_count": part.get("review_count", 0)
        }
    }