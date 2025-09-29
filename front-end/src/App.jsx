import React, { useState } from 'react';
import './App.css';

function App() {
  // Data input states
  const [file, setFile] = useState(null);
  const [rawData, setRawData] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [dataInputMethod, setDataInputMethod] = useState('file'); // 'file', 'raw', 'url'
  
  // Question input states
  const [question, setQuestion] = useState('');
  const [questionFile, setQuestionFile] = useState(null);
  const [questionInputMethod, setQuestionInputMethod] = useState('text'); // 'text', 'file', 'suggested'
  
  // Results and UI states
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [analysisHistory, setAnalysisHistory] = useState([]);
  
  // New UX enhancement states
  const [dataPreview, setDataPreview] = useState(null);
  const [processingStep, setProcessingStep] = useState('');
  const [progressPercent, setProgressPercent] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // Suggested questions
  const suggestedQuestions = [
    "What are the key statistics and summary of this dataset?",
    "Show me the distribution of numerical columns with visualizations",
    "Are there any missing values or data quality issues?",
    "What correlations exist between different variables?",
    "Can you identify any outliers or anomalies in the data?",
    "What are the most interesting patterns or trends?",
    "Generate a comprehensive data analysis report",
    "Create visualizations for the most important insights"
  ];

  const handleDataUpload = async () => {
    setIsLoading(true);
    setIsUploading(true);
    setProgressPercent(0);
    setProcessingStep('Preparing data...');
    setUploadStatus('Processing...');
    
    const formData = new FormData();
    
    try {
      if (dataInputMethod === 'file' && file) {
        formData.append('file', file);
      } else if (dataInputMethod === 'raw' && rawData.trim()) {
        // Create a blob from raw data and append as file
        const blob = new Blob([rawData], { type: 'text/plain' });
        const fileName = rawData.includes(',') ? 'data.csv' : 'data.json';
        formData.append('file', blob, fileName);
      } else if (dataInputMethod === 'url' && websiteUrl.trim()) {
        setProcessingStep('Fetching website data...');
        setProgressPercent(25);
        // Send URL to backend for processing using FormData
        formData.append('url', websiteUrl);
        // We'll use the same upload endpoint but with URL data
      } else {
        setUploadStatus('❌ Please provide data input');
        setIsLoading(false);
        setIsUploading(false);
        return;
      }
      
      setProcessingStep('Uploading to server...');
      setProgressPercent(50);
      
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });
      
      setProcessingStep('Processing data...');
      setProgressPercent(75);
      
      const result = await response.json();
      
      if (response.ok) {
        setProcessingStep('Generating preview...');
        setProgressPercent(100);
        
        // Set data preview information
        setDataPreview({
          filename: result.filename || 'Unknown',
          rows: result.rows || 0,
          columns: result.columns || 0,
          type: result.type || 'file',
          size: result.size || 'Unknown',
          preview: result.preview || null
        });
        
        setUploadStatus(`✅ ${result.message || 'Data uploaded successfully!'} - ${result.rows || 0} rows loaded`);
      } else {
        setUploadStatus(`❌ Upload failed: ${result.detail || 'Unknown error'}`);
        setDataPreview(null);
      }
    } catch (error) {
      setUploadStatus(`❌ Connection error: ${error.message}`);
      setDataPreview(null);
      console.error('Upload error:', error);
    } finally {
      setIsLoading(false);
      setIsUploading(false);
      setProgressPercent(0);
      setProcessingStep('');
    }
  };

  const handleFileUpload = async (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;
    setFile(selectedFile);
  };

  const handleQuery = async () => {
    setIsAnalyzing(true);
    setProgressPercent(0);
    setProcessingStep('Preparing analysis...');
    
    let questionText = '';
    
    // Determine question based on input method
    if (questionInputMethod === 'text') {
      questionText = question.trim();
    } else if (questionInputMethod === 'file' && questionFile) {
      try {
        questionText = await questionFile.text();
      } catch (error) {
        setResults({ error: 'Failed to read question file' });
        return;
      }
    } else if (questionInputMethod === 'suggested') {
      questionText = question.trim();
    }
    
    if (!questionText) {
      setResults({ error: 'Please provide a question' });
      return;
    }
    
    setIsLoading(true);
    setResults(null);
    setProgressPercent(20);
    setProcessingStep('Sending query to AI...');
    
    try {
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: questionText }),
      });
      
      setProgressPercent(60);
      setProcessingStep('Processing analysis...');
      
      const data = await response.json();
      
      setProgressPercent(90);
      setProcessingStep('Finalizing results...');
      
      if (response.ok) {
        setResults(data);
        // Add to history
        setAnalysisHistory(prev => [{
          id: Date.now(),
          question: questionText,
          result: data,
          timestamp: new Date().toLocaleString()
        }, ...prev.slice(0, 9)]); // Keep last 10 analyses
      } else {
        setResults({ 
          error: `Query failed: ${data.detail || 'Unknown error'}` 
        });
      }
    } catch (error) {
      setResults({ 
        error: `Connection error: ${error.message}. Make sure the backend server is running on http://localhost:8000` 
      });
      console.error('Query error:', error);
    } finally {
      setIsLoading(false);
      setIsAnalyzing(false);
      setProgressPercent(0);
      setProcessingStep('');
    }
  };

  return (
    <div className="app">
      <header>
        <h1>🤖 <span>AI Data Analyst Agent</span></h1>
        <p>Upload your data, ask questions, and get intelligent insights with visualizations</p>
      </header>
      
      <main>
        {/* Data Upload Section */}
        <section className="upload-section">
          <h2>📁 Data Input</h2>
          <div className="input-method-selector">
            <label className={dataInputMethod === 'file' ? 'active' : ''}>
              <input 
                type="radio" 
                name="dataMethod" 
                value="file"
                checked={dataInputMethod === 'file'}
                onChange={(e) => setDataInputMethod(e.target.value)}
              />
              📄 File Upload
            </label>
            <label className={dataInputMethod === 'raw' ? 'active' : ''}>
              <input 
                type="radio" 
                name="dataMethod" 
                value="raw"
                checked={dataInputMethod === 'raw'}
                onChange={(e) => setDataInputMethod(e.target.value)}
              />
              📝 Raw Data
            </label>
            <label className={dataInputMethod === 'url' ? 'active' : ''}>
              <input 
                type="radio" 
                name="dataMethod" 
                value="url"
                checked={dataInputMethod === 'url'}
                onChange={(e) => setDataInputMethod(e.target.value)}
              />
              🌐 Website URL
            </label>
          </div>

          <div className="input-content">
            {dataInputMethod === 'file' && (
              <div className="file-input">
                <input 
                  type="file" 
                  accept=".csv,.json,.xlsx,.xls,.txt" 
                  onChange={handleFileUpload}
                  disabled={isLoading}
                />
                {file && <p className="file-info">Selected: {file.name}</p>}
              </div>
            )}

            {dataInputMethod === 'raw' && (
              <div className="raw-input">
                <textarea
                  value={rawData}
                  onChange={(e) => setRawData(e.target.value)}
                  placeholder="Paste your CSV data, JSON data, or any structured text here..."
                  rows="8"
                  disabled={isLoading}
                />
                <small>Supports CSV, JSON, or any structured text format</small>
              </div>
            )}

            {dataInputMethod === 'url' && (
              <div className="url-input">
                <input
                  type="url"
                  value={websiteUrl}
                  onChange={(e) => setWebsiteUrl(e.target.value)}
                  placeholder="https://example.com/data.csv or any webpage with data"
                  disabled={isLoading}
                />
                <small>Enter a URL to a data file or webpage with data tables</small>
              </div>
            )}

            <button 
              onClick={handleDataUpload} 
              disabled={isLoading || (
                (dataInputMethod === 'file' && !file) ||
                (dataInputMethod === 'raw' && !rawData.trim()) ||
                (dataInputMethod === 'url' && !websiteUrl.trim())
              )}
              className="upload-button"
            >
              {isLoading ? '⏳ Processing...' : '📤 Process Data'}
            </button>
          </div>

          {uploadStatus && <div className={`status ${uploadStatus.includes('✅') ? 'success' : 'error'}`}>{uploadStatus}</div>}
          
          {/* Progress Indicator */}
          {(isUploading || isAnalyzing) && (
            <div className="progress-section">
              <div className="progress-info">
                <span className="processing-step">{processingStep}</span>
                <span className="progress-percent">{progressPercent}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${progressPercent}%` }}
                ></div>
              </div>
              <div className="loading-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
        </section>

        {/* Data Preview Section */}
        {dataPreview && (
          <section className="data-preview-section">
            <h2>📊 Data Preview</h2>
            <div className="preview-content">
              <div className="preview-stats">
                <div className="stat-item">
                  <span className="stat-label">📄 File:</span>
                  <span className="stat-value">{dataPreview.filename}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">📏 Rows:</span>
                  <span className="stat-value">{dataPreview.rows.toLocaleString()}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">📋 Columns:</span>
                  <span className="stat-value">{dataPreview.columns}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">📂 Type:</span>
                  <span className="stat-value">{dataPreview.type}</span>
                </div>
              </div>
              {dataPreview.preview && (
                <div className="data-sample">
                  <h4>Sample Data:</h4>
                  <div className="sample-table">
                    <pre>{JSON.stringify(dataPreview.preview, null, 2)}</pre>
                  </div>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Question Input Section */}
        <section className="query-section">
          <h2>❓ Ask Questions</h2>
          <div className="input-method-selector">
            <label className={questionInputMethod === 'text' ? 'active' : ''}>
              <input 
                type="radio" 
                name="questionMethod" 
                value="text"
                checked={questionInputMethod === 'text'}
                onChange={(e) => setQuestionInputMethod(e.target.value)}
              />
              ✏️ Type Question
            </label>
            <label className={questionInputMethod === 'file' ? 'active' : ''}>
              <input 
                type="radio" 
                name="questionMethod" 
                value="file"
                checked={questionInputMethod === 'file'}
                onChange={(e) => setQuestionInputMethod(e.target.value)}
              />
              📄 Upload Questions
            </label>
            <label className={questionInputMethod === 'suggested' ? 'active' : ''}>
              <input 
                type="radio" 
                name="questionMethod" 
                value="suggested"
                checked={questionInputMethod === 'suggested'}
                onChange={(e) => setQuestionInputMethod(e.target.value)}
              />
              💡 Suggested Questions
            </label>
          </div>

          <div className="input-content">
            {questionInputMethod === 'text' && (
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="What would you like to know about the data? Be specific for better insights..."
                rows="4"
                disabled={isLoading}
              />
            )}

            {questionInputMethod === 'file' && (
              <div className="file-input">
                <input 
                  type="file" 
                  accept=".txt,.md,.doc,.docx" 
                  onChange={(e) => setQuestionFile(e.target.files[0])}
                  disabled={isLoading}
                />
                {questionFile && <p className="file-info">Selected: {questionFile.name}</p>}
                <small>Upload a text file containing your questions</small>
              </div>
            )}

            {questionInputMethod === 'suggested' && (
              <div className="suggested-questions">
                <div className="questions-grid">
                  {suggestedQuestions.map((q, idx) => (
                    <button 
                      key={idx}
                      onClick={() => setQuestion(q)}
                      className={`suggestion-button ${question === q ? 'selected' : ''}`}
                      disabled={isLoading}
                    >
                      {q}
                    </button>
                  ))}
                </div>
                {question && (
                  <div className="selected-question">
                    <strong>Selected Question:</strong>
                    <p>{question}</p>
                  </div>
                )}
              </div>
            )}

            <button 
              onClick={handleQuery} 
              disabled={isLoading || (
                (questionInputMethod === 'text' && !question.trim()) ||
                (questionInputMethod === 'file' && !questionFile) ||
                (questionInputMethod === 'suggested' && !question.trim())
              )}
              className="analyze-button"
            >
              {isAnalyzing ? (
                <>
                  <span className="loading-spinner"></span>
                  🤖 AI Analyzing...
                </>
              ) : '🔍 Analyze Data'}
            </button>
          </div>
        </section>

        {/* Results Section */}
        {results && (
          <section className="results-section">
            <h2>📊 Analysis Results</h2>
            {results.error ? (
              <div className="error">
                <strong>❌ Error:</strong> {results.error}
              </div>
            ) : (
              <div className="results-content">
                {results.explanation && (
                  <div className="text-result">
                    <h3>🔍 Analysis Explanation:</h3>
                    <div className="explanation-content">
                      <pre>{results.explanation}</pre>
                    </div>
                  </div>
                )}
                
                {results.result && (
                  <div className="text-result">
                    <h3>📊 Detailed Results:</h3>
                    <div className="result-content">
                      <pre>{typeof results.result === 'string' ? results.result : JSON.stringify(results.result, null, 2)}</pre>
                    </div>
                  </div>
                )}
                
                {results.image && (
                  <div className="image-result">
                    <h3>📈 Data Visualization:</h3>
                    <div className="image-container">
                      <img 
                        src={`data:image/png;base64,${results.image}`} 
                        alt="Analysis visualization"
                        onClick={() => {
                          const w = window.open('', '_blank');
                          w.document.write(`
                            <html>
                              <head><title>Data Visualization</title></head>
                              <body style="margin:0;padding:20px;background:#000;">
                                <img src="data:image/png;base64,${results.image}" style="max-width:100%;height:auto;display:block;margin:0 auto;" />
                              </body>
                            </html>
                          `);
                        }}
                        title="Click to open in full screen"
                      />
                      <div className="image-actions">
                        <button 
                          onClick={() => {
                            const link = document.createElement('a');
                            link.href = `data:image/png;base64,${results.image}`;
                            link.download = `analysis-chart-${Date.now()}.png`;
                            link.click();
                          }}
                          className="download-button"
                        >
                          📥 Download Chart
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                <div className="result-actions">
                  <button 
                    onClick={() => {
                      const content = {
                        question: results.question || question,
                        explanation: results.explanation,
                        result: results.result,
                        timestamp: new Date().toLocaleString()
                      };
                      const blob = new Blob([JSON.stringify(content, null, 2)], { type: 'application/json' });
                      const link = document.createElement('a');
                      link.href = URL.createObjectURL(blob);
                      link.download = `analysis-results-${Date.now()}.json`;
                      link.click();
                    }}
                    className="export-button"
                  >
                    📄 Export Results
                  </button>
                </div>
              </div>
            )}
          </section>
        )}

        {/* Analysis History */}
        {analysisHistory.length > 0 && (
          <section className="history-section">
            <h2>📈 Analysis History</h2>
            <div className="history-list">
              {analysisHistory.map((item) => (
                <div key={item.id} className="history-item">
                  <div className="history-header">
                    <span className="timestamp">{item.timestamp}</span>
                    <button 
                      onClick={() => {
                        setQuestion(item.question);
                        setResults(item.result);
                      }}
                      className="reload-button"
                    >
                      🔄 Load
                    </button>
                  </div>
                  <div className="history-question">
                    <strong>Q:</strong> {item.question.length > 100 ? item.question.substring(0, 100) + '...' : item.question}
                  </div>
                  {item.result.image && (
                    <div className="history-preview">
                      <img 
                        src={`data:image/png;base64,${item.result.image}`}
                        alt="Chart preview"
                        onClick={() => setResults(item.result)}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
