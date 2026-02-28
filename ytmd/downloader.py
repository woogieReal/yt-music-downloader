import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor
from typing import Dict, Any
import os
import re

class ID3TagPostProcessor(PostProcessor):
    def __init__(self, downloader=None):
        super().__init__(downloader)

    def run(self, info):
        filepath = info.get('filepath')
        if filepath and filepath.endswith('.mp3'):
            from mutagen.easyid3 import EasyID3
            from mutagen.id3 import ID3NoHeaderError
            
            # 1. Metadata Extraction (Title & Artist)
            title = info.get('title')
            artist = info.get('artist')
            
            # Fallback for Title
            if not title:
                filename = os.path.basename(filepath)
                basename = os.path.splitext(filename)[0]
                title = re.sub(r'^\d+\s*-\s*', '', basename)
            
            try:
                audio = EasyID3(filepath)
            except ID3NoHeaderError:
                import mutagen
                audio = mutagen.File(filepath, easy=True)
                audio.add_tags()
                audio = EasyID3(filepath)
            except Exception as e:
                from rich import print
                print(f"[bold red]Failed to read ID3 tags from {filepath}: {e}[/bold red]")
                return [], info
            
            # Apply Tags
            audio['title'] = title
            if artist:
                audio['artist'] = artist
                
            audio.save()
            from rich import print
            tag_status = f"Title: {title}"
            if artist:
                tag_status += f", Artist: {artist}"
            print(f"[bold green]Applied ID3 tags (from metadata): {tag_status}[/bold green]")
            
        return [], info

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
        # Strip "Album - " prefix if present (common in YouTube Music albums)
        playlist_title = info_dict.get('title', '%(playlist_title)s')
        if isinstance(playlist_title, str) and playlist_title.startswith('Album - '):
            clean_title = playlist_title[len('Album - '):]
            ydl_opts['outtmpl'] = f'download/{clean_title}/%(playlist_index)s - %(title)s.%(ext)s'
        else:
            ydl_opts['outtmpl'] = 'download/%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'
    else:
        ydl_opts['outtmpl'] = 'download/%(title)s.%(ext)s'
    
    # We will pass progress hooks
    progress_manager = DownloadProgressManager(info_dict)
    ydl_opts['progress_hooks'] = [progress_manager.yt_dlp_hook]
    
    try:
        with progress_manager:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.add_post_processor(ID3TagPostProcessor(downloader=ydl), when='post_process')
                ydl.download([url])
    except Exception as e:
        from rich import print
        print(f"\n[bold red]Fatal Download Error: {e}[/bold red]")
