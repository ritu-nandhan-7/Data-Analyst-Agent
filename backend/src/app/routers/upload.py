from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.utils.data_handler import handle_upload, handle_url_data
from app.memory import memory_store
from fastapi.responses import JSONResponse
from typing import Optional

router = APIRouter()

@router.post("/upload", summary="Upload dataset or provide URL for scraping")
async def upload_dataset(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None)
):
    """
    Upload a dataset file or provide a URL for data scraping.
    
    - **file**: Upload CSV, JSON, or Excel file (optional)
    - **url**: URL to scrape data from (optional)
    
    At least one of file or url must be provided.
    """
    if file:
        # Validate file type
        allowed_extensions = ['.csv', '.json', '.xlsx', '.xls', '.txt']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        result = await handle_upload(file)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return JSONResponse(result)
        
    elif url:
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
            
        result = await handle_url_data(url)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return JSONResponse(result)
        
    else:
        raise HTTPException(status_code=400, detail="Either file or URL must be provided")
