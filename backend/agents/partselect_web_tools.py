"""
PartSelect Web Tools - Web search and URL construction for PartSelect.com
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import requests
from urllib.parse import quote
import re

logger = logging.getLogger(__name__)

# PartSelect website structure and data
PARTSELECT_BASE_URL = "https://www.partselect.com"

# Popular models from PartSelect
POPULAR_DISHWASHER_MODELS = [
    "FPHD2491KF0", "WDT730PAHZ0", "WDT750SAHZ0", "WDTA50SAHZ0", "FGHD2433KF1",
    "WDT970SAHZ0", "LDF7774ST", "FGHD2465NF1A", "MDB8959SFZ4", "KDTM354DSS4",
    "KDTE104DSS0", "WDF520PADM7", "KDTE254ESS2", "JDB1100AWS", "PDW7880J10SS",
    "LDF6920ST", "LDF5545ST"
]

POPULAR_REFRIGERATOR_MODELS = [
    "LFSS2612TF0", "FGHS2631PF4A", "WRS325FDAM04", "FFSS2615TS0", "WRS325FDAM02",
    "FGHC2331PFAA", "MFI2568AES", "LFSS2612TE0", "WRX735SDBM00", "WRF535SMBM00",
    "GFSS2HCYCSS", "FFHS2611PFEA", "LFX28968ST"
]

# Part categories
DISHWASHER_PARTS = [
    "Dishracks", "Wheels and Rollers", "Seals and Gaskets", "Spray Arms", "Hardware",
    "Elements and Burners", "Pumps", "Latches", "Valves", "Racks", "Hoses and Tubes",
    "Filters", "Brackets and Flanges", "Hinges", "Dispensers", "Springs and Shock Absorbers",
    "Caps and Lids", "Thermostats", "Switches", "Circuit Boards and Touch Pads", "Motors",
    "Bearings", "Sensors", "Panels", "Trays and Shelves", "Touch-Up Paint", "Handles",
    "Fuses", "Drawers and Glides", "Grilles and Kickplates", "Insulation", "Knobs",
    "Tanks and Containers", "Wire Plugs and Connectors", "Transmissions and Clutches",
    "Lights and Bulbs", "Ducts and Vents", "Timers", "Legs and Feet", "Power Cords",
    "Doors", "Trim", "Electronics", "Manuals and Literature", "Attachments and Accessories"
]

REFRIGERATOR_PARTS = [
    "Trays and Shelves", "Drawers and Glides", "Filters", "Ice Makers", "Seals and Gaskets",
    "Lights and Bulbs", "Hardware", "Hinges", "Switches", "Valves", "Motors", "Thermostats",
    "Caps and Lids", "Electronics", "Door Shelves", "Elements and Burners", 
    "Circuit Boards and Touch Pads", "Wheels and Rollers", "Handles", "Doors",
    "Hoses and Tubes", "Sensors", "Dispensers", "Fans and Blowers", "Compressors",
    "Brackets and Flanges", "Timers", "Springs and Shock Absorbers", "Bearings",
    "Grilles and Kickplates", "Trim", "Latches", "Knobs", "Wire Plugs and Connectors",
    "Tanks and Containers", "Transmissions and Clutches", "Legs and Feet", "Drip Bowls",
    "Racks", "Fuses", "Ducts and Vents", "Panels", "Power Cords", "Grates", "Insulation",
    "Blades", "Deflectors and Chutes", "Starters", "Manuals and Literature", "Brushes",
    "Attachments and Accessories", "Gears", "Transformers", "Cooktops", "Carburetors"
]

# Brands
APPLIANCE_BRANDS = [
    "Admiral", "Amana", "Beko", "Blomberg", "Bosch", "Caloric", "Crosley", "Dacor",
    "Dynasty", "Electrolux", "Estate", "Frigidaire", "Gaggenau", "GE", "Gibson",
    "Haier", "Hardwick", "Hoover", "Hotpoint", "Inglis", "International", "Jenn-Air",
    "Kelvinator", "Kenmore", "KitchenAid", "LG", "Litton", "Magic Chef", "Maytag",
    "Norge", "RCA", "Roper", "Samsung", "Sharp", "SMEG", "Speed Queen", "Tappan",
    "Thermador", "Uni", "Whirlpool", "White-Westinghouse"
]

async def search_partselect_web(query: str, appliance_type: str = "both") -> Dict[str, Any]:
    """
    Search PartSelect website using web search
    """
    try:
        # Construct targeted search for PartSelect
        search_terms = f"site:partselect.com {query}"
        if appliance_type in ["refrigerator", "dishwasher"]:
            search_terms += f" {appliance_type}"
        
        # Note: In a real implementation, you'd use a web search API
        # For now, we'll simulate with URL construction and known data
        
        results = []
        
        # Check if query matches known models
        query_upper = query.upper()
        if query_upper in POPULAR_DISHWASHER_MODELS:
            results.append({
                "title": f"Parts for {query_upper} Dishwasher",
                "url": f"{PARTSELECT_BASE_URL}/Models/{query_upper}/",
                "snippet": f"Find replacement parts for your {query_upper} dishwasher model",
                "type": "model_page"
            })
        
        if query_upper in POPULAR_REFRIGERATOR_MODELS:
            results.append({
                "title": f"Parts for {query_upper} Refrigerator", 
                "url": f"{PARTSELECT_BASE_URL}/Models/{query_upper}/",
                "snippet": f"Find replacement parts for your {query_upper} refrigerator model",
                "type": "model_page"
            })
        
        # Check for part type matches
        query_lower = query.lower()
        for part in DISHWASHER_PARTS:
            if part.lower() in query_lower and appliance_type in ["dishwasher", "both"]:
                results.append({
                    "title": f"Dishwasher {part}",
                    "url": f"{PARTSELECT_BASE_URL}/Dishwasher-{part.replace(' ', '-')}.htm",
                    "snippet": f"Shop for dishwasher {part.lower()} parts",
                    "type": "part_category"
                })
                break
        
        for part in REFRIGERATOR_PARTS:
            if part.lower() in query_lower and appliance_type in ["refrigerator", "both"]:
                results.append({
                    "title": f"Refrigerator {part}",
                    "url": f"{PARTSELECT_BASE_URL}/Refrigerator-{part.replace(' ', '-')}.htm", 
                    "snippet": f"Shop for refrigerator {part.lower()} parts",
                    "type": "part_category"
                })
                break
        
        # Check for brand matches
        for brand in APPLIANCE_BRANDS:
            if brand.lower() in query_lower:
                if appliance_type in ["dishwasher", "both"]:
                    results.append({
                        "title": f"{brand} Dishwasher Parts",
                        "url": f"{PARTSELECT_BASE_URL}/{brand}-Dishwasher-Parts.htm",
                        "snippet": f"Find {brand} dishwasher replacement parts",
                        "type": "brand_page"
                    })
                if appliance_type in ["refrigerator", "both"]:
                    results.append({
                        "title": f"{brand} Refrigerator Parts", 
                        "url": f"{PARTSELECT_BASE_URL}/{brand}-Refrigerator-Parts.htm",
                        "snippet": f"Find {brand} refrigerator replacement parts",
                        "type": "brand_page"
                    })
                break
        
        # Add main category pages if no specific matches
        if not results:
            if appliance_type in ["dishwasher", "both"]:
                results.append({
                    "title": "Dishwasher Parts",
                    "url": f"{PARTSELECT_BASE_URL}/Dishwasher-Parts.htm",
                    "snippet": "Browse all dishwasher parts and accessories",
                    "type": "main_category"
                })
            
            if appliance_type in ["refrigerator", "both"]:
                results.append({
                    "title": "Refrigerator Parts",
                    "url": f"{PARTSELECT_BASE_URL}/Refrigerator-Parts.htm", 
                    "snippet": "Browse all refrigerator parts and accessories",
                    "type": "main_category"
                })
        
        return {
            "found": len(results) > 0,
            "count": len(results),
            "results": results[:5],  # Limit to 5 results
            "search_query": query,
            "appliance_type": appliance_type
        }
        
    except Exception as e:
        logger.error(f"Error searching PartSelect web: {str(e)}")
        return {
            "found": False,
            "count": 0,
            "results": [],
            "error": "Web search service unavailable"
        }

async def get_partselect_url(item_type: str, item_name: str, appliance_type: str = None) -> Dict[str, Any]:
    """
    Construct PartSelect URLs for specific items
    """
    try:
        base_url = PARTSELECT_BASE_URL
        
        if item_type == "model":
            # Model page URL
            model_upper = item_name.upper()
            url = f"{base_url}/Models/{model_upper}/"
            return {
                "found": True,
                "url": url,
                "type": "model",
                "name": model_upper,
                "description": f"Parts for {model_upper} {appliance_type or 'appliance'}"
            }
        
        elif item_type == "part":
            # Part category URL
            if appliance_type:
                part_formatted = item_name.replace(' ', '-')
                url = f"{base_url}/{appliance_type.title()}-{part_formatted}.htm"
                return {
                    "found": True,
                    "url": url,
                    "type": "part_category",
                    "name": item_name,
                    "appliance_type": appliance_type,
                    "description": f"{appliance_type.title()} {item_name} parts"
                }
        
        elif item_type == "brand":
            # Brand page URL
            if appliance_type:
                url = f"{base_url}/{item_name}-{appliance_type.title()}-Parts.htm"
                return {
                    "found": True,
                    "url": url,
                    "type": "brand",
                    "name": item_name,
                    "appliance_type": appliance_type,
                    "description": f"{item_name} {appliance_type} parts"
                }
        
        elif item_type == "main":
            # Main category page
            if appliance_type:
                url = f"{base_url}/{appliance_type.title()}-Parts.htm"
                return {
                    "found": True,
                    "url": url,
                    "type": "main_category",
                    "appliance_type": appliance_type,
                    "description": f"All {appliance_type} parts"
                }
        
        return {
            "found": False,
            "error": "Invalid item type or missing appliance type"
        }
        
    except Exception as e:
        logger.error(f"Error constructing PartSelect URL: {str(e)}")
        return {
            "found": False,
            "error": f"URL construction failed: {str(e)}"
        }

async def validate_model_number(model: str, appliance_type: str = None) -> Dict[str, Any]:
    """
    Validate if a model number exists in PartSelect
    """
    try:
        model_upper = model.upper().strip()
        
        # Check against known popular models
        if model_upper in POPULAR_DISHWASHER_MODELS:
            return {
                "valid": True,
                "model": model_upper,
                "appliance_type": "dishwasher",
                "url": f"{PARTSELECT_BASE_URL}/Models/{model_upper}/",
                "confidence": "high"
            }
        
        if model_upper in POPULAR_REFRIGERATOR_MODELS:
            return {
                "valid": True,
                "model": model_upper,
                "appliance_type": "refrigerator", 
                "url": f"{PARTSELECT_BASE_URL}/Models/{model_upper}/",
                "confidence": "high"
            }
        
        # Basic format validation for appliance model numbers
        # Most appliance models are 6-15 alphanumeric characters
        if re.match(r'^[A-Z0-9]{6,15}$', model_upper):
            return {
                "valid": True,
                "model": model_upper,
                "appliance_type": appliance_type or "unknown",
                "url": f"{PARTSELECT_BASE_URL}/Models/{model_upper}/",
                "confidence": "medium",
                "note": "Model format appears valid but not in popular models list"
            }
        
        return {
            "valid": False,
            "model": model,
            "reason": "Invalid model number format"
        }
        
    except Exception as e:
        logger.error(f"Error validating model: {str(e)}")
        return {
            "valid": False,
            "model": model,
            "error": str(e)
        }

async def get_popular_models(appliance_type: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get popular models for specific appliance type
    """
    try:
        if appliance_type.lower() == "dishwasher":
            models = POPULAR_DISHWASHER_MODELS[:limit]
        elif appliance_type.lower() == "refrigerator":
            models = POPULAR_REFRIGERATOR_MODELS[:limit]
        else:
            return {
                "found": False,
                "error": "Invalid appliance type. Use 'dishwasher' or 'refrigerator'"
            }
        
        model_data = []
        for model in models:
            model_data.append({
                "model": model,
                "appliance_type": appliance_type,
                "url": f"{PARTSELECT_BASE_URL}/Models/{model}/",
                "parts_url": f"{PARTSELECT_BASE_URL}/Models/{model}/"
            })
        
        return {
            "found": True,
            "appliance_type": appliance_type,
            "count": len(model_data),
            "models": model_data
        }
        
    except Exception as e:
        logger.error(f"Error getting popular models: {str(e)}")
        return {
            "found": False,
            "error": str(e)
        }

