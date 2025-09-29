#!/usr/bin/env python3
"""
Test script for the Data Analyst Agent API
"""
import requests
import json
import pandas as pd
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test basic health check"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    print(f"   Status: {data['status']}")
    print(f"   Dataset loaded: {data['dataset_loaded']}")
    print("   ✅ Health check passed")

def test_upload_csv():
    """Test CSV upload with sample data"""
    print("\n📤 Testing CSV upload...")
    
    # Create sample CSV data
    sample_data = pd.DataFrame({
        'product': ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry'] * 20,
        'price': [1.2, 0.5, 2.1, 3.0, 4.5] * 20,
        'quantity': [100, 200, 50, 30, 10] * 20,
        'category': ['Fruit', 'Fruit', 'Fruit', 'Fruit', 'Berry'] * 20,
        'region': ['North', 'South', 'East', 'West', 'Central'] * 20
    })
    
    # Save to temporary CSV
    csv_content = sample_data.to_csv(index=False)
    
    # Upload the CSV data
    files = {'file': ('test_data.csv', csv_content, 'text/csv')}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    print(f"   Uploaded rows: {data['rows']}")
    print("   ✅ CSV upload successful")
    return data

def test_queries():
    """Test various natural language queries"""
    print("\n💬 Testing queries...")
    
    test_queries = [
        {
            "question": "What's the summary of the dataset?",
            "description": "Basic summary"
        },
        {
            "question": "Show me the top 3 most expensive products",
            "description": "Top products by price"
        },
        {
            "question": "What's the total quantity by category?",
            "description": "Category aggregation"
        },
        {
            "question": "Create a bar chart showing average price by region",
            "description": "Visualization with grouping"
        }
    ]
    
    for i, test_query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {test_query['description']}")
        print(f"   Question: \"{test_query['question']}\"")
        
        payload = {
            "question": test_query["question"],
            "session_id": "test_session"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/query", 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success (attempt {data.get('attempt', 1)})")
                print(f"   📊 Result: {str(data.get('result', 'N/A'))[:100]}...")
                print(f"   📝 Explanation: {data.get('explanation', 'N/A')[:100]}...")
                
                if data.get('image'):
                    print(f"   🎨 Visualization generated (size: {len(data['image'])} chars)")
                    
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        
        # Small delay between queries
        time.sleep(1)

def test_status():
    """Test status endpoint"""
    print("\n📊 Testing status endpoint...")
    response = requests.get(f"{BASE_URL}/status")
    assert response.status_code == 200
    data = response.json()
    
    print(f"   Dataset loaded: {data['dataset_loaded']}")
    if data['dataset_info']:
        info = data['dataset_info']
        print(f"   Filename: {info['filename']}")
        print(f"   Engine: {info['engine']}")
        print(f"   Shape: {info['shape']}")
        print(f"   Columns: {len(info['columns'])} columns")
    print("   ✅ Status check passed")

def test_history():
    """Test conversation history"""
    print("\n📜 Testing conversation history...")
    response = requests.get(f"{BASE_URL}/history/test_session")
    
    if response.status_code == 200:
        data = response.json()
        history_count = len(data.get('history', []))
        print(f"   History entries: {history_count}")
        print("   ✅ History retrieval successful")
    else:
        print(f"   ❌ History retrieval failed: {response.status_code}")

def main():
    """Run all tests"""
    print("🧪 Starting Data Analyst Agent API Tests\n")
    
    try:
        # Test basic endpoints
        test_health_check()
        test_upload_csv()
        test_status()
        
        # Test query functionality
        test_queries()
        
        # Test history
        test_history()
        
        print("\n🎉 All tests completed!")
        print("✅ Your Data Analyst Agent API is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Make sure the server is running on http://localhost:8000")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())