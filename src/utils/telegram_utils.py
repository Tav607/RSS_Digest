#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import logging
from typing import Dict, Any

# 创建命名记录器
logger = logging.getLogger(__name__)

class TelegramSender:
    """
    Class for sending messages via Telegram bot
    """
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize the Telegram sender
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        
    def send_message(self, text: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        """
        Send a message via Telegram
        
        Args:
            text: Text message to send
            parse_mode: Message parse mode (Markdown, HTML, or empty string for plain text)
            
        Returns:
            Response from Telegram API
        """
        logger.info(f"Sending message to Telegram, length: {len(text)} characters")
        logger.debug(f"Message categories included: {[line.strip('# ') for line in text.split('\n') if line.startswith('## ')]}")
        
        # Split long messages if needed (Telegram has a 4096 character limit)
        if len(text) > 4000:
            return self._send_long_message(text, parse_mode)
            
        endpoint = f"{self.api_url}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": text
        }
        
        # Only add parse_mode if it's provided (not empty)
        if parse_mode:
            data["parse_mode"] = parse_mode
        
        try:
            response = requests.post(endpoint, data=data)
            result = response.json()
            
            if not result.get("ok"):
                error_msg = f"Failed to send Telegram message: {result.get('description', 'Unknown error')}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
            return {"success": True, "result": result}
        except Exception as e:
            error_msg = f"Error sending Telegram message: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
            
    def _send_long_message(self, text: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        """
        Send a message that exceeds Telegram's character limit by splitting it
        
        Args:
            text: Text message to send
            parse_mode: Message parse mode
            
        Returns:
            Response from the last message sent
        """
        # Split by double newline to try to break at logical points (paragraphs)
        chunks = text.split("\n\n")
        current_chunk = ""
        last_response = None
        
        for chunk in chunks:
            # Check if adding this chunk would exceed the limit
            if len(current_chunk) + len(chunk) + 2 <= 4000:  # +2 for the newlines
                if current_chunk:
                    current_chunk += "\n\n" + chunk
                else:
                    current_chunk = chunk
            else:
                # Send the current chunk and start a new one
                response = self.send_message(current_chunk, parse_mode)
                last_response = response
                current_chunk = chunk
        
        # Send any remaining content
        if current_chunk:
            response = self.send_message(current_chunk, parse_mode)
            last_response = response
            
        return last_response or {"success": False, "error": "No content to send"} 