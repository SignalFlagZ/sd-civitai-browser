import gradio as gr
from modules import script_callbacks
from modules import shared

def on_ui_settings():
    section = "civitai_browser_sfz", "Civitai Browser"
    shared.opts.add_option(
        key="civsfz_number_of_cards",
        info=shared.OptionInfo(
            12 ,
            label="Number of cards per page",
            component=gr.Slider,
            component_args={"minimum": 8, "maximum": 36, "step": 2},
            section=section,
        ),
    )

script_callbacks.on_ui_settings(on_ui_settings)