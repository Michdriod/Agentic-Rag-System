from typing import List, Dict, Any
import asyncpg
from db.connection import get_db_pool
import os
from dotenv import load_dotenv

load_dotenv()

class Retriever:
    def __init__(self):
        self.name = "retriever"
        self.pool = None

    async def initialize(self):
        """Initialize the database pool."""
        try:
            self.pool = await get_db_pool()
            print("Retriever initialized successfully")
        except Exception as e:
            print(f"Error initializing retriever: {e}")
            raise

    async def get_similar_records(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve top-k similar records using direct vector similarity search.
        """
        if not self.pool:
            await self.initialize()
        
        try:
            # Convert embedding to PostgreSQL vector format
            embedding_str = f"[{','.join(map(str, query_embedding))}]"
            
            # Use connection from pool
            async with self.pool.acquire() as conn:
                # Direct SQL query for vector similarity search
                query = """
                    SELECT 
                        id, 
                        description,
                        1 - (embedding <=> $1::vector) as similarity_score
                    FROM transaction_insights 
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> $1::vector
                    LIMIT $2
                """
                
                results = await conn.fetch(query, embedding_str, top_k)
                
                if not results:
                    print("No similar records found in database")
                    return []
                
                # Format results
                formatted_results = []
                for i, record in enumerate(results):
                    formatted_results.append({
                        'id': record['id'],
                        'description': record['description'],
                        'suggestion': record['description'],  # Use description as suggestion base
                        'confidence': float(record['similarity_score']) if record['similarity_score'] else 0.0,
                        'rank': i + 1
                    })
                
                print(f"Successfully retrieved {len(formatted_results)} similar records")
                return formatted_results
                
        except Exception as e:
            print(f"Error retrieving similar records: {e}")
            print(f"Query embedding length: {len(query_embedding) if query_embedding else 'None'}")
            return []

    async def close(self):
        """Close the database pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            print("Retriever connections closed")






# from typing import List, Dict, Any
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_postgres import PGVector
# # from langchain_community.vectorstores import PGVector
# # from langchain_community.embeddings import HuggingFaceEmbeddings
# # # from langchain_community.retrievers import VectorStoreRetriever
# from sqlalchemy.ext.asyncio import create_async_engine
# from db.connection import get_db_pool
# import os
# from dotenv import load_dotenv

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")
# # db_url = os.getenv("DB_POOL_URL")

# class Retriever:
#     def __init__(self):
#         self.name = "retriever"
#         self.pool = None
#         self.retriever = None

#     async def initialize(self):
#         """Initialize the database pool and LangChain retriever."""
#         self.pool = await get_db_pool()
#         embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#         engine = create_async_engine(DATABASE_URL)
#         vectorstore = PGVector(
#             connection=engine,
#             embeddings=embeddings,  # <-- use 'embedding_function' for langchain_postgres PGVector
#             collection_name="transaction_insights",
#             distance_strategy="cosine",
#             create_extension=False
#         )
#         self.retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        
#         # self.retriever = VectorStoreRetriever(
#         #     vectorstore=vectorstore,
#         #     search_kwargs={"k": 3}
#         # )

#     async def get_similar_records(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
#         """Retrieve top-k similar records using LangChain retriever abstraction."""
#         if not self.retriever:
#             await self.initialize()
#         results = await self.retriever.ainvoke(query_embedding)
#         return [
#             {
#                 'suggestion': doc.page_content,  # Use as the suggestion text
#                 'confidence': 1.0 - doc.metadata.get('distance', 0.0) if doc.metadata.get('distance') is not None else None,
#                 'id': doc.metadata.get('id'),
#                 # ...other fields if needed...
#             }
#             for doc in results
#         ]

#     async def close(self):
#         if self.pool:
#             await self.pool.close()
#             self.pool = None



# from typing import List, Dict, Any
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_postgres import PGVector
# from sqlalchemy.ext.asyncio import create_async_engine
# from db.connection import get_db_pool
# import os
# from dotenv import load_dotenv

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

# class Retriever:
#     def __init__(self):
#         self.name = "retriever"
#         self.pool = None
#         self.vectorstore = None
#         self.retriever = None

#     async def initialize(self):
#         """Initialize the database pool and LangChain retriever."""
#         try:
#             self.pool = await get_db_pool()
#             embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#             engine = create_async_engine(DATABASE_URL)
#             self.vectorstore = PGVector(
#                 connection=engine,
#                 embeddings=embeddings,
#                 collection_name="transaction_insights",
#                 distance_strategy="cosine",
#                 create_extension=False
#             )
#             self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
#             print("Retriever initialized successfully")
#         except Exception as e:
#             print(f"Error initializing retriever: {e}")
#             raise

#     async def get_similar_records(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
#         """Retrieve top-k similar records using direct vector similarity search."""
#         if not self.pool:
#             await self.initialize()
        
#         try:
#             # Convert embedding to string format for PostgreSQL
#             embedding_str = f"[{','.join(map(str, query_embedding))}]"
            
#             async with self.pool.acquire() as conn:
#                 # Direct SQL query for vector similarity search
#                 query = """
#                     SELECT id, description, 1 - (embedding <=> $1::vector) as similarity
#                     FROM transaction_insights 
#                     WHERE embedding IS NOT NULL
#                     ORDER BY embedding <=> $1::vector
#                     LIMIT $2
#                 """
#                 results = await conn.fetch(query, embedding_str, top_k)
                
#                 return [
#                     {
#                         'id': record['id'],
#                         'suggestion': record['description'],
#                         'description': record['description'],
#                         'confidence': float(record['similarity']) if record['similarity'] else 0.0
#                     }
#                     for record in results
#                 ]
#         except Exception as e:
#             print(f"Error retrieving similar records: {e}")
#             # Fallback: return empty list or raise
#             return []

#     async def get_similar_records_by_query(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
#         """Retrieve similar records using text query (for LangChain retriever)."""
#         if not self.retriever:
#             await self.initialize()
        
#         try:
#             results = await self.retriever.ainvoke(query)
#             return [
#                 {
#                     'id': doc.metadata.get('id'),
#                     'suggestion': doc.page_content,
#                     'description': doc.page_content,
#                     'confidence': 1.0 - doc.metadata.get('distance', 0.0) if doc.metadata.get('distance') is not None else 0.8,
#                 }
#                 for doc in results[:top_k]
#             ]
#         except Exception as e:
#             print(f"Error retrieving records by query: {e}")
#             return []

#     async def close(self):
#         if self.pool:
#             await self.pool.close()
#             self.pool = None