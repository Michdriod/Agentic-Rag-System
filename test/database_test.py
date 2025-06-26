# ===== DATABASE SETUP AND VERIFICATION SCRIPT =====
import asyncio
import asyncpg
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(__file__)))

load_dotenv()

# Get database URL
RAW_DATABASE_URL = os.getenv("DATABASE_URL")
if RAW_DATABASE_URL and "+asyncpg" in RAW_DATABASE_URL:
    ASYNC_PG_DSN = RAW_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
else:
    ASYNC_PG_DSN = RAW_DATABASE_URL

async def setup_database():
    """Set up the database with proper table structure and sample data."""
    conn = await asyncpg.connect(ASYNC_PG_DSN)
    
    try:
        print("Setting up database...")
        
        # Enable pgvector extension
        await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
        print("✓ Vector extension enabled")
        
        # Create table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS transaction_insights (
            id SERIAL PRIMARY KEY,
            description TEXT NOT NULL,
            category VARCHAR(100),
            amount DECIMAL(10,2),
            insight_type VARCHAR(50),
            embedding vector(384),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await conn.execute(create_table_query)
        print("✓ Table created/verified")
        
        # Check if we have data
        count = await conn.fetchval("SELECT COUNT(*) FROM transaction_insights")
        print(f"✓ Current records in database: {count}")
        
        # If no data, insert sample data
        if count == 0:
            print("Inserting sample transaction insights...")
            sample_data = [
                ("You spend 40% of your income on dining out, consider reducing restaurant visits", "spending", 150.00, "pattern"),
                ("Your grocery spending has increased by 25% this month compared to last month", "spending", 350.00, "trend"),
                ("You have consistent monthly subscriptions totaling $89, review if all are necessary", "subscription", 89.00, "analysis"),
                ("Your savings rate is 15% which is good, try to increase it to 20% for better financial health", "savings", 500.00, "goal"),
                ("You spend most money on weekends, consider budgeting for weekend activities", "timing", 200.00, "pattern"),
                ("Your coffee shop visits cost $85/month, making coffee at home could save $65/month", "recommendation", 85.00, "savings"),
                ("Your utility bills have been stable at $120/month, good budget management", "bills", 120.00, "stability"),
                ("You have irregular income patterns, consider building a larger emergency fund", "income", 0.00, "recommendation"),
                ("Your credit card usage is 60% of limit, consider paying down balance to improve credit score", "credit", 1200.00, "advice"),
                ("You spend $300/month on entertainment, which is 8% of income - within recommended range", "entertainment", 300.00, "analysis")
            ]
            
            for desc, cat, amt, insight_type in sample_data:
                await conn.execute(
                    """
                    INSERT INTO transaction_insights (description, category, amount, insight_type)
                    VALUES ($1, $2, $3, $4)
                    """,
                    desc, cat, amt, insight_type
                )
            print(f"✓ Inserted {len(sample_data)} sample records")
        
        # Generate embeddings for records without them
        records_without_embeddings = await conn.fetch(
            "SELECT id, description FROM transaction_insights WHERE embedding IS NULL"
        )
        
        if records_without_embeddings:
            print(f"Generating embeddings for {len(records_without_embeddings)} records...")
            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            
            for record in records_without_embeddings:
                # Generate embedding
                embedding = model.encode(record['description'])
                embedding_list = embedding.tolist()
                embedding_str = f"[{','.join(map(str, embedding_list))}]"
                
                # Update record
                await conn.execute(
                    "UPDATE transaction_insights SET embedding = $1::vector WHERE id = $2",
                    embedding_str, record['id']
                )
            
            print("✓ Generated embeddings for all records")
        
        # Verify final state
        final_count = await conn.fetchval("SELECT COUNT(*) FROM transaction_insights")
        embedding_count = await conn.fetchval("SELECT COUNT(*) FROM transaction_insights WHERE embedding IS NOT NULL")
        
        print(f"✓ Final state: {final_count} total records, {embedding_count} with embeddings")
        
        return True
        
    except Exception as e:
        print(f"✗ Error setting up database: {e}")
        return False
    finally:
        await conn.close()

async def test_vector_search():
    """Test vector similarity search functionality."""
    conn = await asyncpg.connect(ASYNC_PG_DSN)
    
    try:
        print("\nTesting vector search...")
        
        # Test query
        test_query = "spending too much money"
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        query_embedding = model.encode(test_query)
        embedding_str = f"[{','.join(map(str, query_embedding.tolist()))}]"
        
        # Search for similar records
        results = await conn.fetch(
            """
            SELECT 
                id, 
                description,
                category,
                1 - (embedding <=> $1::vector) as similarity
            FROM transaction_insights 
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> $1::vector
            LIMIT 3
            """,
            embedding_str
        )
        
        print(f"Query: '{test_query}'")
        print("Similar records found:")
        for i, record in enumerate(results, 1):
            print(f"{i}. {record['description'][:80]}..." if len(record['description']) > 80 else f"{i}. {record['description']}")
            print(f"   Category: {record['category']}, Similarity: {record['similarity']:.3f}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"✗ Error testing vector search: {e}")
        return False
    finally:
        await conn.close()

async def verify_system_components():
    """Verify all system components work together."""
    try:
        print("\nTesting system components...")
        
        # Test embedder
        from agents.embedder import Embedder
        embedder = Embedder()
        test_embedding = await embedder.generate_embedding("test query")
        print(f"✓ Embedder works (embedding length: {len(test_embedding)})")
        
        # Test retriever
        from agents.retriever import Retriever
        retriever = Retriever()
        await retriever.initialize()
        similar_records = await retriever.get_similar_records(test_embedding, top_k=3)
        print(f"✓ Retriever works (found {len(similar_records)} records)")
        await retriever.close()
        
        # Test generator
        from agents.generator import Generator
        generator = Generator()
        if similar_records:
            suggestions = await generator.generate_suggestions(similar_records)
            print(f"✓ Generator works (generated {len(suggestions)} suggestions)")
            
            answer = await generator.generate_answer(similar_records, "What should I do about my spending?")
            print(f"✓ Answer generation works (answer length: {len(answer)} chars)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing system components: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main setup and verification function."""
    print("=== DATABASE SETUP AND SYSTEM VERIFICATION ===\n")
    
    # Step 1: Setup database
    db_setup_success = await setup_database()
    if not db_setup_success:
        print("Database setup failed. Cannot continue.")
        return
    
    # Step 2: Test vector search
    vector_search_success = await test_vector_search()
    if not vector_search_success:
        print("Vector search test failed.")
        return
    
    # Step 3: Test system components
    system_test_success = await verify_system_components()
    if not system_test_success:
        print("System component test failed.")
        return
    
    print("\n=== ALL TESTS PASSED ===")
    print("Your system should now work correctly!")
    print("\nNext steps:")
    print("1. Start your FastAPI server: uvicorn main:app --reload")
    print("2. Test the endpoints:")
    print("   POST /suggestions with {'query': 'help with spending'}")
    print("   POST /query with {'query': 'what should I do about my finances?'}")

if __name__ == "__main__":
    asyncio.run(main())