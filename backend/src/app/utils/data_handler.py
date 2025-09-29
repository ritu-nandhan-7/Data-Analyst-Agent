import os
import io
import pandas as pd
import polars as pl
import duckdb
import requests
from tempfile import NamedTemporaryFile
from fastapi import UploadFile
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

from app.memory import memory_store

load_dotenv()
MAX_PANDAS_MB = 100

# Configure Gemini for web scraping
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name

async def handle_upload(file: UploadFile):
    content = await file.read()
    size_mb = len(content) / 1024 / 1024
    ext = file.filename.split('.')[-1].lower()
    if size_mb > MAX_PANDAS_MB:
        # Use Polars or DuckDB
        if ext in ['csv', 'txt']:
            df = pl.read_csv(io.BytesIO(content))
        elif ext in ['json']:
            df = pl.read_json(io.BytesIO(content))
        elif ext in ['xls', 'xlsx']:
            with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                tmp.write(content)
                tmp.flush()
                df = pl.read_excel(tmp.name)
        else:
            return {"error": "Unsupported file type for large file."}
        memory_store['dataframe'] = df
        memory_store['engine'] = 'polars'
    else:
        # Use Pandas
        if ext in ['csv', 'txt']:
            df = pd.read_csv(io.BytesIO(content))
        elif ext in ['json']:
            df = pd.read_json(io.BytesIO(content))
        elif ext in ['xls', 'xlsx']:
            df = pd.read_excel(io.BytesIO(content))
        else:
            return {"error": "Unsupported file type."}
        memory_store['dataframe'] = df
        memory_store['engine'] = 'pandas'
    memory_store['filename'] = file.filename
    return {"status": "success", "rows": len(df)}

async def handle_url(url: str):
    """Handle URL scraping and data extraction"""
    try:
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # First, check if it's a direct data file (CSV, JSON, etc.)
        content_type = response.headers.get('content-type', '').lower()
        if 'csv' in content_type or url.endswith('.csv'):
            df = pd.read_csv(io.StringIO(response.text))
            memory_store['dataframe'] = df
            memory_store['engine'] = 'pandas'
            memory_store['filename'] = url.split('/')[-1] or 'scraped_data.csv'
            return {"status": "success", "rows": len(df), "type": "direct_csv"}
        
        elif 'json' in content_type or url.endswith('.json'):
            df = pd.read_json(io.StringIO(response.text))
            memory_store['dataframe'] = df
            memory_store['engine'] = 'pandas'
            memory_store['filename'] = url.split('/')[-1] or 'scraped_data.json'
            return {"status": "success", "rows": len(df), "type": "direct_json"}
        
        # For HTML pages, use AI to identify and extract tabular data
        # Look for tables first
        tables = soup.find_all('table')
        if tables:
            # Try to parse the first substantial table
            for table in tables:
                try:
                    df = pd.read_html(str(table))[0]
                    if len(df) > 1 and len(df.columns) > 1:  # Must have some data
                        memory_store['dataframe'] = df
                        memory_store['engine'] = 'pandas'
                        memory_store['filename'] = f"scraped_table_{url.split('/')[-1] or 'data'}.csv"
                        return {"status": "success", "rows": len(df), "type": "html_table"}
                except Exception as e:
                    continue
        
        # If no tables found, use AI to extract structured data
        page_text = soup.get_text()[:5000]  # First 5000 chars
        
        prompt = f"""
        Analyze this webpage content and extract any structured data that could be converted to a tabular format.
        Look for lists, data points, statistics, or any information that could form rows and columns.
        
        URL: {url}
        Content: {page_text}
        
        If you find structured data, return Python code that creates a pandas DataFrame with the extracted data.
        If no structured data is found, return: NO_STRUCTURED_DATA
        
        Only return the Python code or NO_STRUCTURED_DATA, nothing else.
        """
        
        try:
            response = model.generate_content(prompt)
            ai_response = response.text.strip()
            
            if ai_response == "NO_STRUCTURED_DATA":
                return {"error": "No structured data found on the webpage"}
            
            # Execute the AI-generated code
            local_vars = {'pd': pd}
            if "```python" in ai_response:
                code = ai_response.split("```python")[1].split("```")[0].strip()
            else:
                code = ai_response
                
            exec(code, local_vars, local_vars)
            
            if 'df' in local_vars:
                df = local_vars['df']
                memory_store['dataframe'] = df
                memory_store['engine'] = 'pandas'
                memory_store['filename'] = f"ai_extracted_{url.split('/')[-1] or 'data'}.csv"
                return {"status": "success", "rows": len(df), "type": "ai_extracted"}
            else:
                return {"error": "AI could not extract structured data"}
                
        except Exception as e:
            return {"error": f"Failed to process webpage with AI: {str(e)}"}
            
    except requests.RequestException as e:
        return {"error": f"Failed to fetch URL: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error processing URL: {str(e)}"}
