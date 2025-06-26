from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.supervisor_instance import supervisor


router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class SuggestionsResponse(BaseModel):
    suggestions: list[dict]

@router.post("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(request: QueryRequest):
    """Return top 3 relevant transaction insights for user selection."""
    try:
        # Only retrieve top 3 relevant records, no LLM synthesis
        suggestions = await supervisor.get_top_suggestions(request.query)
        return SuggestionsResponse(suggestions=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """Return a synthesized answer and sources using the top 3 insights as context."""
    try:
        result = await supervisor.answer_query(request.query)
        return QueryResponse(answer=result["answer"], sources=result["sources"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AdvancedQueryRequest(BaseModel):
    messages: list[dict]  # Each message: {"role": str, "content": str}

class AdvancedQueryResponse(BaseModel):
    messages: list[dict]

@router.post("/advanced_query", response_model=AdvancedQueryResponse)
async def advanced_query_endpoint(request: AdvancedQueryRequest):
    """Run the advanced agentic workflow with message-passing and handoff."""
    from agents.supervisor import advanced_graph
    # Start with the provided messages state
    state = {"messages": request.messages}
    final_state = await advanced_graph.arun(state)
    return AdvancedQueryResponse(messages=final_state["messages"])
