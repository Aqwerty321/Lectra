"""Direct test of Ollama quiz generation."""

import requests
import json

# Test Ollama directly
url = "http://localhost:11434/api/generate"

prompt = """You are an expert educational quiz generator. Create 3 multiple-choice questions based on this lecture content.

LECTURE TOPICS:
- Introduction
- Current State of AI in Healthcare
- Benefits of AI in Healthcare

CONTENT:
Slide 1: Introduction
Welcome to the presentation on Unlocking the Potential of AI in Healthcare Systems

Slide 2: Current State of AI in Healthcare
AI-powered diagnostic tools are being integrated into electronic health records (EHRs) to enhance patient data analysis and improve diagnosis accuracy.
Machine learning algorithms are being applied to medical imaging, enabling doctors to detect diseases at an early stage and reducing the need for invasive procedures.

Slide 3: Benefits of AI in Healthcare
Improved diagnostic accuracy through AI-powered image analysis, reducing misdiagnoses and enhancing patient outcomes
Personalized medicine made possible with AI-driven data analysis, tailoring treatment plans to individual patients' needs and medical histories

REQUIREMENTS:
- Difficulty: medium (Test understanding and application of concepts)
- 3 questions total
- Each question has 4 options (A, B, C, D)
- Only ONE correct answer per question
- Include detailed explanations for why each option is correct/incorrect
- Questions should test understanding, not just memorization

FORMAT YOUR RESPONSE EXACTLY AS:
```json
[
  {
    "question": "What is the main concept discussed in slide 2?",
    "options": {
      "A": "Option text here",
      "B": "Option text here", 
      "C": "Option text here",
      "D": "Option text here"
    },
    "correct_answer": "B",
    "explanation": "B is correct because... A is wrong because... C is wrong because... D is wrong because...",
    "hint": "Think about the key relationship mentioned in the slides",
    "difficulty": "medium",
    "slide_reference": 2
  }
]
```

Generate the MCQs now:"""

print("Sending request to Ollama...")
print(f"Prompt length: {len(prompt)} chars\n")

try:
    response = requests.post(
        url,
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        },
        timeout=120
    )
    
    print(f"Status: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        response_text = result.get("response", "")
        
        print("=" * 80)
        print("OLLAMA RESPONSE:")
        print("=" * 80)
        print(response_text)
        print("=" * 80)
        
        # Try to parse JSON
        print("\nAttempting to parse JSON...")
        
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text.strip()
        
        print(f"\nExtracted JSON text ({len(json_text)} chars):")
        print("-" * 80)
        print(json_text[:500])
        print("-" * 80)
        
        try:
            mcqs = json.loads(json_text)
            print(f"\n✓ Successfully parsed {len(mcqs)} questions!")
            for i, q in enumerate(mcqs, 1):
                print(f"\nQuestion {i}: {q.get('question', 'N/A')[:80]}...")
        except json.JSONDecodeError as e:
            print(f"\n✗ JSON parsing failed: {e}")
            
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
