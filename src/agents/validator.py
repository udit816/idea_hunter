import os
import time
import json
import google.generativeai as genai
from serpapi import GoogleSearch
from typing import List
from ..state import PainPoint, ValidatedIdea

class ValidatorAgent:
    def __init__(self, country_code: str = "us"):
        self.serp_api_key = os.getenv("SERPAPI_KEY")
        self.country_code = country_code
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.available_models = []
        
        # --- DYNAMIC DISCOVERY ---
        try:
            all_models = list(genai.list_models())
            valid_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
            self.available_models = sorted(valid_models, key=lambda x: 0 if 'flash' in x else (1 if 'pro' in x else 2))
            print(f"   [Validator] System: Discovered {len(self.available_models)} usable AI models.")
        except:
            self.available_models = ['models/gemini-1.5-flash-latest']

    def validate(self, pains: List[PainPoint]) -> List[ValidatedIdea]:
        if not pains:
            print("   [Validator] No pain points to validate.")
            return []

        print(f"   [Validator] Validating {len(pains)} pain points...")
        validated_ideas = []

        # Process top 5 unique pains
        for pain in pains[:5]: 
            target_keyword = self._generate_keyword_with_retry(pain)
            print(f"     Checking Demand for: '{target_keyword}'...")
            
            metrics = self._check_google_metrics(target_keyword)
            score = self._calculate_score(metrics)

            idea = ValidatedIdea(
                description=f"Solve '{pain.quote}'",
                target_keyword=target_keyword,
                search_volume=metrics['total_results'], 
                cpc=0.0, 
                difficulty=0, 
                opportunity_score=score
            )
            validated_ideas.append(idea)
            
        return validated_ideas

    def _generate_keyword_with_retry(self, pain: PainPoint) -> str:
        prompt = f"Convert this pain point into a Google Search keyword that a buyer would type:\nPain: '{pain.quote}'\nCategory: {pain.pain_category}\nReturn JUST the keyword string:"
        
        # --- RETRY LOOP ---
        for model_name in self.available_models:
            try:
                model = genai.GenerativeModel(model_name)
                res = model.generate_content(prompt)
                return res.text.strip().replace('"', '')
            except Exception as e:
                if "429" in str(e):
                    time.sleep(5)
                    try:
                        res = model.generate_content(prompt)
                        return res.text.strip().replace('"', '')
                    except:
                        pass
                continue
        
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