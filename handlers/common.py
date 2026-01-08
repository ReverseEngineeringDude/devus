from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(
        f"Hello, {hbold(message.from_user.full_name)}!\n\n"
        "I'm a music downloader bot. Send me a song name or a YouTube link to get started."
    )

@router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """
    This handler receives messages with `/help` command
    """
    await message.answer(
        "How to use the bot:\n\n"
        "1.  📝 Send a song name (e.g., 'Never Gonna Give You Up'). I will search for it on YouTube and give you 5 options.\n\n"
        "2.  🔗 Send a valid YouTube link (e.g., 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'). I will download the audio directly.\n\n"
        "That's it! Enjoy the music."
    )

