"""
Vercel serverless entry point for FastAPI application.
This file adapts the FastAPI app to run on Vercel's serverless functions.
"""
from mangum import Mangum
from app.main import app

# Wrap FastAPI with Mangum for AWS Lambda/Vercel compatibility
handler = Mangum(app, lifespan="off")
