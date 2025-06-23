import os
from typing import AsyncGenerator
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Create and yield a database connection."""
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Enable pgvector extension if not already enabled
        await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
        yield conn
    finally:
        await conn.close()

async def get_db_pool() -> asyncpg.Pool:
    """Create and return a connection pool."""
    return await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=10,
        setup=lambda conn: conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
    )
