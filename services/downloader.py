import asyncio
import functools
import yt_dlp
from config import config
import os

def _run_in_executor(func):
    """
    Decorator to run a synchronous function in a separate thread.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,  # Use the default thread pool executor
            functools.partial(func, *args, **kwargs)
        )
    return wrapper

@_run_in_executor
def search_youtube(query: str) -> list[dict]:
    """
    Searches YouTube for a given query and returns the top 5 results.
    This function is blocking and should be run in an executor.
    """
    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch5',  # Search and return 5 results
        'extract_flat': 'in_playlist', # Only extract info, not download
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # For searching, we don't need 'outtmpl' in the search options
            search_result = ydl.extract_info(query, download=False)
            videos = []
            if 'entries' in search_result:
                for entry in search_result['entries']:
                    if entry and entry.get('id'): # Ensure entry is not None and has 'id'
                        videos.append({
                            'id': entry['id'],
                            'title': entry.get('title', 'No Title'),
                            'duration': entry.get('duration', 0)
                        })
            return videos[:5] # Return top 5 results
        except Exception as e:
            print(f"Error during YouTube search: {e}")
            return []


@_run_in_executor
def download_song(video_id: str) -> dict | None:
    """
    Downloads a song from YouTube using its video ID.
    This function is blocking and should be run in an executor.
    Returns a dictionary with metadata or None on failure.
    """
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = config.YDL_OPTS.copy()
    
    # Ensure the 'downloads' directory exists
    os.makedirs('downloads', exist_ok=True)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=True)
            
            # yt-dlp might add a different extension even if 'm4a' is preferred.
            # We need to find the actual downloaded file.
            # The 'outtmpl' format will be 'downloads/%(id)s.%(ext)s'
            base_filename = os.path.join('downloads', video_id)
            
            # Find the actual file downloaded, checking for common extensions
            filepath = None
            for ext in ['m4a', 'opus', 'webm', 'mp3']: # Check for m4a first as preferred
                possible_filepath = f"{base_filename}.{ext}"
                if os.path.exists(possible_filepath):
                    filepath = possible_filepath
                    break
            
            if not filepath:
                # Fallback: try to guess from info dict if 'filepath' is present (yt-dlp often adds it)
                filepath = info.get('filepath')
                if not filepath or not os.path.exists(filepath):
                    # If still not found, search in the downloads directory
                    for f in os.listdir('downloads'):
                        if f.startswith(video_id) and ('m4a' in f or 'opus' in f or 'webm' in f):
                            filepath = os.path.join('downloads', f)
                            break

            if not filepath:
                raise FileNotFoundError(f"Downloaded file for {video_id} not found.")

            return {
                "filepath": filepath,
                "title": info.get('title'),
                "duration": info.get('duration'),
                "thumbnail": info.get('thumbnail')
            }
        except Exception as e:
            print(f"Error during song download: {e}")
            return None
