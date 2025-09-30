# 🔧 InsightEngine - AI-Powered Data Analysis Platform

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18+-blue.svg)](https://reactjs.org/)

A professional-grade, full-stack AI data analysis platform that transforms raw data into actionable insights through natural language queries. Built with React frontend and FastAPI backend, featuring intelligent server status management and seamless deployment on Render.

## ✨ Key Features

### 🎯 **Smart Data Analysis**
- **Natural Language Queries**: Ask questions in plain English about your data
- **AI-Powered Code Generation**: Uses Google Gemini to generate and execute Python analysis code
- **Automatic Visualizations**: Creates charts, graphs, and plots automatically when appropriate
- **Multi-Format Support**: CSV, JSON, Excel files, and URL data scraping

### 🚀 **Professional Frontend**
- **Modern React Interface**: Built with Vite for optimal performance
- **Intelligent Server Status**: Real-time backend status with loading animations
  - 🔍 "Checking Server..." (blue spinning indicator)
  - ⚡ "Starting Server..." (orange progress indicator)
  - ⏳ "Server Almost Ready..." (golden transition state)
  - ● "Server Online" (green success indicator)
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Interactive Help System**: Built-in tutorials and examples

### 🔧 **Robust Backend**
- **FastAPI Framework**: High-performance async API with automatic documentation
- **Self-Healing System**: Intelligent error recovery and code correction (up to 3 attempts)
- **Scalable Data Processing**: Automatic engine selection based on dataset size
  - Pandas for small datasets (<100MB)
  - Polars/DuckDB for large datasets (>100MB)
- **Memory Management**: Persistent conversation history with SQLite storage

### 🌐 **Production Ready**
- **Render Deployment**: Seamless cloud deployment with automatic HTTPS
- **Environment Management**: Secure API key handling and configuration
- **Health Monitoring**: Comprehensive system status and diagnostics
- **Error Handling**: Graceful error management with detailed user feedback

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/))

## 🏗️ Architecture Overview

```
InsightEngine/
├── 🎨 Frontend (React + Vite)
│   ├── Smart server status management
│   ├── Interactive data analysis interface
│   ├── Real-time progress tracking
│   └── Responsive mobile-first design
│
├── ⚡ Backend (FastAPI + Python)
│   ├── RESTful API with async processing
│   ├── AI-powered query processing
│   ├── Scalable data engine selection
│   └── Persistent memory management
│
└── 🚀 Infrastructure
    ├── Render deployment configuration
    ├── Environment-based configuration
    └── Health monitoring system
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/ritu-nandhan-7/Data-Analyst-Agent.git
   cd Data-Analyst-Agent
   ```

2. **Setup Backend**
   ```bash
   # Create virtual environment
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows
   # source .venv/bin/activate    # Linux/Mac

   # Install dependencies
   cd backend
   pip install -r requirements.txt

   # Create environment file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

3. **Setup Frontend**
   ```bash
   cd ../front-end
   npm install
   
   # Create environment file
   echo "VITE_API_URL=http://localhost:8000" > .env.local
   ```

4. **Start Development Servers**
   
   **Option A: Use provided batch files (Windows)**
   ```bash
   # Terminal 1: Start backend
   start-backend.bat
   
   # Terminal 2: Start frontend
   start-frontend.bat
   ```
   
   **Option B: Manual start**
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2: Frontend
   cd front-end
   npm run dev
   ```

5. **Access the Application**
   - **Frontend**: http://localhost:5173
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

## 🌐 Production Deployment

### Deploy to Render (Recommended)

1. **Fork this repository** to your GitHub account

2. **Create Render services**:
   - **Backend**: Create a new Web Service
     - Connect your GitHub repository
     - Set build command: `pip install -r requirements.txt`
     - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - Add environment variable: `GEMINI_API_KEY`
   
   - **Frontend**: Create a new Static Site
     - Connect your GitHub repository
     - Set build command: `npm install && npm run build`
     - Set publish directory: `dist`
     - Add environment variable: `VITE_API_URL` (your backend URL)

3. **The deployment is fully automated** using the included `render.yaml` configuration

### Environment Variables

**Backend (.env)**
```env
GEMINI_API_KEY=your_google_gemini_api_key
```

**Frontend (.env.local)**
```env
VITE_API_URL=https://your-backend-url.onrender.com
```

## 📊 Usage Examples

### Basic Data Analysis
1. **Upload your dataset** (CSV, JSON, Excel, or URL)
2. **Ask natural language questions**:
   - "What are the top 5 products by sales?"
   - "Show me a scatter plot of price vs quantity"
   - "What's the correlation between age and income?"
   - "Create a histogram of customer ratings"

### Advanced Analytics
- **Statistical Analysis**: "Perform a regression analysis on sales data"
- **Time Series**: "Show monthly revenue trends for the last year"
- **Segmentation**: "Group customers by spending behavior"
- **Comparisons**: "Compare performance across different regions"

## 🔧 API Reference

### Core Endpoints

#### Upload Data
```http
POST /api/upload
Content-Type: multipart/form-data

# File upload
file: your_dataset.csv

# OR URL scraping
url: https://example.com/data.csv
```

