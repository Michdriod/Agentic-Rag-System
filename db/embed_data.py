import asyncio
from sentence_transformers import SentenceTransformer
import numpy as np
from connection import get_db_connection
from dotenv import load_dotenv

load_dotenv()

Model_name = "sentence-transformers/all-MiniLM-L6-v2"

async def generate_and_store_embeddings():
    """Generate embeddings for transaction insights and store them in the database."""
    # Load the model
    model = SentenceTransformer(Model_name)
    
    async for conn in get_db_connection():
        # Fetch all records that don't have embeddings
        records = await conn.fetch(
            """
            SELECT id, description FROM transaction_insights 
            WHERE embedding IS NULL
            """
        )
        
        for record in records:
            # Generate embedding
            text_embedding = model.encode(record['description'])
            
            # Convert numpy array to list and from list to str in PostgreSQL format expected for a vector, then store in database
            embedding_list = text_embedding.tolist()
            embedding_str = f"[{', '.join(str(x) for x in embedding_list)}]"
            
            # Update the record with the embedding
            await conn.execute(
                """
                UPDATE transaction_insights 
                SET embedding = $1::vector(384)
                WHERE id = $2
                """,
                embedding_str,
                record['id']
            )
            
            print(f"Generated and stored embedding for record {record['id']}")

if __name__ == "__main__":
    asyncio.run(generate_and_store_embeddings())
