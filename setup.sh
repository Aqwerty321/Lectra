#!/bin/bash
# LECTRA Setup Script for Linux/macOS
# This script sets up LECTRA for development or production use

set -e  # Exit on error

echo "================================================"
echo "  LECTRA - Automated Lecture Generation System"
echo "  Setup Script v2.0"
echo "================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# Check system dependencies
echo "Step 1: Checking system dependencies..."
echo "----------------------------------------"

MISSING_DEPS=0

if ! check_command python3; then
    print_info "Install Python 3.11+: https://www.python.org/downloads/"
    MISSING_DEPS=1
fi

if ! check_command node; then
    print_info "Install Node.js 18+: https://nodejs.org/"
    MISSING_DEPS=1
fi

if ! check_command cargo; then
    print_info "Install Rust: https://rustup.rs/"
    MISSING_DEPS=1
fi

if ! check_command ffmpeg; then
    print_info "Install FFmpeg: https://ffmpeg.org/download.html"
    MISSING_DEPS=1
fi

if [ $MISSING_DEPS -eq 1 ]; then
    print_error "Please install missing dependencies and re-run this script"
    exit 1
fi

echo ""

# Setup Python backend
echo "Step 2: Setting up Python backend..."
echo "-------------------------------------"

cd sidecar

if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

print_info "Activating virtual environment..."
source venv/bin/activate

print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

cd ..
echo ""

# Setup environment file
echo "Step 3: Setting up environment configuration..."
echo "-----------------------------------------------"

if [ ! -f ".env" ]; then
    print_info "Creating .env file from .env.example..."
    cp .env.example .env
    
    # Set OS-specific defaults
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' 's|FFMPEG_BIN=.*|FFMPEG_BIN=/opt/homebrew/bin/ffmpeg|' .env
        sed -i '' 's|OUTPUT_ROOT=.*|OUTPUT_ROOT=~/Lectures|' .env
    else
        # Linux
        sed -i 's|FFMPEG_BIN=.*|FFMPEG_BIN=/usr/bin/ffmpeg|' .env
        sed -i 's|OUTPUT_ROOT=.*|OUTPUT_ROOT=~/Lectures|' .env
    fi
    
    print_success ".env file created"
    print_info "Please edit .env file with your settings"
else
    print_success ".env file already exists"
fi

# Create output directory
OUTPUT_DIR="$HOME/Lectures"
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
    print_success "Created output directory: $OUTPUT_DIR"
else
    print_success "Output directory exists: $OUTPUT_DIR"
fi

echo ""

# Setup Node frontend
echo "Step 4: Setting up Tauri frontend..."
echo "------------------------------------"

cd ui

if [ ! -d "node_modules" ]; then
    print_info "Installing Node dependencies (this may take a few minutes)..."
    npm install
    print_success "Node dependencies installed"
else
    print_success "Node dependencies already installed"
fi

cd ..
echo ""

# Check Ollama
echo "Step 5: Checking Ollama installation..."
echo "---------------------------------------"

if command -v ollama &> /dev/null; then
    print_success "Ollama is installed"
    
    # Check if model is installed
    if ollama list | grep -q "llama3.2:3b"; then
        print_success "llama3.2:3b model is installed"
    else
        print_info "Downloading llama3.2:3b model (this may take a while)..."
        ollama pull llama3.2:3b
        print_success "Model downloaded"
    fi
else
    print_error "Ollama is not installed"
    print_info "Install from: https://ollama.ai"
    print_info "Then run: ollama pull llama3.2:3b"
fi

echo ""

# Create launch script
echo "Step 6: Creating launch scripts..."
echo "----------------------------------"

cat > launch.sh << 'EOF'
#!/bin/bash
# LECTRA Launch Script

echo "Starting LECTRA..."

# Start backend in background
cd sidecar
source venv/bin/activate
export PYTHONPATH="$(pwd)"
python -m uvicorn app.api:app --host 127.0.0.1 --port 8765 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
sleep 3

# Start frontend
cd ../ui
npm run tauri dev

# Cleanup on exit
kill $BACKEND_PID
EOF

chmod +x launch.sh
print_success "Created launch.sh"

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env file if needed: nano .env"
echo "  2. Start LECTRA: ./launch.sh"
echo ""
echo "For production build:"
echo "  cd ui && npm run tauri build"
echo ""
print_success "Setup completed successfully!"
