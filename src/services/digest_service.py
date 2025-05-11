#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Dict, List, Any
import datetime
import json

# 导入项目模块
from src.config import (
    FRESHRSS_DB_PATH, 
    AI_API_KEY, 
    AI_MODEL, 
    AI_BASE_URL,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID, 
    HOURS_BACK,
    PROJECT_ROOT
)
from src.utils import (
    get_recent_entries, 
    AIProcessor,
    TelegramSender
)

# 获取记录器
logger = logging.getLogger(__name__)

# Define the path for storing processed entry IDs
PROCESSED_IDS_FILE = PROJECT_ROOT / "logs" / "processed_entry_ids.json"

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
    
    # Generate the full digest
    ai_generated_digest = ai_processor.generate_digest(entries=entries)

    if not ai_generated_digest or len(ai_generated_digest.strip()) == 0:
        logger.error("AIProcessor generated an empty or invalid digest.")
        return "Failed to generate digest: AI returned empty content."
    
    # Format the current datetime
    formatted_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")

    # Create the title and full digest
    title = f"# RSS 新闻摘要 - {formatted_datetime}"
    full_digest_with_title = f"{title}\n\n{ai_generated_digest}"

    logger.info(f"Digest generated successfully, final length: {len(full_digest_with_title)} characters.")
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

def _update_processed_ids(entry_ids: List[int]):
    """Helper function to update the processed IDs file."""
    try:
        with open(PROCESSED_IDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(entry_ids, f, ensure_ascii=False, indent=4)
        logger.info(f"Successfully updated processed IDs file with {len(entry_ids)} entries: {PROCESSED_IDS_FILE}")
    except Exception as e:
        logger.error(f"Failed to update processed IDs file {PROCESSED_IDS_FILE}: {e}")

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
        
    logger.info(f"Starting RSS digest process (looking back {hours_back} hours, using processed IDs file: {PROCESSED_IDS_FILE})")
    
    # Get entries from database
    entries = get_recent_entries(
        db_path=FRESHRSS_DB_PATH,
        hours_back=hours_back,
        processed_ids_file_path=str(PROCESSED_IDS_FILE)
    )
    
    if not entries:
        message = f"No new entries found in the past {hours_back} hours (after filtering processed IDs)."
        logger.warning(message)
        return message
        
    logger.info(f"Found {len(entries)} new entries in the past {hours_back} hours (after filtering)")
    
    # Generate digest
    digest = generate_digest(entries)

    # Check if digest generation was successful before updating processed IDs
    if "Failed to generate digest" not in digest and digest.strip():
        current_entry_ids = [entry['id'] for entry in entries]
        _update_processed_ids(current_entry_ids)
        
        # Send digest if requested
        if send:
            send_digest(digest)
    else:
        logger.error("Digest generation failed or produced empty content. Processed IDs will not be updated.")
    
    return digest 