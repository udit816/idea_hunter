import os
import time
import json
from serpapi import GoogleSearch
from typing import List, Dict, Optional
from ..state import Competitor
from ..llm import llm_client

class HunterAgent:
    def __init__(self, api_key: str = None, country_code: str = "us"):
        self.serp_api_key = api_key or os.getenv("SERPAPI_KEY")
        # Ensure default is handled gracefully if passed as "us" from existing calls, 
        # but internal logic will prefer global if not strictly needed. 
        # Actually user requested to remove default US bias.
        # We will change the default to None or empty string for global.
        self.country_code = country_code if country_code != "us" else None 

    def hunt(self, niche: str, tracker: Optional[Dict] = None) -> List[Competitor]:
        print(f"   [Hunter] Scouring Google for '{niche}'...")
        
        # 1. Extract Search Seeds
        seeds = self._extract_search_seeds(niche, tracker)
        print(f"     -> Seeds: {seeds}")

        all_results = []
        
        # 2. Search Loop (Per Seed)
        competitors_map = {} # Url -> Competitor
        
        for seed in seeds:
             print(f"     -> Searching Seed: '{seed}'")
             params = {
                "engine": "google",
                "q": f"{seed} competitors pricing reviews", 
                "api_key": self.serp_api_key,
                "num": 4
            }
             if self.country_code:
                 params["gl"] = self.country_code

             try:
                search = GoogleSearch(params)
                results = search.get_dict().get("organic_results", [])
                
                # Dedupe and map to seed
                for r in results:
                    link = r.get('link')
                    if link:
                        if link not in competitors_map:
                            competitors_map[link] = {
                                'title': r.get('title'),
                                'snippet': r.get('snippet'),
                                'seeds': {seed} # Set of seeds that found this link
                            }
                        else:
                            competitors_map[link]['seeds'].add(seed)
                            
             except Exception as e:
                print(f"   [!] Google Search Failed for seed '{seed}': {e}")
                pass
             
             time.sleep(0.5)

        # 3. AI Extraction & Object Creation
        # We need to extract names, then map back to seeds?
        # Or we just return the raw URLs as competitors for now?
        # The current Hunter extracts "Product Names" from snippets.
        # This abstraction layer makes "Seed -> Evidence" hard because we lose the "Search Result -> Product" link if we just extract names.
        
        # Workaround:
        # We will iterate through the EXTRACTED names.
        # IF a name helps us find a URL, that URL is associated with the seeds that found the original search results?
        # This is tricky.
        
        # Simpler approach requested by User Principles:
        # "Hunter must search on concept core... Merge evidence... Score by recurrence across seeds"
        
        # If I change Hunter to return "Competitors found via Seed X", 
        # Miner can then say "Evidence from Competitor A (found via Seed X)".
        
        # Let's update `Competitor` to have `found_via_seeds: List[str]`.
        
        raw_text_combined = ""
        for link, data in list(competitors_map.items())[:12]:
             raw_text_combined += f"Title: {data['title']}\nSnippet: {data['snippet']}\n---\n"

        print("   [Hunter] Using AI to extract actual product names...")
        extracted_names = self._extract_names(niche, raw_text_combined, tracker)
        
        competitors = []
        for name in extracted_names:
            # Re-verify which seeds likely found this name? 
            # Or just assign ALL seeds for now? No that breaks the logic.
            # We need to know which seed produced the snippet that contained the name.
            
            
            # Heuristic: Check if name appears in snippets associated with a seed.
            matched_seeds = set()
            best_snippet = ""
            for link, data in competitors_map.items():
                if name.lower() in (data['title'] + " " + data['snippet']).lower():
                    matched_seeds.update(data['seeds'])
                    if not best_snippet:
                        best_snippet = data['snippet']
            
            # If no direct match (AI hallucinated or inferred), assign 'primary'
            if not matched_seeds and seeds:
                matched_seeds.add(seeds[0])

            competitors.append(Competitor(
                name=name,
                url=f"https://google.com/search?q={name}", 
                is_relevant=True,
                metadata={
                    "found_via_seeds": list(matched_seeds),
                    "snippet": best_snippet
                }
            ))
            
        print(f"   [Hunter] Identified {len(competitors)} candidates.")
        return competitors

    def _validate_market_seeds(self, seeds: List[str]) -> List[str]:
        forbidden_terms = [
            "willingness", "legal", "risk", "privacy", "compliance",
            "assess", "evaluate", "determine", "implications", "concerns"
        ]
        clean_seeds = []
        for seed in seeds:
            if not any(term in seed.lower() for term in forbidden_terms):
                clean_seeds.append(seed)
        return clean_seeds

    def _extract_search_seeds(self, prompt: str, tracker: Optional[Dict] = None) -> List[str]:
        system_prompt = """
        You are a market intelligence analyst.

        Your task is to extract search seeds used ONLY for:
        1) market discovery
        2) competitor identification
        3) user pain discovery

        CRITICAL RULES:
        - Market seeds must represent how USERS describe products or categories.
        - Market seeds must be short noun phrases (2–6 words).
        - Market seeds MUST NOT include:
        • evaluation questions
        • willingness-to-pay language
        • legal, compliance, or risk phrasing
        • verbs like assess, evaluate, determine, analyze
        - Risk, legal, or trust concerns must NEVER be search seeds.

        You must extract:
        - 1 primary market seed
        - 3–5 secondary market seeds
        - 2–4 risk flags (non-search concepts)

        Market seeds are used for search.
        Risk flags are used ONLY for downstream evaluation.

        Return JSON only. No explanations.
        {
          "primary_market_seed": "string",
          "secondary_market_seeds": ["string", "string"],
          "risk_flags": ["string", "string"]
        }
        """
        
        try:
            user_prompt = f"""
            Given the following investigation context, extract market search seeds.

            Context:
            {prompt[:3000]}

            Follow all rules strictly.
            """
            
            response_json = llm_client.generate(user_prompt, model_type="smart", system_instruction=system_prompt, token_tracker=tracker)
            cleaned = response_json.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            
            primary = data.get("primary_market_seed", "")
            secondaries = data.get("secondary_market_seeds", [])
            
            # Use validator
            validated_primary = self._validate_market_seeds([primary])
            validated_secondaries = self._validate_market_seeds(secondaries)
            
            if not validated_primary:
                # ABORT
                raise ValueError("Analysis Aborted: Primary market seed contained forbidden evaluation/risk terms. Please refine input to focus on the market/problem.")

            return validated_primary + validated_secondaries
            
        except ValueError as ve:
            raise ve
        except Exception as e:
            print(f"   [Hunter] Seed extraction failed: {e}")
            # Fallback (Very risky, but prevents total crash if LLM fails format, though likely should fail)
            return [prompt.split("\\n")[0][:50]]

    def _extract_names(self, niche: str, text: str, tracker: Optional[Dict] = None) -> List[str]:
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
        
        try:
            # Smart logic sometimes better for complex extraction, but Flash is likely sufficient for JSON
            # Using 'smart' to be safe for rigorous mining contexts
            response_text = llm_client.generate(prompt, model_type="smart", token_tracker=tracker)
            cleaned_json = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_json)
        except Exception as e:
            print(f"   [Hunter] Extraction failed: {e}")
            return []