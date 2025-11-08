"""Async tagging service for parallel text processing."""

import aiohttp
from pathlib import Path
from ..config import config


# Load system prompt
PROMPT_FILE = Path(__file__).parent / "nuance_system_prompt.txt"
with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()


async def generate_tagged_async(
    text: str,
    system: str,
    model: str = "llama3.1:latest",
    base_url: str = "http://localhost:11434"
) -> str:
    """
    Generate tagged text using Ollama API asynchronously.
    
    Args:
        text: Input text to tag
        system: System prompt
        model: Ollama model name
        base_url: Ollama server URL
        
    Returns:
        Tagged text from Ollama
        
    Raises:
        ConnectionError: If Ollama is unreachable
    """
    url = f"{base_url}/api/generate"
    payload = {
        "model": model,
        "prompt": text,
        "system": system,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9
        }
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ConnectionError(f"Ollama returned status {response.status}: {error_text}")
                
                result = await response.json()
                return result.get("response", "")
    
    except aiohttp.ClientConnectorError as e:
        raise ConnectionError(f"Cannot connect to Ollama at {base_url}: {e}")
    except aiohttp.ClientError as e:
        raise ConnectionError(f"Ollama request failed: {e}")


async def generate_nuanced_text_async(
    text: str,
    model: str = None,
    ollama_url: str = None
) -> str:
    """
    Add nuance tags to input text using Ollama asynchronously.
    
    Args:
        text: Raw input text
        model: Ollama model (default: llama3.1:latest)
        ollama_url: Ollama server URL (default from config)
        
    Returns:
        Tagged text with prosody markers
        
    Raises:
        ConnectionError: If Ollama is unreachable
    """
    model = model or config.OLLAMA_MODEL
    ollama_url = ollama_url or config.OLLAMA_URL
    
    return await generate_tagged_async(
        text=text,
        system=SYSTEM_PROMPT,
        model=model,
        base_url=ollama_url
    )
