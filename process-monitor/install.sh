#!/bin/bash
# Process Monitor - Installation script for Termux

echo "📦 Installing Process Monitor..."

# Install Python if needed
if ! command -v python3 &> /dev/null; then
    echo "Installing Python3..."
    pkg install python3 -y
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make main.py executable
chmod +x main.py

echo "✅ Installation complete!"
echo ""
echo "To run: python3 main.py"
echo "Or: ./main.py"
