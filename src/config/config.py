#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
from pathlib import Path

# 确定项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# FreshRSS database configuration
FRESHRSS_DB_PATH = os.getenv('FRESHRSS_DB_PATH')
USERNAME = os.getenv('USERNAME')
HOURS_BACK = int(os.getenv('HOURS_BACK', "8"))

# AI API configuration
AI_API_KEY = os.getenv('GOOGLE_API_KEY')
AI_MODEL = os.getenv('GOOGLE_MODEL_ID')  
AI_BASE_URL = os.getenv('GOOGLE_BASE_URL')  

# Telegram Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 日志配置
LOG_DIR = PROJECT_ROOT / 'logs'
DIGEST_LOG_PATH = LOG_DIR / 'rss_digest.log'
API_DEBUG_LOG_PATH = LOG_DIR / 'api_debug.log'
