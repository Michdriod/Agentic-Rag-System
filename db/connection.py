# import os
# from typing import AsyncGenerator
# import asyncpg
# from dotenv import load_dotenv

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

# async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
#     """Create and yield a database connection."""
#     conn = await asyncpg.connect(DATABASE_URL)
#     try:
#         # Enable pgvector extension if not already enabled
#         await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
#         yield conn
#     finally:
#         await conn.close()

# async def get_db_pool() -> asyncpg.Pool:
#     """Create and return a connection pool."""
#     return await asyncpg.create_pool(
#         DATABASE_URL,
#         min_size=1,
#         max_size=10,
#         setup=lambda conn: conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
#     )


import os
from typing import AsyncGenerator
import asyncpg
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio



load_dotenv()

def get_database_url():
    """Safely get database URL from environment variables."""
    raw_url = os.getenv("DATABASE_URL")
    
    # Handle various possible formats
    if raw_url is None:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # If it's somehow a list, take the first element
    if isinstance(raw_url, list):
        raw_url = raw_url[0] if raw_url else None
    
    # Convert to string if it's not already
    if not isinstance(raw_url, str):
        raw_url = str(raw_url)
    
    return raw_url

# Get the database URL safely
RAW_DATABASE_URL = get_database_url()

# Create async PostgreSQL DSN (remove +asyncpg if present for asyncpg connections)
ASYNC_PG_DSN = RAW_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# Create SQLAlchemy engine
engine = create_async_engine(RAW_DATABASE_URL)

async def ensure_vector_extension():
    """Ensure the pgvector extension exists in the database."""
    try:
        conn = await asyncpg.connect(ASYNC_PG_DSN)
        try:
            await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
            print("Vector extension ensured")
        finally:
            await conn.close()
    except Exception as e:
        print(f"Error ensuring vector extension: {e}")
        raise

async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Create and yield a database connection."""
    conn = await asyncpg.connect(ASYNC_PG_DSN)
    try:
        yield conn
    finally:
        await conn.close()

async def get_db_pool() -> asyncpg.Pool:
    """Create and return a connection pool."""
    return await asyncpg.create_pool(
        ASYNC_PG_DSN,
        min_size=1,
        max_size=10
    )

# Usage example: run this file directly to ensure the extension exists
if __name__ == "__main__":
    print("RAW_DATABASE_URL:", RAW_DATABASE_URL, type(RAW_DATABASE_URL))
    print("ASYNC_PG_DSN:", ASYNC_PG_DSN, type(ASYNC_PG_DSN))
    asyncio.run(ensure_vector_extension())






# load_dotenv()

# RAW_DATABASE_URL = os.getenv("DATABASE_URL")
# if isinstance(RAW_DATABASE_URL, list):
#     RAW_DATABASE_URL = RAW_DATABASE_URL[0]
# elif RAW_DATABASE_URL is not None and not isinstance(RAW_DATABASE_URL, str):
#     RAW_DATABASE_URL = str(RAW_DATABASE_URL)
# ASYNC_PG_DSN = RAW_DATABASE_URL.replace("+asyncpg", "") if RAW_DATABASE_URL else None


# # Use a plain Postgres DSN for asyncpg (strip +asyncpg if present)
# # RAW_DATABASE_URL = os.getenv("DATABASE_URL")
# # if isinstance(RAW_DATABASE_URL, list):
# #     # If it's a list, join it into a string (or pick the first element)
# #     RAW_DATABASE_URL = RAW_DATABASE_URL[0]
# # ASYNC_PG_DSN = RAW_DATABASE_URL.replace("+asyncpg", "") if RAW_DATABASE_URL else None
# # # RAW_DATABASE_URL = os.getenv("DATABASE_URL")
# # # ASYNC_PG_DSN = RAW_DATABASE_URL.replace("+asyncpg", "") if RAW_DATABASE_URL else None

# engine = create_async_engine(RAW_DATABASE_URL)

# async def ensure_vector_extension():
#     """Ensure the pgvector extension exists in the database."""
#     conn = await asyncpg.connect(ASYNC_PG_DSN)
#     try:
#         await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
#     finally:
#         await conn.close()

# async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
#     """Create and yield a database connection."""
#     conn = await asyncpg.connect(ASYNC_PG_DSN)
#     try:
#         yield conn
#     finally:
#         await conn.close()

# async def get_db_pool() -> asyncpg.Pool:
#     """Create and return a connection pool."""
#     return await asyncpg.create_pool(
#         ASYNC_PG_DSN,
#         min_size=1,
#         max_size=10
#     )

# # Usage example: run this file directly to ensure the extension exists
# if __name__ == "__main__":
#     asyncio.run(ensure_vector_extension())
# print("RAW_DATABASE_URL:", RAW_DATABASE_URL, type(RAW_DATABASE_URL))
# print("DEBUG RAW_DATABASE_URL:", RAW_DATABASE_URL, type(RAW_DATABASE_URL))