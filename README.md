# InsightEngine 🔧📊

An AI-powered data analysis engine that allows you to upload datasets and ask natural language questions to get insights, visualizations, and analysis results.

## 🚀 Features

- **Smart Data Ingestion**: Upload CSV, JSON, Excel files or scrape data from URLs
- **Natural Language Queries**: Ask questions in plain English about your data
- **AI-Powered Analysis**: Uses Google Gemini to generate Python code for analysis
- **Automatic Visualizations**: Creates charts and graphs when appropriate
- **Conversation Memory**: Maintains chat history for follow-up questions
- **Large Dataset Support**: Automatically switches to Polars/DuckDB for files >100MB
- **Error Recovery**: Intelligent retry mechanism with error correction
- **Web Scraping**: Extract structured data from websites automatically

## 📋 Prerequisites

- Python 3.10+
- Google Gemini API Key (get from [Google AI Studio](https://makersuite.google.com/))

## 🛠️ Installation

1. **Clone/Download the project**
   ```bash
   git clone <your-repo-url>
   cd Data\ Analyst\ Agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows
   # source .venv/bin/activate    # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Start the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🌐 API Usage

### Base URL
```
http://localhost:8000
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 📤 Upload Dataset

**Endpoint**: `POST /upload`

**Option 1: Upload File**
```bash
curl -X POST "http://localhost:8000/upload" \
     -F "file=@your_dataset.csv"
```

**Option 2: Scrape from URL**
```bash
curl -X POST "http://localhost:8000/upload" \
     -F "url=https://example.com/data.csv"
```

**Response**:
```json
{
  "status": "success",
  "rows": 1000,
  "type": "csv"
}
```

### 💬 Query Your Data

**Endpoint**: `POST /query`

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What are the top 5 categories by sales?",
       "context": {},
       "session_id": "my_session"
     }'
```

**Response**:
```json
{
  "result": {
    "Category A": 15000,
    "Category B": 12000,
    "Category C": 9500
  },
  "explanation": "Based on the sales data, here are the top 5 categories...",
  "image": "base64_encoded_chart_image",
  "code_executed": "result = dataframe.groupby('category').sum()...",
  "attempt": 1
}
```

### 📊 Example Queries

```json
{
  "question": "Show me a histogram of prices"
}

{
  "question": "What's the correlation between age and income?"
}

{
  "question": "Create a scatter plot of sales vs marketing spend"
}

{
  "question": "Find all customers from California with orders > $1000"
}

{
  "question": "What's the average monthly revenue trend?"
}
```

### 🔍 Check System Status

**Endpoint**: `GET /status`

```bash
curl http://localhost:8000/status
```

**Response**:
```json
{
  "dataset_loaded": true,
  "dataset_info": {
    "filename": "sales_data.csv",
    "engine": "pandas",
    "shape": [1000, 15],
    "columns": ["date", "product", "sales", "region"]
  },
  "memory_usage": 3
}
```

### 📜 Get Conversation History

**Endpoint**: `GET /history/{session_id}`

```bash
curl http://localhost:8000/history/my_session
```

### 🔄 Reset Memory

**Endpoint**: `DELETE /reset`

```bash
curl -X DELETE http://localhost:8000/reset
```

## 🏗️ Architecture

```
app/
├── main.py              # FastAPI application
├── routers/
│   ├── upload.py        # File upload & URL scraping
│   └── query.py         # Natural language queries
├── utils/
│   ├── data_handler.py  # Data processing & loading
│   └── llm_agent.py     # AI query processing
└── memory/
    └── __init__.py      # In-memory storage & SQLite
```

## 🧠 How It Works

1. **Data Upload**: Files are processed and stored in memory using Pandas (small files) or Polars (large files)

2. **Query Processing**: 
   - User question is sent to Gemini AI
   - AI generates Python code for analysis
   - Code is executed in a secure environment
   - Results are returned with explanations

3. **Error Recovery**: If code fails, the error is sent back to AI to generate a corrected version (up to 3 attempts)

4. **Visualization**: Charts are automatically created and returned as base64-encoded images

## 🔧 Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

### Scaling Thresholds

- Files >100MB automatically use Polars/DuckDB instead of Pandas
- Modify `MAX_PANDAS_MB` in `data_handler.py` to adjust threshold

## 🚨 Error Handling

The API includes comprehensive error handling:

- **Upload Errors**: Invalid file types, processing failures
- **Query Errors**: Missing dataset, AI failures, code execution errors
- **Retry Logic**: Automatic code correction up to 3 attempts
- **Detailed Responses**: Clear error messages and troubleshooting info

## 🔒 Security Notes

- Code execution is sandboxed with limited scope
- File uploads are validated for type and size
- URLs are validated before scraping
- No persistent file storage (data stays in memory)

## 🛣️ Roadmap

- [ ] Add authentication and user management
- [ ] Implement data persistence options
- [ ] Add more visualization libraries
- [ ] Support for real-time data streams
- [ ] Export results to various formats
- [ ] Advanced statistical analysis features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Troubleshooting

### Common Issues

**"No dataset loaded" error**
- Make sure to upload a dataset first using `/upload`

**Gemini API errors**
- Check your API key in `.env` file
- Verify API key has proper permissions

**Large file processing slow**
- Files >100MB use Polars - this is expected
- Consider data preprocessing for very large datasets

**Visualization not appearing**
- Check that matplotlib backend is set correctly
- Ensure sufficient memory for image generation

### Getting Help

- Check the interactive docs at http://localhost:8000/docs
- Review error messages in API responses
- Check server logs in terminal

---

**Happy analyzing! 🎉📈**
- In-memory/SQLite query memory
- Agentic loop for code correction
- Scalable data handling (Pandas/Polars/DuckDB)
- Visualization (Matplotlib/Seaborn/Plotly)

## Setup
1. Python 3.10+
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Gemini API key to a `.env` file
4. Run: `uvicorn app.main:app --reload`

---

See code for API usage details.