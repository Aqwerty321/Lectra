"""Test the upload endpoint directly with a sample PDF."""

import sys
import requests
from pathlib import Path
import json

# Try to create a simple test PDF
def create_test_pdf():
    """Create a simple test PDF file."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        test_dir = Path.home() / "Lectures" / "_test_upload"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_path = test_dir / "test_document.pdf"
        
        # Create PDF
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.setFont("Helvetica", 12)
        
        # Add content
        y = 750
        c.drawString(100, y, "Introduction to Machine Learning")
        y -= 30
        c.drawString(100, y, "Machine Learning is a branch of artificial intelligence.")
        y -= 20
        c.drawString(100, y, "It focuses on building systems that can learn from data.")
        y -= 40
        
        c.drawString(100, y, "Types of Machine Learning:")
        y -= 25
        c.drawString(120, y, "1. Supervised Learning - Learning from labeled data")
        y -= 20
        c.drawString(120, y, "2. Unsupervised Learning - Finding patterns in unlabeled data")
        y -= 20
        c.drawString(120, y, "3. Reinforcement Learning - Learning through trial and error")
        y -= 40
        
        c.drawString(100, y, "Applications:")
        y -= 25
        c.drawString(120, y, "- Image Recognition")
        y -= 20
        c.drawString(120, y, "- Natural Language Processing")
        y -= 20
        c.drawString(120, y, "- Recommendation Systems")
        y -= 20
        c.drawString(120, y, "- Autonomous Vehicles")
        
        c.save()
        
        print(f"✅ Created test PDF: {pdf_path}")
        return pdf_path
        
    except ImportError:
        print("⚠️  reportlab not installed, creating text file instead")
        return None


def test_upload_endpoint():
    """Test the document upload endpoint."""
    
    print("\n" + "="*60)
    print("TESTING DOCUMENT UPLOAD ENDPOINT")
    print("="*60 + "\n")
    
    # Create or use existing test PDF
    pdf_path = create_test_pdf()
    
    if not pdf_path or not pdf_path.exists():
        print("❌ Could not create test PDF")
        return False
    
    print(f"📄 Using test file: {pdf_path.name}")
    print(f"   Size: {pdf_path.stat().st_size:,} bytes\n")
    
    # Upload the document
    print("🚀 Uploading document to backend...")
    
    url = "http://127.0.0.1:8765/upload_document"
    project_name = "test_upload"
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path.name, f, 'application/pdf')}
            data = {'project': project_name}
            
            response = requests.post(url, files=files, data=data, timeout=60)
        
        print(f"📥 Response status: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Upload successful!\n")
            print("📊 Response data:")
            print(f"   Status: {result.get('status')}")
            print(f"   Filename: {result.get('filename')}")
            print(f"   Collection: {result.get('collection_name')}")
            print(f"   Characters: {result.get('char_count', 0):,}")
            print(f"   Chunks: {result.get('chunk_count', 0)}")
            print(f"   Topics: {len(result.get('topics', []))}")
            
            if result.get('topics'):
                print(f"\n🎯 Detected Topics:")
                for i, topic in enumerate(result['topics'][:10], 1):
                    print(f"   {i}. {topic}")
            
            print("\n" + "="*60)
            print("✅ UPLOAD TEST PASSED!")
            print("="*60)
            print("\n💡 The document upload pipeline is working correctly!")
            print("   You can now use this in the Tauri app.\n")
            
            return True
        else:
            print(f"❌ Upload failed!")
            print(f"   Status code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend!")
        print("   Make sure the backend server is running on port 8765")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = test_upload_endpoint()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
