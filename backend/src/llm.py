import os
import time
from typing import Dict, Optional, List
from openai import OpenAI
import httpx

class LLMClient:
    def __init__(self):
        # Ensure API key is present
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("   [LLM] WARNING: OPENAI_API_KEY not found. Calls will fail.")
        
        self.client = OpenAI(api_key=api_key)
        
        # Define models
        self.smart_model = "gpt-4o"
        self.fast_model = "gpt-4o-mini"
        
        print(f"   [LLM] Initialized OpenAI Client. Smart: {self.smart_model}, Fast: {self.fast_model}")

    def generate(self, prompt: str, model_type: str = "smart", system_instruction: str = None, token_tracker: Optional[Dict] = None) -> str:
        """
        Generates content using OpenAI and tracks token usage.
        model_type: 'smart' (gpt-4o) or 'fast' (gpt-4o-mini)
        token_tracker: Dict with 'input' and 'output' keys to update.
        """
        model_name = self.smart_model if model_type == "smart" else self.fast_model
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            return self._call_openai(model_name, messages, token_tracker)
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                print(f"   [LLM] Rate limit hit ({model_name}). Retrying in 5s...")
                time.sleep(5)
                return self._call_openai(model_name, messages, token_tracker)
            else:
                print(f"   [LLM] Error: {e}")
                raise e

    def _call_openai(self, model_name: str, messages: List[Dict], token_tracker: Optional[Dict]) -> str:
        response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7
        )
        
        # Track Usage
        if token_tracker is not None and response.usage:
            token_tracker["input"] += response.usage.prompt_tokens
            token_tracker["output"] += response.usage.completion_tokens
            
        return response.choices[0].message.content.strip()

# Singleton instance
llm_client = LLMClient()
