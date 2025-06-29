# Agentic Retrieval-Augmented Generation (RAG) System

## Overview

This project is a **modular, production-ready, agentic Retrieval-Augmented Generation (RAG) system** for retrieving and generating actionable transaction insights from a PostgreSQL database using vector search and LLMs. It is built with:

- **LangGraph** for agentic, graph-based orchestration
- **LangChain** for LLM and retrieval abstractions
- **FastAPI** for the async backend API
- **PostgreSQL/pgvector** for scalable vector search
- **Hugging Face** for embeddings
- **Modern HTML/CSS** frontend

---

## Features

- Agentic, graph-based workflow using LangGraph
- Async, modular codebase for scalability and maintainability
- LLM-powered generation with LangChain’s ChatGroq and PromptTemplate
- Semantic retrieval using pgvector and Hugging Face embeddings
- Configurable, separate prompts for suggestions and direct answers
- Modern, responsive frontend for user interaction
- Comprehensive code comments and documentation

---

## Architecture

```User ↔️ Frontend (HTML/CSS) ↔️ FastAPI Backend ↔️ LangGraph Supervisor
    ↳ Retriever Agent (LangChain + pgvector)
    ↳ Generator Agent (LangChain LLM)
    ↳ Embedder Agent (Hugging Face)
    ↳ PostgreSQL/pgvector (Vector DB)
```

- **Supervisor**: Orchestrates the agentic workflow using LangGraph
- **Retriever**: Finds relevant transaction insights using vector search
- **Generator**: Produces suggestions or direct answers using LLM and prompts
- **Embedder**: Handles embedding generation for queries and ingestion

---

## Directory Structure

Agentic-Rag-System/
├── app/
│   ├── main.py                # FastAPI app entrypoint
│   └── api_routes.py          # API route definitions
├── agents/
│   ├── supervisor.py          # LangGraph workflow orchestrator
│   ├── retriever.py           # Retrieval agent (LangChain + pgvector)
│   ├── generator.py           # Generation agent (LLM + prompts)
│   └── embedder.py            # Embedding agent (Hugging Face)
├── db/
│   ├── connection.py          # PostgreSQL/pgvector connection
│   └── embed_data.py          # Ingestion/embedding logic
├── ingest/
│   └── loader.py              # Document loader for ingestion (optional)
├── utils/
│   └── formatter.py           # Output formatting utilities
├── prompts/
│   ├── suggestions_system.txt # System prompt for suggestions
│   ├── suggestions_user.txt   # User prompt for suggestions
│   ├── query_system.txt       # System prompt for query answers
│   └── query_user.txt         # User prompt for query answers
├── frontend/
│   ├── index.html             # Main frontend UI
│   └── style.css              # Frontend styling
├── .env.example               # Example environment variables
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
└── LICENSE                    # License file

---

## Technology Stack

- **Python 3.10+**
- **FastAPI** (async API backend)
- **LangChain** (LLM, retrieval, prompt management)
- **LangGraph** (agentic, graph-based orchestration)
- **PostgreSQL** with **pgvector** (vector search)
- **Hugging Face Transformers** (embeddings)
- **Modern HTML/CSS** (frontend)

---

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/Agentic-Rag-System.git
cd Agentic-Rag-System
```

### 2. Install Python Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

- Copy `.env.example` to `.env` and fill in your values:
  - PostgreSQL connection string
  - Hugging Face API key (if needed)
  - LLM provider keys (e.g., Groq)

### 4. Set Up PostgreSQL with pgvector

- Install PostgreSQL and the `pgvector` extension:

```bash
brew install postgresql
brew services start postgresql
psql -c "CREATE EXTENSION IF NOT EXISTS vector;" -d your_db
```

- Create the database and user as needed.

### 5. (Optional) Ingest Documents

- If you want to add new documents, use the ingestion script:

```bash
python db/embed_data.py
```

### 6. Start the Backend API

```bash
uvicorn app.main:app --reload
```

### 7. Open the Frontend

- Open `frontend/index.html` in your browser.
- The frontend communicates with the FastAPI backend.

---

## Usage

### API Endpoints

- **POST /suggestions**:  
  Returns the top 3 most relevant transaction insights for user selection.
  - Request: `{ "query": "Show me customers at risk of churn" }`
  - Response:

    ```json
    {
      "suggestions": [
        {
          "id": 3,
          "title": "Customer Inactivity Alert",
          "description": "...",
          "category": "Analytics"
        },
        ...
      ]
    }
    ```

- **POST /query**:  
  Returns a synthesized answer (and sources) generated by the LLM, using the top 3 insights as context.
  - Request: `{ "query": "What should I do about inactive customers?" }`
  - Response:

    ```
    
    json
    {
      "answer": "High-value customers with 30+ days of inactivity should be targeted with engagement campaigns to prevent churn.",
      "sources": [
        { "id": 3, "title": "Customer Inactivity Alert" }
      ]
    }
    ```

See `app/api_routes.py` for up-to-date endpoint definitions and request/response formats.

### Frontend

- Simple, modern UI for submitting queries and viewing results.
- Customize `frontend/index.html` and `style.css` as needed.

---

## Agentic Workflow (LangGraph)

- **Supervisor** (`agents/supervisor.py`): Orchestrates the workflow as a graph of async nodes (agents)
- **Retriever** (`agents/retriever.py`): Uses LangChain’s VectorStoreRetriever with pgvector to retrieve top-k relevant documents
- **Generator** (`agents/generator.py`): Uses LangChain’s ChatGroq and PromptTemplate, with separate prompts for suggestions and answers
- **Embedder** (`agents/embedder.py`): Uses Hugging Face models for embedding generation

---

## Prompts

- **prompts/suggestions_system.txt**: System prompt for suggestions endpoint
- **prompts/suggestions_user.txt**: User prompt for suggestions endpoint
- **prompts/query_system.txt**: System prompt for query endpoint
- **prompts/query_user.txt**: User prompt for query endpoint

Edit these files to customize the LLM’s behavior for each endpoint.

---

## Configuration

- **.env**: Set all required environment variables (DB, API keys, etc.)
- **requirements.txt**: Add/remove dependencies as needed

---

## Extending the System

- Add new agents: Create new agent modules in `agents/` and update the supervisor graph
- Change LLM or embeddings: Swap out LangChain components in `generator.py` or `embedder.py`
- Customize prompts: Edit prompt files in `prompts/`
- Frontend: Enhance UI/UX in `frontend/`

---

## Async & Modular Design

- All core logic is async for scalability
- Each agent is modular and testable
- State is passed between agents using LangGraph’s node structure

---

## Troubleshooting & FAQ

- **Dependency issues**: Ensure all packages in `requirements.txt` are installed in your virtualenv
- **Database errors**: Check PostgreSQL is running and `pgvector` is enabled
- **API errors**: Check `.env` values and backend logs
- **Frontend not connecting**: Ensure backend is running and CORS is configured if needed

---

## References & Further Reading

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)

---

## License

See [LICENSE](LICENSE) for details.

---

## Maintainers

- Micheal Alejo

---

## Acknowledgements

- LangChain, LangGraph, Hugging Face, FastAPI, pgvector, and the open-source community.

---
