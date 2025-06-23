from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api_routes import router
from agents.supervisor import Supervisor

app = FastAPI(title="Agentic RAG System")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Include API routes
app.include_router(router)

# Create supervisor instance
supervisor = Supervisor()

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    await supervisor.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    await supervisor.cleanup()