async def get_part_categories(appliance_type: str) -> Dict[str, Any]:
    """
    Get available part categories for appliance type
    """
    try:
        if appliance_type.lower() == "dishwasher":
            parts = DISHWASHER_PARTS
        elif appliance_type.lower() == "refrigerator":
            parts = REFRIGERATOR_PARTS
        else:
            return {
                "found": False,
                "error": "Invalid appliance type. Use 'dishwasher' or 'refrigerator'"
            }
        
        categories = []
        for part in parts:
            categories.append({
                "name": part,
                "url": f"{PARTSELECT_BASE_URL}/{appliance_type.title()}-{part.replace(' ', '-')}.htm",
                "appliance_type": appliance_type
            })
        
        return {
            "found": True,
            "appliance_type": appliance_type,
            "count": len(categories),
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Error getting part categories: {str(e)}")
        return {
            "found": False,
            "error": str(e)
        }

async def get_brands(appliance_type: str = None) -> Dict[str, Any]:
    """
    Get available brands, optionally filtered by appliance type
    """
    try:
        brands_data = []
        for brand in APPLIANCE_BRANDS:
            brand_info = {"name": brand}
            
            if appliance_type:
                brand_info["url"] = f"{PARTSELECT_BASE_URL}/{brand}-{appliance_type.title()}-Parts.htm"
                brand_info["appliance_type"] = appliance_type
            else:
                brand_info["dishwasher_url"] = f"{PARTSELECT_BASE_URL}/{brand}-Dishwasher-Parts.htm"
                brand_info["refrigerator_url"] = f"{PARTSELECT_BASE_URL}/{brand}-Refrigerator-Parts.htm"
            
            brands_data.append(brand_info)
        
        return {
            "found": True,
            "count": len(brands_data),
            "appliance_type": appliance_type or "all",
            "brands": brands_data
        }
        
    except Exception as e:
        logger.error(f"Error getting brands: {str(e)}")
        return {
            "found": False,
            "error": str(e)
        } 