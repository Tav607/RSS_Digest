#!/bin/bash

# 获取当前脚本所在的目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 获取项目根目录（脚本上一级目录）
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "开始安装 RSS Digest Generator..."
echo "项目路径: $PROJECT_ROOT"

# 创建目录（如果不存在）
mkdir -p "$PROJECT_ROOT/logs"

# 检查是否存在虚拟环境
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv "$PROJECT_ROOT/venv"
else
    echo "虚拟环境已存在，跳过创建步骤。"
fi

# 激活虚拟环境
source "$PROJECT_ROOT/venv/bin/activate"

# 安装依赖
echo "安装Python依赖项..."
pip install -r "$PROJECT_ROOT/requirements.txt"

# 检查是否存在.env文件
if [ ! -f "$PROJECT_ROOT/src/config/.env" ]; then
    echo "创建环境配置文件..."
    cp "$PROJECT_ROOT/src/config/.env.example" "$PROJECT_ROOT/src/config/.env"
    echo "请编辑 src/config/.env 文件配置必要参数。"
else
    echo ".env文件已存在，跳过创建步骤。"
fi

# 退出虚拟环境
deactivate

echo "安装完成！"
echo "请确保您已经编辑了 src/config/.env 文件并配置了必要的参数。"
echo "使用下面的命令运行程序："
echo "  scripts/run.sh [hours]" 