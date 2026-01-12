import os
import time
import json
import google.generativeai as genai
from serpapi import GoogleSearch
from typing import List
from ..state import Competitor

class HunterAgent:
    def __init__(self, api_key: str = None, country_code: str = "us"):
        self.serp_api_key = api_key or os.getenv("SERPAPI_KEY")
        self.country_code = country_code
        
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.available_models = []
        
        # --- DYNAMIC MODEL DISCOVERY (Same as Verifier) ---
        try:
            all_models = list(genai.list_models())
            valid_models = [
                m.name for m in all_models 
                if 'generateContent' in m.supported_generation_methods
            ]
            # Sort: Flash first, then Pro
            self.available_models = sorted(
                valid_models, 
                key=lambda x: 0 if 'flash' in x else (1 if 'pro' in x else 2)
            )
            print(f"   [Hunter] System: Discovered {len(self.available_models)} usable AI models.")
        except Exception as e:
            print(f"   [Hunter] Warning: Model discovery failed ({e}). using fallback.")
            self.available_models = ['models/gemini-1.5-flash-latest']

    def hunt(self, niche: str) -> List[Competitor]:
        print(f"   [Hunter] Scouring Google for '{niche}' in ({self.country_code.upper()})...")
        
        # 1. Google Search
        params = {
            "engine": "google",
            "q": f"best {niche} software tools list", 
            "api_key": self.serp_api_key,
            "gl": self.country_code,
            "num": 8
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict().get("organic_results", [])
        except Exception as e:
            print(f"   [!] Google Search Failed: {e}")
            return []
        
        # 2. Prepare Data
        raw_text = ""
        for r in results:
            raw_text += f"Title: {r.get('title')}\nSnippet: {r.get('snippet')}\n---\n"

        # 3. AI Extraction with RETRY LOOP
        print("   [Hunter] Using AI to extract actual product names...")
        extracted_names = self._extract_names_with_retry(niche, raw_text)
        
        # 4. Build Objects
        competitors = []
        for name in extracted_names:
            competitors.append(Competitor(
                name=name,
                url=f"https://google.com/search?q={name}",
                is_relevant=True
            ))
            
        print(f"   [Hunter] Identified {len(competitors)} candidates: {', '.join(extracted_names)}")
        return competitors

    def _extract_names_with_retry(self, niche: str, text: str) -> List[str]:
        prompt = f"""
        I am researching competitors in the niche: '{niche}'.
        I searched Google and got the text below.
        
        YOUR TASK:
        Extract a list of software products that are DIRECT COMPETITORS for '{niche}'.
        
        STRICT FILTERING RULES:
        1. IGNORE generic software (e.g., Tally, QuickBooks, Excel) unless niche is accounting.
        2. IGNORE aggregators (Capterra, G2).
        3. IF a tool is a "Multi-purpose Suite", ONLY include it if it explicitly mentions '{niche}' features.
        
        Search Data:
        {text}
        
        Return ONLY a raw JSON list of strings. Example: ["Tool A", "Tool B"]
        """
        
        # Cycle through models
        for model_name in self.available_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                cleaned_json = response.text.replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned_json)
                
            except Exception as e:
                # Handle Rate Limit (429)
                if "429" in str(e) or "quota" in str(e).lower():
                    print(f"     [!] Rate limit on {model_name}. Waiting 5s...")
                    time.sleep(5)
                    try:
                        # Retry once
                        response = model.generate_content(prompt)
                        cleaned_json = response.text.replace("```json", "").replace("```", "").strip()
                        return json.loads(cleaned_json)
                    except:
                        pass # Move to next model
                else:
                    # If 404 or other error, skip immediately
                    continue

        print("   [!] Hunter AI failed (All models exhausted). Returning empty list.")
        return []