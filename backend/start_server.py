"""
Data Analyst Agent Backend - Simple Launcher
Launches the FastAPI server using uvicorn
"""
import sys
import os
import uvicorn

if __name__ == "__main__":
    # Get the current directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(backend_dir, 'src')
    
    # Add src to Python path
    sys.path.insert(0, src_dir)
    
    print("🚀 Starting Data Analyst Agent Backend Server...")
    print(f"📁 Backend directory: {backend_dir}")
    print(f"📁 Source directory: {src_dir}")
    print("🌐 Server will be available at: http://127.0.0.1:8000")
    print("📖 API Documentation: http://127.0.0.1:8000/docs")
    
    # Start the FastAPI server
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[src_dir]
    )