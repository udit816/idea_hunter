import os
import json
from typing import List, Dict, Optional
from ..llm import llm_client

class KillSwitchAgent:
    def __init__(self):
        pass

    def decide(
        self,
        pain_clusters: list[dict],
        feature_decisions: list[dict],
        confidence_data: Optional[Dict] = None, # Calculated Deterministic Confidence
        tracker: Optional[Dict] = None
    ) -> dict:

        prompt = f"""
You are a Principal Product Manager whose job is to STOP bad products.

INPUT:
1. Ranked pain clusters derived from real user evidence
2. Feature decisions proposed for MVP

YOUR TASK:
Decide whether this product should be BUILT or NOT BUILT.

YOU MUST BE SKEPTICAL.
Assume time, money, and trust are scarce.

EVALUATE THE FOLLOWING:
1. Is the pain CRITICAL or merely annoying?
2. Do users CURRENTLY pay to solve this pain?
3. Are workarounds acceptable to users?
4. Can a small MVP realistically fix this pain?
5. Is differentiation achievable, or structural?
6. Is trust, regulation, or data access a blocker?
7. Is timing right, or premature?

IMPORTANT RULES:
- If ≥2 CRITICAL failure conditions exist → DO_NOT_BUILD
- Do NOT invent new features to justify a BUILD
- Prefer ABANDON over optimistic pivots
- Be explicit and harsh if needed

RETURN STRICT JSON ONLY:

{{
  "verdict": "BUILD | DO_NOT_BUILD",
  "confidence": 0.0,
  "primary_reason": "",
  "supporting_reasons": [],
  "failed_criteria": [],
  "what_would_change_verdict": [],
  "recommendation": "Proceed | Pivot | Abandon"
}}

PAIN CLUSTERS:
{json.dumps(pain_clusters, indent=2)}

FEATURE DECISIONS:
{json.dumps(feature_decisions, indent=2)}

CONFIDENCE CONTEXT:
    The system has calculated a confidence score of {confidence_data.get('score', 0) if confidence_data else 'N/A'} ({confidence_data.get('band', 'N/A') if confidence_data else 'N/A'}) based on evidence convergence.
    Safety Override Active: {confidence_data.get('safety_override', False) if confidence_data else False}
"""
        
        try:
            # Critical reasoning -> Smart model
            response_text = llm_client.generate(prompt, model_type="smart", token_tracker=tracker)
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned)
            
            # OVERWRITE CONFIDENCE with Deterministic Logic
            if confidence_data:
                result['confidence'] = confidence_data['score'] / 100.0 # Normalized 0-1 for DB/Frontend
                
                # If Safety Override is active, FORCE DO_NOT_BUILD if not already
                if confidence_data.get('safety_override'):
                    result['verdict'] = "DO_NOT_BUILD"
                    result['primary_reason'] = f"(SAFETY DEFAULT) {result.get('primary_reason', 'Risk triggers detected')}"

            return result
        except Exception as e:
            print(f"Error in KillSwitchAgent: {e}")
            return {
                "verdict": "DO_NOT_BUILD",
                "confidence": 0.0,
                "primary_reason": "Agent Error - Defaulting to Safety",
                "supporting_reasons": [str(e)],
                "failed_criteria": ["system_error"],
                "what_would_change_verdict": [],
                "recommendation": "Abandon"
            }
