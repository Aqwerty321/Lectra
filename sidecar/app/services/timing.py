"""Deterministic timing estimator for generated audio."""

import re
import json
from typing import List, Dict, Optional
from pathlib import Path
from ..config import config


def _count_words(text: str) -> int:
    """Count words in text (simple whitespace-based tokenization)."""
    return len(text.split())


def _count_punctuation(text: str) -> Dict[str, int]:
    """Count punctuation marks for pause estimation (including Hindi punctuation)."""
    return {
        'comma': text.count(','),
        'period': text.count('.') + text.count('।') + text.count('॥'),  # Include Hindi purna viram and double danda
        'question': text.count('?'),
        'exclamation': text.count('!'),
        'ellipsis': text.count('…') + text.count('...')
    }


def _parse_rate_tag(rate_str: Optional[str]) -> float:
    """Parse rate tag like '+10%' or '-20%' to percentage value."""
    if not rate_str:
        return 0.0
    
    match = re.match(r'([+-]?\d+)%', rate_str)
    if match:
        return float(match.group(1))
    return 0.0


def _get_base_wpm(lang: str, voice: str) -> int:
    """Get base words-per-minute for language and voice."""
    # Check for voice-specific override
    if voice in config.VOICE_WPM:
        return config.VOICE_WPM[voice]
    
    # Use language default
    return config.BASE_WPM.get(lang, 165)


def estimate_timings(
    tagged_text: str,
    lang: str = "en",
    default_voice: str = "en-US-GuyNeural",
    fallback_rate: Optional[str] = None
) -> Dict:
    """
    Estimate per-sentence timing without generating audio.
    
    Formula per sentence:
    - words = count_tokens_like_words(sentence_without_tags)
    - base_wpm = by_lang_or_voice
    - rate_pct = last [rate=±##%] in sentence or fallback
    - eff_wpm = clamp(base_wpm * (1 + rate_pct/100), 80, 240)
    - spoken_sec = (words / eff_wpm) * 60
    - punct_ms = count(",")*200 + count(".")*450 + count("…")*700
    - tag_pauses_ms = sum([pause=###ms])
    - duration_sec = spoken_sec + (punct_ms + tag_pauses_ms)/1000
    
    Args:
        tagged_text: Text with nuance tags
        lang: Language code (en, hi)
        default_voice: Voice name for WPM lookup
        fallback_rate: Default rate if no tags present
        
    Returns:
        Dict with timing data and per-sentence breakdown
    """
    from .tag_to_ssml import parse_to_segments
    
    segments = parse_to_segments(tagged_text, default_voice)
    base_wpm = _get_base_wpm(lang, default_voice)
    
    sentence_timings = []
    current_time = 0.0
    
    for i, segment in enumerate(segments):
        text = segment['text']
        
        # Count words (after stripping tags)
        word_count = _count_words(text)
        
        # Get rate adjustment
        rate_pct = _parse_rate_tag(segment.get('rate') or fallback_rate)
        
        # Calculate effective WPM (clamped)
        eff_wpm = max(80, min(240, base_wpm * (1 + rate_pct / 100)))
        
        # Calculate spoken duration
        spoken_sec = (word_count / eff_wpm) * 60 if word_count > 0 else 0.0
        
        # Calculate punctuation pauses
        punct = _count_punctuation(text)
        punct_ms = (
            punct['comma'] * 200 +
            (punct['period'] + punct['question'] + punct['exclamation']) * 450 +
            punct['ellipsis'] * 700
        )
        
        # Get tag-specified pause
        tag_pause_ms = segment.get('pause_after') or 0
        
        # Total duration
        duration_sec = spoken_sec + (punct_ms + tag_pause_ms) / 1000.0
        
        # Record timing
        start_time = current_time
        end_time = start_time + duration_sec
        
        sentence_timings.append({
            'index': i,
            'text': text,
            'start': round(start_time, 3),
            'end': round(end_time, 3),
            'duration': round(duration_sec, 3),
            'words': word_count,
            'rate_pct': rate_pct,
            'eff_wpm': round(eff_wpm, 1)
        })
        
        current_time = end_time
    
    return {
        'total_duration_sec': round(current_time, 3),
        'sentence_count': len(sentence_timings),
        'base_wpm': base_wpm,
        'lang': lang,
        'voice': default_voice,
        'sentences': sentence_timings
    }


def save_timings(timings: Dict, output_dir: Path):
    """
    Save timings to JSON and VTT formats.
    
    Args:
        timings: Timing data from estimate_timings()
        output_dir: Directory to save files
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_path = output_dir / "timings.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(timings, f, indent=2, ensure_ascii=False)
    
    # Save VTT (WebVTT subtitles)
    vtt_path = output_dir / "subs.vtt"
    with open(vtt_path, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")
        
        for sent in timings['sentences']:
            start_time = _format_vtt_time(sent['start'])
            end_time = _format_vtt_time(sent['end'])
            
            f.write(f"{sent['index'] + 1}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{sent['text']}\n\n")
    
    return json_path, vtt_path


def _format_vtt_time(seconds: float) -> str:
    """Format seconds as VTT timestamp (HH:MM:SS.mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
