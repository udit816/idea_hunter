import os
import time
import json
from serpapi import GoogleSearch
from typing import List, Dict, Optional
from ..state import EvidenceSignal, ValidatedIdea
from ..llm import llm_client

class ValidatorAgent:
    def __init__(self, country_code: str = "us"):
        self.serp_api_key = os.getenv("SERPAPI_KEY")
        self.country_code = country_code

    def validate(self, signals: List[EvidenceSignal], tracker: Optional[Dict] = None) -> List[ValidatedIdea]:
        if not signals:
            print("   [Validator] No signals to validate.")
            return []

        print(f"   [Validator] Validating {len(signals)} evidence signals...")
        validated_ideas = []

        # Process top 5 unique signals
        for signal in signals[:5]: 
            target_keyword = self._generate_keyword_with_retry(signal, tracker)
            print(f"     Checking Demand for: '{target_keyword}'...")
            
            metrics = self._check_google_metrics(target_keyword)
            score = self._calculate_score(metrics)

            idea = ValidatedIdea(
                description=f"Solve '{signal.pain_description}'",
                target_keyword=target_keyword,
                search_volume=metrics['total_results'], 
                cpc=0.0, 
                difficulty=0, 
                opportunity_score=score
            )
            validated_ideas.append(idea)
            
        return validated_ideas

    def _generate_keyword_with_retry(self, signal: EvidenceSignal, tracker: Optional[Dict] = None) -> str:
        prompt = f"Convert this user problem into a Google Search keyword that a buyer would type:\nProblem: '{signal.pain_description}'\nContext: {signal.example_evidence}\nReturn JUST the keyword string:"
        
        try:
            # Use 'fast' model for simple keyword generation
            return llm_client.generate(prompt, model_type="fast", token_tracker=tracker).replace('"', '')
        except:
            return "software alternative"

    def _check_google_metrics(self, keyword: str) -> dict:
        params = {
            "engine": "google",
            "q": keyword,
            "api_key": self.serp_api_key,
            "gl": self.country_code,
        }
        try:
            results = GoogleSearch(params).get_dict()
            total_results = results.get("search_information", {}).get("total_results", "0")
            clean_count = int(total_results.split()[0].replace(',', '')) if total_results else 0
            return {"total_results": clean_count}
        except:
            return {"total_results": 0}

    def _calculate_score(self, metrics: dict) -> float:
        count = metrics['total_results']
        if count > 100000: return 8.0 
        if count > 10000: return 9.0 
        if count > 1000: return 6.0 
        return 2.0