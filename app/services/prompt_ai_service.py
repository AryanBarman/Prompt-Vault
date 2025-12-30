from app.core.ai_client import AIClient
from app.core.logging_config import logger
import json

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
            return prompt_text # fallback to original prompt

    def generate_variations(self, text: str, count: int = 3):
        """
        Create multiple alternate rewrites of the same prompt.
        Returns a list of strings.
        """

        system_prompt = f"""
        You are an expert prompt engineer.
        Return ONLY VALID JSON. No explanations.

        Format exactly:
        {{
        "variations": [
            "variation 1",
            "variation 2",
            "variation 3"
        ]
        }}

        Rules:
        - Generate {count} different rewrites of the prompt
        - Each variation MUST be clear and useful
        - Do NOT add commentary
        - Do NOT say 'Here are variations'
        """

        full_prompt = f"{system_prompt}\n\nUser Prompt:\n{text}"

        try:
            raw = self.ai.generate_completion(full_prompt)

            if not raw or not raw.strip():
                raise ValueError("AI returned empty output")

            raw = raw.strip()

            # If wrapped in ```json ... ``` remove formatting
            if raw.startswith("```"):
                raw = raw.strip("`").strip()
                if raw.lower().startswith("json"):
                    raw = raw[4:].strip()

            data = json.loads(raw)

            variations = data.get("variations", [])
            if not isinstance(variations, list):
                raise ValueError("variations is not a list")

            # Guarantee count
            if len(variations) < count:
                while len(variations) < count:
                    variations.append(text)

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

    def suggest_next_version(self, text: str):
        system_prompt = """
            You are an expert prompt engineer.
            Return ONLY valid JSON.
            Format:
            {
            "suggested_prompt": "analyse the existing prompt and suggest an improved version on the basis of great ideas already there behind the prompt topic",
            "explanation": "why this is better in 2-4 sentences",
            "improvements": ["point 1", "point 2", "point 3"]
            }
            """

        full_prompt = f"{system_prompt}\n\nUser Prompt:\n{text}"

        try:
            raw = self.ai.generate_completion(full_prompt)

            if not raw or not raw.strip():
                raise ValueError("AI returned empty output")

            raw = raw.strip()

            # Remove surrounding ``` if present
            if raw.startswith("```"):
                raw = raw.strip("`").strip()   # removes backticks first
                # Optional: remove leading "json"
                if raw.lower().startswith("json"):
                    raw = raw[4:].strip()

            data = json.loads(raw)
            return data
        except Exception as e:
            logger.error(f"suggest_next_version parsing failed: {e}")
            return {
                "suggested_prompt": text,
                "explanation": "AI failed, returning original.",
                "improvements": []
            }


