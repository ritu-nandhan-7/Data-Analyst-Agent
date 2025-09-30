import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, query, self_healing
from app.memory import memory_store

app = FastAPI(
    title="InsightEngine API",
    description="AI-powered data analysis engine with natural language queries and self-healing capabilities",
    version="2.0.0"
)

# Railway/Production handler
handler = app

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["Data Upload"])
app.include_router(query.router, prefix="/api", tags=["Query Analysis"])
app.include_router(self_healing.router, prefix="/api", tags=["Self-Healing System"])

@app.get("/api/health", tags=["Health"])
async def health():
    """Health check endpoint for frontend"""
    try:
        from app.utils.self_healing import auto_healer
        healing_stats = auto_healer.get_healing_stats()
    except:
        healing_stats = {"total_fixes": 0}
    
    return {
        "status": "healthy",
        "version": "2.0.0",
        "components": {
            "api": "operational",
            "self_healing": "operational", 
            "memory": "operational"
        },
        "dataset_loaded": memory_store.get('dataframe') is not None,
        "current_dataset": memory_store.get('filename', 'None'),
        "self_healing": {
            "total_fixes": healing_stats.get('total_fixes', 0),
            "status": "active"
        }
    }

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    from app.utils.self_healing import auto_healer
    healing_stats = auto_healer.get_healing_stats()
    
    return {
        "message": "InsightEngine API is running",
        "status": "healthy",
        "version": "2.0.0",
        "features": {
            "self_healing": True,
            "ai_powered": True,
            "auto_scaling": True,
            "web_scraping": True
        },
        "dataset_loaded": memory_store.get('dataframe') is not None,
        "current_dataset": memory_store.get('filename', 'None'),
        "self_healing": {
            "total_fixes": healing_stats['total_fixes'],
            "status": "active" if healing_stats['total_fixes'] >= 0 else "inactive"
        }
    }

@app.get("/status", tags=["Health"])
async def status():
    """Get current system status"""
    df = memory_store.get('dataframe')
    return {
        "dataset_loaded": df is not None,
        "dataset_info": {
            "filename": memory_store.get('filename'),
            "engine": memory_store.get('engine'),
            "shape": df.shape if df is not None else None,
            "columns": list(df.columns) if df is not None else None
        } if df is not None else None,
        "memory_usage": len(memory_store)
    }

@app.delete("/reset", tags=["Data Management"])
async def reset_memory():
    """Clear all data from memory"""
    memory_store.clear()
    return {"message": "Memory cleared successfully"}
