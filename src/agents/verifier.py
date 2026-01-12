import os
import time
import json
import google.generativeai as genai
from typing import List, Dict

class VerifierAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.available_models = []
        
        # --- DYNAMIC MODEL DISCOVERY ---
        try:
            # 1. Ask Google what models are actually available to YOU
            all_models = list(genai.list_models())
            
            # 2. Filter for models that can generate content
            valid_models = [
                m.name for m in all_models 
                if 'generateContent' in m.supported_generation_methods
            ]
            
            # 3. Sort them to prefer 'Flash' (fast) and 'Pro' (smart)
            # We put them at the front of the list
            self.available_models = sorted(
                valid_models, 
                key=lambda x: 0 if 'flash' in x else (1 if 'pro' in x else 2)
            )
            
            print(f"   [System] Discovered {len(self.available_models)} usable models.")
            
        except Exception as e:
            print(f"   [!] Error listing models: {e}")
            # Fallback if discovery fails
            self.available_models = ['models/gemini-1.5-flash-latest']

    def verify_niche(self, raw_input: str) -> Dict:
        print(f"   [Verifier] Optimizing prompt: '{raw_input}'...")
        
        prompt = f"""
        Act as a MicroSaaS Product Coach.
        I will give you a "Niche Idea".
        
        YOUR JOB:
        1. Check if it fits the formula: "[Specific Process] software for [Specific Industry/Persona]".
        2. If it is too vague (e.g., "AI for fashion", "HR software"), mark it as "vague".
        3. Generate 3 "Investor-Grade" alternatives that are specific, searchable, and solve a hard problem.
        
        INPUT: "{raw_input}"
        
        RETURN JSON ONLY:
        {{
            "status": "valid" OR "vague",
            "critique": "Short explanation of why it's bad",
            "suggestions": [
                "Alternative 1 (Process + Persona)",
                "Alternative 2 (Process + Persona)",
                "Alternative 3 (Process + Persona)"
            ]
        }}
        """
        
        # --- ROBUST RETRY LOOP ---
        # Try every model we discovered until one works
        for model_name in self.available_models:
            try:
                # print(f"     ... Trying {model_name}") 
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                cleaned_json = response.text.replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned_json)
                
            except Exception as e:
                # If Rate Limit (429), wait and retry ONCE
                if "429" in str(e) or "quota" in str(e).lower():
                    print(f"     [!] Rate limit on {model_name}. Waiting 5s...")
                    time.sleep(5)
                    try:
                        response = model.generate_content(prompt)
                        cleaned_json = response.text.replace("```json", "").replace("```", "").strip()
                        return json.loads(cleaned_json)
                    except:
                        pass # Move to next model
                
                # If 404 (Not Found), just skip to the next model immediately
                continue

        # If ALL models fail
        print("   [!] Verifier failed (All models exhausted). Proceeding with manual input.")
        return {"status": "valid", "suggestions": []}