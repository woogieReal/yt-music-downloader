import argparse
import sys
from ytmd.downloader import fetch_info, download_media
from ytmd.ui import display_summary_table
from ytmd.tui import run_tui_app
from rich import print

def process_url(url: str):
    """
    Process a single URL: fetch metadata, display UI, and download.
    """
    try:
        # 1. Fetch info
        print("\n[bold cyan]Fetching metadata...[/bold cyan]")
        info = fetch_info(url)
        
        # 2. Display Table UI
        display_summary_table(info)
        
        # 3. Confirm download (Optional, skip for pure CLI, but good for UX)
        print()
        
        # 4. Download
        download_media(url, info)
        
    except KeyboardInterrupt:
        print("\n\n[bold red]Download cancelled by user.[/bold red]")
        sys.exit(1)
    except Exception as e:
        print(f"\n[bold red]Error: {e}[/bold red]")
        # Don't exit on error if processing multiple URLs, just print and continue

def main():
    parser = argparse.ArgumentParser(description="YouTube MP3 Downloader CLI")
    parser.add_argument("url", nargs="?", help="YouTube Video or Playlist URL (Optional, opens UI if omitted)")
    
    args = parser.parse_args()
    
    url = args.url
    if not url:
        # Enable full TUI Downloader automatically
        run_tui_app()
    else:
        # Run pure CLI mode for automation
        process_url(url)

if __name__ == "__main__":
    main()
