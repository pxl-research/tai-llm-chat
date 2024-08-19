import os
import time

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def append_user(user_message, chat_history, message_list):
    chat_history.append((user_message, None))
    message_list.append({"role": "user", "content": user_message})
    return "", chat_history, message_list


def append_bot(chat_history, message_list):
    response_stream = client.chat.completions.create(model='openai/gpt-4o-mini',
                                                     messages=message_list,
                                                     # tools=tools,
                                                     extra_headers={
                                                         "HTTP-Referer": "PXL University College",
                                                         "X-Title": "basic_chat.py"
                                                     },
                                                     stream=True)

    partial_message = ""
    for chunk in response_stream:  # stream the response
        if len(chunk.choices) > 0:
            if chunk.choices[0].delta.content is not None:
                partial_message = partial_message + chunk.choices[0].delta.content
                chat_history[-1][1] = partial_message
                yield chat_history, message_list

    message_list.append({"role": "assistant", "content": chat_history[-1][1]})
    print(message_list)


# UI
# https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks
with (gr.Blocks(fill_height=True, title='Tool Calling') as llm_client_ui):
    messages = gr.State([])
    cb_live = gr.Chatbot(label='Chat', scale=1)
    with gr.Group() as gr_live:
        with gr.Row():
            tb_user = gr.Textbox(show_label=False, placeholder='Enter prompt here...', scale=10)
            btn_send = gr.Button('', scale=0, min_width=64, icon='../../assets/icons/send.png')
    btn_clear = gr.Button("Clear")

    # event handlers
    tb_user.submit(append_user, [tb_user, cb_live, messages], [tb_user, cb_live, messages],
                   queue=False).then(append_bot, [cb_live, messages], [cb_live, messages])
    btn_send.click(append_user, [tb_user, cb_live, messages], [tb_user, cb_live, messages],
                   queue=False).then(append_bot, [cb_live, messages], [cb_live, messages])
    btn_clear.click(lambda: None, None, cb_live, queue=False)

llm_client_ui.launch(auth=None, server_name='0.0.0.0')