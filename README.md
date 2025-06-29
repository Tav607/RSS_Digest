# RSS Digest Generator

An automated RSS digest generator that fetches articles from FreshRSS, categorizes and summarizes them using AI, and sends the digest via Telegram.

## Directory Structure

```
.
├── logs/                   # Log file directory
├── scripts/                # Utility scripts
│   ├── run.sh              # Main execution script
│   └── setup.sh            # Installation and setup script
├── src/                    # Source code
│   ├── config/             # Configuration files
│   │   ├── config.py       # Main configuration
│   │   ├── .env            # Environment variables (gitignored)
│   │   └── .env.example    # Environment variable template
│   ├── services/           # Business logic
│   │   └── digest_service.py   # Digest generation service
│   ├── utils/              # Helper utilities
│   │   ├── ai_utils.py     # AI processing utility
│   │   ├── db_utils.py     # Database interaction utility
│   │   ├── telegram_utils.py   # Telegram notification utility
│   │   └── system_prompt.md  # System prompt for the AI model
│   ├── __init__.py         # Package initializer
│   └── main.py             # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── crontab.example         # Example crontab configuration
```

## Features

- Reads recent RSS entries for a specified user from a FreshRSS database.
- Uses an AI model (e.g., OpenAI's GPT-4) to process and summarize content.
- Categorizes content by topics (AI, Tech, World News, etc.).
- Generates a digest in bullet-point format.
- Sends the digest via a Telegram Bot.
- Supports scheduled execution via cron jobs.

## Prerequisites

- Python 3.7+
- A FreshRSS instance with database access.
- An OpenAI compatible AI API key.
- A Telegram Bot token and chat ID.

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://your-repository-url/rss_digest.git
    cd rss_digest
    ```

2.  **Run the setup script:**
    This script will create a Python virtual environment and install the required dependencies.
    ```bash
    ./scripts/setup.sh
    ```

3.  **Configure environment variables:**
    Copy the example `.env` file. **Important:** The `.env` file must be located in the `src/config/` directory.
    ```bash
    cp src/config/.env.example src/config/.env
    ```

4.  **Edit the configuration file:**
    Fill in your details in `src/config/.env`.
    ```bash
    nano src/config/.env
    ```
    You need to set:
    - `FRESHRSS_DB_PATH`: The absolute path to your FreshRSS SQLite database file.
    - `USERNAME`: The FreshRSS user for whom to fetch articles.
    - `OPENROUTER_API_KEY`: Your AI provider API key.
    - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
    - `TELEGRAM_CHAT_ID`: The destination chat ID for the digest.

## Usage

### Using the Run Script

The easiest way to run the generator is by using the provided script.

```bash
./scripts/run.sh [hours_back]
```

- **`hours_back`**: (Optional) The number of hours to look back for new articles. Defaults to the value in your configuration (8 hours).

Example:
```bash
# Generate a digest for articles from the last 12 hours
./scripts/run.sh 12
```

### Direct Execution with Python

You can also run the main script directly with more granular control. Make sure you have activated the virtual environment first (`source venv/bin/activate`).

```bash
python -m src.main [options]
```

**Options:**

- `--hours <number>`: Specify the look-back period in hours.
- `--no-send`: Generate the digest but do not send it via Telegram.
- `--save`: Save the generated digest to a `.txt` file in the project root.
- `--debug`: Enable detailed debug logging.

Example:
```bash
python -m src.main --hours 12 --save --debug
```

## Automation with Cron

You can automate the digest generation using a cron job.

1.  Open your crontab for editing:
    ```bash
    crontab -e
    ```

2.  Add a new line to schedule the script. Refer to `crontab.example` for more samples.

    ```crontab
    # Run every day at 7 AM and 7 PM, generating a digest for the last 12 hours.
    0 7,19 * * * cd /path/to/your/rss_digest && ./scripts/run.sh 12
    ```
    **Important:** Make sure to use the absolute path to your project directory.

## Advanced Configuration

You can customize the application's behavior by editing `src/config/config.py`:

- **AI Model:** Change `AI_MODEL` to use a different model (e.g., `gpt-4`, `gpt-3.5-turbo`).
- **API Provider:** Modify `AI_BASE_URL` to use a different API endpoint.
- **Categorization:** Adjust the keywords and logic for categorization within `digest_service.py`.
- **Output Language:** Modify the `system_prompt.md` to change the output language or format.

## Troubleshooting

If you encounter issues, please check the following:
- Ensure all variables in `src/config/.env` are correctly set.
- Verify that the path to your FreshRSS database is correct and the file is readable.
- Check the log files in the `logs/` directory for detailed error messages (`rss_digest.log` and `api_debug.log`).
