import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

class GuardrailAction(Enum):
    """Actions to take when hallucination is detected"""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    LOG = "log"

@dataclass
class GuardrailResult:
    """Result of hallucination evaluation"""
    is_hallucination: bool
    confidence_score: float  # 0-1, higher means more confident it's a hallucination
    reasons: List[str]
    action: GuardrailAction
    details: Dict[str, Any]

class HallucinationGuardrail:
    """
    Hallucination guardrail using deepseek-chat to evaluate responses
    for potential inaccuracies in the appliance parts domain
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 base_url: str = "https://api.deepseek.com",
                 model: str = "deepseek-chat",
                 threshold: float = 0.7,
                 action: GuardrailAction = GuardrailAction.WARN):
        """
        Initialize the guardrail
        
        Args:
            api_key: DeepSeek API key (if None, will use DEEPSEEK_API_KEY env var)
            base_url: DeepSeek API base URL
            model: Model to use for evaluation
            threshold: Confidence threshold above which to trigger action (0-1)
            action: Default action to take when hallucination detected
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key is required. Set DEEPSEEK_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        self.model = model
        self.threshold = threshold
        self.default_action = action
        
        # Parts-specific evaluation criteria
        self.evaluation_criteria = {
            "part_accuracy": "Check if part numbers mentioned are realistic and properly formatted",
            "compatibility_claims": "Verify compatibility statements are not overly broad or specific without evidence",
            "safety_instructions": "Ensure safety instructions are accurate and complete",
            "pricing_claims": "Check if price ranges are reasonable for appliance parts",
            "installation_steps": "Verify installation steps are logical and safe",
            "troubleshooting_advice": "Ensure troubleshooting advice is sound and appropriate",
            "model_specificity": "Check if model-specific claims are appropriately qualified"
        }
    
    def get_evaluation_prompt(self, 
                            user_query: str, 
                            assistant_response: str, 
                            context: Dict[str, Any] = None) -> str:
        """Build the evaluation prompt for deepseek-chat"""
        
        context_info = ""
        if context:
            if "tools_used" in context:
                context_info += f"\nTools used: {', '.join(context['tools_used'])}"
            if "parts_found" in context:
                part_list = context['parts_found']
                context_info += f"\nParts found in database: {len(part_list)}"
                if part_list:
                    context_info += f" (examples: {', '.join(part_list[:3])})"
            if "conversation_history" in context:
                context_info += f"\nPrevious conversation turns: {len(context['conversation_history'])}"
            if context.get("is_tool_result"):
                context_info += f"\nEvaluating tool result from: {context.get('tool_name', 'unknown')}"
        
        return f"""You are an expert evaluator for a appliance parts customer service system. Your job is to detect potential hallucinations or inaccuracies in assistant responses.

DOMAIN CONTEXT:
- This is a parts agent that helps customers find refrigerator and dishwasher parts
- The agent has access to a parts database and various tools
- Responses should be accurate, helpful, and safety-conscious

EVALUATION CRITERIA:
{json.dumps(self.evaluation_criteria, indent=2)}

USER QUERY:
{user_query}

ASSISTANT RESPONSE:
{assistant_response}

CONTEXT:
{context_info}

TASK:
Evaluate the assistant's response for potential hallucinations or inaccuracies. Consider:

1. FACTUAL ACCURACY: Are part numbers, model numbers, prices, and technical details plausible?
2. SAFETY COMPLIANCE: Are safety instructions appropriate and complete?
3. SCOPE ADHERENCE: Does the response stay within the scope of refrigerator/dishwasher parts?
4. LOGICAL CONSISTENCY: Do the recommendations and advice make logical sense?
5. QUALIFICATION OF CLAIMS: Are uncertain statements properly qualified?

Return your evaluation as a JSON object with this exact structure:
{{
    "is_hallucination": boolean,
    "confidence_score": float (0.0 to 1.0),
    "reasons": ["reason1", "reason2", ...],
    "specific_issues": {{
        "part_accuracy": "assessment",
        "safety_concerns": "assessment", 
        "scope_violations": "assessment",
        "logical_inconsistencies": "assessment"
    }},
    "severity": "low|medium|high",
    "recommendation": "allow|warn|block"
}}

Be conservative - only flag clear hallucinations or safety issues. Uncertainty or general advice should generally be allowed."""

    async def evaluate_response(self, 
                              user_query: str, 
                              assistant_response: str, 
                              context: Dict[str, Any] = None) -> GuardrailResult:
        """
        Evaluate a response for potential hallucinations
        
        Args:
            user_query: Original user query
            assistant_response: Response from the parts agent
            context: Additional context (tools used, parts found, etc.)
            
        Returns:
            GuardrailResult with evaluation details
        """
        try:
            prompt = self.get_evaluation_prompt(user_query, assistant_response, context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise evaluator. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent evaluation
                max_tokens=1000
            )
            
            evaluation_text = response.choices[0].message.content.strip()
            
            # Parse JSON response (handle markdown wrapping)
            try:
                # Remove markdown code block formatting if present
                if evaluation_text.startswith("```json"):
                    evaluation_text = evaluation_text.replace("```json", "").replace("```", "").strip()
                elif evaluation_text.startswith("```"):
                    evaluation_text = evaluation_text.replace("```", "").strip()
                
                evaluation = json.loads(evaluation_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.error(f"Failed to parse evaluation JSON: {evaluation_text}")
                return GuardrailResult(
                    is_hallucination=False,
                    confidence_score=0.0,
                    reasons=["Evaluation service error"],
                    action=GuardrailAction.LOG,
                    details={"error": "JSON parsing failed", "raw_response": evaluation_text}
                )
            
            # Determine action based on confidence and severity
            confidence = evaluation.get("confidence_score", 0.0)
            severity = evaluation.get("severity", "low")
            recommendation = evaluation.get("recommendation", "allow")
            
            action = self._determine_action(confidence, severity, recommendation)
            
            return GuardrailResult(
                is_hallucination=evaluation.get("is_hallucination", False),
                confidence_score=confidence,
                reasons=evaluation.get("reasons", []),
                action=action,
                details={
                    "specific_issues": evaluation.get("specific_issues", {}),
                    "severity": severity,
                    "recommendation": recommendation,
                    "evaluation_model": self.model
                }
            )
            
        except Exception as e:
            logger.error(f"Error evaluating response: {str(e)}")
            return GuardrailResult(
                is_hallucination=False,
                confidence_score=0.0,
                reasons=[f"Evaluation error: {str(e)}"],
                action=GuardrailAction.LOG,
                details={"error": str(e)}
            )
    
    def _determine_action(self, confidence: float, severity: str, recommendation: str) -> GuardrailAction:
        """Determine what action to take based on evaluation results"""
        
        # High confidence hallucinations with high severity should be blocked
        if confidence >= 0.8 and severity == "high":
            return GuardrailAction.BLOCK
        
        # Medium-high confidence or explicit block recommendation
        if confidence >= self.threshold or recommendation == "block":
            return GuardrailAction.BLOCK if severity in ["high", "medium"] else GuardrailAction.WARN
        
        # Low confidence issues or explicit warn recommendation
        if confidence >= 0.3 or recommendation == "warn":
            return GuardrailAction.WARN
        
        # Very low confidence or explicit allow
        if recommendation == "allow":
            return GuardrailAction.ALLOW
            
        # Default to log for monitoring
        return GuardrailAction.LOG
    
    def should_block_response(self, result: GuardrailResult) -> bool:
        """Check if response should be blocked"""
        return result.action == GuardrailAction.BLOCK
    
    def should_warn_user(self, result: GuardrailResult) -> bool:
        """Check if user should be warned"""
        return result.action in [GuardrailAction.WARN, GuardrailAction.BLOCK]
    
    def get_fallback_response(self, original_query: str, result: GuardrailResult) -> str:
        """Generate a safe fallback response when blocking"""
        return (
            "I want to make sure I provide you with accurate information. "
            "Let me search our database more carefully for your specific request. "
            "Could you please provide your appliance's model number so I can give you "
            "the most precise part recommendations and installation guidance?"
        )
    
    def get_warning_message(self, result: GuardrailResult) -> str:
        """Generate a warning message to append to response"""
        if result.action == GuardrailAction.WARN:
            return (
                "\n\n⚠️ Please verify this information with your appliance manual "
                "or contact our support team if you need additional confirmation."
            )
        return "" 