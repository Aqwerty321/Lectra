"""Entry point for PyInstaller - launches the FastAPI sidecar."""

import sys
import os
from pathlib import Path

# Add the app directory to path so imports work
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Now import and run the app
if __name__ == "__main__":
    import uvicorn
    from app.api import app
    
    # Get port from command line args
    port = 8765
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
    
    # Run uvicorn
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
