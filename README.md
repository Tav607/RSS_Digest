# RSS Digest

自动从FreshRSS生成新闻简报并通过Telegram发送。

## 功能特性

- 从FreshRSS数据库读取指定用户的最近RSS条目
- 使用AI模型（如OpenAI的GPT-4）处理和总结内容
- 按主题（AI、科技、世界新闻等）分类整理内容
- 生成中文简报，以bullet points形式呈现
- 通过Telegram Bot发送简报
- 支持自动定时运行

## 系统要求

- Python 3.6+
- FreshRSS安装并有数据库访问权限
- OpenAI API账户和API密钥
- Telegram Bot

## 安装

1. 克隆本仓库

```bash
git clone https://your-repository-url/rss_digest.git
cd rss_digest
```

2. 安装依赖:

```bash
pip install -r requirements.txt
```

3. 配置环境变量:

```bash
cp .env.example .env
```

4. 编辑`.env`文件，填入你的配置信息：
   - FreshRSS数据库路径
   - OpenAI API密钥
   - Telegram Bot Token和聊天ID

## 使用方法

### 基本用法

```bash
python main.py
```

这将:
- 读取过去8小时的RSS条目
- 生成简报
- 通过Telegram发送

### 命令行选项

```bash
# 指定时间范围（过去12小时）
python main.py --hours 12

# 生成但不发送简报
python main.py --no-send

# 将简报保存到文件
python main.py --save

# 启用调试日志
python main.py --debug
```

### 使用脚本运行

项目提供了运行脚本:

```bash
# 赋予执行权限
chmod +x run.sh

# 运行脚本
./run.sh
```

## 定时运行

你可以使用crontab设置定时运行:

```bash
# 编辑crontab
crontab -e

# 每8小时运行一次
0 */8 * * * cd /path/to/rss_digest && ./run.sh
```

参考`crontab.example`文件获取更多样例。

## Telegram Bot设置

1. 通过Telegram的@BotFather创建新Bot，获取Bot Token
2. 找到你的聊天ID (可使用@userinfobot)
3. 在`.env`文件中填入这些信息

## 高级配置

你可以通过编辑`config.py`自定义：

- AI模型（gpt-4, gpt-3.5-turbo等）
- API提供商
- 分类关键词
- 输出语言
- 简报长度和格式

## 故障排除

如果遇到问题，请检查：
- `.env`文件配置是否正确
- FreshRSS数据库路径是否可访问
- API密钥是否有效
- 查看`rss_digest.log`获取详细错误信息

## 项目结构

- `main.py` - 主程序
- `config.py` - 配置加载和管理
- `ai_utils.py` - AI处理相关功能
- `db_utils.py` - 数据库操作功能
- `telegram_utils.py` - Telegram发送功能
- `run.sh` - 运行脚本
- `setup.sh` - 初始安装脚本
