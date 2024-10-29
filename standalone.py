import gradio as gr
import argparse
from scripts.civsfz_ui import Components
from scripts.civsfz_downloader import Downloader

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    downloader = Downloader()
    tabNames=["a"]
    with gr.Blocks() as civitai_interface:
        with gr.Tabs(elem_id='civsfz_tab-element', elem_classes="civsfz-custom-property"):
            for i,name in enumerate(tabNames):
                with gr.Tab(label=name, id=f"tab{i}", elem_id=f"civsfz_tab{i}") as tab:
                    Components(downloader, tab)  # (tab)
        with gr.Row():
            gr.Markdown(value=f'<div style="text-align:center;">{ver}</div>')
            downloader.uiJsEvent(gr)

    civitai_interface.queue()
    civitai_interface.launch(inbrowser=(not args.disable_browser_open))
