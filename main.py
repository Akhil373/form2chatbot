from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

submit_form_answer = {
    "name": "submit_form_answer",
    "description": "Call this function to submit the user's answer for a single form question.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The exact, original question string from the form JSON, e.g., 'Enter your name'.",
            },
            "answer": {
                "type": "string",
                "description": "The user's final, extracted answer, e.g., 'John Doe' or 'Highly aware' or '7'.",
            },
        },
        "required": ["question", "answer"],
    },
}


raw_data = ""
try:
    with open("test.json", "r", encoding="utf-8") as f:
        raw_data += f.read()
except Exception as e:
    print(e)

system = f"""
You are a friendly and helpful assistant. Your primary goal is to have a 
natural, casual conversation with a user to fill out a form.

Here's the form questions and details:
{raw_data}

**Your Instructions:**
1.  Ask one question at a time and be conversational.
2.  When you get a valid answer, you MUST call the `submit_form_answer` function.
3.  **IMPORTANT:** If the user asks a clarifying question (like 'what does that mean?') 
    or goes on a small tangent, you should engage with them naturally. 
    Answer their question first. Do not be overly rigid.
4.  After you've answered their question, gently guide them back to 
    the form question you were trying to ask.
"""

client = genai.Client()
tools = types.Tool(function_declarations=[submit_form_answer])
config = types.GenerateContentConfig(system_instruction=system, tools=[tools])


chat = client.chats.create(model="gemini-2.5-flash", config=config)

form_data = {}

print("type '/bye' to exit chat.")
while True:
    user_prompt = input("You: ")
    if user_prompt.strip().lower() == "/bye":
        break

    response = chat.send_message(user_prompt)

    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call

        print(f"Function call: {function_call.name}")
        print(f"Arguments: {function_call.args}")

        question_text = function_call.args["question"]
        answer_text = function_call.args["answer"]
        form_data[question_text] = answer_text

        function_response_part = types.Part.from_function_response(
            name=function_call.name,
            response={
                "status": "success",
                "message": f"Answer for '{question_text}' recorded.",
            },
        )
        response = chat.send_message(function_response_part)

        print("AI: " + response.text)

    else:
        print("AI: " + response.text)

print("\n--- Form Complete ---")
import json

print(json.dumps(form_data, indent=2))
