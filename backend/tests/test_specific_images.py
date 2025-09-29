#!/usr/bin/env python3
"""
Test specific image-generating questions
"""

import requests
import json
import base64

BASE_URL = "http://127.0.0.1:8000"

def test_specific_image_questions():
    print("🎨 Testing Specific Image Questions")
    print("="*50)
    
    # Upload dataset
    try:
        with open("../data/adult_dataset.csv", 'rb') as file:
            files = {'file': ('adult_dataset.csv', file, 'text/csv')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        print(f"✅ Dataset uploaded")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return
    
    # Image questions
    image_questions = [
        "Create a bar chart showing the distribution of different work classes",
        "Generate a histogram of age distribution colored by income level", 
        "Make a pie chart showing education level distribution",
        "Create a scatter plot of age vs hours worked per week",
        "Show me a heatmap of the correlation between numerical features"
    ]
    
    for i, question in enumerate(image_questions, 1):
        print(f"\n{i}. {question}")
        print("-" * 50)
        
        payload = {"question": question}
        
        try:
            response = requests.post(f"{BASE_URL}/api/query", json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                image_data = data.get('image')
                if image_data:
                    print(f"✅ Image: {len(image_data)} chars base64")
                    
                    # Save image
                    try:
                        decoded = base64.b64decode(image_data)
                        with open(f"chart_{i}.png", "wb") as f:
                            f.write(decoded)
                        print(f"💾 Saved: chart_{i}.png")
                    except Exception as e:
                        print(f"❌ Save failed: {e}")
                else:
                    print("❌ No image returned")
                    
                print(f"📝 Answer: {data.get('explanation', 'No explanation')[:80]}...")
                
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_specific_image_questions()