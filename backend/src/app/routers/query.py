from fastapi import APIRouter, Request, HTTPException
from app.utils.llm_agent import process_query
from app.memory import memory_store, get_conversation
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = {}
    session_id: Optional[str] = "default"

@router.post("/query", summary="Ask questions about your dataset")
async def query_api(query_request: QueryRequest):
    """
    Ask natural language questions about your uploaded dataset.
    
    - **question**: Your question about the data (required)
    - **context**: Additional context or parameters (optional)
    - **session_id**: Session identifier to maintain conversation history (optional)
    
    Returns analysis results, explanations, and visualizations when applicable.
    """
    if not query_request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Check if dataset is loaded
    df = memory_store.get('dataframe')
    if df is None:
        raise HTTPException(status_code=400, detail="No dataset loaded. Please upload a dataset first using /upload")
    
    try:
        # Add timeout handling for complex queries
        import asyncio
        
        result = await asyncio.wait_for(
            process_query(
                query_request.question, 
                query_request.context, 
                query_request.session_id
            ),
            timeout=120  # 2 minutes timeout
        )
        
        # Handle self-healing error responses
        if isinstance(result, dict) and result.get("success") == False:
            if result.get("auto_fix_attempted"):
                return JSONResponse({
                    "success": False,
                    "error": result.get("error"),
                    "message": "Query failed but self-healing was attempted",
                    "auto_healing_info": {
                        "attempted": True,
                        "successful": result.get("auto_fix_successful", False)
                    }
                })
            else:
                raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
        
        return JSONResponse(result)
        
    except asyncio.TimeoutError:
        return JSONResponse({
            "success": False,
            "error": "Query timeout - operation took too long",
            "message": "Complex queries may take time. Consider simplifying or breaking into smaller parts.",
            "timeout": True
        })
    except Exception as e:
        return JSONResponse({
            "success": False, 
            "error": str(e),
            "message": "An unexpected error occurred during query processing"
        })

@router.get("/history/{session_id}", summary="Get conversation history")
async def get_history(session_id: str):
    """
    Get conversation history for a specific session.
    
    - **session_id**: Session identifier
    """
    try:
        history = get_conversation(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

# Legacy endpoint for backward compatibility
@router.post("/query-legacy", include_in_schema=False)
async def query_api_legacy(request: Request):
    """Legacy endpoint - use /query instead"""
    body = await request.json()
    query_request = QueryRequest(
        question=body.get("question", ""),
        context=body.get("context", {}),
        session_id=body.get("session_id", "default")
    )
    return await query_api(query_request)
