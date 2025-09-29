import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileUpload = async (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;
    
    setFile(selectedFile);
    setIsLoading(true);
    setUploadStatus('Uploading...');
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      if (response.ok) {
        setUploadStatus(`✅ ${result.message || 'File uploaded successfully!'}`);
      } else {
        setUploadStatus(`❌ Upload failed: ${result.detail || 'Unknown error'}`);
      }
    } catch (error) {
      setUploadStatus(`❌ Connection error: ${error.message}`);
      console.error('Upload error:', error);
    }
    setIsLoading(false);
  };

  const handleQuery = async () => {
    if (!question.trim()) return;
    
    setIsLoading(true);
    setResults(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setResults(data);
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
    }
    setIsLoading(false);
  };

  return (
    <div className="app">
      <header>
        <h1>AI Data Analyst Agent</h1>
        <p>Upload your data, ask questions, and get intelligent insights</p>
      </header>
      
      <main>
        <div className="upload-section">
          <h2>Upload Data</h2>
          <input 
            type="file" 
            accept=".csv,.json,.xlsx" 
            onChange={handleFileUpload}
            disabled={isLoading}
          />
          {uploadStatus && <p className="status">{uploadStatus}</p>}
        </div>

        <div className="query-section">
          <h2>Ask a Question</h2>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What would you like to know about the data?"
            rows="4"
            disabled={isLoading}
          />
          <button 
            onClick={handleQuery} 
            disabled={isLoading || !question.trim()}
          >
            {isLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {results && (
          <div className="results-section">
            <h2>📊 Analysis Results</h2>
            {results.error ? (
              <div className="error">
                <strong>Error:</strong> {results.error}
              </div>
            ) : (
              <div className="results-content">
                {results.explanation && (
                  <div className="text-result">
                    <h3 style={{ color: '#00d4ff', marginBottom: '15px' }}>🔍 Analysis:</h3>
                    <pre>{results.explanation}</pre>
                  </div>
                )}
                {results.result && (
                  <div className="text-result">
                    <h3 style={{ color: '#00d4ff', marginBottom: '15px' }}>📊 Result:</h3>
                    <pre>{JSON.stringify(results.result, null, 2)}</pre>
                  </div>
                )}
                {results.image && (
                  <div className="image-result">
                    <h3 style={{ color: '#00d4ff', marginBottom: '15px' }}>📈 Visualization:</h3>
                    <img 
                      src={`data:image/png;base64,${results.image}`} 
                      alt="Analysis visualization"
                      style={{ maxWidth: '100%', height: 'auto' }}
                      onClick={() => {
                        const img = new Image();
                        img.src = `data:image/png;base64,${results.image}`;
                        const w = window.open('', '_blank');
                        w.document.write(`<img src="${img.src}" style="max-width: 100%; height: auto;">`);
                      }}
                      title="Click to open in new window"
                    />
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
