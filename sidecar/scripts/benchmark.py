"""Benchmark script for LECTRA performance testing."""

import asyncio
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import slide_generator_async, image_fetcher_async, tagging_async
from app.utils.profiler import PerformanceProfiler, Timer


async def benchmark_slide_generation():
    """Benchmark parallel slide generation."""
    print("\n" + "="*60)
    print("BENCHMARK: Slide Generation (Parallel)")
    print("="*60)
    
    topic = "Artificial Intelligence in Healthcare"
    
    with Timer("Total Slide Generation"):
        async with slide_generator_async.AsyncSlideGenerator() as generator:
            # Generate outline
            with Timer("Generate Outline"):
                outline = await generator.generate_outline(topic)
                print(f"Generated {len(outline['slides'])} slide outline")
            
            # Generate full script (parallel)
            with Timer("Generate Script (Parallel)"):
                script = await generator.generate_full_script(outline)
                print(f"Generated content for {len(script['slides'])} slides")
    
    print(PerformanceProfiler.get_report())
    return script


async def benchmark_image_fetching(script):
    """Benchmark parallel image fetching."""
    print("\n" + "="*60)
    print("BENCHMARK: Image Fetching (Parallel)")
    print("="*60)
    
    # Use OUTPUT_ROOT from config or default to ~/Lectures
    from app.config import config
    output_dir = config.OUTPUT_ROOT / "benchmark-test"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with Timer("Fetch Images (Parallel)"):
        slide_images = await image_fetcher_async.fetch_images_for_slides_async(script, output_dir)
        print(f"Fetched images for {len(slide_images)} slides")
    
    print(PerformanceProfiler.get_report())
    return slide_images


async def benchmark_prosody_tagging():
    """Benchmark async prosody tagging."""
    print("\n" + "="*60)
    print("BENCHMARK: Prosody Tagging (Async)")
    print("="*60)
    
    text = """
    Artificial intelligence is transforming healthcare by improving diagnosis accuracy,
    streamlining clinical workflows, and enabling personalized medicine. AI-powered tools
    can analyze medical images, predict patient outcomes, and assist in drug discovery.
    However, challenges remain in data privacy, algorithmic bias, and clinical validation.
    """
    
    with Timer("Prosody Tagging"):
        tagged_text = await tagging_async.generate_nuanced_text_async(text)
        print(f"Tagged {len(text)} characters → {len(tagged_text)} characters")
    
    print(PerformanceProfiler.get_report())


async def run_full_benchmark():
    """Run complete benchmark suite."""
    print("\n" + "🚀 "*20)
    print("LECTRA PERFORMANCE BENCHMARK")
    print("🚀 "*20)
    
    total_start = time.time()
    
    try:
        # 1. Slide Generation
        script = await benchmark_slide_generation()
        
        # 2. Image Fetching
        slide_images = await benchmark_image_fetching(script)
        
        # 3. Prosody Tagging
        await benchmark_prosody_tagging()
        
        # Final Report
        total_time = time.time() - total_start
        
        print("\n" + "="*60)
        print("FINAL BENCHMARK RESULTS")
        print("="*60)
        print(f"Total Time: {total_time:.2f}s")
        print(f"Slides Generated: {len(script['slides'])}")
        print(f"Images Fetched: {len(slide_images)}")
        print("="*60)
        
        # Performance targets
        print("\n📊 Performance vs. Targets:")
        targets = {
            "Slide Generation": 15,
            "Image Fetching": 12,
            "Prosody Tagging": 8
        }
        
        for stage, target in targets.items():
            actual = PerformanceProfiler._timings.get(stage, [0])[-1] if stage in PerformanceProfiler._timings else 0
            if actual > 0:
                status = "✅" if actual <= target else "⚠️"
                print(f"{status} {stage}: {actual:.2f}s (target: {target}s)")
        
        if total_time <= 60:
            print("\n🏆 SUCCESS: Sub-60-second generation achieved!")
        else:
            print(f"\n⚠️ Total time: {total_time:.2f}s (target: < 60s)")
    
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting LECTRA Performance Benchmark...")
    print("Make sure Ollama is running with llama3.1 model loaded!")
    print("Press Ctrl+C to cancel\n")
    
    try:
        asyncio.run(run_full_benchmark())
    except KeyboardInterrupt:
        print("\n\n❌ Benchmark cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Benchmark error: {e}")
        import traceback
        traceback.print_exc()
