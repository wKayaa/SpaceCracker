#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(__file__))

# Make the scanner executable with python -m
from scanner import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())