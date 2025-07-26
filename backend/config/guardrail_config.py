"""
Hallucination Guardrail Configuration

This module provides configuration options for the hallucination detection system.
"""

import os
from typing import Dict, Any
from enum import Enum

class GuardrailPreset(Enum):
    """Predefined configuration presets for different use cases"""
    STRICT = "strict"
    BALANCED = "balanced"
    LENIENT = "lenient"
    MONITORING_ONLY = "monitoring_only"

class GuardrailConfig:
    """Configuration class for hallucination guardrail settings"""
    
    PRESET_CONFIGS = {
        GuardrailPreset.STRICT: {
            "threshold": 0.5,
            "block_high_confidence": True,
            "warn_medium_confidence": True,
            "log_all_evaluations": True,
            "evaluation_timeout": 10.0,
            "description": "Aggressive hallucination detection - blocks questionable responses"
        },
        GuardrailPreset.BALANCED: {
            "threshold": 0.7,
            "block_high_confidence": True,
            "warn_medium_confidence": True,
            "log_all_evaluations": False,
            "evaluation_timeout": 8.0,
            "description": "Balanced approach - blocks clear hallucinations, warns on concerns"
        },
        GuardrailPreset.LENIENT: {
            "threshold": 0.85,
            "block_high_confidence": False,
            "warn_medium_confidence": True,
            "log_all_evaluations": False,
            "evaluation_timeout": 5.0,
            "description": "Conservative approach - only warns on high-confidence issues"
        },
        GuardrailPreset.MONITORING_ONLY: {
            "threshold": 0.3,
            "block_high_confidence": False,
            "warn_medium_confidence": False,
            "log_all_evaluations": True,
            "evaluation_timeout": 5.0,
            "description": "Log all evaluations for monitoring but don't block or warn"
        }
    }
    
    @classmethod
    def get_config_from_env(cls) -> Dict[str, Any]:
        """Load configuration from environment variables with fallbacks"""
        
        # Get preset if specified
        preset_name = os.getenv("GUARDRAIL_PRESET", "balanced").lower()
        try:
            preset = GuardrailPreset(preset_name)
            config = cls.PRESET_CONFIGS[preset].copy()
        except ValueError:
            # Invalid preset, use balanced as default
            config = cls.PRESET_CONFIGS[GuardrailPreset.BALANCED].copy()
        
        # Override with specific environment variables if provided
        config.update({
            "enabled": os.getenv("GUARDRAIL_ENABLED", "true").lower() == "true",
            "threshold": float(os.getenv("GUARDRAIL_THRESHOLD", str(config["threshold"]))),
            "block_high_confidence": os.getenv("GUARDRAIL_BLOCK_HIGH", str(config["block_high_confidence"])).lower() == "true",
            "warn_medium_confidence": os.getenv("GUARDRAIL_WARN_MEDIUM", str(config["warn_medium_confidence"])).lower() == "true",
            "log_all_evaluations": os.getenv("GUARDRAIL_LOG_ALL", str(config["log_all_evaluations"])).lower() == "true",
            "evaluation_timeout": float(os.getenv("GUARDRAIL_TIMEOUT", str(config["evaluation_timeout"]))),
            "deepseek_model": os.getenv("DEEPSEEK_GUARDRAIL_MODEL", "deepseek-chat"),
            "deepseek_base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        })
        
        return config
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize configuration values"""
        
        # Ensure threshold is between 0 and 1
        config["threshold"] = max(0.0, min(1.0, config["threshold"]))
        
        # Ensure timeout is reasonable
        config["evaluation_timeout"] = max(1.0, min(30.0, config["evaluation_timeout"]))
        
        # Ensure boolean values
        for bool_key in ["enabled", "block_high_confidence", "warn_medium_confidence", "log_all_evaluations"]:
            config[bool_key] = bool(config.get(bool_key, False))
        
        return config

# Environment variables documentation
ENV_VARS_DOCUMENTATION = """
Hallucination Guardrail Environment Variables:

Core Settings:
- DEEPSEEK_API_KEY: Required - Your DeepSeek API key
- GUARDRAIL_ENABLED: true/false (default: true) - Enable/disable guardrail
- GUARDRAIL_PRESET: strict/balanced/lenient/monitoring_only (default: balanced)

Fine-tuning (overrides preset):
- GUARDRAIL_THRESHOLD: 0.0-1.0 (default: 0.7) - Confidence threshold for action
- GUARDRAIL_BLOCK_HIGH: true/false - Block high-confidence hallucinations
- GUARDRAIL_WARN_MEDIUM: true/false - Warn on medium-confidence issues  
- GUARDRAIL_LOG_ALL: true/false - Log all evaluations for monitoring
- GUARDRAIL_TIMEOUT: 1.0-30.0 (default: 8.0) - Max evaluation time in seconds

API Settings:
- DEEPSEEK_GUARDRAIL_MODEL: deepseek-chat (default) - Model for evaluation
- DEEPSEEK_BASE_URL: https://api.deepseek.com (default) - API base URL

Example .env configuration:
DEEPSEEK_API_KEY=your_deepseek_api_key_here
GUARDRAIL_ENABLED=true
GUARDRAIL_PRESET=balanced
GUARDRAIL_THRESHOLD=0.7
"""

def print_config_help():
    """Print configuration help to console"""
    print(ENV_VARS_DOCUMENTATION)
    print("\nAvailable Presets:")
    for preset, config in GuardrailConfig.PRESET_CONFIGS.items():
        print(f"\n{preset.value.upper()}:")
        print(f"  Description: {config['description']}")
        print(f"  Threshold: {config['threshold']}")
        print(f"  Blocks high confidence: {config['block_high_confidence']}")
        print(f"  Warns medium confidence: {config['warn_medium_confidence']}")

if __name__ == "__main__":
    print_config_help() 