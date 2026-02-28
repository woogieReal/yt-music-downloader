import argparse
import os
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
import mutagen
from rich import print

def update_id3_tags(file_path, artist=None, album=None, year=None):
    """
    Updates the ID3 tags of a single MP3 file.
    Only updates the fields that are provided.
    """
    if not file_path.lower().endswith('.mp3'):
        return

    try:
        try:
            audio = EasyID3(file_path)
        except ID3NoHeaderError:
            audio = mutagen.File(file_path, easy=True)
            audio.add_tags()
            audio = EasyID3(file_path)
        
        updated = False
        if artist is not None:
            audio['artist'] = artist
            updated = True
        if album is not None:
            audio['album'] = album
            updated = True
        if year is not None:
            audio['date'] = str(year)
            updated = True
            
        if updated:
            audio.save()
            print(f"[green]Successfully updated:[/green] {os.path.basename(file_path)}")
            
    except Exception as e:
        print(f"[bold red]Error updating {file_path}:[/bold red] {e}")

def main():
    parser = argparse.ArgumentParser(description="Update ID3 tags for MP3 files or directories.")
    parser.add_argument("path", help="Path to an MP3 file or a directory containing MP3 files.")
    parser.add_argument("--artist", type=str, help="Artist name to set.")
    parser.add_argument("--album", type=str, help="Album name to set.")
    parser.add_argument("--year", type=str, help="Year (Date) to set.")

    args = parser.parse_args()

    target_path = os.path.abspath(args.path)

    if not os.path.exists(target_path):
        print(f"[bold red]Error:[/bold red] Path '{args.path}' does not exist.")
        return

    # Collect tags to update (only those provided by the user)
    # We use None as a sentinel to mean "do not update"
    update_params = {
        'artist': args.artist,
        'album': args.album,
        'year': args.year
    }

    if os.path.isfile(target_path):
        update_id3_tags(target_path, **update_params)
    elif os.path.isdir(target_path):
        print(f"[bold cyan]Scanning directory:[/bold cyan] {target_path}")
        mp3_files = [f for f in os.listdir(target_path) if f.lower().endswith('.mp3')]
        
        if not mp3_files:
            print("[yellow]No MP3 files found in the directory.[/yellow]")
            return
            
        for filename in mp3_files:
            file_path = os.path.join(target_path, filename)
            update_id3_tags(file_path, **update_params)
        
        print(f"\n[bold green]Finished processing {len(mp3_files)} files.[/bold green]")

if __name__ == "__main__":
    main()
