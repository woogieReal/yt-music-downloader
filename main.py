import argparse
import sys
from ytmd.downloader import fetch_info, download_media
from ytmd.ui import display_summary_table

def main():
    parser = argparse.ArgumentParser(description="YouTube MP3 Downloader CLI")
    parser.add_argument("url", help="YouTube Video or Playlist URL")
    
    args = parser.parse_args()
    
    try:
        # 1. Fetch info
        print("\n[bold cyan]Fetching metadata...[/bold cyan]")
        info = fetch_info(args.url)
        
        # 2. Display Table UI
        display_summary_table(info)
        
        # 3. Confirm download (Optional, skip for pure CLI, but good for UX)
        print()
        
        # 4. Download
        download_media(args.url, info)
        
    except KeyboardInterrupt:
        print("\n\n[bold red]Download cancelled by user.[/bold red]")
        sys.exit(1)
    except Exception as e:
        print(f"\n[bold red]Error: {e}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    from rich import print
    main()
