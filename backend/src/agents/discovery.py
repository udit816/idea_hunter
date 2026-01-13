import os
import time
import json
import google.generativeai as genai
from ..state import DiscoveryData, ProblemStatement

class DiscoveryAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.available_models = []
        
        # --- DYNAMIC DISCOVERY ---
        try:
            all_models = list(genai.list_models())
            valid_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
            # Prefer Pro for complex reasoning, Flash for speed
            self.available_models = sorted(valid_models, key=lambda x: 0 if 'pro' in x else (1 if 'flash' in x else 2))
        except:
            self.available_models = ['models/gemini-1.5-flash-latest']

    def discover(self, raw_input: str) -> DiscoveryData:
        print(f"   [Discovery] Analyzing input: '{raw_input}'...")
        
        prompt = f"""
        You are a Product Discovery Agent.

        INPUT: "{raw_input}"
        
        INPUT may contain:
        - URLs
        - competitor names
        - vague ideas
        - observations
        - partial hypotheses

        Your task:
        1. Infer what market or workflow the user is exploring
        2. Generate 2–3 PROBLEM STATEMENTS (not solutions)
        3. Each problem must be:
           - Specific
           - Painful
           - Experienced repeatedly
           - Expressed in user language

        RETURN JSON ONLY:
        {{
          "interpreted_domain": "...",
          "problem_statements": [
            {{
              "who": "persona",
              "problem": "clear pain statement",
              "why_now": "why this problem matters today"
            }}
          ]
        }}
        """

        # --- RETRY LOOP ---
        for model_name in self.available_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                cleaned = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(cleaned)
                return DiscoveryData(**data)
            except Exception as e:
                if "429" in str(e):
                    time.sleep(5)
                    try:
                        response = model.generate_content(prompt)
                        cleaned = response.text.replace("```json", "").replace("```", "").strip()
                        data = json.loads(cleaned)
                        return DiscoveryData(**data)
                    except:
                        pass
                continue
        
        # Fallback
        return DiscoveryData(
            interpreted_domain="Unknown Domain", 
            problem_statements=[
                ProblemStatement(who="Unknown", problem="Could not analyze input", why_now="Error in AI processing")
            ]
        )
