"""Async image fetching with parallel downloads and connection pooling."""

import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List
import json

from .image_fetcher import (
    search_duckduckgo_images,
    search_wikimedia_commons,
    search_pixabay,
    DDGS_AVAILABLE
)


async def download_image_async(session: aiohttp.ClientSession, url: str, output_path: Path) -> bool:
    """
    Download image asynchronously using aiohttp with WEBP conversion.
    
    Args:
        session: Shared aiohttp session
        url: Image URL
        output_path: Local path to save image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                content = await response.read()
                
                # Save to temporary file first
                temp_path = output_path.with_suffix('.tmp')
                temp_path.write_bytes(content)
                
                # Check if image is WEBP and convert to JPEG
                try:
                    from PIL import Image
                    
                    with Image.open(temp_path) as img:
                        # Convert WEBP or any unsupported format to JPEG
                        if img.format == 'WEBP' or img.format not in ['JPEG', 'JPG', 'PNG', 'GIF', 'BMP']:
                            print(f"  ⚙️ Converting {img.format} to JPEG...")
                            # Convert to RGB if needed (for transparency)
                            if img.mode in ('RGBA', 'LA', 'P'):
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                if img.mode == 'P':
                                    img_rgba = img.convert('RGBA')
                                    background.paste(img_rgba, mask=img_rgba.split()[-1])
                                else:
                                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                                img_to_save = background
                            elif img.mode != 'RGB':
                                img_to_save = img.convert('RGB')
                            else:
                                img_to_save = img.copy()
                            
                            # Save converted image
                            img_to_save.save(output_path, 'JPEG', quality=90)
                            # Delete temp file after successful conversion
                            if temp_path.exists():
                                temp_path.unlink()
                        else:
                            # No conversion needed
                            pass
                    
                    # If no conversion was needed, rename the temp file
                    if not output_path.exists() and temp_path.exists():
                        temp_path.rename(output_path)
                        
                except Exception as convert_error:
                    print(f"  ⚠️ Image conversion failed: {convert_error}")
                    # Try to use the file as-is
                    if temp_path.exists() and not output_path.exists():
                        try:
                            temp_path.rename(output_path)
                        except:
                            pass
                
                return output_path.exists()
            else:
                return False
    except Exception as e:
        print(f"  ⚠️ Download failed for {url}: {e}")
        return False


async def fetch_images_for_slide_async(
    session: aiohttp.ClientSession,
    slide: Dict,
    slide_idx: int,
    images_dir: Path
) -> tuple[int, List[Dict]]:
    """
    Fetch images for a single slide asynchronously.
    
    Args:
        session: Shared aiohttp session
        slide: Slide data
        slide_idx: Slide index
        images_dir: Directory to save images
        
    Returns:
        Tuple of (slide_idx, list of downloaded images)
    """
    print(f"\n--- Slide {slide_idx}: {slide['title']} ---")
    
    if slide["type"] == "title":
        print("Skipping title slide")
        return (slide_idx, [])
    
    # Create enhanced search query
    base_query = slide["title"]
    
    if slide.get("points") and len(slide["points"]) > 0:
        first_point = slide["points"][0][:80]
        enhanced_query = f"{base_query} {first_point}"
    else:
        enhanced_query = base_query
    
    # Add visual context
    if any(word in base_query.lower() for word in ["how", "what", "why", "process", "steps"]):
        enhanced_query = f"{enhanced_query} infographic"
    
    query = enhanced_query.strip()
    print(f"Search query: {query}")
    
    # Search multiple sources (synchronous - these are fast API calls)
    images = []
    
    # 1. DuckDuckGo Images (most current)
    ddg_images = search_duckduckgo_images(query, max_results=2)
    images.extend(ddg_images)
    
    # 2. Wikimedia Commons as backup
    if len(images) < 2:
        wiki_images = search_wikimedia_commons(query, max_results=2 - len(images))
        images.extend(wiki_images)
    
    # 3. Pixabay as fallback
    if len(images) < 2:
        pixabay_images = search_pixabay(query, max_results=2 - len(images))
        images.extend(pixabay_images)
    
    # Download candidates in parallel
    downloaded = []
    if images:
        print(f"Attempting to download {min(len(images), 2)} image candidates in parallel...")
        
        download_tasks = []
        for img_idx, img in enumerate(images[:2]):
            filename = f"slide_{slide_idx}_candidate_{img_idx}.jpg"
            filepath = images_dir / filename
            
            # Create download task
            task = download_image_async(session, img["url"], filepath)
            download_tasks.append((task, img, filepath, img_idx))
        
        # Execute downloads in parallel
        for task, img, filepath, img_idx in download_tasks:
            success = await task
            if success:
                img["local_path"] = str(filepath)
                downloaded.append(img)
                source_info = f" from {img.get('source', 'unknown')}"
                if img.get('source') == 'duckduckgo':
                    source_info = f" from DuckDuckGo ({img.get('source_site', 'web')})"
                print(f"  ✓ Candidate {img_idx + 1}{source_info}")
            else:
                print(f"  ✗ Candidate {img_idx + 1} download failed")
    
    # Pick the first successfully downloaded image
    final_images = []
    if downloaded:
        best_image = downloaded[0]
        old_path = Path(best_image["local_path"])
        new_filename = f"slide_{slide_idx}_0.jpg"
        new_path = images_dir / new_filename
        
        # Delete target if it exists
        if new_path.exists():
            new_path.unlink()
        
        # Rename to final name
        try:
            old_path.rename(new_path)
            best_image["local_path"] = str(new_path)
            final_images.append(best_image)
            
            source_info = f"{best_image.get('source', 'unknown')}"
            if best_image.get('source') == 'duckduckgo':
                source_info = f"DuckDuckGo ({best_image.get('source_site', 'web')})"
            print(f"  ✅ SELECTED: {new_filename} from {source_info}")
        except Exception as e:
            print(f"  ⚠️ Failed to rename {old_path.name}: {e}")
        
        # Delete other candidates
        for img in downloaded[1:]:
            candidate_path = Path(img["local_path"])
            if candidate_path.exists():
                try:
                    candidate_path.unlink()
                except Exception as e:
                    print(f"  ⚠️ Failed to delete {candidate_path.name}: {e}")
        
        print(f"✓ Slide {slide_idx} has {len(final_images)} image(s)")
    else:
        print(f"✗ No images for slide {slide_idx}")
    
    return (slide_idx, final_images)


async def fetch_images_for_slides_async(
    script: Dict,
    output_dir: Path
) -> Dict[int, List[Dict]]:
    """
    Fetch images for all slides in parallel.
    
    Args:
        script: Complete presentation script
        output_dir: Directory to save images
        
    Returns:
        Dict mapping slide index to list of image info dicts with local paths
    """
    print("\n" + "="*50)
    print("STARTING ASYNC IMAGE FETCH FOR PRESENTATION")
    print("="*50)
    
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    print(f"Images directory: {images_dir}")
    
    # Create shared HTTP session
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Create tasks for all slides
        tasks = []
        for idx, slide in enumerate(script["slides"]):
            task = fetch_images_for_slide_async(session, slide, idx, images_dir)
            tasks.append(task)
        
        # Execute all image fetching in parallel
        print(f"🚀 Fetching images for {len(tasks)} slides in parallel...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        slide_images = {}
        for result in results:
            if isinstance(result, Exception):
                print(f"⚠️ Image fetch failed: {result}")
            else:
                slide_idx, images = result
                if images:
                    slide_images[slide_idx] = images
    
    print(f"\n{'='*50}")
    print(f"TOTAL: {len(slide_images)} slides with images")
    print(f"{'='*50}\n")
    
    return slide_images


def save_image_metadata(slide_images: Dict[int, List[Dict]], output_path: Path):
    """Save image metadata to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(slide_images, indent=2), encoding='utf-8')


async def fetch_images_for_slide_standalone(
    slide: Dict,
    output_dir: Path
) -> List[Dict]:
    """
    Fetch images for a single slide (standalone version that manages its own session).
    
    Use this when fetching images for one slide at a time in a streaming pipeline.
    For batch fetching all slides, use fetch_images_for_slides_async() instead.
    
    Args:
        slide: Slide data with 'title', 'type', 'points', 'slide_index'
        output_dir: Directory to save images (will create 'images' subdirectory)
        
    Returns:
        List of image info dicts with local paths
    """
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    slide_idx = slide.get("slide_index", 0)
    
    # Create temporary session for this slide
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        _, images = await fetch_images_for_slide_async(session, slide, slide_idx, images_dir)
        return images
