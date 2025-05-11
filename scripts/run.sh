#!/bin/bash

# 获取当前脚本所在的目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 获取项目根目录（脚本上一级目录）
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 激活虚拟环境（如果存在）
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 获取参数，使用默认值
HOURS=${1:-48}

# 运行 Python 脚本
python -m src.main --hours "$HOURS"

# 如果使用了虚拟环境，则退出
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 