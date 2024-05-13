import json
import os
import time

import gradio as gr
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

system_instruction = {
    "role": "system",
    "content": "Be concise. Be precise. "
               "I would like you to take a deep breath before responding. "
               "Always think step by step. "
}


def store_history(history, log_folder):
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    timestamp = time.time()
    log_file = open(f"{log_folder}{timestamp}.json", "w")
    content = json.dumps(history, indent=1)
    log_file.write(content)
    log_file.close()


def predict(message, history):
    history_openai_format = [system_instruction]  # openai format

    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human})
        history_openai_format.append({"role": "assistant", "content": assistant})
    history_openai_format.append({"role": "user", "content": message})

    # call the language model
    response_stream = client.chat.completions.create(model='anthropic/claude-3-haiku',
                                                     messages=history_openai_format,
                                                     extra_headers={
                                                         "HTTP-Referer": "PXL University College",
                                                         "X-Title": "chat_demo.py"
                                                     },
                                                     stream=True)
    partial_message = ""
    for chunk in response_stream:  # stream the response
        if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
            partial_message = partial_message + chunk.choices[0].delta.content
            yield partial_message

    # store in a log file
    history_openai_format.append({"role": "assistant", "content": partial_message})
    store_history(history_openai_format, 'logs/')

    # cost estimate (based on GPT-4 pricing)
    tokeniser = tiktoken.encoding_for_model("gpt-4")
    hist_string = json.dumps(history_openai_format)
    hist_len = len(tokeniser.encode(hist_string))
    cost_in_cents = round(hist_len / 1000 * 3, ndigits=1)
    if cost_in_cents > 0:
        print(f"Cost estimate: {cost_in_cents} cents for history of {hist_len} tokens")


# https://www.gradio.app/guides/creating-a-chatbot-fast
gr.ChatInterface(predict).launch(server_name='0.0.0.0')
