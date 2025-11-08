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
        difficulty: str = "medium",
        lang: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple choice questions from slide content.
        
        Args:
            slide_content: Combined text content from slides
            slide_titles: List of slide titles for context
            num_questions: Number of MCQs to generate
            difficulty: easy, medium, or hard
            lang: Language code (en or hi)
            
        Returns:
            List of MCQ dictionaries with question, options, correct_answer, explanation
        """
        
        print(f"\n--- QuizGenerator.generate_mcqs ---")
        print(f"Titles: {slide_titles}")
        print(f"Num questions: {num_questions}")
        print(f"Difficulty: {difficulty}")
        print(f"Language: {lang}")
        
        # Craft prompt for Ollama
        prompt = self._build_quiz_prompt(slide_content, slide_titles, num_questions, difficulty, lang)
        
        print(f"Prompt length: {len(prompt)} chars")
        print(f"Calling Ollama at {self.ollama_url}...")
        
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
            
            print(f"Ollama response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                print(f"Ollama response length: {len(response_text)} chars")
                print(f"Response preview: {response_text[:200]}...")
                
                mcqs = self._parse_mcqs(response_text)
                print(f"Parsed {len(mcqs)} MCQs from response")
                
                final_mcqs = mcqs[:num_questions]
                print(f"Returning {len(final_mcqs)} MCQs")
                return final_mcqs
            else:
                print(f"✗ Ollama API error: {response.status_code}")
                print(f"Response: {response.text}")
                print("Falling back to simple MCQs")
                return self._generate_fallback_mcqs(slide_titles, num_questions)
                
        except Exception as e:
            print(f"✗ Quiz generation exception: {e}")
            import traceback
            traceback.print_exc()
            print("Falling back to simple MCQs")
            return self._generate_fallback_mcqs(slide_titles, num_questions)
    
    def _build_quiz_prompt(
        self,
        content: str,
        titles: List[str],
        num_questions: int,
        difficulty: str,
        lang: str = "en"
    ) -> str:
        """Build the prompt for Ollama to generate MCQs."""
        
        difficulty_guidelines = {
            "easy": "Focus on basic recall and simple concepts",
            "medium": "Test understanding and application of concepts",
            "hard": "Require analysis, synthesis, and critical thinking"
        }
        
        # Language-specific instructions
        language_instruction = ""
        if lang == "hi":
            language_instruction = "\n\nIMPORTANT: Generate ALL quiz questions, options, explanations, and hints in HINDI language (Devanagari script). The questions should be natural Hindi, not English transliterated to Devanagari."
        
        prompt = f"""You are an expert educational quiz generator. Create {num_questions} multiple-choice questions based on this lecture content.
{language_instruction}

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
{"- ALL text must be in HINDI (Devanagari script)" if lang == "hi" else ""}

CRITICAL: Respond ONLY with the JSON array. Do not include any introductory text, explanations, or markdown code blocks.

FORMAT YOUR RESPONSE EXACTLY AS (JUST THE JSON ARRAY, NOTHING ELSE):
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

Generate ONLY the JSON array now (no other text):"""
        
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
                # No code blocks - try to find JSON array directly
                # Look for the first [ and last ]
                json_start = response_text.find('[')
                json_end = response_text.rfind(']')
                
                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_text = response_text[json_start:json_end + 1].strip()
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
        
        print(f"\n⚠️ Generating {num_questions} fallback MCQs...")
        
        fallback_mcqs = []
        for i in range(min(num_questions, len(titles))):
            title = titles[i]
            fallback_mcqs.append({
                "question": f"What is the main topic covered in the section titled '{title}'?",
                "options": {
                    "A": title,
                    "B": "None of the above",
                    "C": "All of the above",
                    "D": "Not covered in this presentation"
                },
                "correct_answer": "A",
                "explanation": f"The correct answer is A. The section '{title}' directly addresses this topic as indicated by its title.",
                "hint": "Look at the section title for the answer",
                "difficulty": "easy",
                "slide_reference": i + 1
            })
        
        # If we need more questions than titles, add generic ones
        while len(fallback_mcqs) < num_questions:
            fallback_mcqs.append({
                "question": f"This is a placeholder question {len(fallback_mcqs) + 1}. What was covered in this lecture?",
                "options": {
                    "A": "Important concepts",
                    "B": "Key principles",
                    "C": "Core ideas",
                    "D": "All of the above"
                },
                "correct_answer": "D",
                "explanation": "This is a fallback question. All options are correct as the lecture covered important concepts, key principles, and core ideas.",
                "hint": "All options are valid",
                "difficulty": "easy",
                "slide_reference": 1
            })
        
        print(f"✓ Generated {len(fallback_mcqs)} fallback MCQs")
        return fallback_mcqs
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
    
    print(f"\n--- Generate Quiz For Slides ---")
    print(f"Project: {project_path}")
    print(f"Slide range: {slide_range}")
    
    # Load presentation metadata
    metadata_path = project_path / "metadata.json"
    if not metadata_path.exists():
        print(f"✗ Metadata not found: {metadata_path}")
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")
    
    print(f"✓ Loading metadata from {metadata_path}")
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Detect language from metadata
    lang = metadata.get("lang", "en")
    print(f"Language: {lang}")
    
    # Extract slide content from range
    slides = metadata.get("slides", [])
    start, end = slide_range
    
    print(f"Total slides in metadata: {len(slides)}")
    print(f"Requested range: {start} to {end}")
    
    if start < 0 or end >= len(slides):
        print(f"✗ Invalid slide range: {slide_range} (total slides: {len(slides)})")
        raise ValueError(f"Invalid slide range: {slide_range} (total slides: {len(slides)})")
    
    target_slides = slides[start:end + 1]
    print(f"Extracted {len(target_slides)} slides for quiz")
    
    # Combine content
    slide_titles = [slide.get("title", f"Slide {i+start+1}") for i, slide in enumerate(target_slides)]
    slide_content = "\n\n".join([
        f"Slide {i+start+1}: {slide.get('title', '')}\n{slide.get('content', '')}"
        for i, slide in enumerate(target_slides)
    ])
    
    print(f"Slide titles: {slide_titles}")
    print(f"Content length: {len(slide_content)} chars")
    
    # Generate quiz with language support
    print(f"Calling QuizGenerator with {num_questions} questions, difficulty: {difficulty}")
    generator = QuizGenerator()
    mcqs = generator.generate_mcqs(slide_content, slide_titles, num_questions, difficulty, lang)
    
    print(f"✓ Generated {len(mcqs)} MCQs")
    
    quiz_data = {
        "slide_range": slide_range,
        "slide_titles": slide_titles,
        "num_questions": len(mcqs),
        "difficulty": difficulty,
        "lang": lang,
        "questions": mcqs,
        "checkpoint_id": f"quiz_{start}_{end}"
    }
    
    print(f"--- Quiz Generation Complete ---\n")
    return quiz_data
