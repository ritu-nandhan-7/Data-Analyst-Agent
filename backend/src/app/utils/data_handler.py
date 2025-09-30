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
import re
from urllib.parse import urlparse
import numpy as np

from app.memory import memory_store

load_dotenv()
MAX_PANDAS_MB = 100

# Configure Gemini for web scraping
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name

def make_json_serializable(obj):
    """Convert pandas/numpy objects to JSON serializable format"""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    elif hasattr(obj, 'dtype'):  # pandas/numpy objects with dtype
        if pd.isna(obj):
            return None
        elif hasattr(obj, 'item'):  # numpy scalars
            return obj.item()
        else:
            return str(obj)
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    elif hasattr(obj, 'name'):  # pandas dtype objects
        return str(obj)
    else:
        return obj

def create_safe_preview_data(df):
    """Create JSON-safe preview data from DataFrame"""
    try:
        # Convert data types to string representation
        dtypes_dict = {}
        for col, dtype in df.dtypes.items():
            dtypes_dict[col] = str(dtype)
        
        # Convert null counts safely
        null_counts = {}
        for col, count in df.isnull().sum().items():
            null_counts[col] = int(count) if pd.notna(count) else 0
        
        # Convert sample data safely
        sample_data = []
        for _, row in df.head(5).iterrows():
            row_dict = {}
            for col, val in row.items():
                if pd.isna(val):
                    row_dict[col] = None
                elif hasattr(val, 'item'):  # numpy scalars
                    row_dict[col] = val.item()
                elif isinstance(val, (np.integer, np.floating)):
                    row_dict[col] = val.item()
                else:
                    row_dict[col] = str(val) if not isinstance(val, (int, float, str, bool, type(None))) else val
            sample_data.append(row_dict)
        
        return {
            "sample_data": sample_data,
            "columns": list(df.columns),
            "data_types": dtypes_dict,
            "shape": list(df.shape),
            "size_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            "null_counts": null_counts
        }
    except Exception as e:
        # Fallback to basic info if detailed preview fails
        return {
            "sample_data": [],
            "columns": list(df.columns),
            "data_types": {},
            "shape": list(df.shape),
            "size_mb": 0,
            "null_counts": {}
        }

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
    
    # Generate preview data
    preview_data = None
    try:
        if hasattr(df, 'head'):  # pandas
            preview_data = make_json_serializable(df.head(3).to_dict('records'))
        else:  # polars
            preview_data = df.head(3).to_dicts()
    except:
        preview_data = None
    
    return {
        "status": "success", 
        "rows": len(df),
        "columns": len(df.columns),
        "filename": file.filename,
        "size": f"{len(content) / 1024:.1f} KB",
        "type": "file_upload",
        "preview": preview_data,
        "message": f"Successfully loaded {len(df)} rows and {len(df.columns)} columns"
    }

async def handle_url_data(url: str):
    """Enhanced URL data handler with Wikipedia specialization"""
    try:
        # Check if it's a Wikipedia URL
        if is_wikipedia_url(url):
            return await handle_wikipedia_url(url)
        else:
            return await handle_generic_url(url)
    except Exception as e:
        return {"error": f"Failed to process URL: {str(e)}"}

def is_wikipedia_url(url: str) -> bool:
    """Check if URL is a Wikipedia page"""
    parsed = urlparse(url.lower())
    return 'wikipedia.org' in parsed.netloc

