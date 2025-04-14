#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Dict, List, Any
import datetime

# 导入项目模块
from src.config import (
    FRESHRSS_DB_PATH, 
    AI_API_KEY, 
    AI_MODEL, 
    AI_BASE_URL,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID, 
    HOURS_BACK,
    TARGET_WORD_COUNT
)
from src.utils import (
    get_recent_entries, 
    group_entries_by_category,
    AIProcessor,
    TelegramSender
)

# 获取记录器
logger = logging.getLogger(__name__)

def generate_digest(entries: List[Dict[Any, Any]]) -> str:
    """
    Generate a digest from the RSS entries
    
    Args:
        entries: List of entry dictionaries
        
    Returns:
        Generated digest text including timestamp header
    """
    logger.info(f"Generating digest from {len(entries)} entries using single AI call.")
    
    # Initialize AI processor
    ai_processor = AIProcessor(
        api_key=AI_API_KEY,
        model=AI_MODEL,
        base_url=AI_BASE_URL
    )
    
    # Directly generate the full digest using the new method
    ai_generated_digest = ai_processor.generate_digest(entries=entries)

    if not ai_generated_digest or len(ai_generated_digest.strip()) == 0:
        logger.error("AIProcessor generated an empty or invalid digest.")
        # Return a more informative message or raise an exception
        return "Failed to generate digest: AI returned empty content."
    
    # Format the current datetime
    now = datetime.datetime.now()
    # Use yyyy/mm/dd format as requested
    formatted_datetime = now.strftime("%Y/%m/%d %H:%M")

    # Create the title string
    title = f"# RSS 新闻摘要 - {formatted_datetime}"

    # Prepend the title and a blank line to the AI generated content
    full_digest_with_title = f"{title}\n\n{ai_generated_digest}"

    logger.info(f"Digest generated successfully, final length (incl. title): {len(full_digest_with_title)} characters.")
    # Log beginning of the final digest with title
    logger.debug(f"Final digest content (first 150 chars): {full_digest_with_title[:150]}...")
    
    return full_digest_with_title

def send_digest(digest_text: str) -> Dict[str, Any]:
    """
    Send the digest via Telegram
    
    Args:
        digest_text: Digest text to send
        
    Returns:
        Response from Telegram
    """
    logger.info("Sending digest via Telegram")
    
    # 记录摘要中的分类顺序
    categories_order = [line.strip('# ') for line in digest_text.split('\n') if line.startswith('## ')]
    logger.info(f"Sending digest with categories in this order: {categories_order}")
    
    telegram = TelegramSender(
        bot_token=TELEGRAM_BOT_TOKEN,
        chat_id=TELEGRAM_CHAT_ID
    )
    
    response = telegram.send_message(digest_text)
    
    if response.get("success"):
        logger.info("Digest sent successfully")
    else:
        logger.error(f"Failed to send digest: {response.get('error')}")
        
    return response

def run_digest_process(hours_back: int = None, send: bool = True) -> str:
    """
    Run the complete digest generation and sending process
    
    Args:
        hours_back: Hours back to look for entries (overrides config)
        send: Whether to send the digest via Telegram
        
    Returns:
        Generated digest text
    """
    # Use config value if not provided
    if hours_back is None:
        hours_back = HOURS_BACK
        
    logger.info(f"Starting RSS digest process (looking back {hours_back} hours)")
    
    # Get entries from database
    entries = get_recent_entries(
        db_path=FRESHRSS_DB_PATH,
        hours_back=hours_back
    )
    
    if not entries:
        message = f"No entries found in the past {hours_back} hours"
        logger.warning(message)
        return message
        
    logger.info(f"Found {len(entries)} entries in the past {hours_back} hours")
    
    # Generate digest
    digest = generate_digest(entries)
    
    # Send digest if requested
    if send:
        send_digest(digest)
    
    return digest 