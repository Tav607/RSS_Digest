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

# 读取 system prompt 内容
SYSTEM_PROMPT = "你是一位资深新闻编辑，擅长从大量资讯中提取核心信息并生成摘要。" # Default fallback
try:
    # Use absolute path based on the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(script_dir, "system_prompt.md")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            SYSTEM_PROMPT = f.read()
        logger.info(f"Successfully loaded system prompt from {prompt_path}")
    else:
        logger.error(f"System prompt file '{prompt_path}' not found. Using default prompt.")

except Exception as e:
    logger.error(f"Error reading system prompt file '{prompt_path}': {e}. Using default prompt.")


class AIProcessor:
    """
    通过 AI 模型处理内容并生成摘要的类。
    """
    def __init__(self, api_key: str, model: str, base_url: str):
        """
        初始化 AI 处理器。

        Args:
            api_key: AI 服务的 API 密钥。
            model: 要使用的 AI 模型。
            base_url: API 的基础 URL。
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        api_logger.debug(f"AIProcessor initialized with model: {model}, base_url: {base_url}")

    def generate_digest(self, entries: List[Dict[Any, Any]]) -> str:
        """
        一次性处理所有 RSS 条目，生成完整的摘要。

        Args:
            entries: 包含所有 RSS 条目的字典列表。

        Returns:
            由 AI 生成的完整摘要文本。
        """
        if not entries:
            logger.warning("No entries provided for digest generation.")
            return "没有可供处理的 RSS 条目。"

        # 准备所有条目的内容作为 User Prompt
        content_text = ""
        entry_count = 0
        for entry in entries:
            # 截断内容
            truncated_content = self._truncate_content(entry.get('content', ''), max_chars=5000) # 每个条目限制5000字符
            title = entry.get('title', 'N/A')
            source = entry.get('feed_name', 'N/A')

            content_text += f"标题: {title}\n"
            content_text += f"来源: {source}\n"
            content_text += f"正文摘要: {truncated_content}\n\n"
            entry_count += 1
            # 可以根据需要增加 token 估算和提前停止的逻辑

        if not content_text.strip():
             logger.warning("Content text for AI prompt is empty after processing entries.")
             return "处理后无有效内容可生成摘要。"

        api_logger.debug(f"Generating digest from {entry_count} entries.")
        logger.info(f"Sending {entry_count} entries to AI for digest generation.")

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content_text}
                ],
                max_tokens=2000, # 根据预期输出长度调整, 考虑增加温度等参数
                temperature=0.5 # 添加温度参数，控制生成文本的随机性
            )

            digest = completion.choices[0].message.content.strip()
            logger.info(f"Digest generated, length: {len(digest)} characters.")
            logger.debug(f"Generated digest content (first 150 chars): {digest[:150]}...")
            api_logger.debug(f"AI digest response: length={len(digest)} chars")

            # 在 AI 生成的内容前添加日期标题
            current_date = self._get_formatted_date()
            # 假设 system prompt 指导 AI 输出包含 Markdown 标题的完整格式
            # 这里直接返回 AI 的结果，如果需要强制添加主标题，可以取消下面注释
            final_digest = digest
            # 如果需要强制添加日期主标题，即使AI已生成部分标题:
            # if not digest.lstrip().startswith("#"):
            #      final_digest = f"# RSS 新闻摘要 - {current_date} {datetime.datetime.now().strftime('%H:%M')}\n\n{digest}"
            # else:
                 # 可选：如果 AI 输出了内容，但没有主标题，则添加
                 # pass # 或者保持 final_digest = digest

            # 确保返回非空字符串
            if not final_digest:
                logger.warning("AI generated an empty digest.")
                return "AI生成了空的摘要内容。"

            return final_digest

        except Exception as e:
            error_msg = f"Error generating digest: {str(e)}"
            logger.exception(f"AI API error during digest generation: {error_msg}") # 使用 exception 记录堆栈信息
            api_logger.error(f"AI API error during digest generation: {str(e)}")
            return f"无法生成摘要。错误: {str(e)}"

    def _truncate_content(self, content: str, max_chars: int = 1000) -> str:
        """将内容截断到合理长度"""
        if content is None:
            return ""
        content_str = str(content) # 确保是字符串
        if len(content_str) <= max_chars:
            return content_str
        return content_str[:max_chars] + "..."

    def _get_formatted_date(self) -> str:
        """获取中文格式的当前日期"""
        now = datetime.datetime.now()
        return f"{now.year}年{now.month}月{now.day}日" 