from typing import List
from sentence_transformers import SentenceTransformer

Model_name = "sentence-transformers/all-MiniLM-L6-v2"

class Embedder:
    def __init__(self):
        self.name = "embedder"
        self.model = SentenceTransformer(Model_name)
        
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for the input text."""
        embedding = self.model.encode(text)
        return embedding.tolist()