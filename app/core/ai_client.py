import os
from groq import Groq
from app.core.logging_config import logger


class AIClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            logger.warning("GROQ_API_KEY not found — AIClient running in MOCK MODE.")
            self.mock_mode = True
            return

        try:
            self.client = Groq(api_key=api_key)
            self.model_name = "llama-3.3-70b-versatile"   # excellent free model
            self.embedding_model = "text-embedding-3-large"
            self.mock_mode = False
        except Exception as e:
            logger.error(f"Groq init failed, switching to MOCK mode: {e}")
            self.mock_mode = True
    
    def generate_completion(self, prompt: str):
        if self.mock_mode:
            return f"[MOCK COMPLETION] {prompt}"
        
        try: 
            chat = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
            )
            return chat.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq completion error — fallback to mock: {e}")
            return f"[MOCK COMPLETION FALLBACK] {prompt}"
    
    def improve_prompt(self, prompt_text: str):
        if self.mock_mode:
            return f"[MOCK] Improved prompt: {prompt_text}"

        system_instruction = (
            "Rewrite the user's prompt to be clearer, more detailed, and more effective for a language model."
        )

        full_prompt = (
            f"{system_instruction}\n\n"
            f"User prompt:\n{prompt_text}"
        )

        try:
            chat = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt_text},
                ],
                max_tokens=300,
            )
            return chat.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq improve_prompt error — fallback to mock: {e}")
            return f"[MOCK FALLBACK] Improved prompt: {prompt_text}"

    def embed_text(self, text: str):
        if self.mock_mode:
            return [0.1, 0.3, 0.5, 0.9]

        try:
            embedding = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return embedding.data[0].embedding
        except Exception as e:
            logger.error(f"Groq embedding error — fallback to mock: {e}")
            return [0.1, 0.3, 0.5, 0.9]
