from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.main import supervisor

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class SuggestionsResponse(BaseModel):
    suggestions: list[dict]

@router.post("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(request: QueryRequest):
    """Get suggestions based on user query."""
    try:
        suggestions = await supervisor.process_query(request.query)
        return SuggestionsResponse(suggestions=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
