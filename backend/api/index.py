"""
Vercel serverless function handler.
Uses Mangum to adapt FastAPI for serverless environments.
"""
import sys
import os

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import the FastAPI app
from index import app

# Use Mangum to wrap FastAPI for Vercel serverless
from mangum import Mangum

# This is the handler that Vercel will invoke
handler = Mangum(app, lifespan="off")
