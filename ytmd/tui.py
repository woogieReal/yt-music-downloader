from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Header, Footer
from textual.containers import Vertical

class URLInputApp(App[str]):
    """A Textual App to ask the user for a YouTube URL."""
    
    CSS = """
    Screen {
        align: center middle;
    }
    #dialog {
        padding: 1 2;
        width: 60;
        height: 11;
        border: thick $background 80%;
        background: $surface;
    }
    #url_input {
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="dialog"):
            yield Label("Enter YouTube Video or Playlist URL, and press Enter:")
            yield Input(placeholder="https://youtube.com/...", id="url_input")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip():
            self.exit(event.value.strip())
        else:
            self.exit("")

def get_url_from_ui() -> str:
    app = URLInputApp()
    result = app.run()
    return result if result else ""
