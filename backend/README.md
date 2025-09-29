# Data Analyst Agent Backend

A production-ready FastAPI backend for AI-powered data analysis with self-healing capabilities.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
backend/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── src/
│   └── app/            # Main application code
│       ├── routers/    # API endpoints
│       ├── utils/      # Core utilities (LLM, self-healing)
│       └── memory/     # Data persistence
├── data/               # Datasets and database files
├── logs/               # Application logs
└── tests/              # Test scripts
```

## 🔧 Features

- **File Upload**: CSV, Excel, URL scraping
- **Natural Language Queries**: Powered by Google Gemini AI
- **Self-Healing**: Automatic error detection and fixing
- **Data Analysis**: Advanced statistical analysis and visualizations
- **Memory Persistence**: Conversation history and dataset storage

## 📚 API Documentation

- Interactive docs: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## 🛠️ Endpoints

- `POST /api/upload` - Upload datasets
- `POST /api/query` - Process natural language queries  
- `GET /api/self-healing/stats` - Self-healing statistics
- `GET /api/health` - Health check