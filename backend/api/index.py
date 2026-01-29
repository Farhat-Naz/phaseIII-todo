"""
Vercel API entry point.
Re-exports the FastAPI app from the main index.py file.
"""
import sys
import os

# Add parent directory to path to import from index.py
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the app from the main index.py
from index import app

# Export for Vercel
__all__ = ["app"]
