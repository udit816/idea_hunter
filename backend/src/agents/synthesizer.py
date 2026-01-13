import os
import time
import json
from typing import List, Dict, Optional
from ..state import EvidenceSignal, PainCluster, ProductIntent
from ..llm import llm_client

class SynthesizerAgent:
    def __init__(self):
        # No init needed
        pass

    def synthesize(self, signals: List[EvidenceSignal], tracker: Optional[Dict] = None) -> List[PainCluster]:
        print(f"   [Synthesizer] Clustering {len(signals)} evidence signals into themes...")
        
        # Serialize to dicts for JSON dump
        evidence_signals = [s.model_dump() for s in signals]
        
        prompt = f"""
        You are a Product Insight Synthesizer.

        INPUT:
        A list of evidence signals extracted from users across platforms.

        YOUR TASK:
        1. Group signals into PAIN CLUSTERS based on the SAME underlying problem.
        2. Ignore cosmetic issues unless repeated.
        3. Prefer:
           - workflow failures
           - trust collapse
           - payment blockers
        4. Rank severity by frequency + impact.

        RETURN STRICT JSON ONLY.

        FORMAT:
        {{
          "pain_clusters": [
            {{
              "cluster_id": "PC-01",
              "cluster_name": "",
              "description": "",
              "affected_personas": [],
              "evidence_count": 0,
              "platforms_affected": [],
              "impact_summary": {{
                "trial_blocker": true,
                "conversion_blocker": true,
                "trust_collapse": false
              }},
              "severity": "low | medium | high | critical",
              "why_users_get_angry": "",
              "representative_quotes": []
            }}
          ]
        }}

        EVIDENCE:
        {json.dumps(evidence_signals, indent=2)}
        """

        try:
            # Using Smart model for complex synthesis
            response_text = llm_client.generate(prompt, model_type="smart", token_tracker=tracker)
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            return [PainCluster(**item) for item in data.get("pain_clusters", [])]
        except Exception as e:
            print(f"   [Synthesizer] Error: {e}")
            return []

    def derive_intent(self, clusters: List[PainCluster], tracker: Optional[Dict] = None) -> ProductIntent:
        print(f"   [Synthesizer] Deriving Product Intent from {len(clusters)} clusters...")
        
        if not clusters:
            return ProductIntent(primary_problem="", non_negotiable_user_expectation="", current_market_failure="", opportunity_statement="")

        cluster_context = json.dumps([c.model_dump() for c in clusters[:5]], default=str)
        
        prompt = f"""
        You are a Head of Product Strategy.
        
        INPUT:
        Top ranked pain clusters derived from market research.

        YOUR TASK:
        Synthesize these clusters into a single strategic Product Intent.

        Return STRICT JSON:
        {{
          "primary_problem": "The one sentence meta-problem",
          "non_negotiable_user_expectation": "What users demand as a baseline",
          "current_market_failure": "Why all existing competitors suck",
          "opportunity_statement": "Strategic hook for the new product"
        }}

        INPUT DATA:
        {cluster_context}
        """
        
        try:
            response_text = llm_client.generate(prompt, model_type="smart", token_tracker=tracker)
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            return ProductIntent(**data)
        except:
             return ProductIntent(primary_problem="", non_negotiable_user_expectation="", current_market_failure="", opportunity_statement="")
