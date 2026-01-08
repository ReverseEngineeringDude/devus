# Telegram Music Downloader Bot

This is a simple yet powerful Telegram bot for downloading music from YouTube. It's built with Python using the `aiogram` framework (v3.x) and `yt-dlp`.

## Features

- **Search by Name:** Send a song title to search on YouTube and get the top 5 results.
- **Download by Link:** Send a YouTube video link to download the audio directly.
- **Asynchronous:** Built on `asyncio` to handle multiple users and requests without blocking.
- **Optimized:** Downloads audio in `m4a` format directly to avoid slow FFmpeg conversions.
- **Self-cleaning:** Downloaded audio files are automatically deleted after being sent to the user.

## How to Run

Follow these steps to get your own instance of the bot running.

### 1. Prerequisites

- Python 3.10 or higher.
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather).

### 2. Setup

First, clone or download this project. Then, navigate to the project directory.

**Create and activate a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Install the required dependencies:**
```bash
pip install -r requirements.txt
```

**Configure your Bot Token:**
Rename the `.env.example` file to `.env` (if it exists) or create a new `.env` file. Add your bot token to it:
```
BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
```

### 3. Running the Bot

Once the setup is complete, you can start the bot with the following command:

```bash
python3 main.py
```

Your bot should now be online and ready to receive commands!
