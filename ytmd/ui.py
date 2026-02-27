from rich.table import Table
from rich import print
from rich.progress import (
    Progress, 
    BarColumn, 
    TextColumn, 
    TimeRemainingColumn, 
    TransferSpeedColumn,
    TaskID
)
from typing import Dict, Any

def display_summary_table(info_dict: Dict[str, Any]) -> None:
    """Displays a pre-download summary table."""
    table = Table(title="Download Target Summary", show_lines=True)
    table.add_column("Index", justify="center", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Duration (s)", justify="right", style="green")

    if 'entries' in info_dict:
        # It's a playlist
        print(f"[bold yellow]Playlist Detected:[/bold yellow] {info_dict.get('title', 'Unknown')}")
        entries = info_dict.get('entries', [])
        for i, entry in enumerate(entries, 1):
            if not entry: continue
            title = entry.get('title', 'Unknown')
            duration = str(entry.get('duration', 'N/A'))
            table.add_row(str(i), title, duration)
    else:
        # Single Video
        print("[bold yellow]Single Video Detected[/bold yellow]")
        title = info_dict.get('title', 'Unknown')
        duration = str(info_dict.get('duration', 'N/A'))
        table.add_row("1", title, duration)

    if table.row_count > 0:
        print(table)
    else:
        print("[bold red]No downloadable content found.[/bold red]")


class DownloadProgressManager:
    """Manages the Rich progress bars for downloads."""
    
    def __init__(self, info_dict: Dict[str, Any]):
        self.is_playlist = 'entries' in info_dict
        if self.is_playlist:
            # count valid entries (ignoreerrors leaves None for blocked videos)
            entries = info_dict.get('entries', [])
            self.total_items = sum(1 for e in entries if e is not None)
            self.overall_title = info_dict.get('title', 'Playlist')
        else:
            self.total_items = 1
            self.overall_title = info_dict.get('title', 'Video')
            
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        )
        
        self.overall_task_id: TaskID | None = None
        self.current_task_id: TaskID | None = None
        self.completed_items = 0

    def __enter__(self):
        self.progress.start()
        if self.is_playlist and self.total_items > 1:
            self.overall_task_id = self.progress.add_task(
                f"[bold yellow]Overall ({self.total_items} items)[/bold yellow]", 
                total=self.total_items
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()

    def yt_dlp_hook(self, d: Dict[str, Any]):
        """The callback function for yt-dlp."""
        status = d.get('status')
        filename = d.get('info_dict', {}).get('title', d.get('filename', 'Unknown'))
        
        if status == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            
            # Create a task for the current file if it doesn't exist
            if self.current_task_id is None:
                short_name = filename[:30] + '...' if len(filename) > 30 else filename
                self.current_task_id = self.progress.add_task(
                    f"[green]{short_name}[/green]", total=total_bytes
                )
            
            # Update the task progress
            if total_bytes > 0:
                self.progress.update(self.current_task_id, completed=downloaded, total=total_bytes)
                
        elif status == 'finished':
            if self.current_task_id is not None:
                self.progress.update(self.current_task_id, completed=d.get('total_bytes', 100), total=d.get('total_bytes', 100))
                # Remove the current task so a new one is created for the next item
                self.progress.remove_task(self.current_task_id)
                self.current_task_id = None
                
            self.completed_items += 1
            if self.overall_task_id is not None:
                self.progress.update(self.overall_task_id, completed=self.completed_items)
