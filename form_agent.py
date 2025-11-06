import asyncio
import json

from browser_use import ActionResult, Agent, Browser, ChatGoogle, Tools
from dotenv import load_dotenv
from pydantic import BaseModel


class GetNextFormItemInput(BaseModel):
    pass


load_dotenv()
tools = Tools()

URL = "https://forms.gle/RqqqodXEZuyG9A4t7"
# URL = "https://aishe.nic.in/moetaskforce/#/surveyForm?langId=23&questionUserType=YjkyNTQ0Mjg2ZTI5NWVlMzU4NjdmOWJkNjgyMzQ1ZjE6OjNmNjc2OTkxNDA4NjI2MWJjN2JmOTM0OTllNGJjNTNmNTE2YTk5NmU5NjlhOWRmYTkyMDJjMDZlOWQ2MjA1YmQ6Olh2ZTlETmpmWGdQT0ROWjMvbXJrK0E9PQ%3D%3D"

json_data = ""
try:
    with open("test.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
except Exception as e:
    print(e)

task = f"""
You are an expert browser automation assistant.
Your goal is to fill out a web form at the URL: {URL}.
IMPORTANT: You must ALWAYS reply with valid JSON containing an "action" field (and optionally "thinking").

You must follow this exact loop:
1.  Call the `get_next_form_item` tool.
2.  It will return a Question, Answer, and Type.
3.  Use your browser tools to find the element on the page
    that matches the "Question" and fill it with the "Answer".
4.  Once that step is done, go back to step 1 and call
    `get_next_form_item` again.
5.  Continue this loop until the tool returns "ALL_ITEMS_COMPLETE".
6.  Do not hit the submit button.
"""

current_question_index = 0


@tools.action("Get the next form item to fill")
def get_next_form_item(input: GetNextFormItemInput) -> ActionResult:
    """
    Gets the next item (question, answer, type) from the
    list for the LLM to process.
    """
    global current_question_index
    global json_data

    if current_question_index < len(json_data):
        item = json_data[current_question_index]

        current_question_index += 1

        return_string = f"""
        Here is the next item to process:

        Question: {item["question"]}
        Answer: {item["answer"]}
        Type: {item["type"]}

        Your task is to find the element for this question
        and fill it with the answer.
        After you are done, call this tool again.
        """
        return ActionResult(extracted_content=return_string)

    return ActionResult(extracted_content="ALL_ITEMS_COMPLETE")


llm = ChatGoogle(model="gemini-2.5-flash", temperature=0.1)


browser = Browser(
    executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    user_data_dir="./userData",
    profile_directory="Default",
)

agent = Agent(task=task, llm=llm, browser=browser, generate_gif=True, tools=tools)


async def main():
    await agent.run(max_steps=50)
    input("Press ENTER to close...")


asyncio.run(main())
