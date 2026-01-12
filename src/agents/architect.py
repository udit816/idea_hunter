import os
import time
import json
import google.generativeai as genai
from ..state import ValidatedIdea, PainPoint, ProductSpec

class ArchitectAgent:
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

    def create_spec(self, idea: ValidatedIdea, pains: list[PainPoint]) -> ProductSpec:
        print(f"   [Architect] Designing MVP for: '{idea.target_keyword}'...")
        
        pain_context = "\n".join([f"- {p.pain_category}: {p.quote}" for p in pains[:5]])
        
        prompt = f"""
        Act as a Senior Product Manager for a MicroSaaS.
        
        CONTEXT:
        We are building a tool to solve this specific problem: "{idea.description}".
        The users are complaining about these things in current solutions:
        {pain_context}
        
        YOUR TASK:
        Design a "Minimum Viable Product" (MVP) spec. Keep it lean, simple, and solvable by a solo developer.
        
        RETURN JSON ONLY with this structure:
        {{
            "mvp_name": "Catchy Name",
            "tagline": "Short value prop",
            "core_features": ["Feature 1", "Feature 2", "Feature 3"],
            "tech_stack_recommendation": ["Frontend tool", "Backend tool", "Database"],
            "user_stories": ["As a user, I want to...", "As a user, I need to..."],
            "marketing_hook": "The one-liner for the landing page hero section"
        }}
        """

        # --- RETRY LOOP ---
        for model_name in self.available_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                cleaned = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(cleaned)
                return ProductSpec(**data)
            except Exception as e:
                if "429" in str(e):
                    time.sleep(5)
                    try:
                        response = model.generate_content(prompt)
                        cleaned = response.text.replace("```json", "").replace("```", "").strip()
                        data = json.loads(cleaned)
                        return ProductSpec(**data)
                    except:
                        pass
                continue
        
        # Fallback empty spec if AI fails completely
        return ProductSpec(
            mvp_name="Error Generating Spec", tagline="", core_features=[], 
            tech_stack_recommendation=[], user_stories=[], marketing_hook=""
        )