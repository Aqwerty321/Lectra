"""Quiz generation service using Ollama for interactive study mode."""

import requests
import json
from typing import List, Dict, Any, Optional
from pathlib import Path


class QuizGenerator:
    """Generates MCQs from slide content using Ollama."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
    
    def generate_mcqs(
        self,
        slide_content: str,
        slide_titles: List[str],
        num_questions: int = 5,
        difficulty: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple choice questions from slide content.
        
        Args:
            slide_content: Combined text content from slides
            slide_titles: List of slide titles for context
            num_questions: Number of MCQs to generate
            difficulty: easy, medium, or hard
            
        Returns:
            List of MCQ dictionaries with question, options, correct_answer, explanation
        """
        
        # Craft prompt for Ollama
        prompt = self._build_quiz_prompt(slide_content, slide_titles, num_questions, difficulty)
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
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
            
            if response.status_code == 200:
                result = response.json()
                mcqs = self._parse_mcqs(result.get("response", ""))
                return mcqs[:num_questions]  # Ensure we return exactly num_questions
            else:
                print(f"Ollama API error: {response.status_code}")
                return self._generate_fallback_mcqs(slide_titles, num_questions)
                
        except Exception as e:
            print(f"Quiz generation error: {e}")
            return self._generate_fallback_mcqs(slide_titles, num_questions)
    
    def _build_quiz_prompt(
        self,
        content: str,
        titles: List[str],
        num_questions: int,
        difficulty: str
    ) -> str:
        """Build the prompt for Ollama to generate MCQs."""
        
        difficulty_guidelines = {
            "easy": "Focus on basic recall and simple concepts",
            "medium": "Test understanding and application of concepts",
            "hard": "Require analysis, synthesis, and critical thinking"
        }
        
        prompt = f"""You are an expert educational quiz generator. Create {num_questions} multiple-choice questions based on this lecture content.

LECTURE TOPICS:
{chr(10).join(f"- {title}" for title in titles)}

CONTENT:
{content[:3000]}  

REQUIREMENTS:
- Difficulty: {difficulty} ({difficulty_guidelines.get(difficulty, '')})
- {num_questions} questions total
- Each question has 4 options (A, B, C, D)
- Only ONE correct answer per question
- Include detailed explanations for why each option is correct/incorrect
- Questions should test understanding, not just memorization

FORMAT YOUR RESPONSE EXACTLY AS:
```json
[
  {{
    "question": "What is the main concept discussed in slide 2?",
    "options": {{
      "A": "Option text here",
      "B": "Option text here", 
      "C": "Option text here",
      "D": "Option text here"
    }},
    "correct_answer": "B",
    "explanation": "B is correct because... A is wrong because... C is wrong because... D is wrong because...",
    "hint": "Think about the key relationship mentioned in the slides",
    "difficulty": "{difficulty}",
    "slide_reference": 2
  }}
]
```

Generate the MCQs now:"""
        
        return prompt
    
    def _parse_mcqs(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse Ollama's response into structured MCQ format."""
        
        try:
            # Extract JSON from markdown code blocks if present
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
            
            # Parse JSON
            mcqs = json.loads(json_text)
            
            # Validate structure
            validated_mcqs = []
            for mcq in mcqs:
                if self._validate_mcq(mcq):
                    validated_mcqs.append(mcq)
            
            return validated_mcqs
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text[:500]}")
            return []
    
    def _validate_mcq(self, mcq: Dict[str, Any]) -> bool:
        """Validate MCQ structure."""
        required_fields = ["question", "options", "correct_answer", "explanation"]
        
        if not all(field in mcq for field in required_fields):
            return False
        
        if not isinstance(mcq["options"], dict):
            return False
        
        if len(mcq["options"]) != 4:
            return False
        
        if mcq["correct_answer"] not in ["A", "B", "C", "D"]:
            return False
        
        return True
    
    def _generate_fallback_mcqs(self, titles: List[str], num_questions: int) -> List[Dict[str, Any]]:
        """Generate simple fallback MCQs if Ollama fails."""
        
        fallback_mcqs = []
        for i in range(min(num_questions, len(titles))):
            title = titles[i]
            fallback_mcqs.append({
                "question": f"What is the main topic of slide '{title}'?",
                "options": {
                    "A": title,
                    "B": "None of the above",
                    "C": "All of the above",
                    "D": "Not covered in this presentation"
                },
                "correct_answer": "A",
                "explanation": f"The correct answer is A. The slide '{title}' directly addresses this topic.",
                "hint": "Look at the slide title",
                "difficulty": "easy",
                "slide_reference": i + 1
            })
        
        return fallback_mcqs
    
    def generate_quiz_checkpoints(
        self,
        total_slides: int,
        checkpoint_interval: int = 3
    ) -> List[int]:
        """
        Determine which slides should trigger quizzes.
        
        Args:
            total_slides: Total number of slides in presentation
            checkpoint_interval: Number of slides between quizzes
            
        Returns:
            List of slide numbers (0-indexed) that should trigger quizzes
        """
        checkpoints = []
        current = checkpoint_interval
        
        while current < total_slides:
            checkpoints.append(current)
            current += checkpoint_interval
        
        # Always add a final checkpoint if not already present
        if total_slides > checkpoint_interval and (total_slides - 1) not in checkpoints:
            checkpoints.append(total_slides - 1)
        
        return checkpoints


def generate_quiz_for_slides(
    project_path: Path,
    slide_range: tuple[int, int],
    num_questions: int = 5,
    difficulty: str = "medium"
) -> Dict[str, Any]:
    """
    Generate a quiz for a specific range of slides.
    
    Args:
        project_path: Path to project directory
        slide_range: (start_slide, end_slide) tuple (0-indexed)
        num_questions: Number of MCQs to generate
        difficulty: Quiz difficulty level
        
    Returns:
        Dictionary with quiz data and metadata
    """
    
    # Load presentation metadata
    metadata_path = project_path / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Extract slide content from range
    slides = metadata.get("slides", [])
    start, end = slide_range
    
    if start < 0 or end >= len(slides):
        raise ValueError(f"Invalid slide range: {slide_range} (total slides: {len(slides)})")
    
    target_slides = slides[start:end + 1]
    
    # Combine content
    slide_titles = [slide.get("title", f"Slide {i+start+1}") for i, slide in enumerate(target_slides)]
    slide_content = "\n\n".join([
        f"Slide {i+start+1}: {slide.get('title', '')}\n{slide.get('content', '')}"
        for i, slide in enumerate(target_slides)
    ])
    
    # Generate quiz
    generator = QuizGenerator()
    mcqs = generator.generate_mcqs(slide_content, slide_titles, num_questions, difficulty)
    
    return {
        "slide_range": slide_range,
        "slide_titles": slide_titles,
        "num_questions": len(mcqs),
        "difficulty": difficulty,
        "questions": mcqs,
        "checkpoint_id": f"quiz_{start}_{end}"
    }
