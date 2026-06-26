import os
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from google import genai

from app.data.policy_corpus import get_policy_excerpts


class PolicyRetriever:
    def __init__(self, top_k: int = 3):
        self.top_k = top_k
        self.policy_excerpts = get_policy_excerpts()
        self._policy_embeddings: Optional[np.ndarray] = None
        self._client = None
        self._initialized = False

    def _get_client(self):
        if self._client is None:
            api_key = os.environ.get("GEMINI_API_KEY", "")
            self._client = genai.Client(api_key=api_key) if api_key else genai.Client()
        return self._client

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        client = self._get_client()
        try:
            result = client.models.embed_content(
                model="gemini-embedding-2",
                contents=texts,
            )
            return [e.values for e in result.embeddings]
        except Exception:
            return [self._fallback_embedding(t) for t in texts]

    def _fallback_embedding(self, text: str) -> List[float]:
        rng = np.random.RandomState(hash(text) % (2**31))
        vec = rng.randn(768)
        vec = vec / np.linalg.norm(vec)
        return vec.tolist()

    def initialize_corpus(self):
        if self._initialized:
            return

        texts = [excerpt["text"] for excerpt in self.policy_excerpts]
        embeddings = self._embed_texts(texts)
        self._policy_embeddings = np.array(embeddings, dtype=np.float32)
        self._initialized = True

    def retrieve(
        self, claim_context: str
    ) -> List[Tuple[Dict[str, str], float]]:
        if not self._initialized:
            self.initialize_corpus()

        query_embedding = self._embed_texts([claim_context])[0]
        query_vec = np.array(query_embedding, dtype=np.float32)

        dot_products = np.dot(self._policy_embeddings, query_vec)
        norms = np.linalg.norm(self._policy_embeddings, axis=1) * np.linalg.norm(query_vec)
        similarities = dot_products / (norms + 1e-10)

        top_indices = np.argsort(similarities)[-self.top_k:][::-1]

        results = []
        for idx in top_indices:
            results.append((self.policy_excerpts[idx], float(similarities[idx])))

        return results

    def format_claim_context(self, claim: Dict[str, Any]) -> str:
        return (
            f"A claim was filed by provider {claim.get('provider_id', 'unknown')} "
            f"(specialty: {claim.get('provider_specialty', 'unknown')}) "
            f"in the {claim.get('region', 'unknown')} region. "
            f"CPT code: {claim.get('cpt_code', 'unknown')}, "
            f"ICD-10: {claim.get('icd10_code', 'unknown')}, "
            f"billed amount: ${claim.get('billed_amount', 0):.2f}, "
            f"units: {claim.get('units', 1)}."
        )