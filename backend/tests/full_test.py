#!/usr/bin/env python3
"""
Test all 5 adult dataset questions
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

QUESTIONS = [
    "How many individuals are from the 'United-States'?",
    "Which occupation has the highest number of individuals with an income greater than 50K?",
    "How many 'Female' individuals are 'Divorced'?",
    "What percentage of 'Bachelors' have an income greater than 50K?",
    "What is the maximum average number of hours worked per week across different work classes?",
    "Plot a smooth distribution curve of the age column in the given dataset"
]

def test_all_questions():
    print("🧪 Testing All 5 Adult Dataset Questions")
    print("="*60)
    
    # Upload dataset
    print("1. Uploading dataset...")
    try:
        with open("../data/adult_dataset.csv", 'rb') as file:
            files = {'file': ('adult_dataset.csv', file, 'text/csv')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        print(f"✅ Dataset uploaded: {response.json()['rows']} rows")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return
    
    # Test each question
    print(f"\n2. Testing {len(QUESTIONS)} questions...")
    results = []
    
    for i, question in enumerate(QUESTIONS, 1):
        print(f"\n{'='*60}")
        print(f"Question {i}: {question}")
        print('='*60)
        
        payload = {"question": question}
        
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/query", json=payload, timeout=60)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ SUCCESS ({end_time - start_time:.2f}s)")
                print(f"📊 Result: {data.get('result', 'N/A')}")
                print(f"💡 Explanation: {data.get('explanation', 'No explanation')}")
                
                if data.get('image'):
                    print("🎨 Visualization: Created!")
                else:
                    print("🎨 Visualization: None")
                
                if data.get('attempt', 1) > 1:
                    print(f"🔧 Self-healed: {data['attempt']} attempts")
                
                print(f"🔍 Code executed:")
                print(f"   {data.get('code_executed', 'No code shown')[:100]}...")
                
                results.append({
                    'question': question,
                    'result': data.get('result'),
                    'explanation': data.get('explanation'),
                    'time': end_time - start_time,
                    'attempts': data.get('attempt', 1)
                })
                
            else:
                print(f"❌ FAILED: {response.status_code}")
                if response.content:
                    error_data = response.json()
                    print(f"Error: {error_data.get('detail', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
        
        time.sleep(1)  # Brief pause between requests
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 SUMMARY OF ALL RESULTS")
    print('='*60)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['question']}")
        print(f"   Answer: {result['result']}")
        print(f"   Time: {result['time']:.2f}s | Attempts: {result['attempts']}")
    
    print(f"\n🎉 Test completed! {len(results)}/{len(QUESTIONS)} questions answered successfully")

if __name__ == "__main__":
    test_all_questions()