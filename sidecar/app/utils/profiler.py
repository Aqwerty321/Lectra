"""Performance profiling utilities for LECTRA pipeline."""

import time
import functools
from typing import Callable, Any, Dict
from collections import defaultdict
import asyncio


class PerformanceProfiler:
    """Global performance profiler to track stage execution times."""
    
    _timings: Dict[str, list] = defaultdict(list)
    _current_session: Dict[str, float] = {}
    
    @classmethod
    def start(cls, stage_name: str):
        """Start timing a stage."""
        cls._current_session[stage_name] = time.time()
    
    @classmethod
    def end(cls, stage_name: str) -> float:
        """End timing a stage and return duration."""
        if stage_name not in cls._current_session:
            return 0.0
        
        start_time = cls._current_session.pop(stage_name)
        duration = time.time() - start_time
        cls._timings[stage_name].append(duration)
        
        # Print immediately for real-time feedback
        print(f"[⏱] {stage_name}: {duration:.2f}s")
        
        return duration
    
    @classmethod
    def get_report(cls) -> str:
        """Generate a human-readable performance report."""
        if not cls._timings:
            return "No profiling data collected."
        
        report = "\n" + "="*60 + "\n"
        report += "⏱  PERFORMANCE REPORT\n"
        report += "="*60 + "\n"
        
        total_time = 0
        for stage_name, durations in sorted(cls._timings.items()):
            avg_time = sum(durations) / len(durations)
            last_time = durations[-1]
            total_time += last_time
            
            report += f"  {stage_name:<40} {last_time:>6.2f}s"
            if len(durations) > 1:
                report += f"  (avg: {avg_time:.2f}s)"
            report += "\n"
        
        report += "-"*60 + "\n"
        report += f"  {'TOTAL':<40} {total_time:>6.2f}s\n"
        report += "="*60 + "\n"
        
        return report
    
    @classmethod
    def reset(cls):
        """Reset all profiling data."""
        cls._timings.clear()
        cls._current_session.clear()


def timeit(stage_name: str):
    """
    Decorator to time function execution.
    Works with both sync and async functions.
    
    Usage:
        @timeit("Image Fetch")
        def fetch_images():
            ...
        
        @timeit("TTS Synthesis")
        async def synthesize_audio():
            ...
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                PerformanceProfiler.start(stage_name)
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    PerformanceProfiler.end(stage_name)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                PerformanceProfiler.start(stage_name)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    PerformanceProfiler.end(stage_name)
            return sync_wrapper
    
    return decorator


def log_timing(stage_name: str, duration: float):
    """Manually log timing for a code block."""
    PerformanceProfiler._timings[stage_name].append(duration)
    print(f"[⏱] {stage_name}: {duration:.2f}s")


class Timer:
    """Context manager for timing code blocks."""
    
    def __init__(self, stage_name: str):
        self.stage_name = stage_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        log_timing(self.stage_name, duration)


# Example usage:
# with Timer("Database Query"):
#     result = db.query()
