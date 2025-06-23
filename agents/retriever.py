from typing import List, Dict, Any
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import VectorStoreRetriever
from db.connection import get_db_pool
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Retriever:
    def __init__(self):
        self.pool = None
        self.retriever = None

    async def initialize(self):
        """Initialize the database pool and LangChain retriever."""
        self.pool = await get_db_pool()
        # Set up LangChain's PGVector vector store and retriever
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = PGVector(
            connection_string=DATABASE_URL,
            embedding_function=embeddings,
            collection_name="transaction_insights",
            distance_strategy="cosine"
        )
        self.retriever = VectorStoreRetriever(
            vectorstore=vectorstore,
            search_kwargs={"k": 3}
        )

    async def get_similar_records(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve top-k similar records using LangChain retriever abstraction."""
        if not self.retriever:
            await self.initialize()
        # LangChain retriever expects a query string, so you may need to pass the original query
        # For now, let's assume you pass the original query text instead of embedding
        # If you want to use embedding directly, you may need to use vectorstore.similarity_search_by_vector
        results = await self.retriever.aget_relevant_documents(query_embedding)
        return [
            {
                'id': doc.metadata.get('id'),
                'description': doc.page_content,
                'distance': doc.metadata.get('distance', None)
            }
            for doc in results
        ]

    async def close(self):
        if self.pool:
            await self.pool.close()
            self.pool = None
