import json
import queue
from threading import Thread

from elevenlabs.client import ElevenLabs
from pyttsx3 import speak
from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Button, Input, Markdown

import chatbot as cb


class ChatBotTUI(App):
    CSS = """
    Screen {
        background: #1e1e2e;
    }
    #history {
        height: 1fr;
        margin: 1;
        padding: 2;
        background: #1e1e2e;
        border: round #cba6f7;
    }
    Input {
        dock: bottom;
        margin: 1;
        background: #313244;
        color: #cdd6f4;
        border: round #cba6f7;
    }
    Input:focus {
        border: double #f5c2e7;
    }
    Markdown {
        background: #1e1e2e;
    }
    .user-message {
        background: #313244;
        color: #cdd6f4;
        padding: 1;
        margin: 0 0 1 0;
        border: round #89b4fa;
    }
    .ai-message {
        background: #313244;
        color: #a6adc8;
        padding: 1;
        margin: 0 0 1 0;
        border: round #94e2d5;
    }
    #mute_btn {
        dock: top;
        margin: 1 2;
        width: 10;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Button("🔊", id="mute_btn")
            with VerticalScroll(id="history"):
                yield Markdown(id="md")
            yield Input(placeholder="Type here…", id="inp")

    def on_mount(self):
        self.q_in = queue.Queue()
        self.q_out = queue.Queue()
        self.conversation = ""
        Thread(target=self.worker, daemon=True).start()
        self.send_system("Hi! Let's fill the form together.")
        self.set_timer(0.1, self.update_ui)
        self.speak_q = queue.Queue()
        self.muted = False
        Thread(target=self._speaker_worker, daemon=True).start()

    def send_system(self, text: str):
        self.conversation = text
        self.query_one("#md").update(self.conversation)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        msg = event.value
        if not msg.strip():
            return
        event.input.clear()
        self.conversation += f"\n\n**You**: {msg}"
        self.query_one("#md").update(self.conversation)
        self.query_one("#history").scroll_end(animate=True)
        self.q_in.put(msg)

    def save_form(self):
        try:
            for q in cb.json_data:
                q_text = q["question"]
                if q_text in cb.form_data:
                    q["answer"] = cb.form_data[q_text]

            with open("db.json", "w", encoding="utf-8") as f:
                json.dump(cb.json_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.q_out.put(f"[ERROR] Failed to save form data: {e}")
            return False

    def _speaker_worker(self):
        client = ElevenLabs(
            api_key="sk_78520589ee9adb60534c8078ff9897e82f00562f2bd3fbf4"
        )
        while True:
            text = self.speak_q.get()
            if text is None:
                break
            try:
                # audio = client.text_to_speech.convert(
                #     text=text,
                #     voice_id="JBFqnCBsd6RMkjVDRZzb",
                #     model_id="eleven_multilingual_v2",
                #     output_format="mp3_44100_128",
                # )
                # play.play(audio)
                speak(text)
            except Exception as e:
                print(f"TTS error: {e}")

    def on_button_pressed(self, event):
        if event.button.id == "mute_btn":
            self.muted = not self.muted
            event.button.label = "🔇" if self.muted else "🔊"
            if self.muted:
                with self.speak_q.mutex:
                    self.speak_q.queue.clear()

    def worker(self):
        cb.input = lambda _: self.q_in.get()
        cb.print = lambda txt, **k: self.q_out.put(txt)
        try:
            while True:
                user = cb.input("")
                if user.strip().lower() == "/bye":
                    self.q_out.put("Saving form data...")
                    if self.save_form():
                        self.q_out.put("Form saved successfully!")
                    self.q_out.put(None)
                    self.exit()
                    break
                cb.response = cb.chat.send_message(
                    f"Don't forget to call submit_form_answer function to submit my previous answers(if any).\nAnyway, let's continue:\n{
                        user
                    }"
                )
                if cb.response.candidates[0].content.parts[0].function_call:
                    fc = cb.response.candidates[0].content.parts[0].function_call
                    cb.print(f"Function call: {fc.name}")
                    cb.print(f"Arguments: {fc.args}")
                    q, a = fc.args["question"], fc.args["answer"]
                    cb.form_data[q] = a
                    fr = cb.types.Part.from_function_response(
                        name=fc.name,
                        response={
                            "status": "success",
                            "message": f"Answer for '{q}' recorded.",
                        },
                    )
                    cb.response = cb.chat.send_message(fr)
                    cb.print(cb.response.text)
                else:
                    cb.print(cb.response.text)
        except Exception as e:
            self.q_out.put(f"[ERROR] {e}")

    def update_ui(self):
        updated = False
        while True:
            try:
                txt = self.q_out.get_nowait()
                if txt is None:
                    break
                self.conversation += f"\n\n**AI**: {txt}"
                if not self.muted and not (
                    txt.startswith("Function call:")
                    or txt.startswith("Arguments:")
                    or txt.startswith("[ERROR]")
                ):
                    self.speak_q.put(txt)
                self.query_one("#md").update(self.conversation)
                updated = True
            except queue.Empty:
                break

        if updated:
            self.call_later(self.query_one("#history").scroll_end, animate=False)

        self.set_timer(0.1, self.update_ui)


if __name__ == "__main__":
    ChatBotTUI().run()
