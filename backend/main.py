"""
Data Analyst Agent Backend - Main Entry Point
Organized backend structure for production deployment
"""
import sys
import os

# Add the src directory to Python path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(backend_dir, 'src')
sys.path.insert(0, src_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, query, self_healing
from app.memory import initialize_memory
import logging

# Configure logging to use backend logs directory
log_dir = os.path.join(backend_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'app.log')),
        logging.StreamHandler()
    ]
)

# Initialize FastAPI app
app = FastAPI(
    title="Data Analyst Agent API",
    description="AI-powered data analysis with self-healing capabilities",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize memory store
initialize_memory()

# Include routers with API prefix
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(self_healing.router, prefix="/api", tags=["self-healing"])

@app.get("/", summary="Root endpoint")
async def root():
    return {
        "message": "Data Analyst Agent Backend API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/api/docs"
    }

@app.get("/api/health", summary="Health check")
async def health():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "components": {
            "api": "operational",
            "self_healing": "operational",
            "memory": "operational"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)