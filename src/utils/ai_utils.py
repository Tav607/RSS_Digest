#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import datetime
from typing import Dict, List, Any, Union
from openai import OpenAI

# 从配置导入API调试日志路径
from src.config import API_DEBUG_LOG_PATH

# 创建命名记录器
logger = logging.getLogger(__name__)

# 为API调用创建专用的调试记录器
api_logger = logging.getLogger("api")
api_handler = logging.FileHandler(API_DEBUG_LOG_PATH)
api_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
api_logger.addHandler(api_handler)
api_logger.setLevel(logging.DEBUG)

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
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        api_logger.debug(f"AIProcessor initialized with model: {model}, base_url: {base_url}")
        
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
        请阅读以下RSS文章集合，基于所有内容生成一份结构化、简洁明了的中文摘要，要求如下：
        1. 使用bullet point格式输出，每条不超过100字；
        2. 所有bullet point之间不要留空行，排列紧凑；
        3. 内容应信息密度高、语言简洁有力、条理清晰，准确反映整体信息和关键信息点；
        4. 本次内容归属类别："{category}"；
        5. 控制总字数约为**{word_limit}字以内**，确保摘要紧凑有效。

        RSS条目内容:
        {content_text}
        """
        
        try:
            api_logger.debug(f"Generating summary for category: {category} with {len(entries)} entries")
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位资深新闻编辑，擅长从大量资讯中提取核心信息，具备高度的语言概括能力与逻辑组织能力。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            
            summary = completion.choices[0].message.content.strip()
            logger.info(f"Category '{category}' summary generated, length: {len(summary)} characters")
            logger.debug(f"Category '{category}' summary content: {summary[:100]}...")
            api_logger.debug(f"AI summary response for '{category}': length={len(summary)} chars")
            return summary
        except Exception as e:
            error_msg = f"Error generating summary: {str(e)}"
            logger.error(error_msg)
            api_logger.error(f"AI API error for '{category}': {str(e)}")
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
        api_logger.debug(f"Generating full digest with {len(category_summaries)} categories")
        
        current_date = self._get_formatted_date()
        
        # Create title with current date
        full_digest = f"# RSS 新闻摘要 - {current_date} {datetime.datetime.now().strftime('%H:%M')}\n\n"
        
        # 按指定顺序排列分类
        priority_order = ["AI and Tech", "Market", "World News"]
        
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
        
        api_logger.debug(f"Full digest generated, total length: {len(full_digest)} characters")
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