import os
import json
from typing import List, Dict, Optional
from ..llm import llm_client

class FeatureJustificationAgent:
    def __init__(self):
        pass

    def justify(self, pain_clusters: list[dict], tracker: Optional[Dict] = None) -> list[dict]:
        prompt = f"""
You are a Senior Product Manager deciding WHAT to build and WHAT NOT to build.

INPUT:
A ranked list of pain clusters discovered from real user evidence.

YOUR TASK:
For each CRITICAL or HIGH severity pain cluster:
1. Propose ONE feature that directly removes the pain
2. Explain why existing solutions fail
3. Decide if the feature MUST be in MVP
4. Define ONE success metric
5. Estimate complexity (low/medium/high)
6. State the consequence of NOT building it

STRICT RULES:
- One feature per pain cluster
- No feature with a pain
- No MVP feature with high complexity unless unavoidable
- Prefer workflow fixes over UI polish

RETURN STRICT JSON ONLY:

{{
  "feature_decisions": [
    {{
      "feature_id": "F-01",
      "feature_name": "",
      "solves_pain_clusters": [],
      "user_problem": "",
      "why_existing_solutions_fail": "",
      "mvp_priority": true | false,
      "expected_user_outcome": "",
      "success_metric": "",
      "if_we_dont_build": "",
      "complexity": "low | medium | high"
    }}
  ]
}}

PAIN CLUSTERS:
{json.dumps(pain_clusters, indent=2)}
"""
        try:
            # Using smart model for decision making
            response_text = llm_client.generate(prompt, model_type="smart", token_tracker=tracker)
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)["feature_decisions"]
        except Exception as e:
            print(f"Error in FeatureJustificationAgent: {e}")
            return []
