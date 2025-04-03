#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import requests
import datetime
from typing import Dict, List, Any, Union

# 创建命名记录器
logger = logging.getLogger(__name__)

class AIProcessor:
    """
    Class for processing content through AI models and generating summaries
    """
    def __init__(self, api_key: str, model: str, base_url: str):
        """
        Initialize the AI processor
        
        Args:
            api_key: API key for the AI service
            model: AI model to use
            base_url: Base URL for the VolceEngine API
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.api_url = f"{base_url}/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
    def generate_category_summary(self, entries: List[Dict[Any, Any]], category: str, 
                                 language: str = None, word_limit: int = 500) -> str:
        """
        Generate a summary for a specific category of RSS entries
        
        Args:
            entries: List of entry dictionaries
            category: Original RSS category name
            language: Output language (deprecated, output is hardcoded to Chinese)
            word_limit: Approximate word limit for the summary
            
        Returns:
            A summary of the entries in the specified category
        """
        if not entries:
            return f"No content for category: {category}"
            
        # Prepare content for the AI
        content_text = ""
        for entry in entries[:50]:  # Limit to top 50 entries to avoid token limits
            content_text += f"标题: {entry['title']}\n"
            content_text += f"来源: {entry['feed_name']}\n"
            content_text += f"内容摘要: {self._truncate_content(entry['content'])}\n\n"
            
        prompt = f"""
        请阅读以下汇集的RSS文章, 并根据所有文章的信息生成一篇全面的中文摘要总结。要求如下：
        1. 以bullet point的形式输出, 每条bullet point不超过100字;
        2. 每条bullet point之间紧凑排列, 不要添加额外空行;
        3. 输出的内容应逻辑清晰、语言简洁、条理分明，能够准确反映所有文章的整体内容和精髓。
        4. 这些内容都属于"{category}"类别。
        5. 输出内容保持在约{word_limit}字以内。

        RSS条目内容:
        {content_text}
        """
        
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一位专业的新闻编辑，擅长总结新闻内容。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                summary = result["choices"][0]["message"]["content"].strip()
                logger.info(f"Category '{category}' summary generated, length: {len(summary)} characters")
                logger.debug(f"Category '{category}' summary content: {summary[:100]}...")
                return summary
            else:
                error_msg = f"API request failed with status code: {response.status_code}, response: {response.text}"
                logger.error(error_msg)
                return f"无法为'{category}'生成摘要。错误: {error_msg}"
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"无法为'{category}'生成摘要。错误: {str(e)}"
    
    def generate_full_digest(self, category_summaries: Dict[str, str], 
                           language: str = None, word_limit: int = 2000) -> str:
        """
        Generate a full digest by concatenating all category summaries
        
        Args:
            category_summaries: Dictionary of category names and their summaries
            language: Output language (not used, included for backwards compatibility)
            word_limit: Not used anymore, included for backwards compatibility
            
        Returns:
            A complete digest combining all categories
        """
        current_date = self._get_formatted_date()
        
        # Create title with current date
        full_digest = f"# RSS 新闻摘要 - {current_date} {datetime.datetime.now().strftime('%H:%M')}\n\n"
        
        # 按指定顺序排列分类
        priority_order = ["AI and Tech", "PC and Smartphone", "World News"]
        
        # 首先添加高优先级的分类
        for category in priority_order:
            if category in category_summaries:
                logger.info(f"Adding priority category '{category}' to digest, summary length: {len(category_summaries[category])} characters")
                full_digest += f"## {category}\n\n{category_summaries[category]}\n\n"
        
        # 然后添加剩余的分类
        for category, summary in category_summaries.items():
            if category not in priority_order:
                logger.info(f"Adding other category '{category}' to digest, summary length: {len(summary)} characters")
                full_digest += f"## {category}\n\n{summary}\n\n"
            
        return full_digest

    def _truncate_content(self, content: str, max_chars: int = 2000) -> str:
        """Truncate content to a reasonable length"""
        if len(content) <= max_chars:
            return content
        return content[:max_chars] + "..."
        
    def _get_formatted_date(self) -> str:
        """Get current date formatted in Chinese style"""
        now = datetime.datetime.now()
        return f"{now.year}年{now.month}月{now.day}日" 