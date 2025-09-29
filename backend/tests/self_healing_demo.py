#!/usr/bin/env python3
"""
Self-Healing Demo
Shows how the system automatically fixes errors in real-time
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def demo_self_healing():
    print("🤖 Self-Healing System Demo")
    print("="*50)
    
    # 1. Check self-healing status
    print("\n1️⃣ Check Self-Healing Status")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Self-Healing Status: {data['self_healing']['status']}")
            print(f"   Total Fixes: {data['self_healing']['total_fixes']}")
        
        # Get detailed stats
        response = requests.get(f"{BASE_URL}/self-healing/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Self-Healing Statistics:")
            print(f"   - Total Fixes: {stats['statistics']['total_fixes']}")
            print(f"   - Average Attempts: {stats['statistics']['average_attempts']}")
    except Exception as e:
        print(f"❌ Error checking status: {e}")
    
    # 2. Upload dataset to trigger potential errors
    print("\n2️⃣ Upload Dataset and Test Error Handling")
    try:
        with open('adult_dataset.csv', 'rb') as file:
            files = {'file': ('adult_dataset.csv', file, 'text/csv')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            print("✅ Dataset uploaded successfully")
    except Exception as e:
        print(f"❌ Upload error: {e}")
    
    # 3. Test queries that might trigger self-healing
    print("\n3️⃣ Test Queries (Self-Healing Active)")
    
    # This query might cause JSON serialization issues that get auto-fixed
    tricky_queries = [
        "Count all unique values in each column and return as a detailed summary",
        "Create a complex analysis with multiple data types that might cause serialization issues",
        "Calculate advanced statistics that return numpy data types"
    ]
    
    for i, query in enumerate(tricky_queries, 1):
        print(f"\n   Query {i}: {query[:50]}...")
        
        try:
            payload = {"question": query, "session_id": "self_healing_demo"}
            response = requests.post(f"{BASE_URL}/query", json=payload, timeout=60)
            
            if response.status_code == 200:
                print("   ✅ Query successful (may have been auto-fixed)")
            else:
                print(f"   ⚠️ Query failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)
    
    # 4. Check healing logs
    print("\n4️⃣ Check Self-Healing Activity")
    try:
        response = requests.get(f"{BASE_URL}/self-healing/logs")
        if response.status_code == 200:
            logs = response.json()
            recent_logs = logs['recent_logs'][-10:]  # Last 10 lines
            
            print(f"✅ Recent Self-Healing Activity ({len(recent_logs)} entries):")
            for log in recent_logs:
                if "Auto-fixing" in log or "Successfully fixed" in log:
                    print(f"   🔧 {log.strip()}")
        else:
            print("   📋 No healing activity yet")
            
    except Exception as e:
        print(f"   ❌ Error reading logs: {e}")
    
    # 5. Final stats
    print("\n5️⃣ Final Self-Healing Statistics")
    try:
        response = requests.get(f"{BASE_URL}/self-healing/stats")
        if response.status_code == 200:
            stats = response.json()['statistics']
            print(f"   🏆 Total Automatic Fixes: {stats['total_fixes']}")
            print(f"   📊 Average Fix Attempts: {stats['average_attempts']}")
            
            if stats['success_rate_by_function']:
                print("   🎯 Success Rate by Function:")
                for func, rate in stats['success_rate_by_function'].items():
                    success_rate = (rate['fixes'] / rate['attempts']) * 100
                    print(f"      - {func}: {success_rate:.1f}%")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 Self-Healing Demo Complete!")
    print(f"🔮 Your system can now fix errors automatically!")

if __name__ == "__main__":
    demo_self_healing()