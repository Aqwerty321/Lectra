"""Convert custom nuance tags to EdgeTTS-compatible segments."""

import re
from typing import Optional, Tuple, List, Dict


def _split_sentences(text: str) -> list[str]:
    """Simple sentence splitter on .!? followed by whitespace."""
    # Split on sentence boundaries but keep the punctuation
    sentences = re.split(r'([.!?])\s+', text)
    
    # Re-combine punctuation with sentences
    result = []
    i = 0
    while i < len(sentences):
        if i + 1 < len(sentences) and sentences[i + 1] in '.!?':
            result.append(sentences[i] + sentences[i + 1])
            i += 2
        else:
            if sentences[i].strip():
                result.append(sentences[i])
            i += 1
    
    return [s.strip() for s in result if s.strip()]


def strip_all_tags(text: str) -> str:
    """Strip all nuance tags and return clean text."""
    # First process emphasis tags to preserve the text content
    text = re.sub(r'\[emphasis\](.*?)\[/emphasis\]', r'\1', text)
    # Remove all other square bracket tags
    clean = re.sub(r'\[/?[^\]]+\]', '', text)
    # Clean up multiple spaces
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


def _extract_tag(pattern: str, text: str) -> Tuple[Optional[str], str]:
    """Extract a tag value and remove it from text."""
    match = re.search(pattern, text)
    if match:
        value = match.group(1)
        text = re.sub(pattern, '', text, count=1).strip()
        return value, text
    return None, text


def parse_to_segments(tagged: str, default_voice: str = "en-US-GuyNeural") -> List[Dict]:
    """
    Parse tagged text into segments for EdgeTTS.
    Each segment is a dict with: text, voice, rate, pitch, pause_after
    
    Since EdgeTTS only supports ONE prosody tag, we split into segments.
    """
    sentences = _split_sentences(tagged)
    segments = []
    
    for sentence in sentences:
        # Extract tags (only at sentence start)
        voice, sentence = _extract_tag(r'^\s*\[voice=([\w-]+)\]', sentence)
        style, sentence = _extract_tag(r'^\s*\[style=([\w-]+)\]', sentence)  # Ignore - not supported
        rate, sentence = _extract_tag(r'^\s*\[rate=([+-]?\d+%)\]', sentence)
        pitch, sentence = _extract_tag(r'^\s*\[pitch=([+-]?\d+st)\]', sentence)
        
        # Extract pause ONLY at sentence end
        pause_match = re.search(r'\[pause=(\d+)ms\]\s*$', sentence)
        pause_after = None
        if pause_match:
            pause_after = int(pause_match.group(1))
            sentence = re.sub(r'\[pause=\d+ms\]\s*$', '', sentence)
        
        # Clean up: remove ALL remaining tags (they shouldn't be there)
        sentence = re.sub(r'\[emphasis\](.*?)\[/emphasis\]', r'\1', sentence)
        sentence = re.sub(r'\[/?[^\]]+\]', '', sentence)
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        
        if not sentence:
            continue
            
        # Create segment
        segment = {
            'text': sentence,
            'voice': voice or default_voice,
            'rate': rate,
            'pitch': pitch,
            'pause_before': None,  # No longer used
            'pause_after': pause_after
        }
        
        segments.append(segment)
    
    return segments


def to_ssml(
    tagged: str,
    default_voice: str = "en-US-GuyNeural",
    fallback_rate: Optional[str] = None,
    fallback_pitch: Optional[str] = None
) -> str:
    """
    Convert tagged text to simple SSML for logging/reference.
    NOTE: EdgeTTS has limited SSML support, so actual audio generation uses parse_to_segments().
    """
    # Just return a simple SSML document with clean text
    clean_text = strip_all_tags(tagged)
    
    # Determine language from voice
    lang = "en-US"
    if "hi-" in default_voice.lower():
        lang = "hi-IN"
    
    return f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{lang}">
<voice name="{default_voice}">{clean_text}</voice>
</speak>'''
