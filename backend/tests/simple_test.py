#!/usr/bin/env python3
"""
Simple direct test of backend responses
"""

import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"

def test_single_query():
    print("🧪 Direct Backend Test")
    print("="*40)
    
    # Upload dataset first
    dataset_path = "../data/adult_dataset.csv"
    
    print("1. Uploading dataset...")
    try:
        with open(dataset_path, 'rb') as file:
            files = {'file': ('adult_dataset.csv', file, 'text/csv')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        print(f"Upload response: {response.status_code}")
        print(f"Upload data: {response.json()}")
        
    except Exception as e:
        print(f"Upload error: {e}")
        return
    
    # Test one simple question
    print("\n2. Testing simple question...")
    question = "How many individuals are from the 'United-States'?"
    
    payload = {"question": question}
    
    try:
        response = requests.post(f"{BASE_URL}/api/query", json=payload, timeout=30)
        
        print(f"Query response status: {response.status_code}")
        print(f"Query response headers: {dict(response.headers)}")
        
        if response.content:
            try:
                data = response.json()
                print(f"Query response data: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Raw response content: {response.text}")
        else:
            print("No response content")
            
    except Exception as e:
        print(f"Query error: {e}")

if __name__ == "__main__":
    test_single_query()