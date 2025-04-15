# RSS Digest Generator

一个自动化的RSS摘要生成器，可以从FreshRSS获取文章，使用AI进行分类摘要，并通过Telegram发送。

## 目录结构

```
.
├── logs/                   # 日志文件目录
├── scripts/                # 脚本文件目录
│   ├── run.sh              # 运行脚本
│   └── setup.sh            # 安装配置脚本
├── src/                    # 源代码目录
│   ├── config/             # 配置目录
│   │   ├── config.py       # 配置文件
│   │   ├── .env            # 环境变量文件
│   │   └── .env.example    # 环境变量示例文件
│   ├── services/           # 业务服务目录
│   │   └── digest_service.py   # 摘要生成服务
│   ├── utils/              # 工具类目录
│   │   ├── ai_utils.py     # AI处理工具
│   │   ├── db_utils.py     # 数据库工具
│   │   ├── telegram_utils.py   # Telegram发送工具
│   │   └── system_prompt.md  # 系统提示文件
│   ├── __init__.py         # 包初始化文件
│   └── main.py             # 主程序入口
├── requirements.txt        # 依赖项列表
├── README.md               # 项目说明文件
└── crontab.example         # 定时任务配置示例
```

## 安装与配置

1. 克隆本仓库
2. 运行安装脚本:
   ```
   ./scripts/setup.sh
   ```
3. 编辑配置文件:
   ```
   nano src/config/.env
   ```
4. 确保你的FreshRSS数据库路径正确配置，以及Telegram和AI API信息已设置

## 使用方法

运行RSS摘要生成器:
```
./scripts/run.sh [hours_back]
```

参数:
- `hours_back`: 可选，查找几小时前的文章，默认为配置文件中的设置(8小时)

### 命令行选项

也可以直接使用Python运行并传递更多参数:
```
python -m src.main --hours 12 --save --debug
```

选项:
- `--hours`: 同上，指定查找几小时前的文章
- `--no-send`: 生成摘要但不通过Telegram发送
- `--save`: 将摘要保存到文件
- `--debug`: 启用调试日志输出

## 自动化运行

编辑crontab来设置自动运行:
```
crontab -e
```

示例 (每天早上7点和晚上7点运行):
```
0 7,19 * * * cd /path/to/repository && ./scripts/run.sh 12
```

## 依赖项

- Python 3.7+
- FreshRSS 实例和数据库
- OpenAI 或兼容的AI API
- Telegram 机器人

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
- `.env`