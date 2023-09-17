import gradio as gr
from modules import script_callbacks
from modules import shared

def on_ui_settings():
    section = 'civitai_browser_sfz', 'Civitai Browser'
    shared.opts.add_option(
        key='civsfz_number_of_tabs',
        info=shared.OptionInfo(
            3 ,
            label='Number of tabs (requires Reload UI)',
            component=gr.Slider,
            component_args={'minimum': 1, 'maximum': 8, 'step': 1},
            section=section,
        )   # .needs_reload_ui()
    )
    shared.opts.add_option(
        key='civsfz_number_of_cards',
        info=shared.OptionInfo(
            12 ,
            label='Number of cards per page',
            component=gr.Slider,
            component_args={'minimum': 8, 'maximum': 36, 'step': 1},
            section=section,
        )
    )

script_callbacks.on_ui_settings(on_ui_settings)