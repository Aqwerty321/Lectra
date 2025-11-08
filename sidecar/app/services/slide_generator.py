"""AI-powered presentation slide content generator using Ollama with DuckDuckGo web context."""

import json
import requests
from typing import Dict, List, Optional
from pathlib import Path

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    print("⚠️ duckduckgo_search not available - presentations will use only LLM knowledge")


def get_current_context(topic: str, max_results: int = 5) -> str:
    """
    Fetch current web context about the topic using DuckDuckGo.
    
    Args:
        topic: The presentation topic
        max_results: Number of search results to fetch
        
    Returns:
        Formatted string with current information
    """
    if not DDGS_AVAILABLE:
        return ""
    
    try:
        print(f"🌐 Searching web for current context on: {topic}")
        ddgs = DDGS()
        results = ddgs.text(topic, max_results=max_results)
        
        context_parts = []
        for idx, result in enumerate(results, 1):
            title = result.get('title', '')
            body = result.get('body', '')
            context_parts.append(f"{idx}. {title}\n{body}")
        
        if context_parts:
            context = "\n\n".join(context_parts)
            print(f"✓ Found {len(context_parts)} current sources")
            return f"\n\nCURRENT WEB CONTEXT:\n{context}\n"
        else:
            print("⚠️ No web results found")
            return ""
            
    except Exception as e:
        print(f"⚠️ DuckDuckGo search failed: {e}")
        return ""


OUTLINE_SYSTEM_PROMPT = """You are a professional presentation outline creator. Given a topic, generate a comprehensive presentation outline with 8-12 slides.

Return ONLY valid JSON in this exact format:
{
  "title": "Presentation Title",
  "slides": [
    {"title": "Slide Title", "type": "title"},
    {"title": "Introduction", "type": "content"},
    {"title": "Main Point 1", "type": "content"},
    ...
  ]
}

Rules:
- First slide must be type "title" with the main presentation title
- All other slides are type "content"
- Use clear, professional slide titles
- 8-12 slides total
- No markdown, no extra text, ONLY JSON"""


CONTENT_SYSTEM_PROMPT = """You are a professional presentation content writer. Given a slide title and presentation context, generate detailed bullet points for that slide.

Return ONLY valid JSON in this exact format:
{
  "points": [
    "First key point with clear explanation",
    "Second important point with details",
    "Third critical concept",
    ...
  ],
  "speaker_notes": "Detailed speaker notes explaining the slide content, providing context, examples, and talking points for the presenter. This should be 2-3 sentences."
}

Rules:
- 3-5 bullet points per slide
- Each point should be clear and actionable
- Speaker notes should be conversational and detailed
- No markdown formatting
- ONLY return JSON"""


def generate_outline(topic: str, model: str = "llama3.1", ollama_url: str = "http://localhost:11434") -> Dict:
    """
    Generate presentation outline from topic using Ollama with current web context.
    
    Args:
        topic: The presentation topic
        model: Ollama model name
        ollama_url: Ollama API URL
        
    Returns:
        Dict with 'title' and 'slides' list
    """
    # Fetch current web context
    web_context = get_current_context(topic)
    
    prompt = f"Create a professional presentation outline for the topic: {topic}{web_context}"
    
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": OUTLINE_SYSTEM_PROMPT,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            },
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        outline_text = result.get("response", "")
        
        # Extract JSON from response (LLM might add extra text)
        # Look for the first '{' and last '}' to extract just the JSON
        start_idx = outline_text.find('{')
        end_idx = outline_text.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            raise ValueError(f"No JSON object found in response: {outline_text}")
        
        json_text = outline_text[start_idx:end_idx + 1]
        
        # Parse JSON from response
        outline = json.loads(json_text.strip())
        
        return outline
        
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to connect to Ollama: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse outline JSON: {e}\nExtracted: {json_text if 'json_text' in locals() else outline_text}")


def generate_slide_content(
    slide_title: str,
    presentation_context: str,
    model: str = "llama3.1",
    ollama_url: str = "http://localhost:11434"
) -> Dict:
    """
    Generate content for a specific slide.
    
    Args:
        slide_title: Title of the slide
        presentation_context: Context about the presentation topic
        model: Ollama model name
        ollama_url: Ollama API URL
        
    Returns:
        Dict with 'points' and 'speaker_notes'
    """
    prompt = f"""Presentation Topic: {presentation_context}
Slide Title: {slide_title}

Generate detailed content for this slide."""
    
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": CONTENT_SYSTEM_PROMPT,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9
                }
            },
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        content_text = result.get("response", "")
        
        # Extract JSON from response (LLM might add extra text)
        start_idx = content_text.find('{')
        end_idx = content_text.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            raise ValueError(f"No JSON object found in response: {content_text}")
        
        json_text = content_text[start_idx:end_idx + 1]
        
        # Parse JSON from response
        content = json.loads(json_text.strip())
        
        return content
        
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to connect to Ollama: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse content JSON: {e}\nExtracted: {json_text if 'json_text' in locals() else content_text}")


def generate_full_script(
    outline: Dict,
    model: str = "llama3.1",
    ollama_url: str = "http://localhost:11434"
) -> Dict:
    """
    Generate content for all slides in the outline.
    
    Args:
        outline: Presentation outline with title and slides
        model: Ollama model name
        ollama_url: Ollama API URL
        
    Returns:
        Complete presentation dict with all slide content
    """
    presentation = {
        "title": outline["title"],
        "slides": []
    }
    
    context = outline["title"]
    
    for slide in outline["slides"]:
        if slide["type"] == "title":
            # Title slide doesn't need bullet points
            presentation["slides"].append({
                "title": slide["title"],
                "type": "title",
                "points": [],
                "speaker_notes": f"Welcome to the presentation on {outline['title']}"
            })
        else:
            # Generate content for content slides
            content = generate_slide_content(slide["title"], context, model, ollama_url)
            presentation["slides"].append({
                "title": slide["title"],
                "type": "content",
                "points": content["points"],
                "speaker_notes": content["speaker_notes"]
            })
    
    return presentation


def save_outline(outline: Dict, output_path: Path):
    """Save outline to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(outline, indent=2, ensure_ascii=False), encoding='utf-8')


def save_script(script: Dict, output_path: Path):
    """Save full script to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(script, indent=2, ensure_ascii=False), encoding='utf-8')
