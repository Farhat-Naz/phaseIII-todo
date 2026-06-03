"""
AWS Lambda handler for FastAPI backend using Mangum.

This file provides the Lambda function handler that wraps the FastAPI application
using Mangum, an adapter for running ASGI applications on AWS Lambda.

Environment Variables Required:
    - DATABASE_URL: PostgreSQL connection string
    - SECRET_KEY: JWT signing secret
    - REFRESH_TOKEN_SECRET: Refresh token signing secret
    - CORS_ORIGINS: Comma-separated list of allowed origins
    - OPENAI_API_KEY: OpenAI API key for chatbot (optional)
    - All other environment variables from .env.example

Usage:
    This file is used as the Lambda function handler.
    Set the handler to: lambda_handler.handler
"""
from mangum import Mangum
from index import app
import logging

# Configure logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create the Mangum handler
# This wraps the FastAPI app and makes it compatible with AWS Lambda
handler = Mangum(app, lifespan="off")

# The handler function is called by AWS Lambda for each request
# Format: lambda_handler.handler in Lambda configuration
