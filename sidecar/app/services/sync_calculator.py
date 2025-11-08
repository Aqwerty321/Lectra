"""
🎯 ROBUST SYNC CALCULATOR v2.0
================================

Calculates precise slide timings from ACTUAL audio/video output using FFmpeg probe.
Eliminates sync drift by measuring real durations instead of estimating.

WORKFLOW:
1. Generate audio with TTS
2. Probe audio file for ACTUAL duration (FFmpeg)
3. Calculate slide timings based on real audio length
4. Create video with precise timings
5. Verify final video sync (optional)

This ensures perfect synchronization regardless of TTS variations.
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def get_ffmpeg_path() -> str:
    """Get FFmpeg executable path."""
    import shutil
    import os
    
    # First check if ffmpeg is in PATH
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg:
        return ffmpeg
    
    # Check common Windows locations
    common_paths = [
        r'C:\ffmpeg\bin\ffmpeg.exe',
        r'C:\ffmpeg\ffmpeg.exe',
        r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            logger.info(f"Found FFmpeg at: {path}")
            return path
    
    return None  # Return None if not found


def probe_media_duration(file_path: Path) -> float:
    """
    Get ACTUAL duration of audio/video file using FFmpeg probe.
    Falls back to pydub if FFmpeg is not available.
    
    This is the SOURCE OF TRUTH for timing calculations.
    
    Args:
        file_path: Path to audio/video file
        
    Returns:
        Duration in seconds (float)
        
    Raises:
        RuntimeError: If all probing methods fail
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Media file not found: {file_path}")
    
    ffmpeg_path = get_ffmpeg_path()
    
    # If FFmpeg not available, use pydub fallback immediately
    if not ffmpeg_path:
        logger.warning("FFmpeg not found in PATH, using pydub for duration")
        return _probe_with_pydub(file_path)
    
    # Construct ffprobe path from ffmpeg path
    import os
    ffprobe_path = ffmpeg_path.replace('ffmpeg.exe', 'ffprobe.exe')
    
    # If the replacement didn't work, try the same directory
    if ffprobe_path == ffmpeg_path:
        ffmpeg_dir = os.path.dirname(ffmpeg_path)
        ffprobe_path = os.path.join(ffmpeg_dir, 'ffprobe.exe')
    
    # Verify ffprobe exists
    if not os.path.exists(ffprobe_path):
        logger.warning(f"FFprobe not found at {ffprobe_path}, using pydub")
        return _probe_with_pydub(file_path)
    
    # Use FFprobe (part of FFmpeg) to get precise duration
    cmd = [
        ffprobe_path,
        '-v', 'error',  # Only show errors
        '-show_entries', 'format=duration',  # Get duration
        '-of', 'default=noprint_wrappers=1:nokey=1',  # Simple output
        str(file_path)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        
        duration_str = result.stdout.strip()
        duration = float(duration_str)
        
        logger.info(f"📊 Probed duration: {duration:.3f}s for {file_path.name}")
        return duration
        
    except subprocess.CalledProcessError as e:
        # Fallback: Try parsing FFmpeg output
        logger.warning(f"FFprobe failed, trying FFmpeg: {e}")
        return _probe_with_ffmpeg(file_path)
    
    except (ValueError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        # Final fallback: Use pydub
        logger.warning(f"FFmpeg probe failed ({e}), falling back to pydub")
        return _probe_with_pydub(file_path)


def _probe_with_ffmpeg(file_path: Path) -> float:
    """
    Fallback: Extract duration from FFmpeg output.
    
    Args:
        file_path: Path to media file
        
    Returns:
        Duration in seconds
    """
    ffmpeg_path = get_ffmpeg_path()
    
    cmd = [
        ffmpeg_path,
        '-i', str(file_path),
        '-f', 'null',
        '-'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Parse duration from FFmpeg stderr output
        # Format: Duration: HH:MM:SS.ms
        output = result.stderr
        match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', output)
        
        if match:
            hours, minutes, seconds, centiseconds = match.groups()
            duration = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(centiseconds) / 100
            logger.info(f"📊 Extracted duration: {duration:.3f}s from FFmpeg output")
            return duration
        
        raise ValueError("Could not parse duration from FFmpeg output")
        
    except (subprocess.TimeoutExpired, ValueError) as e:
        raise RuntimeError(f"FFmpeg duration extraction failed: {e}")


def _probe_with_pydub(file_path: Path) -> float:
    """
    Fallback: Use pydub to get audio duration (works without FFmpeg for reading).
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Duration in seconds
    """
    try:
        from pydub import AudioSegment
        
        # Load audio file
        audio = AudioSegment.from_file(str(file_path))
        duration = len(audio) / 1000.0  # Convert ms to seconds
        
        logger.info(f"📊 Pydub duration: {duration:.3f}s for {file_path.name}")
        return duration
        
    except Exception as e:
        raise RuntimeError(f"Pydub duration extraction failed: {e}")


def calculate_slide_timings_from_audio(
    audio_path: Path,
    sentence_timings: List[Dict],
    slide_mapping: List[Dict]
) -> Dict:
    """
    🎯 ROBUST TIMING CALCULATOR
    
    Calculates slide timings based on ACTUAL audio duration (not estimates).
    
    Algorithm:
    1. Probe actual audio duration (SOURCE OF TRUTH)
    2. Calculate estimated total from sentence timings
    3. Compute scaling factor: actual / estimated
    4. Scale all sentence timings proportionally
    5. Map scaled timings to slides
    6. Return slide timings ready for video generation
    
    Args:
        audio_path: Path to generated audio file
        sentence_timings: List of sentence timing dicts from estimate_timings()
        slide_mapping: List of slide-to-sentence mappings
        
    Returns:
        Dict with:
            - 'actual_duration': Real audio duration (seconds)
            - 'estimated_duration': Estimated duration (seconds)
            - 'scale_factor': Correction factor
            - 'slides': List of slide timing dicts
            - 'sentences': Scaled sentence timings
    """
    print("\n" + "="*70)
    print("🎯 ROBUST SYNC CALCULATOR v2.0")
    print("="*70)
    
    # === STEP 1: PROBE ACTUAL DURATION ===
    actual_duration = probe_media_duration(audio_path)
    print(f"✅ Actual audio duration: {actual_duration:.3f}s (SOURCE OF TRUTH)")
    
    # === STEP 2: GET ESTIMATED DURATION ===
    if not sentence_timings:
        raise ValueError("No sentence timings provided")
    
    estimated_duration = sentence_timings[-1]['end'] if sentence_timings else 0.0
    print(f"📊 Estimated duration: {estimated_duration:.3f}s")
    
    # === STEP 3: CALCULATE SCALE FACTOR ===
    if estimated_duration == 0:
        scale_factor = 1.0
    else:
        scale_factor = actual_duration / estimated_duration
    
    print(f"⚖️  Scale factor: {scale_factor:.4f} ({abs(1-scale_factor)*100:.1f}% correction)")
    
    if abs(1 - scale_factor) > 0.15:  # More than 15% off
        logger.warning(f"⚠️  Large timing correction needed: {abs(1-scale_factor)*100:.1f}%")
    
    # === STEP 4: SCALE SENTENCE TIMINGS ===
    scaled_sentences = []
    for sent in sentence_timings:
        scaled = {
            'index': sent['index'],
            'text': sent['text'],
            'start': sent['start'] * scale_factor,
            'end': sent['end'] * scale_factor,
            'duration': sent['duration'] * scale_factor,
            'original_start': sent['start'],
            'original_end': sent['end']
        }
        scaled_sentences.append(scaled)
    
    print(f"🔄 Scaled {len(scaled_sentences)} sentence timings")
    
    # === STEP 5: MAP TO SLIDES ===
    slide_timings = []
    current_time = 0.0  # Track cumulative time for title slides
    
    for slide_info in slide_mapping:
        slide_num = slide_info['slide_number']
        sentence_indices = slide_info['sentence_indices']
        is_title = slide_info.get('is_title', False)
        fixed_duration = slide_info.get('fixed_duration', None)
        
        # Handle title slides or slides with no narration
        if not sentence_indices or fixed_duration is not None:
            if fixed_duration is not None:
                # Use fixed duration (for title slides)
                start_time = current_time
                duration = fixed_duration
                end_time = start_time + duration
                current_time = end_time
                
                slide_timings.append({
                    'slide_number': slide_num,
                    'start': round(start_time, 3),
                    'end': round(end_time, 3),
                    'duration': round(duration, 3),
                    'sentence_count': 0,
                    'sentence_indices': [],
                    'is_title': is_title
                })
                
                print(f"  📄 Slide {slide_num} {'(TITLE)' if is_title else ''}: {start_time:.3f}s - {end_time:.3f}s "
                      f"({duration:.3f}s, fixed duration)")
                continue
            else:
                # Empty slide without fixed duration - skip
                logger.warning(f"⚠️  Slide {slide_num} has no sentences and no fixed duration - skipping")
                continue
        
        # Get timing range from first to last sentence
        first_idx = sentence_indices[0]
        last_idx = sentence_indices[-1]
        
        if first_idx >= len(scaled_sentences) or last_idx >= len(scaled_sentences):
            logger.error(f"❌ Invalid sentence indices for slide {slide_num}")
            continue
        
        start_time = scaled_sentences[first_idx]['start'] + current_time
        end_time = scaled_sentences[last_idx]['end'] + current_time
        duration = end_time - start_time
        
        # Update current_time to track cumulative position
        # (Note: For content slides, this should match the sentence timing)
        if slide_timings:  # If we had title slides, adjust timing
            # Start content slides after title slides
            if current_time > 0:
                # Shift all sentence-based timings
                start_time = scaled_sentences[first_idx]['start'] + current_time
                end_time = scaled_sentences[last_idx]['end'] + current_time
                duration = end_time - start_time
            else:
                # Normal sentence-based timing
                start_time = scaled_sentences[first_idx]['start']
                end_time = scaled_sentences[last_idx]['end']
                duration = end_time - start_time
                current_time = end_time
        else:
            # First slide - use normal sentence timing
            start_time = scaled_sentences[first_idx]['start']
            end_time = scaled_sentences[last_idx]['end']
            duration = end_time - start_time
            current_time = end_time
        
        slide_timings.append({
            'slide_number': slide_num,
            'start': round(start_time, 3),
            'end': round(end_time, 3),
            'duration': round(duration, 3),
            'sentence_count': len(sentence_indices),
            'sentence_indices': sentence_indices
        })
        
        print(f"  📄 Slide {slide_num}: {start_time:.3f}s - {end_time:.3f}s "
              f"({duration:.3f}s, {len(sentence_indices)} sentences)")
    
    # === VALIDATION: Check timing coverage ===
    if slide_timings:
        first_slide_start = slide_timings[0]['start']
        last_slide_end = slide_timings[-1]['end']
        coverage = (last_slide_end / actual_duration) * 100
        
        print(f"\n  🔍 Timing coverage: {first_slide_start:.3f}s - {last_slide_end:.3f}s")
        print(f"     Audio duration: {actual_duration:.3f}s")
        print(f"     Coverage: {coverage:.1f}%")
        
        if coverage < 95:
            logger.warning(f"⚠️  Low coverage: {coverage:.1f}% - audio may be truncated")
        elif coverage > 105:
            logger.warning(f"⚠️  Over coverage: {coverage:.1f}% - slides may run too long")
    
    # === STEP 6: RETURN COMPLETE TIMING DATA ===
    result = {
        'actual_duration': round(actual_duration, 3),
        'estimated_duration': round(estimated_duration, 3),
        'scale_factor': round(scale_factor, 4),
        'total_duration': round(actual_duration, 3),  # For compatibility
        'slide_count': len(slide_timings),
        'sentence_count': len(scaled_sentences),
        'slides': slide_timings,
        'sentences': scaled_sentences
    }
    
    print(f"✅ Generated timings for {len(slide_timings)} slides")
    print("="*70 + "\n")
    
    return result


def verify_video_sync(
    video_path: Path,
    expected_duration: float,
    tolerance: float = 0.5
) -> Tuple[bool, float, str]:
    """
    Verify final video has correct duration.
    
    Args:
        video_path: Path to generated video
        expected_duration: Expected duration (seconds)
        tolerance: Acceptable difference (seconds)
        
    Returns:
        Tuple of (is_synced, actual_duration, message)
    """
    try:
        actual_duration = probe_media_duration(video_path)
        diff = abs(actual_duration - expected_duration)
        
        is_synced = diff <= tolerance
        
        if is_synced:
            message = f"✅ Perfect sync: {actual_duration:.3f}s (expected {expected_duration:.3f}s)"
        else:
            message = f"⚠️  Sync drift: {actual_duration:.3f}s vs expected {expected_duration:.3f}s (diff: {diff:.3f}s)"
        
        print(f"\n{'='*70}")
        print("🔍 VIDEO SYNC VERIFICATION")
        print(f"{'='*70}")
        print(message)
        print(f"{'='*70}\n")
        
        return is_synced, actual_duration, message
        
    except Exception as e:
        logger.error(f"❌ Video sync verification failed: {e}")
        return False, 0.0, f"Verification failed: {e}"


def map_sentences_to_slides(
    slides: List[Dict],
    sentence_timings: List[Dict]
) -> List[Dict]:
    """
    Map sentences to slides based on content structure.
    
    Args:
        slides: List of slide data dicts with 'slide_number' and 'content'
        sentence_timings: List of sentence timing dicts
        
    Returns:
        List of mappings: [{'slide_number': 1, 'sentence_indices': [0, 1, 2]}, ...]
    """
    mapping = []
    sentence_idx = 0
    
    for slide in slides:
        slide_num = slide.get('slide_number', len(mapping) + 1)
        
        # Count sentences in this slide (simple heuristic: count periods/questions)
        content = slide.get('content', '')
        speaker_notes = slide.get('speaker_notes', '')
        full_text = content + " " + speaker_notes
        
        # Estimate sentence count (rough)
        sentence_count = full_text.count('.') + full_text.count('?') + full_text.count('!')
        sentence_count = max(1, sentence_count)  # At least 1
        
        # Assign sentences
        indices = []
        for _ in range(sentence_count):
            if sentence_idx < len(sentence_timings):
                indices.append(sentence_idx)
                sentence_idx += 1
        
        mapping.append({
            'slide_number': slide_num,
            'sentence_indices': indices
        })
    
    # Handle remaining sentences (add to last slide)
    if sentence_idx < len(sentence_timings) and mapping:
        mapping[-1]['sentence_indices'].extend(range(sentence_idx, len(sentence_timings)))
    
    return mapping
