#!/usr/bin/env python3
"""
Test image generation and base64 return
"""

import requests
import json
import base64
import os

BASE_URL = "http://127.0.0.1:8000"

def test_image_generation():
    print("🎨 Testing Image Generation and Base64 Return")
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
    
    # Test a question that should generate an image
    questions_with_images = [
        "Which occupation has the highest number of individuals with an income greater than 50K? Create a bar chart.",
        "Create a visualization showing the distribution of age groups by income level",
        "Generate a heatmap showing the relationship between education and income",
        "Create a pie chart showing the distribution of work classes",
        "Show me a histogram of hours worked per week by gender"
    ]
    
    for i, question in enumerate(questions_with_images, 1):
        print(f"\n{'='*60}")
        print(f"Image Test {i}: {question}")
        print('='*60)
        
        payload = {"question": question}
        
        try:
            response = requests.post(f"{BASE_URL}/api/query", json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ SUCCESS")
                print(f"💡 Explanation: {data.get('explanation', 'No explanation')[:100]}...")
                
                # Check image data
                image_data = data.get('image')
                if image_data:
                    print(f"🎨 Image generated: YES")
                    print(f"📏 Base64 length: {len(image_data)} characters")
                    
                    # Validate base64
                    try:
                        decoded = base64.b64decode(image_data)
                        print(f"✅ Valid base64: YES ({len(decoded)} bytes)")
                        
                        # Save image for verification
                        with open(f"test_image_{i}.png", "wb") as f:
                            f.write(decoded)
                        print(f"💾 Saved as: test_image_{i}.png")
                        
                    except Exception as e:
                        print(f"❌ Invalid base64: {e}")
                        
                else:
                    print(f"❌ No image data returned!")
                    print(f"🔍 Response keys: {list(data.keys())}")
                    print(f"🔍 Full response: {json.dumps(data, indent=2)[:500]}...")
                
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
        
        # Only test first question for now
        break
    
    print(f"\n🎉 Image test completed!")

if __name__ == "__main__":
    test_image_generation()