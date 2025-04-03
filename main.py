#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import argparse
import datetime
from typing import Dict, List, Any

# Import project modules
import config
from db_utils import get_recent_entries, group_entries_by_category
from ai_utils import AIProcessor
from telegram_utils import TelegramSender

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'rss_digest.log'))
    ]
)

logger = logging.getLogger(__name__)

def generate_digest(entries: List[Dict[Any, Any]]) -> str:
    """
    Generate a digest from the RSS entries
    
    Args:
        entries: List of entry dictionaries
        
    Returns:
        Generated digest text
    """
    logger.info(f"Generating digest from {len(entries)} entries")
    
    # Initialize AI processor
    ai_processor = AIProcessor(
        api_key=config.AI_API_KEY,
        model=config.AI_MODEL,
        base_url=config.AI_BASE_URL
    )
    
    # Group entries by category
    grouped_entries = group_entries_by_category(entries)
    
    # Log category counts
    for category, category_entries in grouped_entries.items():
        logger.info(f"Category '{category}': {len(category_entries)} entries")
    
    # Generate summary for each category
    category_summaries = {}
    for category, category_entries in grouped_entries.items():
        if category_entries:
            logger.info(f"Generating summary for category: {category}")
            summary = ai_processor.generate_category_summary(
                entries=category_entries,
                category=category,
                word_limit=int(config.TARGET_WORD_COUNT / max(1, len(grouped_entries)))
            )
            if summary and len(summary.strip()) > 0:
                logger.info(f"Summary for '{category}' generated successfully: {len(summary)} characters")
                category_summaries[category] = summary
            else:
                logger.warning(f"Empty or invalid summary generated for '{category}'")
    
    # Debug log all summaries
    for category, summary in category_summaries.items():
        logger.debug(f"Category '{category}' summary: {summary[:100]}...")
    
    # Generate full digest
    logger.info("Generating full digest")
    logger.info(f"Categories with summaries: {list(category_summaries.keys())}")
    full_digest = ai_processor.generate_full_digest(
        category_summaries=category_summaries,
        word_limit=config.TARGET_WORD_COUNT
    )
    
    # Check categories in final digest
    categories_in_digest = [line.strip('# ') for line in full_digest.split('\n') if line.startswith('## ')]
    logger.info(f"Categories in final digest (ordered): {categories_in_digest}")
    
    # Check for missing categories
    missing_categories = set(category_summaries.keys()) - set(categories_in_digest)
    if missing_categories:
        logger.warning(f"Categories missing from final digest: {missing_categories}")
    
    return full_digest

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
        bot_token=config.TELEGRAM_BOT_TOKEN,
        chat_id=config.TELEGRAM_CHAT_ID
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
        hours_back = config.HOURS_BACK
        
    logger.info(f"Starting RSS digest process (looking back {hours_back} hours)")
    
    # Get entries from database
    entries = get_recent_entries(
        db_path=config.FRESHRSS_DB_PATH,
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

def main():
    """Main entry point with command line argument parsing"""
    parser = argparse.ArgumentParser(description='RSS Feed Digest Generator')
    parser.add_argument('--hours', type=int, default=None, 
                        help='Hours back to look for entries (default: from config)')
    parser.add_argument('--no-send', action='store_true', 
                        help='Generate digest but do not send via Telegram')
    parser.add_argument('--save', action='store_true', 
                        help='Save digest to a file')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Run the process
    digest = run_digest_process(
        hours_back=args.hours,
        send=not args.no_send
    )
    
    # Save to file if requested
    if args.save:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(os.path.dirname(__file__), f"digest_{timestamp}.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest)
        logger.info(f"Digest saved to {filename}")
    
    # Print summary to console
    print(f"Digest generation completed. Length: {len(digest)} characters")
    
if __name__ == "__main__":
    main() 