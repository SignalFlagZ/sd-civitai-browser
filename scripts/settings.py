import gradio as gr
from modules import script_callbacks
from modules import shared

def on_ui_settings():
    section = 'Civsfz_Browser', 'CivBrowser'
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
            component_args={'minimum': 8, 'maximum': 48, 'step': 1},
            section=section,
        )
    )
    shared.opts.add_option(
        key='civsfz_card_size_width',
        info=shared.OptionInfo(
            8 ,
            label='Card width (unit:1em)',
            component=gr.Slider,
            component_args={'minimum': 5, 'maximum': 30, 'step': 1},
            section=section,
        )
    )
    shared.opts.add_option(
        key='civsfz_card_size_height',
        info=shared.OptionInfo(
            12 ,
            label='Card height (unit:1em)',
            component=gr.Slider,
            component_args={'minimum': 5, 'maximum': 30, 'step': 1},
            section=section,
        )
    )
    shared.opts.add_option(
        key='civsfz_hover_zoom_magnification',
        info=shared.OptionInfo(
            1.5 ,
            label='Zoom magnification when hovering',
            component=gr.Slider,
            component_args={'minimum': 1, 'maximum': 2.4, 'step': 0.1},
            section=section,
        )
    )
    shared.opts.add_option(
        key='civsfz_treat_x_as_nsfw',
        info=shared.OptionInfo(
            True ,
            label='If the first image is of type "X", treat the model as nsfw',
            component=gr.Checkbox,
            section=section,
        )
    )
    shared.opts.add_option(
        key='civsfz_treat_slash_as_folder_separator',
        info=shared.OptionInfo(
            True,
            label=r'Treat "/" as folder separator. If you change this, some models may not be able to confirm the existence of the file.',
            component=gr.Checkbox,
            section=section,
        )
    )
    shared.opts.add_option(
        key='civsfz_figcaption_background_color',
        info=shared.OptionInfo(
            '#798a9f' ,
            label='Background color of model name',
            component=gr.ColorPicker,
            section=section,
        )
    )
    shared.opts.add_option(
        key='civsfz_default_shadow_color',
        info=shared.OptionInfo(
            '#798a9f' ,
            label='Frame color of cards',
            component=gr.ColorPicker,
            section=section,
        )
    )
    shared.opts.add_option(
        key='civsfz_alreadyhave_shadow_color',
        info=shared.OptionInfo(
            '#7fffd4' ,
            label='Frame color of cards you already have',
            component=gr.ColorPicker,
            section=section,
        )
    )

script_callbacks.on_ui_settings(on_ui_settings)