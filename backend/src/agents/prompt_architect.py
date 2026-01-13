import os
from ..llm import llm_client

class PromptArchitectAgent:
    def __init__(self):
        # llm_client handles config
        pass

    def generate_prompt(self, context: str) -> str:
        mode = self._choose_mode(context)
        print(f"   [PromptArchitect] Mode: {mode} (Input length: {len(context.split())} words)")
        
        if mode.startswith("NORMALIZE"):
            if mode == "NORMALIZE-AUGMENT":
                 # Augment mode: Add missing axes
                system_instruction = """
                You are a senior product researcher.
                
                The user has provided a detailed product idea but missed some critical evaluation axes.
                Your task is to Normalize the existing input AND Augment it with checks for missing risks.
                
                Rules:
                1. Preserve the core idea and domain exactly.
                2. Remove marketing/sales language.
                3. Add specific investigation bullets for: Willingness to Pay, Current Behavior, and Risks (Legal/Trust) IF missing.
                4. Do NOT add new features or adjacent markets.
                5. Keep output under 220 words.
                """
            else:
                # Strict mode
                system_instruction = """
                You are a senior product researcher.
                Your task is to Normalize the input into a neutral investigation prompt.
                
                Rules:
                1. Compress and neutralize the text.
                2. Remove marketing language.
                3. Do NOT add new scope.
                4. Keep output under 200 words.
                """
            
            prompt = f"""
            Input:
            {context[:3000]}

            Output format:
            Context paragraph...
            
            Investigate:
            • ...
            • ...
            
            Evaluate whether...
            """
            
            try:
                # Using 'smart' model for augmentation to ensure it follows strict constraints? 
                # Actually 'fast' (mini) is usually good enough for formatting if prompted well, 
                # but 'smart' (4o) follows complex negative constraints better. 
                # Let's stick to fast for speed unless it fails, but user said "Model choice is NOT the problem".
                # Actually, "Normalize-Augment" is tricky. Let's use 'smart' for Augment to be safe? 
                # User's previous logs showed 429s on Pro. Let's try 'fast' first. 
                generated = llm_client.generate(prompt, model_type="fast", system_instruction=system_instruction)
                return self._enforce_length(generated)
            except Exception as e:
                print(f"Prompt Architect Error: {e}")
                return context # Fallback
        
        else:
            # EXPAND Mode (Existing)
            prompt = f"""
            You are a senior product researcher.

            Given a short or vague idea, expand it into a neutral, evidence-seeking
            investigation prompt.

            Rules:
            - Do not propose features or solutions
            - Do not assume the idea is valid
            - Focus on real user pain, current behavior, willingness to pay,
              and legal, operational, or trust risks
            - Explicitly allow for DO NOT BUILD as a valid outcome
            - Keep the output under 220 words
            - Use 1 context paragraph + 4–5 investigation bullets + 1 outcome clause

            Input:
            {context[:1000]}

            Output:
            """
            try:
                 return self._enforce_length(llm_client.generate(prompt, model_type="fast"))
            except Exception:
                 return context

    def _choose_mode(self, user_input: str) -> str:
        words = user_input.split()
        word_count = len(words)
        lower_input = user_input.lower()

        has_structure = any(
            marker in lower_input
            for marker in ["•", "-", "1.", "2.", "investigate", "platform", "b2b"]
        )
        
        # Heuristic 1: Short/Vague -> EXPAND
        if word_count < 150 and not has_structure:
            return "EXPAND"

        # Heuristic 2: Detailed -> Check for AUGMENT
        missing_axes = []
        if not any(w in lower_input for w in ["pay", "budget", "pricing", "buy", "spend", "subscribe"]):
            missing_axes.append("willingness_to_pay")
        if not any(w in lower_input for w in ["risk", "legal", "compliance", "fraud", "trust", "policy"]):
             missing_axes.append("risk")
        if not any(w in lower_input for w in ["currently", "today", "existing", "workaround", "spreadsheet", "manual"]):
             missing_axes.append("current_behavior")

        if missing_axes:
            return "NORMALIZE-AUGMENT"
        
        return "NORMALIZE-STRICT"

    def _enforce_length(self, prompt: str, max_words=220) -> str:
        words = prompt.split()
        if len(words) <= max_words:
            return prompt
        return " ".join(words[:max_words]) + "…"
