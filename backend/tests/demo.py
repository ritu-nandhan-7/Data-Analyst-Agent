#!/usr/bin/env python3
"""
Quick demo of the Data Analyst Agent API
This script demonstrates the key features of the API.
Run this AFTER starting the server with: uvicorn app.main:app --reload
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def demo():
    print("🤖 Data Analyst Agent API Demo")
    print("="*50)
    
    # 1. Check health
    print("\n1️⃣ Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ API is running!")
            data = response.json()
            print(f"   Status: {data['status']}")
        else:
            print("❌ API not responding")
            return
    except:
        print("❌ Cannot connect to API. Make sure server is running!")
        return
    
    # 2. Upload Adult Dataset
    print("\n2️⃣ Upload Adult Dataset")
    
    # Upload the adult_dataset.csv file
    try:
        with open('adult_dataset.csv', 'rb') as file:
            files = {'file': ('adult_dataset.csv', file, 'text/csv')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Adult Dataset uploaded! Rows: {data['rows']}")
        else:
            print(f"❌ Upload failed: {response.text}")
            return
    except FileNotFoundError:
        print("❌ adult_dataset.csv not found in current directory!")
        return
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return
    
    # 3. Complex Error-Prone Queries (Self-Healing Test)
    print("\n3️⃣ Complex Self-Healing Test Queries")
    queries = [
        # Query 1: Complex aggregation that might cause JSON serialization issues
        "Create a comprehensive statistical summary with means, medians, modes, and standard deviations for ALL numerical columns grouped by income level. Include numpy data types and return detailed analysis with correlation matrices.",
        
        # Query 2: Complex data type mixing that often causes errors
        "Generate a pivot table showing workclass vs education with income percentages, then create a heatmap visualization. Use complex pandas operations like crosstab, pivot_table, and advanced indexing that might break.",
        
        # Query 3: Memory-intensive operation that might fail
        "Create multiple visualizations in one go: (1) correlation heatmap of all numeric features, (2) distribution plots for age, education.num, hours.per.week, (3) box plots comparing income levels across all categorical variables. Save all plots and return detailed statistics.",
        
        # Query 4: Complex string operations and filtering that often breaks
        "Find all unique combinations of (workclass, education, marital.status) where income is '>50K', then calculate the percentage distribution of each combination. Create a complex multi-level analysis with nested grouping and return as hierarchical data structure.",
        
        # Query 5: Advanced statistical analysis with potential numpy/pandas conflicts
        "Perform advanced statistical analysis: calculate chi-square tests between categorical variables and income, create confusion matrix-style analysis, compute odds ratios, and generate a comprehensive statistical report with p-values and confidence intervals using scipy if available."
    ]
    
    for i, question in enumerate(queries, 1):
        print(f"\n   🧪 Query {i}: {question[:80]}...")
        
        payload = {"question": question, "session_id": "self_healing_test"}
        
        try:
            response = requests.post(f"{BASE_URL}/query", json=payload, timeout=90)  # Longer timeout for complex queries
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {data.get('explanation', 'Analysis completed')[:100]}...")
                if data.get('image'):
                    print("   🎨 Visualization created!")
                if data.get('attempt', 1) > 1:
                    print(f"   🔧 Auto-healed after {data.get('attempt')} attempts")
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"   ❌ Failed: {error_detail[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)[:100]}...")
        
        time.sleep(3)  # Longer pause for complex operations
    
    print(f"\n4️⃣ Check Self-Healing Statistics")
    try:
        # Check healing statistics
        response = requests.get(f"{BASE_URL}/self-healing/stats")
        if response.status_code == 200:
            stats = response.json()['statistics']
            print(f"🔧 Self-Healing Results:")
            print(f"   - Total Auto-Fixes: {stats['total_fixes']}")
            print(f"   - Average Fix Attempts: {stats['average_attempts']}")
            
            if stats['success_rate_by_function']:
                print(f"   - Functions Auto-Fixed: {len(stats['success_rate_by_function'])}")
                for func, rate in stats['success_rate_by_function'].items():
                    success_rate = (rate['fixes'] / rate['attempts']) * 100 if rate['attempts'] > 0 else 0
                    print(f"     • {func}: {success_rate:.1f}% success rate")
            
            if stats['recent_fixes']:
                print(f"   - Recent Fixes: {len(stats['recent_fixes'])}")
        
        # Check healing logs
        response = requests.get(f"{BASE_URL}/self-healing/logs")
        if response.status_code == 200:
            logs = response.json()['recent_logs']
            healing_logs = [log for log in logs if 'Auto-fixing' in log or 'Successfully fixed' in log]
            if healing_logs:
                print(f"\n📋 Recent Auto-Fix Activity:")
                for log in healing_logs[-5:]:  # Show last 5 healing events
                    print(f"   {log.strip()}")
    except Exception as e:
        print(f"❌ Error checking healing stats: {e}")

    print(f"\n5️⃣ Final System Status")
    response = requests.get(f"{BASE_URL}/status")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Dataset info:")
        info = data.get('dataset_info', {})
        print(f"   - Shape: {info.get('shape')}")
        print(f"   - Columns: {info.get('columns')}")
        print(f"   - Engine: {info.get('engine')}")
    
    print("\n🎉 Self-Healing Demo Complete!")
    print(f"🤖 Your AI system automatically fixed any errors that occurred!")
    print(f"🔮 Visit http://127.0.0.1:8000/docs for interactive API documentation")

if __name__ == "__main__":
    demo()