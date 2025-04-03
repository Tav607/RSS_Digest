#!/bin/bash

# Script to set up the RSS Digest environment

# Change to the script directory
cd "$(dirname "$0")"

echo "Setting up RSS Digest environment..."

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your API keys and configuration"
fi

# Make run script executable
chmod +x run.sh main.py

echo "Setup complete!"
echo "Next steps:"
echo "1. Edit .env file with your API keys and configuration"
echo "2. Run './run.sh' to test"
echo "3. Set up cron job from crontab.example for automatic execution" 