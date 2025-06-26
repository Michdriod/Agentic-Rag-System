# ===== FIXED SUPERVISOR.PY =====
from typing_extensions import TypedDict
from typing import Any, Annotated, List, Dict
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from langchain.chat_models import init_chat_model
from agents.retriever import Retriever
from agents.generator import Generator
from agents.embedder import Embedder
from utils.formatter import format_suggestions

class State(TypedDict):
    query: str
    embedding: Any
    similar_records: Any
    suggestions: Any
    response: Any

# Initialize agents
retriever_agent = Retriever()
generator_agent = Generator()
embedder_agent = Embedder()

class Supervisor:
    def __init__(self):
        self.retriever = retriever_agent
        self.generator = generator_agent
        self.embedder = embedder_agent

    async def initialize(self):
        """Initialize all components"""
        try:
            await self.retriever.initialize()
            print("Supervisor initialized successfully")
        except Exception as e:
            print(f"Error initializing supervisor: {e}")
            raise

    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.retriever.close()
            print("Supervisor cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    async def get_top_suggestions(self, query: str) -> List[Dict]:
        """
        Get top 3 suggestions based on user query.
        This is for the /suggestions endpoint.
        """
        try:
            # Step 1: Generate embedding for the query
            embedding = await self.embedder.generate_embedding(query)
            print(f"Generated embedding for query: {query}")
            
            # Step 2: Retrieve similar records from database
            similar_records = await self.retriever.get_similar_records(embedding, top_k=3)
            print(f"Retrieved {len(similar_records)} similar records")
            
            if not similar_records:
                return [{"suggestion": "No relevant suggestions found.", "confidence": 0.0}]
            
            # Step 3: Generate natural language suggestions using LLM
            suggestions = await self.generator.generate_suggestions(similar_records)
            print(f"Generated {len(suggestions)} suggestions")
            
            # Step 4: Format and return suggestions
            return suggestions[:3]  # Ensure we return exactly 3 suggestions
            
        except Exception as e:
            print(f"Error getting top suggestions: {e}")
            return [{"suggestion": f"Error: {str(e)}", "confidence": 0.0}]

    async def answer_query(self, query: str) -> Dict:
        """
        Answer a query by retrieving context and generating a single comprehensive answer.
        This is for the /query endpoint.
        """
        try:
            # Step 1: Generate embedding for the query
            embedding = await self.embedder.generate_embedding(query)
            print(f"Generated embedding for query: {query}")
            
            # Step 2: Retrieve similar records from database
            similar_records = await self.retriever.get_similar_records(embedding, top_k=3)
            print(f"Retrieved {len(similar_records)} similar records for answer generation")
            
            if not similar_records:
                return {
                    "answer": "I don't have enough information to answer your question.",
                    "sources": []
                }
            
            # Step 3: Generate comprehensive answer using LLM
            answer = await self.generator.generate_answer(similar_records, query)
            
            # Step 4: Prepare sources
            sources = [
                {
                    "id": record.get("id", "unknown"),
                    "title": record.get("description", "")[:100] + "..." if len(record.get("description", "")) > 100 else record.get("description", ""),
                    "confidence": record.get("confidence", 0.0)
                }
                for record in similar_records
            ]
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            print(f"Error answering query: {e}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "sources": []
            }

# Create the supervisor instance
supervisor_instance = Supervisor()







# from typing_extensions import TypedDict
# from typing import Any, Annotated
# from langchain_core.tools import tool, InjectedToolCallId
# from langgraph.prebuilt import InjectedState
# from langgraph.graph import StateGraph, START, END, MessagesState
# from langgraph.types import Command
# from langchain_core.runnables import RunnableConfig
# from langgraph_supervisor import create_supervisor
# from langchain.chat_models import init_chat_model
# from agents.retriever import Retriever, retriever
# from agents.generator import Generator
# from agents.embedder import Embedder
# from utils.formatter import format_suggestions

# class State(TypedDict):
#     query: str
#     embedding: Any
#     similar_records: Any
#     suggestions: Any
#     response: Any

# # Initialize agents (ensure they are compatible with LangGraph's agent interface)
# retriever_agent = Retriever()
# generator_agent = Generator()
# embedder_agent = Embedder()

# # Initialize your model (replace with your actual model if not OpenAI)
# model = init_chat_model("llama-3.3-70b-versatile", model_provider="groq") # llama3-8b-8192, llama-3.3-70b-versatile

# # Create the supervisor agent
# supervisor = create_supervisor(
#     model=model,
#     agents=[retriever_agent, generator_agent, embedder_agent],
#     prompt=(
#         "You are a supervisor managing three agents:\n"
#         "- a retriever agent for vector DB retrieval\n"
#         "- a generator agent for LLM suggestion generation\n"
#         "- an embedder agent for text embedding\n"
#         "Assign work to one agent at a time, do not call agents in parallel.\n"
#         "Do not do any work yourself."
#     ),
#     add_handoff_back_messages=True,
#     output_mode="full_history",
# ).compile()

# class Supervisor:
#     def __init__(self):
#         self.graph = self._build_graph()

#     def _build_graph(self):
#         builder = StateGraph(State)

#         # Node: Embed the user query into a vector
#         async def embed(state: State, config: RunnableConfig = None) -> State:
#             query = state["query"]
#             embedding = await embedder_agent.generate_embedding(query)
#             state["embedding"] = embedding
#             return state

#         # Node: Retrieve top-k similar records from the vector DB
#         async def retrieve(state: State, config: RunnableConfig = None) -> State:
#             embedding = state["embedding"]
#             similar_records = await retriever_agent.get_similar_records(embedding)
#             state["similar_records"] = similar_records
#             return state

#         # Node: Generate suggestions using the LLM based on retrieved records
#         async def generate(state: State, config: RunnableConfig = None) -> State:
#             records = state["similar_records"]
#             suggestions = await generator_agent.generate_suggestions(records)
#             state["suggestions"] = suggestions
#             return state

#         # Node: Format the suggestions for API/frontend response
#         async def format_output(state: State, config: RunnableConfig = None) -> State:
#             suggestions = state["suggestions"]
#             formatted_response = format_suggestions(suggestions)
#             state["response"] = formatted_response
#             return state

#         builder.add_node("embed", embed)
#         builder.add_node("retrieve", retrieve)
#         builder.add_node("generate", generate)
#         builder.add_node("format", format_output)
#         builder.add_edge(START, "embed")
#         builder.add_edge("embed", "retrieve")
#         builder.add_edge("retrieve", "generate")
#         builder.add_edge("generate", "format")
#         builder.add_edge("format", END)

#         return builder.compile()

#     async def process_query(self, query: str) -> Any:
#         state = {"query": query}
#         final_state = await self.graph.arun(state)
#         return final_state["response"]

#     async def initialize(self):
#         await retriever_agent.initialize()

#     async def cleanup(self):
#         await retriever_agent.close()

#     async def get_top_suggestions(self, query: str):
#         embedding = await embedder_agent.generate_embedding(query)
#         records = await retriever_agent.get_similar_records(embedding)
#         return records

#     async def answer_query(self, query: str):
#         embedding = await embedder_agent.generate_embedding(query)
#         records = await retriever_agent.get_similar_records(embedding)
#         answer = await generator_agent.generate_answer(records, query)
#         sources = [{"id": r.get("id"), "title": r.get("title")} for r in records]
#         return {"answer": answer, "sources": sources}

# # --- Advanced agentic workflow with message-passing, handoff, and tool-calling ---

# def create_handoff_tool(*, agent_name: str, description: str | None = None):
#     name = f"transfer_to_{agent_name}"
#     description = description or f"Ask {agent_name} for help."

#     @tool(name, description=description)
#     def handoff_tool(
#         state: Annotated[MessagesState, InjectedState],
#         tool_call_id: Annotated[str, InjectedToolCallId],
#     ) -> Command:
#         tool_message = {
#             "role": "tool",
#             "content": f"Successfully transferred to {agent_name}",
#             "name": name,
#             "tool_call_id": tool_call_id,
#         }
#         return Command(
#             goto=agent_name,
#             update={**state, "messages": state["messages"] + [tool_message]},
#             graph=Command.PARENT,
#         )
#     return handoff_tool

# # Example agent nodes using MessagesState and InjectedState
# async def retriever_node(
#     state: Annotated[MessagesState, InjectedState],
#     config: dict = None
# ) -> Command:
#     user_message = state["messages"][-1]["content"]
#     # Call your retriever logic here (e.g., use retriever_agent)
#     # For demo, just echo
#     new_message = {"role": "retriever", "content": f"Retrieved for: {user_message}"}
#     return Command(update={**state, "messages": state["messages"] + [new_message]})

# async def generator_node(
#     state: Annotated[MessagesState, InjectedState],
#     config: dict = None
# ) -> Command:
#     last_message = state["messages"][-1]["content"]
#     # Call your generator logic here (e.g., use generator_agent)
#     new_message = {"role": "generator", "content": f"Generated for: {last_message}"}
#     return Command(update={**state, "messages": state["messages"] + [new_message]})

# # Build the advanced graph
# advanced_builder = StateGraph(MessagesState)
# advanced_builder.add_node("retriever", retriever_node)
# advanced_builder.add_node("generator", generator_node)
# advanced_builder.add_node("handoff_to_generator", create_handoff_tool(agent_name="generator"))
# advanced_builder.add_edge(START, "retriever")
# advanced_builder.add_edge("retriever", "handoff_to_generator")
# advanced_builder.add_edge("handoff_to_generator", "generator")
# advanced_builder.add_edge("generator", END)
# advanced_graph = advanced_builder.compile()

# # You can now expose advanced_graph as an alternative workflow in your API or for testing



# # supervisor_instance = Supervisor()