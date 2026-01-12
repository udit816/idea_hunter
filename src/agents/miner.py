import os
import time
import json
import requests
import google.generativeai as genai
from serpapi import GoogleSearch
from typing import List
from ..state import Competitor, PainPoint

class MinerAgent:
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
            print(f"   [Miner] System: Discovered {len(self.available_models)} usable AI models.")
        except:
            self.available_models = ['models/gemini-1.5-flash-latest']

    def mine(self, competitors: List[Competitor]) -> List[PainPoint]:
        all_pains = []
        print(f"   [Miner] Deep Dive on {len(competitors)} competitors...")

        for comp in competitors:
            if not comp.is_relevant: continue
            
            print(f"   [Miner] Analyzing: {comp.name}...")
            
            # 1. Reddit Strategy
            text_data = self._get_reddit_data(comp.name)
            
            # 2. Fallback to General Reviews
            if not text_data:
                print(f"     -> No Reddit data. Checking general reviews...")
                text_data = self._get_general_reviews(comp.name)

            if text_data:
                pains = self._analyze_with_retry(comp.name, text_data)
                all_pains.extend(pains)
                print(f"     -> Found {len(pains)} insights.")
            
            time.sleep(1) # Polite delay
            
        return all_pains

    def _analyze_with_retry(self, name: str, text: str) -> List[PainPoint]:
        prompt = f"""
        Analyze these review snippets for '{name}'.
        Extract 1-2 distinct pain points (Pricing, UX, or Missing Features).
        If the text is positive or marketing fluff, return an empty list.
        
        Return ONLY valid JSON. Format:
        [{{"source": "Google Snippet", "quote": "...", "pain_category": "Pricing", "sentiment_score": -0.5, "frequency": 1}}]
        
        Data:
        {text[:5000]}
        """
        
        # --- RETRY LOOP ---
        for model_name in self.available_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                cleaned = response.text.replace("```json", "").replace("```", "").strip()
                return [PainPoint(**item) for item in json.loads(cleaned)]
            except Exception as e:
                if "429" in str(e):
                    time.sleep(5)
                    try:
                        response = model.generate_content(prompt)
                        cleaned = response.text.replace("```json", "").replace("```", "").strip()
                        return [PainPoint(**item) for item in json.loads(cleaned)]
                    except:
                        pass
                continue
        
        return []

    def _get_reddit_data(self, name: str) -> str:
        params = {
            "engine": "google",
            "q": f"site:reddit.com {name} software", 
            "api_key": self.serp_api_key,
            "gl": self.country_code,
            "num": 3
        }
        try:
            results = GoogleSearch(params).get_dict().get("organic_results", [])
            text = ""
            for r in results:
                text += f"Source: Reddit | Content: {r.get('snippet', '')}\n"
            return text
        except:
            return ""

    def _get_general_reviews(self, name: str) -> str:
        params = {
            "engine": "google",
            "q": f"{name} software reviews cons complaints",
            "api_key": self.serp_api_key,
            "gl": self.country_code,
            "num": 5
        }
        try:
            results = GoogleSearch(params).get_dict().get("organic_results", [])
            text = ""
            for r in results:
                text += f"Source: Review Site | Content: {r.get('snippet', '')}\n"
            return text
        except:
            return ""