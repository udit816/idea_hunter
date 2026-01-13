import os
import time
import json
import requests
from serpapi import GoogleSearch
from typing import List, Dict, Optional
from ..state import Competitor, EvidenceSignal
from ..llm import llm_client

class MinerAgent:
    def __init__(self, country_code: str = "us"):
        self.serp_api_key = os.getenv("SERPAPI_KEY")
        self.country_code = country_code
        
    def mine(self, competitors: List[Competitor], tracker: Optional[Dict] = None) -> List[EvidenceSignal]:
        all_signals = []
        print(f"   [Miner] Deep Dive on {len(competitors)} competitors...")
        
        for comp in competitors:
            try:
                # Extract seeds from metadata if available
                seeds = comp.metadata.get("found_via_seeds", []) if comp.metadata else []
                
                signals = self._analyze_competitor(comp, seeds, tracker)
                all_signals.extend(signals)
            except Exception as e:
                print(f"   [Miner] Failed to mine {comp.name}: {e}")
            
        return all_signals

    def _analyze_competitor(self, comp: Competitor, seeds: List[str] = [], tracker: Optional[Dict] = None) -> List[EvidenceSignal]:
        print(f"     -> Analyzing {comp.name}...")
        
        # 1. Collect Evidence (Multi-Source Strategy)
        raw_text = self._collect_evidence(comp.name)
        
        if not raw_text:
            print(f"     -> No data found for {comp.name}.")
            return []

        # 2. Extract Signals (Deep Analysis)
        signals = self._extract_signals(comp.name, raw_text, seeds, tracker)
        print(f"     -> Found {len(signals)} evidence signals.")
        return signals

    def _collect_evidence(self, name: str) -> str:
        """Aggregates text from multiple query patterns."""
        aggregated_text = ""
        
        queries = [
            f"site:reddit.com {name} scam | review | problem",
            f"site:play.google.com {name} reviews",
            f"{name} fraud complaint",
            f"{name} hidden charges premium",
            f"{name} vs competitors alternatives reddit"
        ]
        
        for q in queries:
            params = {
                "engine": "google",
                "q": q,
                "api_key": self.serp_api_key,
                "gl": self.country_code,
                "num": 4 
            }
            try:
                # Basic search loop
                results = GoogleSearch(params).get_dict().get("organic_results", [])
                for r in results:
                    snippet = r.get('snippet', '')
                    if len(snippet) > 50: # Filter noise
                        aggregated_text += f"[Source: Google Search - '{q}'] {snippet}\n"
            except Exception:
                pass
            
            time.sleep(0.5) 

        return aggregated_text

    def _extract_signals(self, name: str, text: str, seeds: List[str] = [], tracker: Optional[Dict] = None) -> List[EvidenceSignal]:
        prompt = f"""
        You are a Product Research Miner.

        INPUT:
        - Product: {name}
        - Mixed raw text from Reddit, Reviews, Complaints, etc.

        YOUR OBJECTIVE:
        Extract EVIDENCE-BASED USER PAINS that indicate:
        - broken workflows
        - trust failure
        - pricing resentment
        - missing critical information
        - operational friction

        IMPORTANT:
        You are NOT summarizing opinions.
        You are identifying REPEATED FAILURE MODES.

        CLASSIFY each pain into one of:
        - Discovery Friction
        - Trust & Safety
        - Pricing / Paywall
        - Workflow Breakdown
        - UX / Usability
        - Missing Capability

        FOR EACH PAIN:
        1. Identify the underlying problem (not just the symptom)
        2. Determine if this pain:
           - blocks trial
           - blocks payment
           - causes churn
           - causes legal or financial risk
        3. Capture at least ONE direct quote or paraphrase

        Return STRICT JSON only:

        [
          {{
            "source_type": "Reddit | AppReview | Blog | FAQ | Complaint",
            "platform": "{name}",
            "pain_theme": "short label",
            "pain_description": "what users are really struggling with",
            "example_evidence": "quote or paraphrase",
            "impact": "trial_blocker | conversion_blocker | churn | trust_collapse",
            "severity": "low | medium | high | critical",
            "confidence": 0.9
          }}
        ]
        
        DATA:
        {text[:15000]}
        """
        
        try:
            # Smart Pro model for deep analysis
            response_text = llm_client.generate(prompt, model_type="smart", token_tracker=tracker)
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            
            # Enrich with seeds
            for item in data:
                # Heuristic: Assign all seeds that led to this competitor. 
                # In a perfect world we'd track which seed led to the specific text chunk, 
                # but "Competitor" level association is a strong enough proxy for V1 optimization request.
                item['metadata'] = {'source_seeds': seeds}

            return [EvidenceSignal(**item) for item in data]
        except Exception as e:
            if "429" in str(e):
               # LLMClient handles internal retries, but if it bubbles up, we return empty here or log
               pass
            # print(e)
            return []

    # Synthesis moved to SynthesizerAgent