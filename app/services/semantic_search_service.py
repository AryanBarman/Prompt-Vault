import numpy as np 
from sqlalchemy.orm import Session
from app.models.prompt import Prompt
from app.services.prompt_ai_service import PromptAIService

class SemanticSearchService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = PromptAIService()

    def cosine_similarity(self, a, b):
        a = np.array(a)
        b = np.array(b)

        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def search_prompts(self, query: str, limit: int = 5):
        query_embedding = self.ai.embed_prompt(query)

        prompts = (
            self.db.query(Prompt)
            .filter(Prompt.embedding.isnot(None))
            .all()
        )

        scored = []

        for p in prompts:
            score = self.cosine_similarity(query_embedding, p.embedding)
            scored.append((score, p))

        # Sort by similarity desc
        scored.sort(key=lambda x: x[0], reverse=True)

        return [p for _, p in scored[:limit]]
    