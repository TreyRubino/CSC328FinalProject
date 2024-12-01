#!/usr/bin/env python3
import sys
import os

# Add the project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# import any modules you need such as Utility, Request, or Response

# Start server logic (main.py)
try:
    pass
except Exception as e:
    print(f"An error has occurred: {e}")
