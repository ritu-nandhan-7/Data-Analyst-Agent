#!/usr/bin/env python3
"""
Quick test to get actual answers for the adult dataset questions
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

questions = [
    "How many individuals are from the 'United-States'?",
    "Which occupation has the highest number of individuals with an income greater than 50K?", 
    "How many 'Female' individuals are 'Divorced'?",
    "What percentage of 'Bachelors' have an income greater than 50K?",
    "What is the maximum average number of hours worked per week across different work classes?"
]

def quick_test():
    print("🔍 Quick Adult Dataset Analysis")
    print("=" * 50)
    
    # Upload dataset first
    try:
        with open("../../backend/data/adult_dataset.csv", 'rb') as file:
            files = {'file': ('adult_dataset.csv', file, 'text/csv')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        print(f"✅ Dataset uploaded: {response.json().get('rows', 'Unknown')} rows")
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Test each question
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. {question}")
        print("-" * 60)
        
        payload = {"question": question}
        
        try:
            response = requests.post(f"{BASE_URL}/api/query", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ ANSWER: {data.get('response', 'No response')}")
                
                if data.get('image'):
                    print("📊 + Includes visualization")
                    
            else:
                print(f"❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)
    
    print(f"\n🎉 Test complete!")

if __name__ == "__main__":
    quick_test()