#!/bin/bash

# 确保 PATH 包含用户本地的 bin 目录（cron 环境默认不包含）
# 使用脚本路径推断用户目录，避免 $HOME 在 cron 中未设置的问题
USER_HOME="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
export PATH="$USER_HOME/.local/bin:$HOME/.local/bin:/home/paladinllq/.local/bin:$PATH"

# 获取当前脚本所在的目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 获取项目根目录（脚本上一级目录）
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 获取参数，使用默认值
HOURS=${1:-48}

# 运行 Python 脚本
uv run python -m src.main --hours "$HOURS" 