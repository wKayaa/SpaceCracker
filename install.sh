#!/bin/bash
# SpaceCracker Installation and Setup Script

echo "🚀 SpaceCracker - Advanced Web Vulnerability Scanner"
echo "=================================================="
echo

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Make scanner executable
echo "🔧 Making scanner executable..."
chmod +x scanner.py

# Create results directory
echo "📁 Creating results directory..."
mkdir -p results

echo
echo "✅ SpaceCracker is ready to use!"
echo
echo "Quick start examples:"
echo "  Basic scan: python3 scanner.py -t examples/targets.txt"
echo "  Specific modules: python3 scanner.py -t examples/targets.txt --modules ggb js git"
echo "  High performance: python3 scanner.py -t targets.txt --threads 50 --rate-limit 10"
echo
echo "For help: python3 scanner.py --help"
echo "For documentation: see README.md"