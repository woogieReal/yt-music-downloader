from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Header, Footer, DataTable, ProgressBar, RichLog, Button, Checkbox
from textual.containers import Vertical
from textual import work
from typing import Dict, Any

class TUIProgressHooks:
    def __init__(self, app: "YouTubeDownloaderApp", info_dict: Dict[str, Any]):
        self.app = app
        self.is_playlist = 'entries' in info_dict
        if self.is_playlist:
            entries = info_dict.get('entries', [])
            self.total_items = sum(1 for e in entries if e is not None)
        else:
            self.total_items = 1
            
        self.completed_items = 0

    def __enter__(self):
        self.app.call_from_thread(self.app.setup_progress, self.is_playlist, self.total_items)
        return self

    def __exit__(self, *args):
        pass

    def yt_dlp_hook(self, d: Dict[str, Any]):
        status = d.get('status')
        filename = d.get('info_dict', {}).get('title', d.get('filename', 'Unknown'))
        
        if status == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            
            if total_bytes > 0:
                self.app.call_from_thread(self.app.update_file_progress, filename, downloaded, total_bytes)
                
        elif status == 'finished':
            self.completed_items += 1
            if self.is_playlist:
                self.app.call_from_thread(self.app.update_overall_progress, self.completed_items)
            self.app.call_from_thread(self.app.tui_print, f"[cyan]Finished downloading {filename}[/cyan]")


