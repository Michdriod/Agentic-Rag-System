# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from app.api_routes import router
# from agents.supervisor_instance import supervisor

# app = FastAPI(title="Agentic RAG System")

# # CORS middleware configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, replace with specific origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Mount static files for frontend
# app.mount("/static", StaticFiles(directory="frontend"), name="static")

# # Include API routes
# app.include_router(router)

# # Create supervisor instance
# # supervisor = Supervisor()

# @app.on_event("startup")
# async def startup_event():
#     """Initialize components on startup."""
#     pass
#     # await supervisor.initialize()

# @app.on_event("shutdown")
# async def shutdown_event():
#     """Cleanup resources on shutdown."""
#     pass
#     # await supervisor.cleanup()




from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api_routes import router
from agents.supervisor_instance import supervisor
import os

app = FastAPI(title="Agentic RAG System")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend if directory exists
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Include API routes
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    try:
        print("Starting up application...")
        await supervisor.initialize()
        print("Application startup completed successfully")
    except Exception as e:
        print(f"Error during startup: {e}")
        # Don't raise here to allow the app to start even if initialization fails
        # raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    try:
        print("Shutting down application...")
        await supervisor.cleanup()
        print("Application shutdown completed successfully")
    except Exception as e:
        print(f"Error during shutdown: {e}")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Agentic RAG System is running"}

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "Agentic RAG System",
        "version": "1.0.0"
    }