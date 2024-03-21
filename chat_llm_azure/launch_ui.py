import gradio as gr

from auth import (
    auth_method
)
from blocks_history import (
    load_files,
    file_selected,
    set_folder,
    remove_file
)
from blocks_live_chat import (
    append_user,
    append_ai,
    clear_log
)


def show_live():
    return {
        cb_live: gr.Chatbot(visible=True),
        gr_live: gr.Group(visible=True),
        row_live: gr.Row(visible=True),
        btn_live: gr.Button(interactive=False),

        cb_history: gr.Chatbot(visible=False),
        gr_history: gr.Group(visible=False),
        btn_history: gr.Button(interactive=True)
    }


def show_history():
    return {
        cb_live: gr.Chatbot(visible=False),
        gr_live: gr.Group(visible=False),
        row_live: gr.Row(visible=False),
        btn_live: gr.Button(interactive=True),

        cb_history: gr.Chatbot(visible=True),
        gr_history: gr.Group(visible=True),
        btn_history: gr.Button(interactive=False)
    }


css = """
.danger {background: red;} 
"""

with gr.Blocks(fill_height=True, title='PXL CheaPT', css=css) as llm_client_ui:
    # live client UI
    cb_live = gr.Chatbot(label='Chat', scale=1)
    with gr.Group() as gr_live:
        with gr.Row():
            tb_user = gr.Textbox(show_label=False, placeholder='Enter prompt here...', scale=10)
            btn_send = gr.Button('', scale=0, min_width=64, icon='../assets/icons/send.png')
            btn_remove = gr.Button('', scale=0, min_width=64, icon='../assets/icons/disposal.png')
    with gr.Row() as row_live:
        lbl_debug = gr.HTML()

    # event handlers
    tb_user.submit(append_user, [tb_user, cb_live], [cb_live]
                   ).then(append_ai, [tb_user, cb_live], [tb_user, cb_live, lbl_debug])
    btn_send.click(append_user, [tb_user, cb_live], [cb_live]
                   ).then(append_ai, [tb_user, cb_live], [tb_user, cb_live, lbl_debug])
    btn_remove.click(clear_log, None, [tb_user, cb_live])

    # log viewer UI
    cb_history = gr.Chatbot(label='History', scale=1, visible=False)

    with gr.Group(visible=False) as gr_history:
        with gr.Row():
            dd_files = gr.Dropdown(
                [],
                show_label=False,
                info="Select a log file to view the details",
                scale=10
            )
            btn_refresh = gr.Button(value='', scale=0, min_width=64, icon='../assets/icons/refresh.png')
            btn_remove = gr.Button(value='', scale=0, min_width=64, icon='../assets/icons/disposal.png',
                                   elem_classes='danger')

    # event handlers
    btn_refresh.click(load_files, [], [dd_files])
    btn_remove.click(remove_file, [dd_files], [dd_files])
    dd_files.input(file_selected, [dd_files], [cb_history])

    # toggle UI
    with gr.Row():
        btn_live = gr.Button('Chat', icon='../assets/icons/chat.png', interactive=False)
        btn_history = gr.Button('History', icon='../assets/icons/history.png')

    # event handlers
    btn_live.click(show_live, [], [cb_live, gr_live, row_live, cb_history, gr_history, btn_live, btn_history])
    btn_history.click(show_history, [], [cb_live, gr_live, row_live, cb_history, gr_history, btn_live, btn_history])
    llm_client_ui.load(set_folder, None, None)

# To create a public link, set `share=True` in `launch()`.
llm_client_ui.launch(auth=auth_method)