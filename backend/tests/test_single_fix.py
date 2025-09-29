"""
Test the specific failing query after infinity/NaN fix
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_infinity_fix():
    print("🔧 Testing infinity/NaN JSON serialization fix...")
    print("Query: Multi-level grouping with complex aggregations")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/query", 
        json={"question": "Group by multiple categorical variables and calculate various statistical measures, creating a comprehensive summary table"}, 
        timeout=60
    )
    end_time = time.time()
    
    print(f"⏱️ Response time: {end_time - start_time:.2f} seconds")
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! JSON serialization fix worked!")
        try:
            result = response.json()
            if "explanation" in result:
                print(f"📝 Explanation length: {len(result['explanation'])} chars")
            if "analysis" in result:
                print(f"📊 Analysis data: {len(str(result['analysis']))} chars")
        except Exception as e:
            print(f"❌ JSON parsing error: {e}")
    else:
        print("❌ STILL FAILED!")
        try:
            error = response.json()
            print(f"Error: {error}")
        except:
            print(f"Raw response: {response.text}")

if __name__ == "__main__":
    test_infinity_fix()