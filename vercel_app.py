"""
Vercel ASGI entry point - kept separate from app/main.py
"""
from app.main import app

# Vercel expects this variable name
app = app
