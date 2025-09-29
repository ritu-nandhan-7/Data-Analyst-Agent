#!/usr/bin/env python3
"""
Complete Self-Healing System Test
Tests the enhanced self-healing system with dataset upload and complex queries
"""

import requests
import json
import time
import os

# Configuration
BASE_URL = "http://localhost:8000"
DATASET_FILE = "adult_dataset.csv"

def test_upload_dataset():
    """Upload the dataset first"""
    print("🔄 Step 1: Uploading dataset...")
    
    if not os.path.exists(DATASET_FILE):
        print(f"❌ Dataset file '{DATASET_FILE}' not found!")
        return False
    
    with open(DATASET_FILE, 'rb') as f:
        files = {'file': (DATASET_FILE, f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Dataset uploaded successfully!")
        print(f"   Rows: {result.get('rows', 'unknown')}")
        print(f"   Columns: {result.get('columns', 'unknown')}")
        return True
    else:
        print(f"❌ Upload failed: {response.text}")
        return False

def test_query(query_text, test_name):
    """Test a single query and check for self-healing"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"QUERY: {query_text}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={
                "question": query_text,
                "session_id": "test_healing"
            },
            timeout=150  # 2.5 minutes timeout
        )
        
        response_time = time.time() - start_time
        print(f"⏱️ Response time: {response_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if self-healing was involved
            if 'auto_healing_info' in result:
                healing_info = result['auto_healing_info']
                print(f"🔧 Self-healing attempted: {healing_info.get('attempted', False)}")
                print(f"✅ Self-healing successful: {healing_info.get('successful', False)}")
            
            if result.get('success', True):
                print("✅ SUCCESS!")
                if 'explanation' in result:
                    print(f"📝 Explanation: {result['explanation'][:200]}...")
                if 'visualization' in result:
                    print("📊 Visualization generated!")
            else:
                print("❌ FAILED!")
                print(f"Error: {result.get('error', 'Unknown error')}")
                if result.get('auto_fix_attempted'):
                    print(f"🔧 Auto-fix attempted: {result.get('auto_fix_successful', False)}")
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print("❌ FAILED!")
            print(f"Error: {error_data}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT!")
        print("Query took too long to execute")
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")

def get_healing_stats():
    """Get self-healing statistics"""
    try:
        response = requests.get(f"{BASE_URL}/self-healing/stats")
        if response.status_code == 200:
            return response.json()
        else:
            # Try alternative endpoint
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                return data.get('self_healing', {})
    except:
        pass
    return None

def main():
    """Run the complete self-healing test"""
    print("🧪 Complete Self-Healing System Test")
    print("Uploading dataset and testing enhanced error handling")
    
    # Step 1: Upload dataset
    if not test_upload_dataset():
        print("❌ Cannot proceed without dataset. Exiting.")
        return
    
    # Step 2: Test queries that previously caused issues
    test_queries = [
        (
            "Create a detailed cross-tabulation between education level and income brackets, showing both counts and percentages",
            "Cross-tabulation with tuple keys (previously failed)"
        ),
        (
            "Perform advanced statistical analysis including correlation matrix, outlier detection, and distribution analysis for all numeric variables",
            "Complex stats with multiple numpy objects (previously failed)"
        ),
        (
            "Group by multiple categorical variables and calculate various statistical measures, creating a comprehensive summary table",
            "Multi-level grouping with complex aggregations"
        ),
        (
            "Use the pandas.np module to analyze the data and create visualizations using non-existent functions",
            "Query with intentional errors to test self-healing"
        ),
        (
            "Perform comprehensive data analysis including: 1) Detailed descriptive statistics for each variable, 2) Correlation analysis with heatmap, 3) Distribution plots for all variables, 4) Outlier analysis, 5) Cross-tabulations for all categorical pairs, 6) Regression analysis for predicting income, and 7) Generate summary insights",
            "Complex multi-part analysis (potential timeout)"
        )
    ]
    
    # Run all test queries
    for query, test_name in test_queries:
        test_query(query, test_name)
        time.sleep(1)  # Brief pause between tests
    
    # Step 3: Get self-healing statistics
    print(f"\n{'='*60}")
    print("📊 SELF-HEALING STATISTICS")
    print(f"{'='*60}")
    
    stats = get_healing_stats()
    if stats:
        print(f"🔧 Total Healing Attempts: {stats.get('healing_attempts', 0)}")
        print(f"✅ Successful Fixes: {stats.get('successful_fixes', 0)}")
        print(f"❌ Failed Fixes: {stats.get('failed_fixes', 0)}")
        print(f"📈 Success Rate: {stats.get('success_rate', 0):.1%}")
        
        if 'recent_fixes' in stats:
            print(f"🕒 Recent Fixes: {len(stats['recent_fixes'])}")
            for fix in stats['recent_fixes'][-3:]:  # Show last 3
                print(f"   - {fix.get('error_type', 'Unknown')}: {fix.get('function', 'Unknown function')}")
    else:
        print("❌ Could not fetch self-healing statistics")
    
    print(f"\n{'='*60}")
    print("🎯 TEST COMPLETE")
    print("The enhanced self-healing system has been tested with:")
    print("✓ JSON serialization fixes")
    print("✓ Timeout handling")
    print("✓ Comprehensive error catching")
    print("✓ AI-powered automatic error fixes")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()