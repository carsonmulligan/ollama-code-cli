#!/bin/bash

# Local Code Agent Setup Script
# This script sets up your local code agent environment

set -e

echo "🤖 Local Code Agent Setup"
echo "========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Ollama is installed
echo -e "${BLUE}Checking for Ollama...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Ollama not found!${NC}"
    echo ""
    echo "Please install Ollama first:"
    echo "  macOS: brew install ollama"
    echo "  Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    echo "Visit: https://ollama.ai"
    exit 1
fi

echo -e "${GREEN}✓ Ollama is installed${NC}"

# Check if Ollama is running
echo -e "${BLUE}Checking if Ollama is running...${NC}"
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}Ollama server is not running${NC}"
    echo ""
    echo "Starting Ollama in the background..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
    
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama server started${NC}"
    else
        echo -e "${RED}✗ Failed to start Ollama${NC}"
        echo "Please run: ollama serve"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Ollama server is running${NC}"
fi

# Check for models
echo -e "${BLUE}Checking for installed models...${NC}"
MODELS=$(ollama list 2>/dev/null | tail -n +2 | wc -l)

if [ "$MODELS" -eq 0 ]; then
    echo -e "${YELLOW}No models found!${NC}"
    echo ""
    echo "Recommended models for coding:"
    echo "  1. qwen2.5-coder:7b  (Best for code, 4.7GB)"
    echo "  2. llama3.2:3b       (Fast, 2GB)"
    echo "  3. deepseek-coder-v2 (Excellent, 8.9GB)"
    echo ""
    read -p "Would you like to pull qwen2.5-coder:7b? (recommended) [Y/n]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo "Downloading qwen2.5-coder:7b (this may take a few minutes)..."
        ollama pull qwen2.5-coder:7b
        echo -e "${GREEN}✓ Model downloaded${NC}"
    else
        echo "Please pull a model manually:"
        echo "  ollama pull llama3.2:3b"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Found $MODELS installed model(s)${NC}"
    echo ""
    echo "Installed models:"
    ollama list
fi

# Install Python dependencies
echo ""
echo -e "${BLUE}Installing Python dependencies...${NC}"

if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt --break-system-packages 2>/dev/null || \
    pip3 install -r requirements.txt --user 2>/dev/null || \
    pip3 install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}pip3 not found, attempting to use pip...${NC}"
    pip install -r requirements.txt --break-system-packages 2>/dev/null || \
    pip install -r requirements.txt --user 2>/dev/null || \
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Make scripts executable
echo ""
echo -e "${BLUE}Making scripts executable...${NC}"
chmod +x enhanced_code_agent.py 2>/dev/null || true
chmod +x local_code_agent.py 2>/dev/null || true
echo -e "${GREEN}✓ Scripts are executable${NC}"

# Done!
echo ""
echo -e "${GREEN}=========================${NC}"
echo -e "${GREEN}Setup complete! 🎉${NC}"
echo -e "${GREEN}=========================${NC}"
echo ""
echo "To start the agent, run:"
echo -e "  ${BLUE}python3 enhanced_code_agent.py${NC}"
echo ""
echo "Or:"
echo -e "  ${BLUE}./enhanced_code_agent.py${NC}"
echo ""
echo "For help, type:"
echo -e "  ${BLUE}/help${NC}"
echo ""
echo "Happy coding! 🚀"