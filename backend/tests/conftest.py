"""
conftest.py — Pytest configuration for the Resume Shapeshifter backend.

Sets up the Python path so `backend.*` imports resolve correctly
when running pytest from the project root.
"""

import sys
import os

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
