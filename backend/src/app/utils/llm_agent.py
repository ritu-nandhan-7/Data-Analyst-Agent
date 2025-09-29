import os
import traceback
import base64
import io
import pandas as pd
import polars as pl
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.io as pio
import plotly.graph_objects as go
import google.generativeai as genai
from app.memory import memory_store
from dotenv import load_dotenv
from app.utils.self_healing import auto_healer, self_healing_decorator

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')  # Using standard model name

def make_json_serializable(obj):
    """Convert numpy/pandas objects to JSON-serializable format"""
    import math
    
    if hasattr(obj, 'to_dict'):
        result = obj.to_dict()
        # Handle tuple keys in dictionaries
        if isinstance(result, dict):
            return {str(k): make_json_serializable(v) for k, v in result.items()}
        return result
    elif hasattr(obj, 'to_dicts'):
        return obj.to_dicts()
    elif hasattr(obj, 'tolist'):  # numpy arrays
        return obj.tolist()
    elif hasattr(obj, 'item'):  # numpy scalars
        value = obj.item()
        # Handle infinity and NaN values
        if isinstance(value, float):
            if math.isnan(value):
                return None
            elif math.isinf(value):
                return "Infinity" if value > 0 else "-Infinity"
        return value
    elif isinstance(obj, dict):
        # Handle tuple keys and other non-serializable keys
        return {str(k) if not isinstance(k, (str, int, float, bool)) else k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return [make_json_serializable(item) for item in obj]  # Convert tuples to lists and process items
    elif isinstance(obj, float):
        # Handle Python float infinity and NaN
        if math.isnan(obj):
            return None
        elif math.isinf(obj):
            return "Infinity" if obj > 0 else "-Infinity"
        return obj
    elif hasattr(obj, 'dtype'):  # numpy data types
        if 'int' in str(obj.dtype):
            return int(obj)
        elif 'float' in str(obj.dtype):
            value = float(obj)
            # Handle infinity and NaN
            if math.isnan(value):
                return None
            elif math.isinf(value):
                return "Infinity" if value > 0 else "-Infinity"
            return value
        else:
            return str(obj)
    elif hasattr(obj, '__dict__'):  # Complex objects
        return str(obj)
    else:
        return obj

def call_gemini(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return """# Fallback code
result = dataframe.describe()
explanation = 'Basic dataset summary generated due to API error.'
"""

@self_healing_decorator
async def process_query(question: str, context: dict, session_id: str):
    """Process user query and generate analysis"""
    df = memory_store.get('dataframe')
    engine = memory_store.get('engine', 'pandas')
    filename = memory_store.get('filename', 'unknown')
    
    if df is None:
        return {"error": "No dataset loaded. Please upload a dataset first."}
    
    # Get basic info about the dataframe
    scraping_code = memory_store.get('scraping_code', None)
    url_source = memory_store.get('url_source', None)
    if engine == 'pandas':
        df_info = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": {str(col): str(dtype) for col, dtype in df.dtypes.items()},
            "sample": df.head(3).to_dict('records') if len(df) > 0 else []
        }
    else:  # polars
        df_info = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": {str(col): str(dtype) for col, dtype in zip(df.columns, df.dtypes)},
            "sample": df.head(3).to_dicts() if len(df) > 0 else []
        }
    
    # Prepare prompt for LLM
    prompt = f"""
You are a data analyst agent. Generate Python code to answer the user's question about their dataset.

Dataset Info:
- Filename: {filename}
- Shape: {df_info['shape']} (rows, columns)
- Columns: {df_info['columns']}
- Data types: {df_info['dtypes']}
- Sample data: {df_info['sample']}

Question: {question}
Context: {context}

CRITICAL INSTRUCTIONS:
1. DO NOT load any CSV files or use pd.read_csv() or similar functions
2. The dataset is ALREADY LOADED in the variable 'dataframe' - use it directly
3. The dataframe variable is already available - just use: dataframe (not pd.read_csv())
4. The engine is '{engine}' so use {'pandas' if engine == 'pandas' else 'polars'} methods
5. If creating visualizations, use matplotlib/seaborn/plotly
6. For matplotlib/seaborn plots, save to BytesIO buffer as PNG:
   ```python
   import io
   buffer = io.BytesIO()
   plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
   buffer.seek(0)
   image_bytes = buffer.getvalue()
   plt.close()
   ```
7. Return these variables:
   - result: Your analysis result (numbers, text, or dict/list)
   - explanation: Clear explanation of what you found
   - image_bytes: (optional) bytes of the visualization

IMPORTANT: Start your code by using the existing 'dataframe' variable, NOT by loading a CSV file.
Example: df_shape = dataframe.shape  # CORRECT
DO NOT: dataframe = pd.read_csv('file.csv')  # WRONG - DON'T DO THIS

Generate ONLY the Python code, no explanatory text before or after.
"""

    # Agentic loop - retry up to 3 times if code fails
    for attempt in range(3):
        try:
            code = call_gemini(prompt)
            
            # Clean up the code (remove markdown formatting if present)
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].strip()
            
            # Execute the code
            local_vars = {
                'dataframe': df,
                'pd': pd,
                'pl': pl,
                'plt': plt,
                'sns': sns,
                'go': go,
                'pio': pio,
                'io': io,
                'np': np
            }
            
            exec(code, local_vars, local_vars)
            
            # Get results
            result = local_vars.get('result', 'No result returned')
            explanation = local_vars.get('explanation', 'Analysis completed')
            image_bytes = local_vars.get('image_bytes')
            
            # Convert result to JSON-serializable format
            result = make_json_serializable(result)
            
            # Encode image if present
            image_b64 = None
            if image_bytes:
                image_b64 = base64.b64encode(image_bytes).decode()
            
            # Save to conversation history
            from app.memory import save_conversation
            save_conversation(session_id, question, {
                "result": result,
                "explanation": explanation,
                "has_image": image_b64 is not None
            })
            
            response_data = {
                "result": result,
                "explanation": explanation,
                "image": image_b64,
                "code_executed": code,
                "attempt": attempt + 1
            }
            
            # Add scraping code and source URL if available
            if scraping_code:
                response_data["scraping_code"] = scraping_code
            if url_source:
                response_data["url_source"] = url_source
                response_data["data_source_type"] = "web_scraping"
            
            return response_data
            
        except Exception as e:
            error_msg = str(e)
            tb = traceback.format_exc()
            
            if attempt == 2:  # Last attempt
                return {
                    "error": f"Failed to execute analysis after 3 attempts. Last error: {error_msg}",
                    "traceback": tb,
                    "last_code": code
                }
            
            # Update prompt with error info for retry
            prompt += f"\n\nThe previous code failed with this error:\n{error_msg}\n\nTraceback:\n{tb}\n\nPlease fix the code and try again."
            
    return {"error": "Unexpected error in processing loop"}
