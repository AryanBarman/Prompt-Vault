from app.core.ai_client import AIClient
from app.core.logging_config import logger

class PromptAIService:
    def __init__(self):
        self.ai = AIClient()
    
    def improve_prompt(self, prompt_text: str):
        """
        Improve clarity, structure, and effectiveness of a prompt.
        """
        try:
            return self.ai.improve_prompt(prompt_text)
        except Exception as e:
            logger.error(f"Failed to improve prompt: {e}")
            return text # fallback to original prompt

    def generate_variations(self, text: str, count: int = 3):
        """
        Create multiple alternate rewrites of the same prompt.
        """
        prompt = (
            f"Generate {count} different variations of the following prompt. "
            "They should be creative, diverse, and effective.\n\n"
            f"Prompt:\n{text}"
        )

        try:
            raw = self.ai.generate_completion(prompt)
            # Split at new lines or list-like formatting
            variations = [v.strip("-• ").strip() for v in raw.split("\n") if v.strip()]
            return variations[:count]
        except Exception as e:
            logger.error(f"PromptAIService.generate_variations error: {e}")
            return [text] * count

    def summarize_prompt(self, text: str) -> str:
        """
        Summarize a prompt into 1–2 sentences.
        """
        prompt = (
            "Summarize the following prompt into 1–2 sentences, focusing on its purpose:\n\n"
            f"{text}"
        )

        try:
            return self.ai.generate_completion(prompt)
        except Exception as e:
            logger.error(f"PromptAIService.summarize_prompt error: {e}")
            return ""

    def embed_prompt(self, text: str):
        """
        Convert prompt text into vector embeddings.
        """
        try:
            return self.ai.embed_text(text)
        except Exception as e:
            logger.error(f"PromptAIService.embed_prompt error: {e}")
            return []

