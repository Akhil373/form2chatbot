from textual.app import App, ComposeResult
from textual.containers import Center, Vertical
from textual.widgets import Button, Header, Static


class LauncherApp(App):
    """Master launcher that runs both extractor and chatbot in sequence"""

    CSS = """
    Screen {
        background: #1e1e2e;
        align: center middle;
    }
    
    #title {
        text-style: bold;
        color: #cba6f7;
        margin: 2;
    }
    
    #description {
        color: #cdd6f4;
        margin: 1;
        text-align: center;
    }
    
    Button {
        margin: 1;
        width: 50%;
        background: #cba6f7;
        color: #1e1e2e;
    }
    
    Button:hover {
        background: #f5c2e7;
    }
    
    #button-container {
        align: center middle;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Vertical():
                yield Static("Form Processing Workflow", id="title")
                yield Static(
                    "This will guide you through:\n\n"
                    "1. Form Extraction → 2. Chat Submission\n\n"
                    "Click Start to begin the automated workflow",
                    id="description",
                )
                with Vertical(id="button-container"):
                    yield Button("Start Workflow", variant="primary", id="start")
                    yield Button("Exit", variant="error", id="exit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start":
            self.run_workflow()
        else:
            self.exit()

    def run_workflow(self):
        """Run both apps in sequence"""
        self.run_worker(self.run_extractor_then_chat(), exclusive=True)

    async def run_extractor_then_chat(self):
        """Run extractor first, then chatbot"""
        from extractor_tui import ExtractorScreen

        extractor_app = ExtractorScreen()

        await extractor_app.run_async()

        from chat_tui import ChatBotTUI  # Replace with your actual chatbot import

        chatbot_app = ChatBotTUI()
        await chatbot_app.run_async()

        self.exit()


if __name__ == "__main__":
    LauncherApp().run()
