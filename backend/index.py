"""
Vercel serverless function entry point for FastAPI backend.

This file imports the FastAPI app from app.main and exports it for Vercel.
"""
from app.main import app

# Export the FastAPI app for Vercel
# Vercel will automatically detect this and serve the app
