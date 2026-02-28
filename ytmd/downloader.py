import yt_dlp
from typing import Dict, Any

def fetch_info(url: str) -> Dict[str, Any]:
    """
    Fetch metadata for a given URL without downloading the content.
    """
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True, # Ignore if a video in a playlist is unavailable
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return info_dict or {}

def get_base_ydl_opts() -> Dict[str, Any]:
    """
    Get the yt-dlp configuration for MP3 192kbps extraction.
    """
    return {
        'format': 'bestaudio/best',
        'writethumbnail': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'EmbedThumbnail',
            }
        ],
        # Template will be set in download_media depending on if it is a playlist or not
        # 'restrictfilenames': True,  # Removes spaces and non-ASCII characters
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True, # Skip unavailable videos
        'updatetime': False,
    }

def download_media(url: str, info_dict: Dict[str, Any]) -> None:
    """
    Download the media using the fetched info dictionary.
    """
    # UI Manager instantiation will happen here, or be passed in
    from ytmd.ui import DownloadProgressManager
    
    ydl_opts = get_base_ydl_opts()
    
    # Set outtmpl dynamically
    if 'entries' in info_dict:
        # Create a folder named after the playlist
        ydl_opts['outtmpl'] = 'download/%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'
    else:
        ydl_opts['outtmpl'] = 'download/%(title)s.%(ext)s'
    
    # We will pass progress hooks
    progress_manager = DownloadProgressManager(info_dict)
    ydl_opts['progress_hooks'] = [progress_manager.yt_dlp_hook]
    
    try:
        with progress_manager:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
    except Exception as e:
        from rich import print
        print(f"\n[bold red]Fatal Download Error: {e}[/bold red]")
