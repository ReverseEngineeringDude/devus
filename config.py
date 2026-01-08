import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set!")

    # yt-dlp options
    # See https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#embedding-yt-dlp
    YDL_OPTS = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,

        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
        'cookiefile': 'cookie.txt',
    }

config = Config()
