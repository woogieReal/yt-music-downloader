import argparse
import sys
import os
from ytmd.downloader import fetch_info, download_media
from ytmd.ui import display_summary_table
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
    parser.add_argument("url", nargs='?', help="YouTube Video or Playlist URL")
    
    args = parser.parse_args()
    
    if args.url:
        # Single URL provided via CLI arguments
        process_url(args.url)
    else:
        # No URL provided, check for items.txt
        items_file = "items.txt"
        if os.path.exists(items_file):
            print(f"\n[bold green]Found '{items_file}'. Proceeding with batch download...[/bold green]")
            with open(items_file, "r") as f:
                urls = [line.strip() for line in f if line.strip()]
            
            if not urls:
                print(f"[bold yellow]Warning: '{items_file}' is empty.[/bold yellow]")
                sys.exit(0)
                
            for index, url in enumerate(urls, 1):
                print(f"\n[bold magenta]--- Processing Item {index}/{len(urls)} ---[/bold magenta]")
                print(f"[yellow]URL: {url}[/yellow]")
                process_url(url)
                
            print("\n[bold green]Batch download completed![/bold green]")
        else:
            print(f"\n[bold red]Error: No URL provided and '{items_file}' not found in current directory.[/bold red]")
            parser.print_help()
            sys.exit(1)

if __name__ == "__main__":
    main()
