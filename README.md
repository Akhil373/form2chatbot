# form2chatbot

Turn a web form into a chatbot conversation, collect answers, then fill the form back automatically.

## How it works

1. **Extract** — open a form URL, scrape the page, and use Gemini to turn fields into structured JSON (`db.json`)
2. **Chat** — talk through the form one question at a time in a TUI; answers are saved back to `db.json`
3. **Fill** — a browser agent walks the form and fills each field from the saved answers

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Google Chrome
- A Gemini API key (`GOOGLE_API_KEY` in `.env`)

Optional: TTS uses `pyttsx3` (local). ElevenLabs is present but not required for the default path.

## Setup

```bash
uv sync
uv run playwright install chromium
```

Create a `.env`:

```env
GOOGLE_API_KEY=your_key_here
```

## Usage

Run the full flow:

```bash
uv run python main.py
```

That launches, in order:

1. `extractor_tui.py` — paste a form URL and extract fields
2. `chat_tui.py` — conversational form fill (type `/bye` to save and exit)
3. `form_agent.py` — browser agent fills the live form from answers

You can also run each step alone:

```bash
uv run python extractor_tui.py   # or extractor.py with FORM_URL set
uv run python chat_tui.py        # or chatbot.py for plain CLI chat
uv run python form_agent.py
```

## Notes

- Extracted/filled form data lives in `db.json` (gitignored).
- `form_agent.py` currently has a hard-coded form URL and Chrome path — edit those before running fill.
- The fill agent does **not** submit the form; it only fills fields.
- Extraction launches a visible browser (`headless=False`).
