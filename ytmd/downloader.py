import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor
from typing import Dict, Any
import os
import re

class ID3TagPostProcessor(PostProcessor):
    def __init__(self, downloader=None, collector: Dict[str, Any] = None, print_func=None, update_tags_func=None):
        super().__init__(downloader)
        self.collector = collector
        self.print_func = print_func or __import__('rich').print
        self.update_tags_func = update_tags_func

    def run(self, info):
        filepath = info.get('filepath')
        if filepath and filepath.endswith('.mp3'):
            from mutagen.easyid3 import EasyID3
            from mutagen.id3 import ID3NoHeaderError
            
            # 1. Metadata Extraction (Title, Artist, Album, Year, Track)
            title = info.get('title')
            artist = info.get('artist')
            album = info.get('album') or info.get('playlist_title')
            track_number = info.get('playlist_index') or info.get('track_number')
            
            # Year logic: release_year first, then fallback to upload_date (YYYYMMDD)
            year = info.get('release_year')
            if not year and info.get('upload_date'):
                upload_date = str(info.get('upload_date'))
                if len(upload_date) >= 4:
                    year = upload_date[:4]
            
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
                self.print_func(f"[bold red]Failed to read ID3 tags from {filepath}: {e}[/bold red]")
                return [], info
            
            # Apply Tags
            audio['title'] = title
            if artist:
                audio['artist'] = artist
            if album:
                audio['album'] = album
            if year:
                audio['date'] = str(year)
            if track_number:
                audio['tracknumber'] = str(track_number)
                
            audio.save()
            
            # Applied tags summary for TUI
            tags_dict = {
                "title": title,
                "artist": artist or "",
                "album": album or "",
                "year": str(year) if year else "",
                "track": str(track_number) if track_number else ""
            }
            
            if self.update_tags_func:
                idx = str(track_number) if track_number else "1"
                self.update_tags_func(idx, tags_dict)
            
            # Collect for xattr (if collector provided)
            if self.collector is not None:
                if artist:
                    self.collector['artists'].append(artist)
                if year:
                    try:
                        self.collector['years'].append(int(year))
                    except (ValueError, TypeError):
                        pass

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

def download_media(url: str, info_dict: Dict[str, Any], progress_manager=None, print_func=None, update_tags_func=None) -> None:
    """
    Download the media using the fetched info dictionary.
    """
    if print_func is None:
        from rich import print as rich_print
        print_func = rich_print
        
    if progress_manager is None:
        from ytmd.ui import DownloadProgressManager
        progress_manager = DownloadProgressManager(info_dict)
    
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
    ydl_opts['progress_hooks'] = [progress_manager.yt_dlp_hook]
    
    # Collector for playlist-level metadata (xattr)
    collector = {'artists': [], 'years': []}
    
    try:
        with progress_manager:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.add_post_processor(ID3TagPostProcessor(downloader=ydl, collector=collector, print_func=print_func, update_tags_func=update_tags_func), when='post_process')
                ydl.download([url])
                
        # After download, if it was a playlist, apply xattr to the directory
        if 'entries' in info_dict:
            # Determine destination directory
            playlist_title = info_dict.get('title', 'Unknown')
            if isinstance(playlist_title, str) and playlist_title.startswith('Album - '):
                playlist_title = playlist_title[len('Album - '):]
            
            root_dir = os.path.join('download', playlist_title)
            
            if os.path.isdir(root_dir):
                import subprocess
                final_artist = None
                if collector['artists']:
                    # Use the most frequent artist as representative
                    from collections import Counter
                    final_artist = Counter(collector['artists']).most_common(1)[0][0]
                
                final_year = None
                if collector['years']:
                    final_year = str(min(collector['years']))
                
                try:
                    if final_artist:
                        subprocess.run(['xattr', '-w', 'user.artist', final_artist, root_dir], stderr=subprocess.DEVNULL, check=True)
                    if final_year:
                        subprocess.run(['xattr', '-w', 'user.year', final_year, root_dir], stderr=subprocess.DEVNULL, check=True)
                    
                    if final_artist or final_year:
                        print_func(f"[bold cyan]  -> 디렉터리 메타데이터 업데이트: Artist='{final_artist}', Year='{final_year}'[/bold cyan]")
                except Exception:
                    # xattr is not available or not supported on this filesystem
                    pass

    except Exception as e:
        print_func(f"\n[bold red]Fatal Download Error: {e}[/bold red]")
