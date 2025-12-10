"""
Vercel ASGI entry point - uses Mangum to adapt FastAPI for Vercel
"""
from mangum import Mangum
from app.main import app as fastapi_app

# Wrap FastAPI with Mangum for AWS Lambda/Vercel compatibility
handler = Mangum(fastapi_app, lifespan="off")

# Vercel looks for these variable names
app = handler
