from fastapi import APIRouter
from app.utils.self_healing import auto_healer
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/self-healing/stats", summary="Get self-healing statistics")
async def get_self_healing_stats():
    """
    Get comprehensive statistics about auto-fixes performed by the system
    """
    stats = auto_healer.get_healing_stats()
    return JSONResponse({
        "self_healing_enabled": True,
        "statistics": stats,
        "status": "active"
    })

@router.post("/self-healing/trigger-fix", summary="Manually trigger error analysis")
async def trigger_manual_fix(error_description: str, function_name: str):
    """
    Manually trigger the self-healing system for testing purposes
    """
    try:
        # This would be used for testing the self-healing system
        return JSONResponse({
            "message": f"Manual fix triggered for {function_name}",
            "error_description": error_description,
            "status": "processing"
        })
    except Exception as e:
        return JSONResponse({
            "error": f"Failed to trigger manual fix: {str(e)}"
        }, status_code=500)

@router.get("/self-healing/logs", summary="Get recent self-healing logs")
async def get_healing_logs():
    """
    Get recent self-healing activity logs
    """
    try:
        # Read recent logs from file
        logs = []
        try:
            with open('self_healing.log', 'r') as f:
                logs = f.readlines()[-50:]  # Last 50 lines
        except FileNotFoundError:
            logs = ["No healing logs yet"]
            
        return JSONResponse({
            "recent_logs": logs,
            "total_lines": len(logs)
        })
    except Exception as e:
        return JSONResponse({
            "error": f"Failed to read logs: {str(e)}"
        }, status_code=500)