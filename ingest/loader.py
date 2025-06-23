import os
from langchain.document_loaders import TextLoader
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Example: Load documents from a directory and ingest into pgvector

def ingest_documents(directory: str, collection_name: str = "transaction_insights"):
    # Load all .txt files in the directory
    loader = TextLoader(directory)
    documents = loader.load()
    # Use HuggingFace embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    # Create or update the vector store
    vectorstore = PGVector.from_documents(
        documents,
        embedding=embeddings,
        connection_string=DATABASE_URL,
        collection_name=collection_name,
        distance_strategy="cosine"
    )
    print(f"Ingested {len(documents)} documents into pgvector collection '{collection_name}'")

# Example usage:
# ingest_documents("/path/to/text/files")
