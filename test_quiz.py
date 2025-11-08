"""Test script to verify quiz generation works."""

import requests
import json

# Test quiz generation endpoint
url = "http://127.0.0.1:8765/generate_quiz"

# Replace 'my-lecture' with actual project name
payload = {
    "project": "my-lecture",
    "slide_start": 0,
    "slide_end": 2,
    "num_questions": 3,
    "difficulty": "medium"
}

print("Testing quiz generation...")
print(f"Request: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, timeout=30)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        quiz_data = response.json()
        print("\n✓ Quiz Generated Successfully!")
        print(f"Questions: {len(quiz_data.get('questions', []))}")
        print(f"Difficulty: {quiz_data.get('difficulty')}")
        print(f"Checkpoint ID: {quiz_data.get('checkpoint_id')}")
        
        # Print first question
        if quiz_data.get('questions'):
            q1 = quiz_data['questions'][0]
            print(f"\nFirst Question:")
            print(f"  Q: {q1.get('question')}")
            print(f"  Options: {list(q1.get('options', {}).keys())}")
            print(f"  Answer: {q1.get('correct_answer')}")
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"\n✗ Exception: {e}")
