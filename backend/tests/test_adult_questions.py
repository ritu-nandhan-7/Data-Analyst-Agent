#!/usr/bin/env python3
"""
Test script for specific adult dataset questions
Run this after starting the backend server with: uvicorn app.main:app --reload
"""

import requests
import json
import time
import os

BASE_URL = "http://127.0.0.1:8000"

# Your specific questions about the adult dataset
ADULT_QUESTIONS = [
    "How many individuals are from the 'United-States'?",
    "Which occupation has the highest number of individuals with an income greater than 50K?",
    "How many 'Female' individuals are 'Divorced'?",
    "What percentage of 'Bachelors' have an income greater than 50K?",
    "What is the maximum average number of hours worked per week across different work classes?"
]

def test_adult_dataset():
    print("🧪 Testing Adult Dataset Questions")
    print("="*60)
    
    # 1. Health Check
    print("\n1️⃣ Checking API Health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ API is running!")
        else:
            print("❌ API not responding properly")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the backend server is running:")
        print("cd backend/src && python -m uvicorn app.main:app --reload")
        return False
    
    # 2. Upload Adult Dataset
    print("\n2️⃣ Uploading Adult Dataset...")
    dataset_path = "../data/adult_dataset.csv"
    
    # Try different possible paths for the dataset
    possible_paths = [
        "../../backend/data/adult_dataset.csv",
        "../data/adult_dataset.csv",
        "../../data/adult_dataset.csv", 
        "../backend/data/adult_dataset.csv",
        "data/adult_dataset.csv",
        "adult_dataset.csv"
    ]
    
    dataset_uploaded = False
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'rb') as file:
                    files = {'file': ('adult_dataset.csv', file, 'text/csv')}
                    response = requests.post(f"{BASE_URL}/api/upload", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Dataset uploaded! Rows: {data.get('rows', 'Unknown')}")
                    print(f"   Columns: {data.get('columns', 'Unknown')}")
                    dataset_uploaded = True
                    break
                else:
                    print(f"❌ Upload failed: {response.text}")
            except Exception as e:
                print(f"❌ Error uploading file: {e}")
        
    if not dataset_uploaded:
        print("❌ Could not find or upload adult_dataset.csv")
        print("Available paths searched:", possible_paths)
        return False
    
    # 3. Test each question
    print(f"\n3️⃣ Testing {len(ADULT_QUESTIONS)} Adult Dataset Questions")
    print("-" * 60)
    
    results = []
    
    for i, question in enumerate(ADULT_QUESTIONS, 1):
        print(f"\n📊 Question {i}: {question}")
        
        payload = {"question": question}
        
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/query", json=payload, timeout=60)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ SUCCESS ({response_time:.2f}s)")
                
                # Display the response
                if data.get('response'):
                    print(f"📝 Answer: {data['response'][:200]}...")
                    results.append({
                        'question': question,
                        'status': 'success',
                        'answer': data['response'],
                        'time': response_time,
                        'has_image': bool(data.get('image'))
                    })
                
                if data.get('image'):
                    print("🎨 Visualization created!")
                
                if data.get('attempt', 1) > 1:
                    print(f"🔧 Self-healed after {data.get('attempt')} attempts")
                    
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else 'No response content'
                print(f"❌ FAILED: {error_detail}")
                results.append({
                    'question': question,
                    'status': 'failed',
                    'error': error_detail,
                    'time': response_time
                })
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            results.append({
                'question': question,
                'status': 'exception',
                'error': str(e),
                'time': 0
            })
        
        # Small pause between questions
        time.sleep(2)
    
    # 4. Summary
    print(f"\n4️⃣ Test Results Summary")
    print("=" * 60)
    
    successful = len([r for r in results if r['status'] == 'success'])
    failed = len([r for r in results if r['status'] != 'success'])
    
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    
    if successful > 0:
        avg_time = sum([r['time'] for r in results if r['status'] == 'success']) / successful
        print(f"⏱️ Average Response Time: {avg_time:.2f}s")
    
    # Display successful answers
    print(f"\n📋 Successful Answers:")
    for i, result in enumerate(results, 1):
        if result['status'] == 'success':
            print(f"\n{i}. {result['question']}")
            print(f"   Answer: {result['answer'][:150]}...")
            if result['has_image']:
                print("   📊 Includes visualization")
    
    # 5. Check Self-Healing Stats
    print(f"\n5️⃣ Self-Healing Statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/self-healing/stats")
        if response.status_code == 200:
            stats = response.json()['statistics']
            print(f"🔧 Auto-fixes during test: {stats['total_fixes']}")
            print(f"📈 Success rate: {stats.get('overall_success_rate', 0):.1f}%")
        else:
            print("❌ Could not retrieve self-healing stats")
    except Exception as e:
        print(f"❌ Error checking stats: {e}")
    
    return successful == len(results)

def main():
    print("🚀 Adult Dataset Question Tester")
    print("Make sure your backend is running at http://localhost:8000")
    print("\nQuestions to test:")
    for i, q in enumerate(ADULT_QUESTIONS, 1):
        print(f"  {i}. {q}")
    
    input("\nPress Enter to start testing...")
    
    success = test_adult_dataset()
    
    if success:
        print(f"\n🎉 All tests passed! Your backend is working perfectly.")
    else:
        print(f"\n⚠️ Some tests failed. Check the backend logs for details.")

if __name__ == "__main__":
    main()