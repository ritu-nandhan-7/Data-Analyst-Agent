#!/usr/bin/env python3
"""
Test script to check available Gemini models
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Available Gemini models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")

# Test a simple generation with different model names
models_to_test = [
    'gemini-pro',
    'gemini-1.5-pro', 
    'gemini-2.5-flash',
    'models/gemini-pro',
    'models/gemini-1.5-pro'
]

for model_name in models_to_test:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hello")
        print(f"✅ {model_name}: {response.text[:50]}...")
        break
    except Exception as e:
        print(f"❌ {model_name}: {e}")