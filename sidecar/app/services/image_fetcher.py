"""Automatic image fetching from DuckDuckGo, Wikimedia Commons with Llama Vision ranking."""

import requests
from pathlib import Path
from typing import List, Dict, Optional
import hashlib
import json
from urllib.parse import quote
import base64

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    print("⚠️ duckduckgo_search not available")


def search_duckduckgo_images(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search DuckDuckGo for images (most current and relevant).
    
    Args:
        query: Search query
        max_results: Maximum number of images to return
        
    Returns:
        List of image dicts with url, title, source
    """
    if not DDGS_AVAILABLE:
        print("⚠️ DuckDuckGo not available, skipping")
        return []
    
    print(f"🦆 Searching DuckDuckGo Images for: {query}")
    try:
        ddgs = DDGS()
        results = ddgs.images(
            keywords=query,
            max_results=max_results,
            safesearch='on',
            size='Medium'  # Medium size for faster downloads
        )
        
        images = []
        for idx, result in enumerate(results):
            images.append({
                "url": result.get("image"),
                "full_url": result.get("image"),
                "title": result.get("title", f"Image {idx + 1}"),
                "description": result.get("title", ""),
                "width": result.get("width", 800),
                "height": result.get("height", 600),
                "source": "duckduckgo",
                "source_site": result.get("source", "Unknown")
            })
            print(f"  ✓ Found: {result.get('title', 'Image')[:50]}... from {result.get('source', 'Unknown')}")
        
        print(f"DuckDuckGo returned {len(images)} images")
        return images
        
    except Exception as e:
        print(f"❌ DuckDuckGo image search failed: {e}")
        return []


def rank_image_with_llama_vision(
    image_path: Path,
    slide_title: str,
    slide_context: str,
    model: str = "llama3.2-vision:latest",
    ollama_host: str = "http://localhost:11434"
) -> Optional[float]:
    """
    Use Llama Vision to rate how relevant an image is for a slide.
    
    Args:
        image_path: Path to image file
        slide_title: Title of the slide
        slide_context: Context from slide bullet points
        model: Llama Vision model name
        ollama_host: Ollama API endpoint
        
    Returns:
        Relevance score 0-10, or None if failed
    """
    try:
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Create prompt for relevance scoring
        prompt = f"""You are an expert at evaluating image relevance for educational presentations.

Slide Title: "{slide_title}"
Slide Context: {slide_context}

Rate how relevant and useful this image is for the above slide on a scale of 0-10, where:
- 10 = Perfect match, highly educational, clear and professional
- 7-9 = Very relevant, good visual aid
- 4-6 = Somewhat relevant but not ideal
- 1-3 = Barely relevant or poor quality
- 0 = Completely irrelevant or unusable

Respond with ONLY a single number from 0-10, nothing else."""

        # Call Ollama Vision API
        url = f"{ollama_host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for consistent scoring
                "num_predict": 10
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # Extract score from response
        response_text = result.get("response", "").strip()
        
        # Try to parse the score
        try:
            score = float(response_text.split()[0])  # Get first number
            if 0 <= score <= 10:
                return score
        except (ValueError, IndexError):
            pass
        
        return None
        
    except Exception as e:
        print(f"⚠️ Llama Vision ranking failed: {e}")
        return None


def rank_images_for_slide(
    images_with_paths: List[Dict],
    slide_title: str,
    slide_points: List[str],
    use_vision: bool = True
) -> List[Dict]:
    """
    Use Llama Vision to rank downloaded images by relevance (optional).
    
    Args:
        images_with_paths: List of image dicts with local_path
        slide_title: Title of the slide
        slide_points: Bullet points from the slide
        use_vision: Whether to use Llama Vision for ranking
        
    Returns:
        Sorted list of images (best first) with relevance_score added
    """
    if not use_vision:
        # Return images as-is with default scores
        for img in images_with_paths:
            img["relevance_score"] = 5.0
        return images_with_paths
    
    print(f"  🤖 Using Llama Vision to rank {len(images_with_paths)} images...")
    
    # Create context from slide points
    slide_context = " ".join(slide_points[:3])  # Use first 3 bullet points
    
    scored_images = []
    vision_failed_count = 0
    
    for img in images_with_paths:
        if "local_path" not in img or not Path(img["local_path"]).exists():
            continue
        
        score = rank_image_with_llama_vision(
            Path(img["local_path"]),
            slide_title,
            slide_context
        )
        
        if score is not None:
            img["relevance_score"] = score
            scored_images.append(img)
            print(f"    📊 {Path(img['local_path']).name}: {score}/10")
        else:
            # If ranking fails, keep image with default score
            img["relevance_score"] = 5.0
            scored_images.append(img)
            vision_failed_count += 1
            print(f"    ⚠️ {Path(img['local_path']).name}: ranking failed, using default 5/10")
    
    # If all vision calls failed, disable vision for remaining slides
    if vision_failed_count == len(images_with_paths):
        print(f"  ⚠️ All Llama Vision rankings failed - Ollama may not be running")
        print(f"  💡 Tip: Start Ollama with llama3.2-vision model for AI image ranking")
    
    # Sort by score (highest first)
    scored_images.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    if scored_images:
        print(f"  ✓ Best image: {Path(scored_images[0]['local_path']).name} ({scored_images[0]['relevance_score']}/10)")
    
    return scored_images


def search_wikimedia_commons(query: str, max_results: int = 3) -> List[Dict]:
    """
    Search Wikimedia Commons for free-to-use images.
    
    Args:
        query: Search query
        max_results: Maximum number of images to return
        
    Returns:
        List of image dicts with url, title, description
    """
    print(f"Searching Wikimedia for: {query}")
    try:
        # Simplified Wikimedia search using direct image search
        search_url = "https://commons.wikimedia.org/w/api.php"
        
        # Proper headers required by Wikimedia
        headers = {
            'User-Agent': 'LECTRA/2.0 (Educational presentation tool; contact: research@example.com) Python/requests',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        # Search for images directly
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srnamespace": "6",  # File namespace
            "srlimit": 5,
            "srprop": "snippet"
        }
        
        print(f"Making request to Wikimedia API...")
        response = requests.get(search_url, params=search_params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        images = []
        if "query" in data and "search" in data["query"]:
            print(f"Found {len(data['query']['search'])} results")
            
            for item in data["query"]["search"][:max_results]:
                title = item["title"]
                print(f"Processing: {title}")
                
                # Get image URL
                info_params = {
                    "action": "query",
                    "format": "json",
                    "titles": title,
                    "prop": "imageinfo",
                    "iiprop": "url|size",
                    "iiurlwidth": "800"
                }
                
                info_response = requests.get(search_url, params=info_params, headers=headers, timeout=10)
                info_data = info_response.json()
                
                if "query" in info_data and "pages" in info_data["query"]:
                    page = next(iter(info_data["query"]["pages"].values()))
                    if "imageinfo" in page and len(page["imageinfo"]) > 0:
                        img_info = page["imageinfo"][0]
                        img_url = img_info.get("thumburl", img_info.get("url"))
                        
                        if img_url:
                            print(f"✓ Found image: {img_url}")
                            images.append({
                                "url": img_url,
                                "full_url": img_info.get("url", img_url),
                                "title": title.replace("File:", ""),
                                "description": "",
                                "width": img_info.get("thumbwidth", 800),
                                "height": img_info.get("thumbheight", 600),
                                "source": "wikimedia"
                            })
                
                if len(images) >= max_results:
                    break
        
        print(f"Returning {len(images)} images")
        return images
        
    except Exception as e:
        print(f"❌ Wikimedia search failed: {e}")
        import traceback
        traceback.print_exc()
        return []


def search_unsplash(query: str, max_results: int = 3, access_key: Optional[str] = None) -> List[Dict]:
    """
    Search Unsplash for free-to-use images (requires API key).
    
    Args:
        query: Search query
        max_results: Maximum number of images
        access_key: Unsplash API access key
        
    Returns:
        List of image dicts
    """
    if not access_key:
        return []
    
    try:
        url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {access_key}"}
        params = {
            "query": query,
            "per_page": max_results,
            "orientation": "landscape"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        images = []
        for item in data.get("results", []):
            images.append({
                "url": item["urls"]["regular"],
                "full_url": item["urls"]["full"],
                "title": item.get("description", item.get("alt_description", "Image")),
                "description": item.get("description", ""),
                "width": item["width"],
                "height": item["height"],
                "source": "unsplash",
                "author": item["user"]["name"]
            })
        
        return images
        
    except Exception as e:
        print(f"Unsplash search failed: {e}")
        return []


def search_pexels(query: str, max_results: int = 3, api_key: Optional[str] = None) -> List[Dict]:
    """
    Search Pexels for free-to-use images (requires API key).
    
    Args:
        query: Search query
        max_results: Maximum number of images
        api_key: Pexels API key
        
    Returns:
        List of image dicts
    """
    if not api_key:
        return []
    
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": api_key}
        params = {
            "query": query,
            "per_page": max_results,
            "orientation": "landscape"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        images = []
        for item in data.get("photos", []):
            images.append({
                "url": item["src"]["large"],
                "full_url": item["src"]["original"],
                "title": item.get("alt", "Image"),
                "description": "",
                "width": item["width"],
                "height": item["height"],
                "source": "pexels",
                "author": item["photographer"]
            })
        
        return images
        
    except Exception as e:
        print(f"Pexels search failed: {e}")
        return []


def search_pixabay(query: str, max_results: int = 3) -> List[Dict]:
    """
    Search Pixabay for free-to-use images (no API key required).
    
    Args:
        query: Search query
        max_results: Maximum number of images
        
    Returns:
        List of image dicts
    """
    print(f"Searching Pixabay for: {query}")
    try:
        # Pixabay API (public, no key needed for basic usage)
        url = "https://pixabay.com/api/"
        params = {
            "key": "15516090-c99d8eb39f80078a710a55a8f",  # Public demo key
            "q": query,
            "image_type": "photo",
            "orientation": "horizontal",
            "per_page": max_results,
            "safesearch": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        images = []
        for item in data.get("hits", []):
            print(f"✓ Found Pixabay image: {item['webformatURL']}")
            images.append({
                "url": item["webformatURL"],
                "full_url": item["largeImageURL"],
                "title": item.get("tags", "Image"),
                "description": "",
                "width": item["webformatWidth"],
                "height": item["webformatHeight"],
                "source": "pixabay",
                "author": item.get("user", "Unknown")
            })
        
        print(f"Pixabay returned {len(images)} images")
        return images
        
    except Exception as e:
        print(f"❌ Pixabay search failed: {e}")
        return []


def search_pexels(query: str, max_results: int = 3, api_key: Optional[str] = None) -> List[Dict]:
    """
    Search Pexels for free-to-use images (requires API key).
    
    Args:
        query: Search query
        max_results: Maximum number of images
        api_key: Pexels API key
        
    Returns:
        List of image dicts
    """
    if not api_key:
        return []
    
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": api_key}
        params = {
            "query": query,
            "per_page": max_results,
            "orientation": "landscape"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        images = []
        for item in data.get("photos", []):
            images.append({
                "url": item["src"]["large"],
                "full_url": item["src"]["original"],
                "title": item.get("alt", "Image"),
                "description": "",
                "width": item["width"],
                "height": item["height"],
                "source": "pexels",
                "author": item["photographer"]
            })
        
        return images
        
    except Exception as e:
        print(f"Pexels search failed: {e}")
        return []


def download_image(url: str, output_path: Path) -> Optional[Path]:
    """
    Download image from URL and convert to JPEG if needed.
    
    Args:
        url: Image URL
        output_path: Path to save image
        
    Returns:
        Path to downloaded image or None if failed
    """
    try:
        print(f"Downloading: {url}")
        headers = {'User-Agent': 'LECTRA/1.0 (Educational Purpose)'}
        response = requests.get(url, timeout=20, stream=True, headers=headers)
        response.raise_for_status()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to temporary file first
        temp_path = output_path.with_suffix('.tmp')
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Check if image is WEBP and convert to JPEG
        try:
            from PIL import Image
            
            # Open image with context manager to ensure proper cleanup
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
                        img_to_save = img.copy()  # Make a copy to avoid closing issues
                    
                    # Save converted image
                    img_to_save.save(output_path, 'JPEG', quality=90)
                    # Delete temp file after successful conversion
                    if temp_path.exists():
                        temp_path.unlink()
                else:
                    # Image is already in supported format, no conversion needed
                    pass  # Will rename outside the context manager
            
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
        
        print(f"✓ Downloaded to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Image download failed for {url}: {e}")
        return None


def fetch_images_for_slides(
    script: Dict,
    output_dir: Path,
    unsplash_key: Optional[str] = None,
    pexels_key: Optional[str] = None
) -> Dict[int, List[Dict]]:
    """
    Fetch relevant images for each slide in the presentation.
    
    Args:
        script: Complete presentation script
        output_dir: Directory to save images
        unsplash_key: Optional Unsplash API key
        pexels_key: Optional Pexels API key
        
    Returns:
        Dict mapping slide index to list of image info dicts with local paths
    """
    print("\n" + "="*50)
    print("STARTING IMAGE FETCH FOR PRESENTATION")
    print("="*50)
    
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    print(f"Images directory: {images_dir}")
    
    slide_images = {}
    
    for idx, slide in enumerate(script["slides"]):
        print(f"\n--- Slide {idx}: {slide['title']} ---")
        
        if slide["type"] == "title":
            print("Skipping title slide")
            continue
        
        # Create enhanced search query from slide title and first bullet point
        base_query = slide["title"]
        
        # Enhance query with context from first bullet point if available
        if slide.get("points") and len(slide["points"]) > 0:
            first_point = slide["points"][0][:80]  # First 80 chars of first bullet
            # Remove generic words and focus on specific terms
            enhanced_query = f"{base_query} {first_point}"
        else:
            enhanced_query = base_query
        
        # Add context keywords for better image results
        # Avoid abstract/generic terms, prefer visual concepts
        visual_keywords = ["infographic", "diagram", "illustration", "concept"]
        if any(word in base_query.lower() for word in ["how", "what", "why", "process", "steps"]):
            enhanced_query = f"{enhanced_query} infographic"
        
        query = enhanced_query.strip()
        print(f"Search query: {query}")
        
        # Try multiple sources (prioritize DuckDuckGo for current, relevant images)
        images = []
        
        # 1. Try DuckDuckGo Images first (most current and relevant) - but only download 2 candidates
        ddg_images = search_duckduckgo_images(query, max_results=2)
        images.extend(ddg_images)
        
        # 2. Try Wikimedia Commons as backup (excellent educational content)
        if len(images) < 2:
            wiki_images = search_wikimedia_commons(query, max_results=2 - len(images))
            print(f"Wikimedia returned {len(wiki_images)} images")
            images.extend(wiki_images)
        
        # 3. Try Pixabay as fallback
        if len(images) < 2:
            pixabay_images = search_pixabay(query, max_results=2 - len(images))
            images.extend(pixabay_images)
        
        # 4. Try Unsplash if API key provided
        if unsplash_key and len(images) < 2:
            unsplash_images = search_unsplash(query, max_results=2 - len(images), access_key=unsplash_key)
            print(f"Unsplash returned {len(unsplash_images)} images")
            images.extend(unsplash_images)
        
        # 5. Try Pexels if API key provided
        if pexels_key and len(images) < 2:
            pexels_images = search_pexels(query, max_results=2 - len(images), api_key=pexels_key)
            print(f"Pexels returned {len(pexels_images)} images")
            images.extend(pexels_images)
        
        # Download up to 2 image candidates (fast pipeline - no AI ranking)
        downloaded = []
        if images:
            print(f"Attempting to download {min(len(images), 2)} image candidates...")
        
        for img_idx, img in enumerate(images[:2]):  # Download only 2 candidates max
            # Generate filename
            filename = f"slide_{idx}_candidate_{img_idx}.jpg"
            filepath = images_dir / filename
            
            # Download from URL
            if download_image(img["url"], filepath):
                img["local_path"] = str(filepath)
                downloaded.append(img)
                source_info = f" from {img.get('source', 'unknown')}"
                if img.get('source') == 'duckduckgo':
                    source_info = f" from DuckDuckGo ({img.get('source_site', 'web')})"
                print(f"  ✓ Candidate {img_idx + 1}{source_info}")
            else:
                print(f"  ✗ Candidate {img_idx + 1} download failed")
        
        # Pick the first successfully downloaded image (fast, no AI needed)
        if downloaded:
            best_image = downloaded[0]  # Use first image from DuckDuckGo/Wikimedia
            
            # Rename best image to final name and clean up all other candidates
            final_images = []
            old_path = Path(best_image["local_path"])
            new_filename = f"slide_{idx}_0.jpg"
            new_path = images_dir / new_filename
            
            # Delete target if it exists (from previous run)
            if new_path.exists():
                new_path.unlink()
            
            # Rename to final name
            try:
                old_path.rename(new_path)
                best_image["local_path"] = str(new_path)
                final_images.append(best_image)
                
                # Display selected image info
                source_info = f"{best_image.get('source', 'unknown')}"
                if best_image.get('source') == 'duckduckgo':
                    source_info = f"DuckDuckGo ({best_image.get('source_site', 'web')})"
                print(f"  ✅ SELECTED: {new_filename} from {source_info}")
            except Exception as e:
                print(f"  ⚠️ Failed to rename {old_path.name}: {e}")
            
            # Delete all other candidates (keep only the selected one)
            for img in downloaded[1:]:  # Skip first one (already renamed)
                candidate_path = Path(img["local_path"])
                if candidate_path.exists():
                    try:
                        candidate_path.unlink()
                        print(f"  🗑️ Removed: {candidate_path.name}")
                    except Exception as e:
                        print(f"  ⚠️ Failed to delete {candidate_path.name}: {e}")
            
            slide_images[idx] = final_images
            print(f"✓ Slide {idx} has {len(final_images)} image(s)")
        else:
            print(f"✗ No images for slide {idx}")
    
    print(f"\n{'='*50}")
    print(f"TOTAL: {len(slide_images)} slides with images")
    print(f"{'='*50}\n")
    
    return slide_images


def save_image_metadata(slide_images: Dict[int, List[Dict]], output_path: Path):
    """Save image metadata to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(slide_images, indent=2), encoding='utf-8')
