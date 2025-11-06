import asyncio
import os
import subprocess
import sys

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Input, LoadingIndicator, Static


class ExtractorScreen(App):
    CSS = """
    Screen {
        background: #1e1e2e;  /* Catppuccin Base */
    }
    
    #col {
        height: 100%;
        background: #1e1e2e;
    }
    
    #label {
        color: #cdd6f4;  /* Catppuccin Text */
        margin: 1;
    }
    
    Input { 
        margin: 1; 
        background: #313244;  /* Surface0 */
        color: #cdd6f4;
        border: round #cba6f7;  /* Mauve */
    }
    
    Input:focus {
        border: double #f5c2e7;  /* Pink */
    }
    
    Button { 
        margin: 1; 
        background: #cba6f7;  /* Mauve */
        color: #1e1e2e;  /* Base */
    }
    
    Button:disabled {
        background: #6c7086;  /* Overlay0 */
    }
    
    LoadingIndicator { 
        margin: 1; 
        color: #f5c2e7;  /* Pink */
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="col"):
            yield Static("Enter form URL:", id="label")
            yield Input(placeholder="https://forms.gle/...", id="url")
            yield Button("Extract", variant="primary", id="extract")
            yield LoadingIndicator(id="spin")

    def on_mount(self):
        self.query_one("#spin").visible = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "extract":
            url = self.query_one(Input).value.strip()
            if not url:
                return
            self.query_one("#spin").visible = True
            self.query_one("#extract").disabled = True
            self.run_worker(self.do_extract(url), exclusive=True)

    async def do_extract(self, url: str):
        env = os.environ.copy()
        env["FORM_URL"] = url
        try:
            # Run the extraction process
            result = await asyncio.to_thread(
                subprocess.run, [sys.executable, "extractor.py"], env=env, check=True
            )
            self.extraction_done(True)
        except subprocess.CalledProcessError:
            self.extraction_done(False)

    def extraction_done(self, success: bool):
        self.query_one("#spin").visible = False
        self.query_one("#extract").disabled = False

        if success:
            self.notify("✅ Extraction complete!", severity="information")
        else:
            self.notify(
                "❌ Extraction failed! Please check the URL and try again.",
                severity="error",
            )


if __name__ == "__main__":
    ExtractorScreen().run()
