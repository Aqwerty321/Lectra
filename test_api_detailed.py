"""Test HTTP API with detailed response inspection."""

import requests
import json

url = "http://127.0.0.1:8765/generate_quiz"

payload = {
    "project": "my-lecture",
    "slide_start": 0,
    "slide_end": 2,
    "num_questions": 3,
    "difficulty": "medium"
}

print("Testing HTTP API...")
print(f"Request: {json.dumps(payload, indent=2)}\n")

try:
    response = requests.post(url, json=payload, timeout=120)
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}\n")
    
    if response.status_code == 200:
        quiz_data = response.json()
        
        print("=" * 80)
        print("FULL RESPONSE:")
        print("=" * 80)
        print(json.dumps(quiz_data, indent=2))
        print("=" * 80)
        
        print(f"\nQuestions count: {len(quiz_data.get('questions', []))}")
        print(f"Questions field type: {type(quiz_data.get('questions'))}")
        print(f"Questions field value: {quiz_data.get('questions')}")
        
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