class YouTubeDownloaderApp(App):
    CSS = """
    #input_view {
        align: center middle;
    }
    #input_dialog {
        padding: 1 2;
        width: 60;
        height: auto;
        min-height: 13;
        border: thick $background 80%;
        background: $surface;
    }
    #url_input {
        margin-top: 1;
    }
    #use_playlist_thumb {
        margin-top: 1;
    }
    #manual_metadata_checkbox {
        margin-top: 1;
    }
    #manual_metadata_inputs {
        display: none;
        margin-top: 1;
        padding-left: 1;
        height: auto;
    }
    #manual_metadata_inputs.-active {
        display: block;
    }
    .meta-input {
        margin-top: 1;
    }
    #download_view {
        display: none;
        padding: 1 2;
    }
    #download_view.-active {
        display: block;
    }
    .hidden {
        display: none;
    }
    #summary_table {
        height: 10;
        margin-bottom: 1;
    }
    #log_view {
        height: 1fr;
        border: solid $secondary;
        margin-top: 1;
    }
    #back_button {
        margin-top: 1;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        # Input Screen
        with Vertical(id="input_view"):
            with Vertical(id="input_dialog"):
                yield Label("Enter YouTube Video or Playlist URL, and press Enter:")
                yield Input(placeholder="https://youtube.com/...", id="url_input")
                yield Checkbox("Use Playlist Cover as Album Art for all tracks?", value=False, id="use_playlist_thumb")
                yield Checkbox("Set metadata manually?", value=False, id="manual_metadata_checkbox")
                with Vertical(id="manual_metadata_inputs"):
                    yield Input(placeholder="Artist", id="meta_artist", classes="meta-input")
                    yield Input(placeholder="Album", id="meta_album", classes="meta-input")
                    yield Input(placeholder="Year", id="meta_year", classes="meta-input")
        
        # Download Screen
        with Vertical(id="download_view"):
            yield Label("[bold cyan]Fetching metadata...[/bold cyan]", id="status_label")
            yield DataTable(id="summary_table")
            
            yield Label("Overall Progress", id="overall_progress_label", classes="hidden")
            yield ProgressBar(id="overall_progress", classes="hidden")
            
            yield Label("Current File", id="current_file_label")
            yield ProgressBar(id="current_file_progress")
            
            yield RichLog(id="log_view", markup=True)
            yield Button("Return to Home (Download More)", id="back_button", variant="primary", classes="hidden")
            
        yield Footer()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "manual_metadata_checkbox":
            inputs_view = self.query_one("#manual_metadata_inputs")
            if event.checkbox.value:
                inputs_view.add_class("-active")
                self.query_one("#input_dialog").styles.min_height = 25 # Expand dialog height
            else:
                inputs_view.remove_class("-active")
                self.query_one("#input_dialog").styles.min_height = 13 # Restore dialog height

    def on_input_submitted(self, event: Input.Submitted) -> None:
        url = self.query_one("#url_input", Input).value.strip()
        if not url:
            return
            
        use_playlist_thumb = self.query_one("#use_playlist_thumb", Checkbox).value
        
        manual_meta = None
        if self.query_one("#manual_metadata_checkbox", Checkbox).value:
            manual_meta = {
                'artist': self.query_one("#meta_artist", Input).value.strip(),
                'album': self.query_one("#meta_album", Input).value.strip(),
                'year': self.query_one("#meta_year", Input).value.strip()
            }
            
        self.query_one("#input_view").styles.display = "none"
        self.query_one("#download_view").styles.display = "block"
        self.run_download(url, use_playlist_thumb, manual_meta)
            
    def tui_print(self, text: str):
        """Redirect print statements to the RichLog."""
        log_view = self.query_one("#log_view", RichLog)
        log_view.write(text)

    @work(thread=True)
    def run_download(self, url: str, use_playlist_thumb: bool = True, manual_meta: Dict[str, str] = None) -> None:
        from ytmd.downloader import fetch_info, download_media
        
        self.call_from_thread(self.tui_print, f"Started fetching info for: {url}")
        
        try:
            info = fetch_info(url)
            self.call_from_thread(self.update_summary_table, info)
            
            pm = TUIProgressHooks(self, info)
            
            def update_tags(idx: str, tags: dict):
                self.call_from_thread(self.update_row_status, idx, tags)
                
            download_media(url, info, progress_manager=pm, print_func=self.tui_print, update_tags_func=update_tags, use_playlist_thumb=use_playlist_thumb, manual_meta=manual_meta)
            
            self.call_from_thread(self.tui_print, "[bold green]Download Process Completed![/bold green]")
            self.call_from_thread(self.show_finish_button)
        except Exception as e:
            self.call_from_thread(self.tui_print, f"[bold red]Error[/bold red]: {e}")
            self.call_from_thread(self.show_finish_button)

    def show_finish_button(self):
        self.query_one("#back_button", Button).remove_class("hidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_button":
            # 1. Reset widgets
            self.query_one("#url_input", Input).value = ""
            self.query_one("#use_playlist_thumb", Checkbox).value = False
            self.query_one("#manual_metadata_checkbox", Checkbox).value = False
            self.query_one("#meta_artist", Input).value = ""
            self.query_one("#meta_album", Input).value = ""
            self.query_one("#meta_year", Input).value = ""
            
            self.query_one("#status_label", Label).update("[bold cyan]Fetching metadata...[/bold cyan]")
            
            table = self.query_one("#summary_table", DataTable)
            table.clear(columns=True)
            
            self.query_one("#overall_progress_label", Label).add_class("hidden")
            self.query_one("#overall_progress", ProgressBar).add_class("hidden")
            self.query_one("#current_file_label", Label).update("Current File")
            self.query_one("#current_file_progress", ProgressBar).update(total=100, progress=0)
            
            self.query_one("#log_view", RichLog).clear()
            self.query_one("#back_button", Button).add_class("hidden")
            
            # 2. Switch views
            self.query_one("#download_view").styles.display = "none"
            self.query_one("#input_view").styles.display = "block"
            self.query_one("#url_input").focus()

    def update_summary_table(self, info_dict: Dict[str, Any]) -> None:
        self.query_one("#status_label", Label).update("[bold green]Metadata fetched. Downloading...[/bold green]")
        table = self.query_one("#summary_table", DataTable)
        table.add_column("Index", key="index")
        table.add_column("YT Title", key="yt_title")
        table.add_column("Duration", key="duration")
        table.add_column("ID3 Title", key="title")
        table.add_column("Artist", key="artist")
        table.add_column("Album", key="album")
        table.add_column("Year", key="year")
        table.add_column("Track", key="track")
        
        if 'entries' in info_dict:
            self.tui_print(f"[bold yellow]Playlist Detected:[/bold yellow] {info_dict.get('title', 'Unknown')}")
            entries = info_dict.get('entries', [])
            for i, entry in enumerate(entries, 1):
                if not entry: continue
                title = entry.get('title', 'Unknown')
                duration = str(entry.get('duration', 'N/A'))
                table.add_row(str(i), title, duration, "-", "-", "-", "-", "-", key=str(i))
        else:
            self.tui_print("[bold yellow]Single Video Detected[/bold yellow]")
            title = info_dict.get('title', 'Unknown')
            duration = str(info_dict.get('duration', 'N/A'))
            table.add_row("1", title, duration, "-", "-", "-", "-", "-", key="1")

    def update_row_status(self, idx: str, tags: dict) -> None:
        try:
            table = self.query_one("#summary_table", DataTable)
            for key, value in tags.items():
                table.update_cell(row_key=idx, column_key=key, value=value, update_width=True)
        except Exception as e:
            self.tui_print(f"[red]Error updating table cells for row {idx}: {e}[/red]")

    def setup_progress(self, is_playlist: bool, total_items: int) -> None:
        if is_playlist and total_items > 1:
            lbl = self.query_one("#overall_progress_label", Label)
            pb = self.query_one("#overall_progress", ProgressBar)
            lbl.remove_class("hidden")
            pb.remove_class("hidden")
            lbl.update(f"Overall Progress ({total_items} items)")
            pb.update(total=total_items, progress=0)

    def update_file_progress(self, filename: str, downloaded: int, total: int) -> None:
        lbl = self.query_one("#current_file_label", Label)
        pb = self.query_one("#current_file_progress", ProgressBar)
        
        short_name = filename[:40] + '...' if len(filename) > 40 else filename
        lbl.update(f"Downloading: [cyan]{short_name}[/cyan]")
        
        # When progress updates are rapidly fired, only update if total/progress changed
        if pb.total != total:
            pb.update(total=total)
        pb.update(progress=downloaded)

    def update_overall_progress(self, completed: int) -> None:
        pb = self.query_one("#overall_progress", ProgressBar)
        pb.update(progress=completed)

def get_url_from_ui() -> str:
    # We no longer just return a URL and exit. The app STAYS ALIVE until completion or exit.
    app = YouTubeDownloaderApp()
    app.run()
    return ""

def run_tui_app(url: str = None):
    app = YouTubeDownloaderApp()
    if url:
        # If url is passed from CLI, we skip Input and go straight to download
        # Textual App has a run method, we can trigger the download on mount
        def trigger_download_on_mount():
            app.query_one("#input_view").styles.display = "none"
            app.query_one("#download_view").styles.display = "block"
            app.run_download(url, use_playlist_thumb=True) # Default from CLI
        # Schedule the action on mount
        app.call_after_refresh(trigger_download_on_mount)
    app.run()

