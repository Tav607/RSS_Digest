#!/bin/bash

# 清理脚本 - 删除不再需要的根目录文件

# 获取当前脚本所在的目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 获取项目根目录（脚本上一级目录）
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 切换到项目根目录
cd "$PROJECT_ROOT"

echo "开始清理根目录中不再需要的文件..."

# 已移动到 src/utils/ 的文件
echo "删除已移动到 src/utils/ 的文件..."
rm -f ai_utils.py db_utils.py telegram_utils.py

# 已移动到 src/config/ 的文件
echo "删除已移动到 src/config/ 的文件..."
rm -f config.py .env.example

# 已移动到 scripts/ 的文件
echo "删除已移动到 scripts/ 的文件..."
rm -f run.sh setup.sh

# 已移动到 logs/ 的文件
echo "删除已移动到 logs/ 的文件..."
rm -f rss_digest.log

# 不再需要的文件
echo "删除不再需要的文件..."
rm -f main.py __init__.py

# 清理 Python 缓存
echo "清理 Python 缓存..."
rm -rf __pycache__

echo "清理完成！"
echo "注意：为安全起见，我们没有删除.env文件，如果确认src/config/.env文件配置正确，"
echo "您可以手动删除根目录下的.env文件。" 