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

# Make launcher executable
echo "🔧 Making launcher executable..."
chmod +x launch.py

# Create results directory
echo "📁 Creating results directory..."
mkdir -p results

echo
echo "✅ SpaceCracker is ready to use!"
echo
echo "Quick start examples:"
echo "  Basic scan: python3 launch.py run demo_targets.txt"
echo "  Interactive mode: python3 launch.py --interactive"
echo "  List modules: python3 launch.py --list-modules"
echo "  High performance: python3 launch.py run targets.txt --threads 50"
echo
echo "For help: python3 launch.py --help"
echo "For documentation: see README.md"