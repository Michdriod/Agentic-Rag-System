from typing import Dict, Any
from langgraph.graph import Graph
from agents.retriever import Retriever
from agents.generator import Generator
from agents.embedder import Embedder
from utils.formatter import format_suggestions

class Supervisor:
    def __init__(self):
        # Initialize agent components for each step of the RAG pipeline
        self.retriever = Retriever()  # Handles vector DB retrieval
        self.generator = Generator()  # Handles LLM suggestion generation
        self.embedder = Embedder()    # Handles text embedding
        # Build the LangGraph pipeline graph
        self.graph = self._build_graph()

    def _build_graph(self) -> Graph:
        """
        Build the LangGraph processing pipeline as a directed graph.
        Each node is an async function (agent) that operates on the shared state dict.
        """
        graph = Graph()

        # Define the nodes
        # Node 1: Embed the user query into a vector
        @graph.node
        async def embed(state: Dict[str, Any]) -> Dict[str, Any]:
            query = state["query"]
            embedding = await self.embedder.generate_embedding(query)
            state["embedding"] = embedding  # Store embedding in state
            return state
        
        @graph.node
        async def mich(state: Dict[str, Any]) -> Dict[str, Any]:
            query = state["query"]
            miching = await self.retriever

        # Node 2: Retrieve top-k similar records from the vector DB
        @graph.node
        async def retrieve(state: Dict[str, Any]) -> Dict[str, Any]:
            embedding = state["embedding"]
            similar_records = await self.retriever.get_similar_records(embedding)
            state["similar_records"] = similar_records  # Store retrieved records
            return state

        # Node 3: Generate suggestions using the LLM based on retrieved records
        @graph.node
        async def generate(state: Dict[str, Any]) -> Dict[str, Any]:
            records = state["similar_records"]
            suggestions = await self.generator.generate_suggestions(records)
            state["suggestions"] = suggestions  # Store LLM suggestions
            return state

        # Node 4: Format the suggestions for API/frontend response
        @graph.node
        async def format_output(state: Dict[str, Any]) -> Dict[str, Any]:
            suggestions = state["suggestions"]
            formatted_response = format_suggestions(suggestions)
            state["response"] = formatted_response  # Store formatted response
            return state

        # Define the edges (data flow) between nodes in the pipeline
        (
            graph.add_node("embed", embed)
            .add_node("retrieve", retrieve)
            .add_node("generate", generate)
            .add_node("format", format_output)
            .add_edge("embed", "retrieve")      # embed -> retrieve
            .add_edge("retrieve", "generate")   # retrieve -> generate
            .add_edge("generate", "format")     # generate -> format
        )

        return graph

    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Entry point for processing a user query through the agentic RAG pipeline.
        Runs the LangGraph graph and returns the formatted response.
        """
        state = {"query": query}  # Initial state with user query
        final_state = await self.graph.arun(state)  # Run the graph asynchronously
        return final_state["response"]  # Return the formatted suggestions

    async def initialize(self):
        """
        Initialize components that require async setup (e.g., DB connection pool).
        Should be called on app startup.
        """
        await self.retriever.initialize()

    async def cleanup(self):
        """
        Cleanup resources (e.g., close DB pool). Should be called on app shutdown.
        """
        await self.retriever.close()
