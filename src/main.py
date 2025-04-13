#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import argparse
import datetime
from pathlib import Path

# 确定项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# 导入项目模块
from src.config import DIGEST_LOG_PATH, PROJECT_ROOT
from src.services import run_digest_process

# 确保日志目录存在
log_dir = PROJECT_ROOT / 'logs'
if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(DIGEST_LOG_PATH)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """主入口点，带命令行参数解析"""
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
    
    # 如果请求开启debug日志
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # 运行摘要生成和发送流程
    digest = run_digest_process(
        hours_back=args.hours,
        send=not args.no_send
    )
    
    # 如果请求保存到文件
    if args.save:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = PROJECT_ROOT / f"digest_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest)
        logger.info(f"Digest saved to {filename}")
    
    # 打印摘要到控制台
    print(f"Digest generation completed. Length: {len(digest)} characters")
    
if __name__ == "__main__":
    main() 