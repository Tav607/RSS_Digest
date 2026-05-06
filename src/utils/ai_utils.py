#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import logging.handlers
import os
import re
import datetime
from typing import Dict, List, Any, Union
from openai import OpenAI
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# 从配置导入API调试日志路径
from src.config import API_DEBUG_LOG_PATH

# 创建命名记录器
logger = logging.getLogger(__name__)

# 为API调用创建专用的调试记录器
api_logger = logging.getLogger("api")
api_handler = logging.handlers.RotatingFileHandler(API_DEBUG_LOG_PATH, maxBytes=5*1024*1024, backupCount=3)
api_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
api_logger.addHandler(api_handler)
api_logger.setLevel(logging.DEBUG)

_PROMPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FALLBACK_PERSONA = "你是通讯社快讯编辑（路透 / Bloomberg 风格），冷静、克制、只陈述事实。"


def _load_prompt(filename: str) -> str:
    """读取与本模块同目录的 prompt 文件；失败时返回 fallback persona 一句话。"""
    path = os.path.join(_PROMPT_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.info(f"Successfully loaded prompt from {path}")
        return content
    except FileNotFoundError:
        logger.error(f"Prompt file '{path}' not found. Using fallback persona.")
    except OSError as e:
        logger.error(f"Error reading prompt file '{path}': {e}. Using fallback persona.")
    return _FALLBACK_PERSONA


SYSTEM_PROMPT = _load_prompt("system_prompt.md")          # 第二阶段：全局汇总
STAGE1_SYSTEM_PROMPT = _load_prompt("system_prompt_stage1.md")  # 第一阶段：单篇摘要


class AIProcessor:
    """
    通过 AI 模型处理内容并生成摘要的类。
    """
    def __init__(self, api_key: str, stage2_model: str, base_url: str, stage1_model: str = None):
        """
        初始化 AI 处理器。

        Args:
            api_key: AI 服务的 API 密钥。
            stage2_model: 第二阶段（全局汇总）使用的模型。
            base_url: API 的基础 URL。
            stage1_model: 第一阶段（单篇摘要）使用的模型；省略则复用 stage2_model。
        """
        self.stage2_model = stage2_model
        self.stage1_model = stage1_model or stage2_model
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        api_logger.debug(
            "AIProcessor initialized with stage1_model=%s, stage2_model=%s, base_url=%s",
            self.stage1_model,
            self.stage2_model,
            base_url,
        )

    # -------------------------
    # 第一阶段：逐篇文章摘要
    # -------------------------
    def summarize_articles(self, entries: List[Dict[str, Any]]) -> tuple[str, dict[str, str]]:
        """
        逐篇并行调用 AI 摘要，合并为一个文本，供第二阶段汇总。
        输出格式：每篇以 --- ARTICLE --- 分隔，包含来源与要点。
        返回 (merged_summaries, url_map) 元组。
        """
        if not entries:
            return "", {}
        from src.config import STAGE1_MAX_WORKERS  # import here to avoid early import side-effects

        def worker(i: int, e: Dict[str, Any]):
            # Create a lightweight client per thread for safety
            local_client = OpenAI(base_url=self.base_url, api_key=self.api_key)
            title = e.get('title', 'N/A')
            source = e.get('feed_name', 'N/A')
            link = e.get('link', '')
            content = e.get('content', '') or ''
            user_prompt = (
                "请基于以下单篇文章内容提炼要点，遵循系统提示的格式要求：\n\n"
                f"标题: {title}\n来源: {source}\n原文链接: {link}\n正文:\n{content}\n"
            )
            max_attempts = 2
            for attempt in range(1, max_attempts + 1):
                try:
                    completion = local_client.chat.completions.create(
                        model=self.stage1_model,
                        messages=[
                            {"role": "system", "content": STAGE1_SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.1,
                    )
                    choice = completion.choices[0] if completion and completion.choices else None
                    summary = (choice.message.content if choice and choice.message else "")
                    summary = (summary or "").strip()
                    if summary:
                        if attempt > 1:
                            api_logger.debug(
                                f"Stage1 success on retry {attempt} for title='{title[:60]}'"
                            )
                        return i, title, source, link, summary
                    else:
                        raise RuntimeError("empty summary")
                except Exception as ex:
                    api_logger.warning(
                        f"Stage1 attempt {attempt}/{max_attempts} failed for '{title[:60]}': {ex}"
                    )
                    if attempt < max_attempts:
                        backoff = 0.3 * (2 ** (attempt - 1)) + random.uniform(0, 0.2)
                        time.sleep(backoff)
                        continue
                    else:
                        api_logger.error(
                            f"Stage1 giving up for '{title[:60]}' after {max_attempts} attempts"
                        )
                        return i, title, source, link, ""

        api_logger.debug(
            f"Stage1 parallel summarization start: entries={len(entries)}, max_workers={STAGE1_MAX_WORKERS}"
        )
        results: List[Any] = [None] * len(entries)
        url_map: dict[str, str] = {}
        skipped = 0
        with ThreadPoolExecutor(max_workers=STAGE1_MAX_WORKERS) as executor:
            futures = [executor.submit(worker, idx, entry) for idx, entry in enumerate(entries, start=1)]
            for fut in as_completed(futures):
                i, title, source, link, per_article = fut.result()
                # Filter out empty or [SKIP] results
                if not per_article or per_article.strip() == "[SKIP]":
                    skipped += 1
                    api_logger.debug(f"Stage1 skipped article {i}: '{title[:60]}'")
                    continue
                # Use REF ID instead of raw URL
                ref_id = f"REF{i}"
                url_map[ref_id] = link
                header = f"[来源:{source}] [链接:{ref_id}] [标题:{title}]"
                block = (
                    f"--- ARTICLE {i} START ---\n{header}\n要点:\n{per_article}\n--- ARTICLE {i} END ---"
                )
                results[i - 1] = block

        parts: List[str] = [blk for blk in results if blk is not None]
        merged = "\n\n".join(parts)
        api_logger.debug(
            f"Stage1 merged summaries: {len(parts)} valid, {skipped} skipped, length={len(merged)}"
        )
        return merged, url_map

    # -------------------------
    # 第二阶段：基于文章摘要进行全局汇总
    # -------------------------
    def finalize_digest_from_article_summaries(
        self,
        merged_summaries: str,
        digest_history: list[str] = None,
        url_map: dict[str, str] = None,
    ) -> str:
        """
        采用现有的 system prompt，对第一阶段的合并摘要做全局分类与排序，生成终稿。

        Args:
            merged_summaries: 第一阶段合并的文章摘要
            digest_history: 最近几次的历史摘要，用于去重
            url_map: REF ID -> 真实 URL 的映射表
        """
        if not merged_summaries or not merged_summaries.strip():
            return ""

        # Build user prompt with optional history context
        user_content_parts = []

        # Add history context if available
        if digest_history:
            history_text = "\n\n---\n\n".join(digest_history)
            user_content_parts.append(
                "以下是最近已发送的摘要（用于去重参考）：\n"
                "--- HISTORY_START ---\n"
                f"{history_text}\n"
                "--- HISTORY_END ---\n"
            )

        # Add current batch
        user_content_parts.append(
            "以下为本次待处理的文章要点摘要：\n"
            "--- ABSTRACT_BATCH_START ---\n\n"
            f"{merged_summaries}\n\n"
            "--- ABSTRACT_BATCH_END ---"
        )

        user_content = "\n".join(user_content_parts)

        try:
            completion = self.client.chat.completions.create(
                model=self.stage2_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                temperature=1.0,
            )
            digest = (completion.choices[0].message.content or "").strip()
            api_logger.debug(
                f"Stage2 digest generated from abstracts, length={len(digest)}"
            )

            # Replace REF IDs with real URLs (use regex to avoid prefix collision: REF1 vs REF10)
            if url_map:
                replaced = 0
                def _ref_replacer(match):
                    nonlocal replaced
                    ref_token = match.group(0)
                    if ref_token in url_map:
                        replaced += 1
                        return url_map[ref_token]
                    return ref_token
                digest = re.sub(r'REF\d+', _ref_replacer, digest)
                api_logger.debug(
                    f"Stage2 URL mapping: {replaced}/{len(url_map)} refs replaced"
                )

            return digest
        except Exception as e:
            api_logger.error(f"Stage2 digest generation error: {e}")
            return ""
