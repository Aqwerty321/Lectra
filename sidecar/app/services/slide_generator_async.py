"""Async optimized slide generation with parallel LLM calls."""

import asyncio
import json
from typing import Dict, List
from pathlib import Path
import aiohttp
from .slide_generator import OUTLINE_SYSTEM_PROMPT, CONTENT_SYSTEM_PROMPT, get_current_context


class AsyncSlideGenerator:
    """Async slide generator with connection pooling and parallel processing."""
    
    def __init__(self, model: str = "llama3.1", ollama_url: str = "http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
        self._session = None
    
    async def __aenter__(self):
        """Create shared aiohttp session."""
        timeout = aiohttp.ClientTimeout(total=120)
        self._session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close shared session."""
        if self._session:
            await self._session.close()
    
    async def generate_outline(self, topic: str) -> Dict:
        """Generate presentation outline asynchronously."""
        web_context = get_current_context(topic)
        prompt = f"Create a professional presentation outline for the topic: {topic}{web_context}"
        
        try:
            async with self._session.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": OUTLINE_SYSTEM_PROMPT,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9
                    }
                }
            ) as response:
                response.raise_for_status()
                result = await response.json()
                outline_text = result.get("response", "")
                
                # Extract JSON
                start_idx = outline_text.find('{')
                end_idx = outline_text.rfind('}')
                
                if start_idx == -1 or end_idx == -1:
                    raise ValueError(f"No JSON object found in response")
                
                json_text = outline_text[start_idx:end_idx + 1]
                outline = json.loads(json_text.strip())
                
                return outline
        
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")
    
    async def generate_slide_content(
        self,
        slide_title: str,
        context: str
    ) -> Dict:
        """Generate content for a single slide asynchronously."""
        prompt = f"""Presentation Context: {context}

Slide Title: {slide_title}

Create comprehensive content for this slide."""
        
        try:
            async with self._session.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": CONTENT_SYSTEM_PROMPT,
                    "stream": False,
                    "options": {
                        "temperature": 0.5,
                        "top_p": 0.9
                    }
                }
            ) as response:
                response.raise_for_status()
                result = await response.json()
                content_text = result.get("response", "")
                
                # Extract JSON
                start_idx = content_text.find('{')
                end_idx = content_text.rfind('}')
                
                if start_idx == -1 or end_idx == -1:
                    raise ValueError(f"No JSON object found in response")
                
                json_text = content_text[start_idx:end_idx + 1]
                content = json.loads(json_text.strip())
                
                return content
        
        except (aiohttp.ClientError, json.JSONDecodeError) as e:
            print(f"⚠️ Content generation failed for '{slide_title}': {e}")
            return {
                "points": [
                    "Content generation in progress",
                    "Please check back later"
                ],
                "speaker_notes": f"This slide covers {slide_title}."
            }
    
    async def generate_full_script(self, outline: Dict) -> Dict:
        """Generate content for all slides in parallel."""
        presentation = {
            "title": outline["title"],
            "slides": []
        }
        
        context = outline["title"]
        tasks = []
        slide_metadata = []
        
        # Create tasks for parallel generation
        for slide in outline["slides"]:
            if slide["type"] == "title":
                # Add title slide immediately (no LLM call needed)
                presentation["slides"].append({
                    "title": slide["title"],
                    "type": "title",
                    "points": [],
                    "speaker_notes": f"Welcome to the presentation on {outline['title']}"
                })
            else:
                # Queue content generation task
                task = self.generate_slide_content(slide["title"], context)
                tasks.append(task)
                slide_metadata.append({
                    "title": slide["title"],
                    "type": "content"
                })
        
        # Execute all content generation in parallel
        print(f"🚀 Generating content for {len(tasks)} slides in parallel...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for metadata, result in zip(slide_metadata, results):
            if isinstance(result, Exception):
                print(f"⚠️ Failed to generate content for '{metadata['title']}': {result}")
                content = {
                    "points": ["Content generation failed"],
                    "speaker_notes": f"This slide covers {metadata['title']}."
                }
            else:
                content = result
            
            presentation["slides"].append({
                "title": metadata["title"],
                "type": metadata["type"],
                "points": content["points"],
                "speaker_notes": content["speaker_notes"]
            })
        
        return presentation
    
    async def generate_slides_streaming(self, outline: Dict):
        """
        Generate slides one by one (streaming) for immediate downstream processing.
        
        Yields each slide as soon as it's generated, allowing parallel TTS/image tasks
        to start immediately instead of waiting for all slides.
        
        Yields:
            Dict: Slide data with title, type, points, speaker_notes, slide_index
        """
        context = outline["title"]
        slide_index = 0
        
        # Process each slide in order
        for slide in outline["slides"]:
            if slide["type"] == "title":
                # Yield title slide immediately (no LLM call)
                yield {
                    "title": slide["title"],
                    "type": "title",
                    "points": [],
                    "speaker_notes": f"Welcome to the presentation on {outline['title']}",
                    "slide_index": slide_index
                }
                slide_index += 1
            else:
                # Generate content for this slide
                try:
                    print(f"[⚡ Streaming] Generating slide {slide_index + 1}: {slide['title']}")
                    content = await self.generate_slide_content(slide["title"], context)
                    
                    yield {
                        "title": slide["title"],
                        "type": "content",
                        "points": content["points"],
                        "speaker_notes": content["speaker_notes"],
                        "slide_index": slide_index
                    }
                    slide_index += 1
                    
                except Exception as e:
                    print(f"⚠️ Failed to generate slide '{slide['title']}': {e}")
                    # Yield placeholder slide
                    yield {
                        "title": slide["title"],
                        "type": "content",
                        "points": ["Content generation failed"],
                        "speaker_notes": f"This slide covers {slide['title']}.",
                        "slide_index": slide_index
                    }
                    slide_index += 1


async def generate_outline_async(topic: str, model: str = "llama3.1", ollama_url: str = "http://localhost:11434") -> Dict:
    """Standalone async outline generation."""
    async with AsyncSlideGenerator(model, ollama_url) as generator:
        return await generator.generate_outline(topic)


async def generate_full_script_async(
    outline: Dict,
    model: str = "llama3.1",
    ollama_url: str = "http://localhost:11434"
) -> Dict:
    """Standalone async script generation."""
    async with AsyncSlideGenerator(model, ollama_url) as generator:
        return await generator.generate_full_script(outline)


async def generate_slides_streaming_async(
    outline: Dict,
    model: str = "llama3.1",
    ollama_url: str = "http://localhost:11434"
):
    """
    Standalone async streaming slide generation.
    
    Yields slides one by one for immediate downstream processing (TTS, images).
    This enables overlapping operations instead of sequential execution.
    """
    async with AsyncSlideGenerator(model, ollama_url) as generator:
        async for slide in generator.generate_slides_streaming(outline):
            yield slide


def save_outline(outline: Dict, output_path: Path):
    """Save outline to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(outline, indent=2, ensure_ascii=False), encoding='utf-8')


def save_script(script: Dict, output_path: Path):
    """Save full script to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(script, indent=2, ensure_ascii=False), encoding='utf-8')