#### Query Data
```http
POST /api/query
Content-Type: application/json

{
  "question": "What are the top 5 categories by sales?",
  "context": {},
  "session_id": "unique_session_id"
}
```

#### System Health
```http
GET /api/health

Response: { "status": "healthy", "timestamp": "2025-09-30T..." }
```

#### Get Dataset Status
```http
GET /api/status

Response: {
  "dataset_loaded": true,
  "dataset_info": {
    "filename": "sales_data.csv",
    "engine": "pandas",
    "shape": [1000, 15],
    "columns": ["date", "product", "sales", "region"]
  }
}
```

## 🧠 How It Works

### 1. **Intelligent Data Processing**
- Automatic file type detection and parsing
- Dynamic engine selection based on dataset size
- Memory-efficient processing for large datasets

### 2. **AI-Powered Analysis**
- Natural language understanding via Google Gemini
- Context-aware Python code generation
- Automatic visualization creation when appropriate

### 3. **Error Recovery System**
- Failed code execution triggers automatic correction
- Up to 3 retry attempts with improved code
- Detailed error reporting and user feedback

### 4. **Smart Frontend Management**
- Real-time server status monitoring
- Graceful handling of cold starts (Render free tier)
- Progressive loading states with visual feedback

## 🎨 Frontend Features

### Server Status Management
The frontend includes a sophisticated server status system:

- **🔍 Checking Server**: Initial health check phase
- **⚡ Starting Server**: Progress-based startup indication (0-100%)
- **⏳ Almost Ready**: Transition state after startup completion
- **● Server Online**: Fully operational status

### User Experience
- **Responsive Design**: Mobile-first approach with desktop optimization
- **Interactive Help**: Comprehensive tutorials and examples
- **Real-time Feedback**: Live progress tracking and status updates
- **Professional Styling**: Modern UI with smooth animations

## 🔒 Security & Performance

### Security Features
- **Sandboxed Code Execution**: Limited scope for AI-generated code
- **Input Validation**: Comprehensive file and URL validation
- **Environment Isolation**: Secure API key management
- **Memory Safety**: Automatic cleanup and memory management

### Performance Optimization
- **Lazy Loading**: Components loaded on demand
- **Caching**: Intelligent data and result caching
- **Async Processing**: Non-blocking operations throughout
- **Resource Management**: Automatic cleanup of large datasets

## 🛠️ Development

### Project Structure
```
Data-Analyst-Agent/
├── backend/                 # FastAPI backend
│   ├── src/app/            # Application modules
│   │   ├── routers/        # API endpoints
│   │   ├── utils/          # Utility functions
│   │   └── memory/         # Data persistence
│   ├── data/               # Sample datasets
│   ├── logs/               # Application logs
│   ├── tests/              # Test suites
│   └── main.py             # Application entry point
│
├── front-end/              # React frontend
│   ├── src/                # Source code
│   │   ├── components/     # React components
│   │   └── assets/         # Static assets
│   ├── public/             # Public assets
│   └── package.json        # Dependencies
│
├── render.yaml             # Render deployment config
└── README.md               # This file
```

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd front-end
npm test
```

### Code Style
- **Backend**: Black formatter, isort imports
- **Frontend**: ESLint + Prettier configuration
- **Git Hooks**: Pre-commit formatting and linting

## � Advanced Configuration

### Scaling Thresholds
Modify data processing behavior in `backend/src/app/utils/data_handler.py`:
```python
MAX_PANDAS_MB = 100  # Switch to Polars for files >100MB
MAX_MEMORY_ROWS = 1000000  # Memory usage threshold
```

### Custom AI Prompts
Enhance AI behavior in `backend/src/app/utils/llm_agent.py`:
```python
SYSTEM_PROMPT = """Your custom analysis instructions..."""
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with proper tests
4. **Follow code style guidelines**
5. **Submit a pull request**

### Development Guidelines
- Write comprehensive tests for new features
- Follow existing code style and patterns
- Update documentation for API changes
- Ensure responsive design for frontend changes

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🆘 Support & Troubleshooting

### Common Issues

**Server Status Stuck on "Starting"**
- Check your Gemini API key in environment variables
- Verify backend is running on the correct port
- Check network connectivity and firewall settings

**"No dataset loaded" Error**
- Upload a dataset first using the upload interface
- Verify file format is supported (CSV, JSON, Excel)
- Check file size limits (adjust as needed)

**Slow Performance on Large Datasets**
- Files >100MB automatically use optimized engines
- Consider data preprocessing for very large datasets
- Monitor memory usage in system status

**Frontend Not Connecting to Backend**
- Verify `VITE_API_URL` environment variable
- Check CORS settings in backend configuration
- Ensure both services are running

### Getting Help
- 📖 Check the [API Documentation](http://localhost:8000/docs)
- 🔍 Review error messages in browser console
- 📊 Monitor server logs for backend issues
- 💬 Open an issue on GitHub for bugs or feature requests

## 🌟 Acknowledgments

- **Google Gemini AI** for powerful natural language processing
- **React & Vite** for modern frontend development
- **FastAPI** for high-performance backend framework
- **Render** for seamless cloud deployment
- **Open Source Community** for amazing libraries and tools

---

**Built with ❤️ for data enthusiasts and analysts worldwide**

*Transform your data into insights with the power of AI* 🚀📊✨