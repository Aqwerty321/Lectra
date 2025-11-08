"""Test the full quiz pipeline."""

import sys
sys.path.insert(0, 'c:\\edgettstest\\LECTRA\\sidecar')

from pathlib import Path
from app.services.quiz_generator import generate_quiz_for_slides

project_path = Path(r"C:\Users") / Path.home().name / "Lectures" / "my-lecture"

print(f"Testing quiz generation for: {project_path}")
print(f"Project exists: {project_path.exists()}\n")

try:
    quiz_data = generate_quiz_for_slides(
        project_path=project_path,
        slide_range=(0, 2),
        num_questions=3,
        difficulty="medium"
    )
    
    print("\n" + "=" * 80)
    print("FINAL QUIZ DATA:")
    print("=" * 80)
    print(f"Questions count: {len(quiz_data.get('questions', []))}")
    print(f"Checkpoint ID: {quiz_data.get('checkpoint_id')}")
    
    if quiz_data.get('questions'):
        print(f"\nFirst question:")
        q = quiz_data['questions'][0]
        print(f"  Q: {q.get('question')}")
        print(f"  Options: {list(q.get('options', {}).keys())}")
        print(f"  Answer: {q.get('correct_answer')}")
    else:
        print("\n⚠️ NO QUESTIONS IN QUIZ DATA!")
        print("Full quiz data:")
        import json
        print(json.dumps(quiz_data, indent=2))
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
