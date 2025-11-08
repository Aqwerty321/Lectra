"""Minimal Ollama client for streaming text generation - refactored as library."""

import requests
import json
from typing import Optional, Dict, List


def generate_tagged(
    text: str, 
    system: str, 
    model: str = "llama3.1:latest",
    base_url: str = "http://127.0.0.1:11434"
) -> str:
    """
    Call local Ollama API to generate tagged text.
    
    Args:
        text: Raw input text to be tagged
        system: System prompt for the LLM
        model: Ollama model name
        base_url: Ollama server URL
        
    Returns:
        Tagged text string
        
    Raises:
        requests.exceptions.RequestException: If Ollama is not reachable
    """
    url = f"{base_url}/api/generate"
    
    payload = {
        "model": model,
        "prompt": f"<INPUT>\n{text}\n</INPUT>",
        "system": system,
        "options": {
            "temperature": 0.1,
            "top_p": 0.8,
            "repeat_penalty": 1.05,
            "num_ctx": 4096
        },
        "stream": True
    }
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=120)
        response.raise_for_status()
        
        result = []
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode('utf-8'))
                if 'response' in chunk:
                    result.append(chunk['response'])
                if chunk.get('done', False):
                    break
        
        return ''.join(result).strip()
        
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Cannot connect to Ollama at {base_url}. "
            "Please ensure Ollama is running and llama3.1:latest is pulled."
        )
    except requests.exceptions.Timeout:
        raise TimeoutError("Ollama request timed out after 120 seconds")
    except Exception as e:
        raise RuntimeError(f"Ollama API error: {str(e)}")


def generate_animation_steps(
    slide_content: str,
    slide_title: str,
    speaker_notes: str,
    model: str = "llama3.2:3b",
    base_url: str = "http://127.0.0.1:11434"
) -> Dict:
    """
    Generate interactive animation steps for a lecture slide using Llama.
    
    Args:
        slide_content: Bullet points or main content of the slide
        slide_title: Title of the slide
        speaker_notes: Detailed speaker notes/narration
        model: Ollama model name (using smaller model for speed)
        base_url: Ollama server URL
        
    Returns:
        Dict with animation steps:
        {
            "steps": [
                {
                    "id": 1,
                    "text": "Introduction to photosynthesis",
                    "action": "fadeIn",
                    "duration": 2.0,
                    "hint": "This is where plants make their food!"
                },
                ...
            ]
        }
    """
    system_prompt = """You are an expert educational animator. Given a lecture slide, break it down into 3-6 interactive animation steps that will engage students.

Each step should:
- Reveal ONE key concept at a time
- Use appropriate animations (fadeIn, slideIn, highlight, pulse, draw)
- Include a helpful hint for students
- Have realistic duration (1-4 seconds)

Return ONLY valid JSON in this format:
{
  "steps": [
    {
      "id": 1,
      "text": "Key point or concept to reveal",
      "action": "fadeIn",
      "duration": 2.0,
      "hint": "Helpful hint or explanation for students",
      "element": "text"
    }
  ]
}

Available actions:
- fadeIn: Gradually appear
- slideIn: Slide from side
- highlight: Color emphasis
- pulse: Attention grab
- draw: Stroke animation (for diagrams)
- zoom: Scale up
- typewriter: Character-by-character reveal

Available elements:
- text: Text content
- image: Visual/diagram
- bullet: Individual bullet point
- title: Section header"""

    prompt = f"""Slide Title: {slide_title}

Content:
{slide_content}

Speaker Notes:
{speaker_notes}

Create 3-6 animation steps that will make this slide engaging and interactive for students."""

    url = f"{base_url}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "options": {
            "temperature": 0.4,
            "top_p": 0.9,
            "num_ctx": 2048
        },
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        raw_text = result.get('response', '').strip()
        
        # Try to extract JSON from the response
        # Handle cases where LLM adds explanation before/after JSON
        json_start = raw_text.find('{')
        json_end = raw_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_text = raw_text[json_start:json_end]
            animation_data = json.loads(json_text)
            
            # Validate structure
            if 'steps' not in animation_data:
                raise ValueError("Missing 'steps' key in animation data")
            
            # Ensure each step has required fields
            for step in animation_data['steps']:
                if 'id' not in step:
                    step['id'] = animation_data['steps'].index(step) + 1
                if 'action' not in step:
                    step['action'] = 'fadeIn'
                if 'duration' not in step:
                    step['duration'] = 2.0
                if 'element' not in step:
                    step['element'] = 'text'
                if 'hint' not in step:
                    step['hint'] = "Pay attention to this key concept!"
            
            return animation_data
        else:
            # Fallback: create simple animation steps
            print("⚠️ Could not parse animation JSON, using fallback")
            return create_fallback_animation(slide_content, slide_title)
            
    except Exception as e:
        print(f"⚠️ Animation generation failed: {e}, using fallback")
        return create_fallback_animation(slide_content, slide_title)


def create_fallback_animation(slide_content: str, slide_title: str) -> Dict:
    """Create basic fallback animation when AI generation fails."""
    # Split content into lines
    lines = [line.strip() for line in slide_content.split('\n') if line.strip()]
    
    steps = []
    steps.append({
        "id": 1,
        "text": slide_title,
        "action": "fadeIn",
        "duration": 1.5,
        "hint": "This is the main topic of this slide",
        "element": "title"
    })
    
    for idx, line in enumerate(lines[:5], start=2):  # Max 5 content lines
        steps.append({
            "id": idx,
            "text": line,
            "action": "slideIn",
            "duration": 2.0,
            "hint": f"Key point: {line[:50]}...",
            "element": "bullet"
        })
    
    return {"steps": steps}
