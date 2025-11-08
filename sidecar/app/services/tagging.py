"""Tagging service - wraps ollama_client for the API."""

from pathlib import Path
from .ollama_client import generate_tagged
from ..config import config


# Load system prompt
PROMPT_FILE = Path(__file__).parent / "nuance_system_prompt.txt"
with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()


def generate_nuanced_text(
    text: str,
    model: str = None,
    ollama_url: str = None
) -> str:
    """
    Add nuance tags to input text using Ollama.
    
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
    
    return generate_tagged(
        text=text,
        system=SYSTEM_PROMPT,
        model=model,
        base_url=ollama_url
    )
