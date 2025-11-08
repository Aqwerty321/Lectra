"""TTS engine wrapper for EdgeTTS with segment-based synthesis."""

import asyncio
import edge_tts
from pathlib import Path
from typing import List, Dict, Optional
from pydub import AudioSegment
from pydub.generators import Sine
import tempfile
import os


def _semitone_to_hz(semitones: int, base_freq: float = 200.0) -> float:
    """Convert semitones to Hz offset (approximate)."""
    # 1 semitone ≈ 10 Hz at typical voice frequencies
    return base_freq + (semitones * 10.0)


def _create_silence(duration_ms: int) -> AudioSegment:
    """Create a silent audio segment."""
    return AudioSegment.silent(duration=duration_ms)


async def _generate_segment_audio(
    text: str,
    voice: str,
    rate: Optional[str] = None,
    pitch: Optional[str] = None,
    output_path: Path = None
) -> Path:
    """
    Generate audio for a single segment using EdgeTTS.
    
    Args:
        text: Clean text (no tags)
        voice: EdgeTTS voice name
        rate: Rate adjustment (e.g., "-10%", "+15%")
        pitch: Pitch adjustment in semitones (e.g., "+2st", "-1st")
        output_path: Output file path
        
    Returns:
        Path to generated audio file
    """
    # Validate text
    if not text or len(text.strip()) == 0:
        raise ValueError("Text cannot be empty for TTS generation")
    
    # Convert pitch from semitones to Hz if provided
    pitch_str = None
    if pitch:
        st_match = __import__('re').match(r'([+-]?\d+)st', pitch)
        if st_match:
            st_value = int(st_match.group(1))
            hz_value = _semitone_to_hz(st_value)
            pitch_str = f"{hz_value:+.0f}Hz"
    
    # Build EdgeTTS communicate object
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate or "+0%",
        pitch=pitch_str or "+0Hz"
    )
    
    # Generate audio
    await communicate.save(str(output_path))
    
    # Verify audio was created
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError(f"No audio was received. Please verify that your parameters are correct. (voice: {voice}, text length: {len(text)})")
    
    return output_path


async def synthesize_from_segments(
    segments: List[Dict],
    output_mp3: Path,
    default_voice: str = "en-US-GuyNeural"
) -> Path:
    """
    Synthesize audio from segments with pauses.
    
    Args:
        segments: List of segment dicts with keys: text, voice, rate, pitch, pause_after
        output_mp3: Final output MP3 path
        default_voice: Fallback voice if segment doesn't specify
        
    Returns:
        Path to generated audio file
    """
    if not segments:
        raise ValueError("No segments provided for TTS synthesis")
    
    # Filter out empty segments
    valid_segments = [s for s in segments if s.get('text') and len(s['text'].strip()) > 0]
    
    if not valid_segments:
        raise ValueError("All segments are empty - no text to synthesize")
    
    temp_dir = Path(tempfile.mkdtemp())
    combined = AudioSegment.empty()
    
    try:
        for i, segment in enumerate(valid_segments):
            # Generate segment audio
            temp_segment = temp_dir / f"seg_{i:03d}.mp3"
            
            try:
                await _generate_segment_audio(
                    text=segment['text'],
                    voice=segment.get('voice') or default_voice,
                    rate=segment.get('rate'),
                    pitch=segment.get('pitch'),
                    output_path=temp_segment
                )
            except Exception as e:
                print(f"⚠️ Failed to generate segment {i}: {e}")
                # Continue with next segment instead of failing completely
                continue
            
            # Load and append to combined audio
            if temp_segment.exists():
                audio = AudioSegment.from_mp3(str(temp_segment))
                combined += audio
            
            # Add pause after if specified
            pause_ms = segment.get('pause_after')
            if pause_ms and pause_ms > 0:
                combined += _create_silence(pause_ms)
        
        if len(combined) == 0:
            raise RuntimeError("No audio was generated from any segments")
        
        # Export final audio
        output_mp3.parent.mkdir(parents=True, exist_ok=True)
        combined.export(str(output_mp3), format="mp3", bitrate="128k")
        
        return output_mp3
        
    finally:
        # Cleanup temp files
        for temp_file in temp_dir.glob("*.mp3"):
            try:
                temp_file.unlink()
            except:
                pass
        try:
            temp_dir.rmdir()
        except:
            pass


async def speak_edge_async(
    segments: List[Dict],
    voice: str,
    output_mp3: Path
) -> Path:
    """
    Async wrapper for segment-based TTS synthesis.
    
    Args:
        segments: Parsed segments from tag_to_ssml.parse_to_segments()
        voice: Default voice name
        output_mp3: Output MP3 file path
        
    Returns:
        Path to generated audio file
    """
    return await synthesize_from_segments(segments, output_mp3, voice)


async def synthesize_slide_narration(
    narration_text: str,
    voice: str,
    output_mp3: Path,
    rate: Optional[str] = None,
    pitch: Optional[str] = None
) -> Path:
    """
    Synthesize audio for a single slide's narration (simple text, no prosody tags).
    
    This is optimized for per-slide streaming TTS where we want to start
    generating audio immediately as each slide is created, without waiting
    for all slides or complex prosody tagging.
    
    Args:
        narration_text: Clean speaker notes text
        voice: EdgeTTS voice name
        output_mp3: Output MP3 file path
        rate: Optional rate adjustment (e.g., "+5%", "-10%")
        pitch: Optional pitch adjustment (e.g., "+2st", "-1st")
        
    Returns:
        Path to generated audio file
    """
    if not narration_text or len(narration_text.strip()) == 0:
        raise ValueError("Narration text cannot be empty")
    
    # Generate audio directly without segments (simpler, faster)
    await _generate_segment_audio(
        text=narration_text.strip(),
        voice=voice,
        rate=rate,
        pitch=pitch,
        output_path=output_mp3
    )
    
    return output_mp3


def speak_edge(
    segments: List[Dict],
    voice: str,
    output_mp3: Path
) -> Path:
    """
    Synchronous wrapper for segment-based TTS synthesis (deprecated).
    Use speak_edge_async() from async contexts.
    
    Args:
        segments: Parsed segments from tag_to_ssml.parse_to_segments()
        voice: Default voice name
        output_mp3: Output MP3 file path
        
    Returns:
        Path to generated audio file
    """
    # For backwards compatibility - but this will fail if called from async context
    return asyncio.run(synthesize_from_segments(segments, output_mp3, voice))
