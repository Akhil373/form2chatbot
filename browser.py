import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from markdownify import markdownify as md
from playwright.sync_api import Playwright, sync_playwright

load_dotenv()
chrome_path = "/usr/bin/google-chrome-stable"
user_data_dir = "/home/axle/code/python/form2chatbot/tmp"

# URL = "https://forms.gle/DFXPpFtFo5WH4LnZ9"
URL = "https://aishe.nic.in/moetaskforce/#/surveyForm?langId=23&questionUserType=YjkyNTQ0Mjg2ZTI5NWVlMzU4NjdmOWJkNjgyMzQ1ZjE6OjNmNjc2OTkxNDA4NjI2MWJjN2JmOTM0OTllNGJjNTNmNTE2YTk5NmU5NjlhOWRmYTkyMDJjMDZlOWQ2MjA1YmQ6Olh2ZTlETmpmWGdQT0ROWjMvbXJrK0E9PQ%3D%3D"


def run(playwright: Playwright) -> str:
    chromium = playwright.chromium
    browser = chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(URL)
    time.sleep(5)
    res_md = page.content()
    browser.close()
    return res_md


def markdown_to_json(md_data: str):
    client = genai.Client()

    system_prompt = """
    You are a specialized web form extractor who follows user instructions without any errors.
    """

    user_prompt = (
        """
    Your task is the take the raw Markdown of a website, and convert it into structured data. Use the following format:

    [{
        "question": "Field label or question",
        "type": "text|radio|checkbox|rating|dropdown|email|etc",
        "options": ["Option1", "Option2", ...],
        "required": true|false,
        "rating_scale": {"min": 1, "max": 10} // Only for rating fields
    }]


    Exclude all the 'newline' \n symbols.
    Do not output anything else other than that.

    Here's your data:
    """
        + md_data
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(system_instruction=system_prompt),
        contents=user_prompt,
    )

    res_md = response.text
    print(response.text)
    start_fence = "```json"
    end_fence = "```"
    if res_md.startswith(start_fence):
        res_md = res_md[len(start_fence) :]
    if res_md.endswith(end_fence):
        res_md = res_md[: -len(end_fence)]
    res_md = res_md.strip()
    # res_md = res_md.removeprefix("```json")
    # res_md = res_md.removesuffix("```")
    res_md = res_md.strip().replace("\\n", "\n")

    try:
        with open("test.json", "w", encoding="utf-8") as f:
            f.write(res_md)
    except Exception as e:
        print(e)


def main():
    with sync_playwright() as playwright:
        print("LOG: scraping html content...")
        raw_html = run(playwright)

    raw_markdown = None

    if raw_html:
        print("LOG: converting html to markdown...")
        raw_markdown = md(raw_html)

        print("LOG: preparing the final json...")
        markdown_to_json(raw_markdown)
    else:
        print("no html content")


if __name__ == "__main__":
    main()
    print("LOG: Done!")
