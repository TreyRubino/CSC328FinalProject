#!/usr/bin/env python3

import sys
import os

# Add the project root directory to Python's path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

try:
    pass
except Exception as e:
    print(f"An error has occurred: {e}")
