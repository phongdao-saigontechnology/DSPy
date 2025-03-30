#!/bin/bash

# Create required directories
python setup.py

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set."
    echo "Please set it using: export OPENAI_API_KEY=your_api_key_here"
    exit 1
fi

# Run the FastAPI application
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
