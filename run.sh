#!/bin/bash

# Change to the script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the digest generator
python main.py "$@"

# If venv was activated, deactivate it
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 