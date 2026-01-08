import os
import re
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.downloader import search_youtube, download_song

router = Router()

# In-memory storage for search results. {user_id: [videos]}
user_search_results = {}

# Regex to check if a string is a valid YouTube URL
# This regex is specifically for YouTube watch links, it won't match channel or playlist URLs
YOUTUBE_URL_REGEX = re.compile(
    r'(https?://)?(www\.)?(youtube|youtu)\.(com|be)/'
    r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')


@router.message(F.text.regexp(YOUTUBE_URL_REGEX))
async def handle_youtube_link(message: Message):
    """
    Handles YouTube links directly.
    """
    url = message.text
    match = YOUTUBE_URL_REGEX.search(url)
    if not match:
        await message.reply("Please send a valid YouTube video link.")
        return

    video_id = match.group(6)
    
    status_msg = await message.reply("⏳ Processing link...")

    try:
        song_data = await download_song(video_id)
        
        if song_data and os.path.exists(song_data["filepath"]):
            await status_msg.edit_text("✅ Download complete! Sending file...")
            
            audio_file = FSInputFile(
                path=song_data["filepath"],
                filename=f"{song_data['title']}.m4a"
            )
            
            # Telegram Bot API limits thumbnail size, sending without for simplicity, or it needs to be pre-processed
            # For a production bot, consider downloading and resizing the thumbnail.
            await message.reply_audio(
                audio=audio_file,
                title=song_data.get("title", "Unknown Title"),
                duration=song_data.get("duration"),
                # thumbnail=FSInputFile(song_data.get("thumbnail")) if song_data.get("thumbnail") else None
            )
            
            # Clean up the downloaded file
            os.remove(song_data["filepath"])
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Failed to download the song. Please try another link.")

    except Exception as e:
        await status_msg.edit_text("❌ An error occurred during link processing. Please try again.")
        print(f"Error handling YouTube link: {e}")


@router.message(F.text)
async def handle_text_search(message: Message):
    """
    Handles text messages by searching on YouTube.
    This handler should be placed after specific link handlers.
    """
    query = message.text
    status_msg = await message.reply(f"🔎 Searching for '{query}'...")

    try:
        videos = await search_youtube(query)
        if not videos:
            await status_msg.edit_text("❌ No results found. Please try another search term.")
            return

        # Store results for the user
        user_search_results[message.from_user.id] = videos

        # Create inline keyboard with results
        builder = InlineKeyboardBuilder()
        for i, video in enumerate(videos):
            title = video['title']
            duration_min = int(video['duration'] // 60) if video['duration'] else 0
            duration_sec = int(video['duration'] % 60) if video['duration'] else 0
            
            # Truncate title if too long for button text
            button_title = title if len(title) <= 30 else f"{title[:27]}..."
            button_text = f"{i+1}. {button_title} ({duration_min}:{duration_sec:02d})"
            
            builder.button(text=button_text, callback_data=f"download_{i}")
        
        builder.adjust(1) # Display one button per row

        await status_msg.edit_text(
            "👇 Here are the top results. Please choose one to download:",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        await status_msg.edit_text("❌ An error occurred during search. Please try again.")
        print(f"Error in text search: {e}")


@router.callback_query(F.data.startswith("download_"))
async def handle_download_callback(callback_query: CallbackQuery):
    """
    Handles the callback query when a user selects a song from search results.
    """
    user_id = callback_query.from_user.id
    await callback_query.answer("Processing your selection...")
    
    original_message = callback_query.message
    await original_message.edit_text("⏳ Processing selection...")

    try:
        video_index = int(callback_query.data.split("_")[1])
        
        if user_id not in user_search_results or video_index >= len(user_search_results[user_id]):
            await original_message.edit_text("❌ Search results have expired or are invalid. Please search again.")
            return

        video = user_search_results[user_id][video_index]
        video_id = video['id']

        await original_message.edit_text(f"⏳ Downloading '{video['title']}'...")
        
        song_data = await download_song(video_id)

        if song_data and os.path.exists(song_data["filepath"]):
            await original_message.edit_text("✅ Download complete! Sending file...")
            
            audio_file = FSInputFile(
                path=song_data["filepath"],
                filename=f"{song_data['title']}.m4a"
            )
            
            await callback_query.message.reply_audio(
                audio=audio_file,
                title=song_data.get("title", "Unknown Title"),
                duration=song_data.get("duration"),
                # Telegram Bot API limits thumbnail size, sending without for simplicity.
                # For a production bot, consider downloading and resizing the thumbnail.
            )

            # Clean up
            os.remove(song_data["filepath"])
            await original_message.delete()
        else:
            await original_message.edit_text("❌ Failed to download the selected song. Please try again.")

    except Exception as e:
        await original_message.edit_text("❌ An error occurred during download callback. Please try again.")
        print(f"Error in download callback: {e}")
    finally:
        # Clear user's search results after selection
        if user_id in user_search_results:
            del user_search_results[user_id]