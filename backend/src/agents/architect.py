import os
import time
import json
from typing import Optional, List, Dict
from ..state import ValidatedIdea, EvidenceSignal, ProductSpec, FeatureDecision, PainCluster, PRD
from ..llm import llm_client

class ArchitectAgent:
    def __init__(self):
        # No init logic needing models
        pass

    def create_spec(self, idea: ValidatedIdea, signals: list[EvidenceSignal], clusters: list[PainCluster] = [], tracker: Optional[Dict] = None) -> ProductSpec:
        print(f"   [Architect] Designing MVP & PRD for: '{idea.target_keyword}'...")
        
        # 1. Feature Strategy (PRD Step 1)
        feature_roadmap = []
        if clusters:
            feature_roadmap = self._plan_features(clusters, tracker)
            
        # 2. Tech Stack (Parallel Step)
        tech_stack = self._recommend_tech_stack(idea, tracker)

        # 3. Full PRD Generation (Step 2)
        prd = self._generate_prd(idea, feature_roadmap, tracker)
        
        # 4. Assemble ProductSpec (Population Logic)
        if prd:
            return ProductSpec(
                # Legacy Mappings
                mvp_name=prd.product_overview.name,
                tagline=prd.product_overview.one_liner,
                core_features=[f.name for f in prd.mvp_features],
                user_stories=prd.user_flow,
                marketing_hook=f"Built for {prd.product_overview.target_user} to {prd.product_overview.one_liner}",
                
                # New Structured Data
                prd=prd,
                feature_roadmap=feature_roadmap,
                tech_stack_recommendation=tech_stack
            )

        # Fallback empty spec
        return ProductSpec(
            mvp_name="Error", tagline="", core_features=[], 
            tech_stack_recommendation=[], user_stories=[], marketing_hook=""
        )

    def _generate_prd(self, idea: ValidatedIdea, features: list[FeatureDecision], tracker: Optional[Dict] = None) -> PRD:
        print(f"   [Architect] Drafting detailed PRD...")
        
        feature_context = "\n".join([f"- {f.proposed_feature} (Solves: {f.pain_theme})" for f in features if f.mvp_priority])
        
        prompt = f"""
        You are a Principal Product Manager.

        INPUT:
        - Validated problem: "{idea.description}"
        - Justified features (MVP Candidates):
        {feature_context}
        - Target keyword: "{idea.target_keyword}"

        Your task:
        Generate a PRD for a MicroSaaS MVP.

        Constraints:
        - Solo developer
        - 30–45 day build
        - No enterprise complexity

        Return JSON only with this exact structure:
        {{
          "product_overview": {{
            "name": "Catchy SaaS Name",
            "one_liner": "Value Prop",
            "target_user": "Persona"
          }},
          "goals": [
            "Reduce X",
            "Enable Y"
          ],
          "non_goals": [
            "What we intentionally do NOT build"
          ],
          "mvp_features": [
            {{
              "name": "Feature Name",
              "description": "What it does",
              "success_metric": "How we measure it"
            }}
          ],
          "user_flow": [
            "Step 1: ...",
            "Step 2: ...",
            "Step 3: ..."
          ],
          "risks_and_unknowns": [
            "..."
          ]
        }}
        """

        try:
            response_text = llm_client.generate(prompt, model_type="smart", token_tracker=tracker)
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            return PRD(**data)
        except Exception as e:
             # print(e)
             return None
                
    def _recommend_tech_stack(self, intent: Optional[ValidatedIdea], tracker: Optional[Dict] = None) -> list[str]:
        desc = intent.description if intent else "MicroSaaS MVP"
        prompt = f"""
        Recommend a modern, solo-dev friendly tech stack for a MicroSaaS described as: "{desc}".
        Return JSON list of strings only: ["Next.js", "Supabase", "TailwindRef"]
        """
        try:
            response_text = llm_client.generate(prompt, model_type="fast", token_tracker=tracker)
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except:
             return ["React", "Python", "SQL"]

    def _plan_features(self, clusters: list[PainCluster], tracker: Optional[Dict] = None) -> list[FeatureDecision]:
        print(f"   [Architect] Generating Feature Roadmap from {len(clusters)} themes...")
        
        # Serialize with new schema handling
        cluster_context = json.dumps([c.model_dump() for c in clusters], default=str)
        
        prompt = f"""
        You are a Senior Product Manager writing a PRD.
        
        INPUT:
        - Ranked pain clusters (from Synthesizer)
        - Each cluster contains: description, impact summary, and why users get angry.

        Your task:
        For each top pain cluster:
        1. Explain why current solutions fail
        2. Propose ONE feature that directly removes the pain
        3. Decide if it belongs in MVP or Phase 2

        Return JSON only:
        {{
          "feature_decisions": [
            {{
              "pain_theme": "cluster_name from input",
              "current_failure": "...",
              "proposed_feature": "...",
              "mvp_priority": true,
              "expected_user_outcome": "what improves for user"
            }}
          ]
        }}
        
        INPUT DATA:
        {cluster_context}
        """
        
        try:
            response_text = llm_client.generate(prompt, model_type="smart", token_tracker=tracker)
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            return [FeatureDecision(**item) for item in data.get("feature_decisions", [])]
        except:
            return []