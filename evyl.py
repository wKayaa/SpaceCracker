#!/usr/bin/env python3
"""
Evyl Framework v3.1 Entry Point
SpaceCracker v3.1 with Evyl-style command interface
"""

import sys
import os

# Add the parent directory to the path so we can import spacecracker
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spacecracker.cli import main

if __name__ == "__main__":
    sys.exit(main())