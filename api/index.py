"""
Vercel serverless entry point for FastAPI application.
This file adapts the FastAPI app to run on Vercel's serverless functions.
"""
from app.main import app

# Vercel uses this handler
handler = app
