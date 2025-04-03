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
FRESHRSS_DB_PATH = os.getenv('FRESHRSS_DB_PATH', "/home/paladinllq/myrss/freshrss_data/users/tav607/db.sqlite")
USERNAME = os.getenv('USERNAME', "tav607")
HOURS_BACK = int(os.getenv('HOURS_BACK', "8"))

# AI API configuration
# Using OpenAI as an example, replace with your preferred AI provider
AI_PROVIDER = os.getenv('AI_PROVIDER', "openai")  # Options: openai, anthropic, etc.
AI_API_KEY = os.getenv('AI_API_KEY', "your_api_key_here")
AI_MODEL = os.getenv('AI_MODEL', "gpt-4o")  # Change to your preferred model
AI_BASE_URL = os.getenv('AI_BASE_URL', "https://api.openai.com/v1")  # Default for OpenAI, override for VolceEngine

# Output configuration
TARGET_WORD_COUNT = int(os.getenv('TARGET_WORD_COUNT', "1000"))
OUTPUT_LANGUAGE = os.getenv('OUTPUT_LANGUAGE', "zh")  # Chinese

# Telegram Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', "your_telegram_bot_token_here")
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', "your_telegram_chat_id_here")

# Optional: Schedule configuration
SCHEDULE_INTERVAL_HOURS = int(os.getenv('SCHEDULE_INTERVAL_HOURS', "8"))  # How often to run the digest 