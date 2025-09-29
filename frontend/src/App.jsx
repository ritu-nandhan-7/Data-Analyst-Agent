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
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        setUploadStatus('File uploaded successfully!');
      } else {
        setUploadStatus('Upload failed');
      }
    } catch (error) {
      setUploadStatus('Upload error: ' + error.message);
    }
    setIsLoading(false);
  };

  const handleQuery = async () => {
    if (!question.trim()) return;
    
    setIsLoading(true);
    setResults(null);
    
    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: question }),
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      setResults({ error: 'Query failed: ' + error.message });
    }
    setIsLoading(false);
  };

  return (
    <div className="app">
      <header>
        <h1>Data Analyst Agent</h1>
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
            <h2>Results</h2>
            {results.error ? (
              <div className="error">{results.error}</div>
            ) : (
              <div className="results-content">
                {results.response && (
                  <div className="text-result">
                    <pre>{results.response}</pre>
                  </div>
                )}
                {results.image && (
                  <div className="image-result">
                    <img 
                      src={`data:image/png;base64,${results.image}`} 
                      alt="Analysis visualization"
                      style={{ maxWidth: '100%', height: 'auto' }}
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