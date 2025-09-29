"""
Enhanced Self-Healing Test Script
Testing the improved error handling and JSON serialization fixes
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_query(question, description=""):
    """Test a single query and show detailed results"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"QUERY: {question}")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/query", 
            json={"question": question}, 
            timeout=130  # Slightly longer than server timeout
        )
        end_time = time.time()
        
        print(f"⏱️ Response time: {end_time - start_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ SUCCESS!")
                
                # Check for self-healing info
                if "auto_healing_info" in result:
                    print(f"🔧 Auto-healing attempted: {result['auto_healing_info']['attempted']}")
                    print(f"🎯 Auto-healing successful: {result['auto_healing_info']['successful']}")
                
                # Show key information without overwhelming output
                if "analysis" in result:
                    print(f"📈 Analysis available: {len(str(result['analysis']))} characters")
                if "code" in result:
                    print(f"💻 Code generated: {len(result['code'])} characters")
                if "visualizations" in result:
                    print(f"📊 Visualizations: {len(result['visualizations'])} charts")
                    
            except json.JSONDecodeError:
                print("❌ FAILED: Invalid JSON response")
                print(f"Response: {response.text[:500]}...")
                
        else:
            print("❌ FAILED!")
            try:
                error = response.json()
                print(f"Error: {error}")
                
                # Check for self-healing in error responses
                if "auto_healing_info" in error:
                    print(f"🔧 Auto-healing attempted: {error['auto_healing_info']['attempted']}")
                    print(f"🎯 Auto-healing successful: {error['auto_healing_info']['successful']}")
                    
            except:
                print(f"Raw error: {response.text}")
                
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Request took longer than 130 seconds")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

def main():
    print("🧪 Enhanced Self-Healing System Test")
    print("Testing queries that previously caused JSON serialization errors")
    
    # Test 1: Previously failing query with tuple keys
    test_query(
        "Create a detailed cross-tabulation between education level and income brackets, showing both counts and percentages",
        "Cross-tabulation with tuple keys (previously failed)"
    )
    
    # Test 2: Complex statistical analysis 
    test_query(
        "Perform advanced statistical analysis including correlation matrix, outlier detection, and distribution analysis for all numeric variables",
        "Complex stats with multiple numpy objects (previously failed)"
    )
    
    # Test 3: Complex grouping that might create tuple keys
    test_query(
        "Group by multiple categorical variables and calculate various statistical measures, creating a comprehensive summary table",
        "Multi-level grouping with complex aggregations"
    )
    
    # Test 4: Very complex query likely to timeout
    test_query(
        "Perform comprehensive data analysis including: 1) Detailed descriptive statistics for each variable, 2) Correlation analysis with heatmap, 3) Distribution plots for all variables, 4) Outlier analysis, 5) Cross-tabulations for all categorical pairs, 6) Regression analysis for predicting income, and 7) Generate summary insights",
        "Complex multi-part analysis (potential timeout)"
    )
    
    # Test 5: Query with intentional errors to trigger self-healing
    test_query(
        "Use the pandas.np module to analyze the data and create visualizations using non-existent functions",
        "Query with intentional errors to test self-healing"
    )
    
    # Get self-healing statistics
    print(f"\n{'='*60}")
    print("📊 SELF-HEALING STATISTICS")
    print(f"{'='*60}")
    
    try:
        stats_response = requests.get(f"{BASE_URL}/health/self-healing")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            for key, value in stats.items():
                print(f"{key}: {value}")
        else:
            print("❌ Could not fetch self-healing statistics")
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")

if __name__ == "__main__":
    main()