#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# FreshRSS database configuration
FRESHRSS_DB_PATH = os.getenv('FRESHRSS_DB_PATH')
USERNAME = os.getenv('USERNAME')
HOURS_BACK = int(os.getenv('HOURS_BACK', "8"))

# AI API configuration
# Using OpenAI as an example, replace with your preferred AI provider
AI_PROVIDER = os.getenv('AI_PROVIDER')  # Options: openai, anthropic, etc.
AI_API_KEY = os.getenv('AI_API_KEY')
AI_MODEL = os.getenv('AI_MODEL')  # Change to your preferred model
AI_BASE_URL = os.getenv('AI_BASE_URL')  # Default for OpenAI, override for VolceEngine

# Output configuration
TARGET_WORD_COUNT = int(os.getenv('TARGET_WORD_COUNT', "1000"))
OUTPUT_LANGUAGE = os.getenv('OUTPUT_LANGUAGE', "zh")  # Chinese

# Telegram Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
