"""Minimal Ollama client for streaming text generation - refactored as library."""

import requests
import json
from typing import Optional


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
