#!/usr/bin/env python3
"""
Debug test to see the actual response structure
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def debug_test():
    print("🐛 Debug Response Structure")
    print("=" * 40)
    
    # Upload dataset
    try:
        with open("../../backend/data/adult_dataset.csv", 'rb') as file:
            files = {'file': ('adult_dataset.csv', file, 'text/csv')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        print(f"✅ Dataset uploaded: {response.json()}")
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Test one question
    question = "How many individuals are from the 'United-States'?"
    payload = {"question": question}
    
    print(f"\n📊 Testing: {question}")
    print("-" * 60)
    
    try:
        response = requests.post(f"{BASE_URL}/api/query", json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.content:
            data = response.json()
            print(f"Full Response: {json.dumps(data, indent=2)}")
        else:
            print("No response content")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_test()