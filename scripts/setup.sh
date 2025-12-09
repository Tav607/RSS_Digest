#!/bin/bash

# 获取当前脚本所在的目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 获取项目根目录（脚本上一级目录）
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "开始安装 RSS Digest Generator..."
echo "项目路径: $PROJECT_ROOT"

# 创建目录（如果不存在）
mkdir -p "$PROJECT_ROOT/logs"

# 检查是否安装了 uv
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到 uv，请先安装 uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# 使用 uv sync 安装依赖（会自动创建 .venv）
echo "使用 uv 安装依赖..."
cd "$PROJECT_ROOT"
uv sync

# 检查是否存在.env文件
if [ ! -f "$PROJECT_ROOT/src/config/.env" ]; then
    echo "创建环境配置文件..."
    cp "$PROJECT_ROOT/src/config/.env.example" "$PROJECT_ROOT/src/config/.env"
    echo "请编辑 src/config/.env 文件配置必要参数。"
else
    echo ".env文件已存在，跳过创建步骤。"
fi

echo "安装完成！"
echo "请确保您已经编辑了 src/config/.env 文件并配置了必要的参数。"
echo "使用下面的命令运行程序："
echo "  scripts/run.sh [hours]" 