async def handle_wikipedia_url(url: str):
    """Specialized Wikipedia data extraction"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract page title for context
        page_title = soup.find('h1', {'class': 'firstHeading'})
        title_text = page_title.get_text() if page_title else "Unknown"
        
        # Find all tables in the Wikipedia page
        tables = soup.find_all('table', {'class': ['wikitable', 'infobox', 'navbox']})
        
        if tables:
            # Process Wikipedia tables with enhanced logic
            for i, table in enumerate(tables):
                try:
                    # Skip navigation and infobox tables that are too small
                    rows = table.find_all('tr')
                    if len(rows) < 2:  # Need header + at least one data row
                        continue
                    
                    # Try to parse the table
                    df_list = pd.read_html(str(table))
                    if df_list:
                        df = df_list[0]
                        
                        # Clean the DataFrame
                        df = clean_wikipedia_dataframe(df)
                        
                        if len(df) > 1 and len(df.columns) > 1:  # Valid table
                            # Use AI to generate web scraping code for this specific Wikipedia page
                            scraping_code = await generate_wikipedia_scraping_code(url, title_text, df.head(3))
                            
                            memory_store['dataframe'] = df
                            memory_store['engine'] = 'pandas'
                            memory_store['filename'] = f"wikipedia_{title_text.replace(' ', '_')}_table_{i+1}.csv"
                            memory_store['scraping_code'] = scraping_code
                            memory_store['url_source'] = url
                            
                            # Generate preview data
                            preview_data = create_safe_preview_data(df)
                            
                            return {
                                "status": "success", 
                                "rows": len(df), 
                                "columns": len(df.columns),
                                "type": "wikipedia_table",
                                "title": title_text,
                                "scraping_code": scraping_code,
                                "table_index": i+1,
                                "preview": preview_data
                            }
                except Exception as e:
                    continue
        
        # If no tables, try to extract list data from Wikipedia
        return await extract_wikipedia_lists(soup, url, title_text)
        
    except Exception as e:
        return {"error": f"Failed to process Wikipedia URL: {str(e)}"}

def clean_wikipedia_dataframe(df):
    """Clean Wikipedia table data"""
    # Remove citation marks like [1], [2], etc.
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(r'\[\d+\]', '', regex=True)
            df[col] = df[col].str.replace(r'\[.*?\]', '', regex=True)  # Remove all bracketed content
            df[col] = df[col].str.strip()
    
    # Remove empty rows
    df = df.dropna(how='all')
    
    # Handle multi-level column headers
    if hasattr(df.columns, 'nlevels') and df.columns.nlevels > 1:
        df.columns = [' '.join(col).strip() for col in df.columns.values]
    
    return df

async def extract_wikipedia_lists(soup, url, title_text):
    """Extract list data from Wikipedia when tables aren't available"""
    try:
        # Look for ordered/unordered lists that might contain structured data
        lists = soup.find_all(['ul', 'ol'])
        
        structured_data = []
        for list_elem in lists:
            items = list_elem.find_all('li')
            if len(items) > 3:  # Only consider lists with multiple items
                list_data = []
                for item in items[:50]:  # Limit to first 50 items
                    text = item.get_text().strip()
                    if text and len(text) > 10:  # Skip very short items
                        # Clean the text
                        text = re.sub(r'\[\d+\]', '', text)  # Remove citations
                        text = re.sub(r'\[.*?\]', '', text)  # Remove all bracketed content
                        list_data.append(text)
                
                if len(list_data) > 3:
                    structured_data.extend(list_data)
        
        if structured_data:
            # Create DataFrame from list data
            df = pd.DataFrame({
                'Item': range(1, len(structured_data) + 1),
                'Description': structured_data
            })
            
            # Generate scraping code
            scraping_code = await generate_wikipedia_scraping_code(url, title_text, df.head(3))
            
            memory_store['dataframe'] = df
            memory_store['engine'] = 'pandas'
            memory_store['filename'] = f"wikipedia_{title_text.replace(' ', '_')}_lists.csv"
            memory_store['scraping_code'] = scraping_code
            memory_store['url_source'] = url
            
            return {
                "status": "success", 
                "rows": len(df), 
                "columns": len(df.columns),
                "type": "wikipedia_lists",
                "title": title_text,
                "scraping_code": scraping_code
            }
    except Exception as e:
        pass
    
    return {"error": "No structured data found in Wikipedia page"}

async def generate_wikipedia_scraping_code(url: str, title: str, sample_data):
    """Generate Python web scraping code for the specific Wikipedia page"""
    
    prompt = f"""
Generate complete Python web scraping code to extract data from this Wikipedia page:

URL: {url}
Page Title: {title}

Sample of extracted data:
{sample_data.to_string()}

Generate a complete Python script that:
1. Imports necessary libraries (requests, beautifulsoup4, pandas)
2. Fetches the webpage with proper headers
3. Parses the HTML with BeautifulSoup
4. Extracts the same type of data shown in the sample
5. Creates a pandas DataFrame
6. Includes error handling
7. Saves the data to a CSV file

Make the code robust and well-commented. The code should work independently when run.
Only return the Python code, no explanations.
"""

    try:
        response = model.generate_content(prompt)
        scraping_code = response.text.strip()
        
        # Clean the code if it has markdown formatting
        if "```python" in scraping_code:
            scraping_code = scraping_code.split("```python")[1].split("```")[0].strip()
        elif "```" in scraping_code:
            scraping_code = scraping_code.split("```")[1].split("```")[0].strip()
            
        return scraping_code
    except Exception as e:
        return f"# Error generating scraping code: {str(e)}\n# Manual scraping required"

async def handle_generic_url(url: str):
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
            
            # Generate preview data
            preview_data = create_safe_preview_data(df)
            
            return {"status": "success", "rows": len(df), "type": "direct_csv", "preview": preview_data}
        
        elif 'json' in content_type or url.endswith('.json'):
            df = pd.read_json(io.StringIO(response.text))
            memory_store['dataframe'] = df
            memory_store['engine'] = 'pandas'
            memory_store['filename'] = url.split('/')[-1] or 'scraped_data.json'
            
            # Generate preview data
            preview_data = create_safe_preview_data(df)
            
            return {"status": "success", "rows": len(df), "type": "direct_json", "preview": preview_data}
        
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
                        
                        # Generate preview data
                        preview_data = create_safe_preview_data(df)
                        
                        return {"status": "success", "rows": len(df), "type": "html_table", "preview": preview_data}
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
                
                # Generate preview data
                preview_data = create_safe_preview_data(df)
                
                return {"status": "success", "rows": len(df), "type": "ai_extracted", "preview": preview_data}
            else:
                return {"error": "AI could not extract structured data"}
                
        except Exception as e:
            return {"error": f"Failed to process webpage with AI: {str(e)}"}
            
    except requests.RequestException as e:
        return {"error": f"Failed to fetch URL: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error processing URL: {str(e)}"}
