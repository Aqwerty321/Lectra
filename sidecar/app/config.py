"""Configuration loader for LECTRA sidecar."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # Ollama settings
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = "llama3.1:latest"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    
    # Output paths
    OUTPUT_ROOT = Path(os.getenv("OUTPUT_ROOT", Path.home() / "Lectures")).expanduser()
    
    # FFmpeg
    FFMPEG_BIN = os.getenv("FFMPEG_BIN", "C:\\ffmpeg\\bin\\ffmpeg.exe" if os.name == 'nt' else "ffmpeg")
    
    # Default voices
    DEFAULT_EN_VOICE = os.getenv("DEFAULT_EN_VOICE", "en-US-GuyNeural")
    DEFAULT_HI_VOICE = os.getenv("DEFAULT_HI_VOICE", "hi-IN-SwaraNeural")
    
    # Voice overrides for timing estimation
    VOICE_WPM = {
        "en-US-AriaNeural": 170,
        "en-US-GuyNeural": 160,
        "hi-IN-SwaraNeural": 150,
        "hi-IN-MadhurNeural": 145,
    }
    
    # Base WPM by language
    BASE_WPM = {
        "en": 165,
        "hi": 150,
    }
    
    @classmethod
    def ensure_output_root(cls):
        """Create output root directory if it doesn't exist."""
        cls.OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        return cls.OUTPUT_ROOT
    
    @classmethod
    def get_project_dir(cls, project_name: str) -> Path:
        """Get project directory path, create if needed."""
        project_dir = cls.OUTPUT_ROOT / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir


config = Config()
