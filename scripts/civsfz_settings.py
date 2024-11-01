import gradio as gr
from modules import script_callbacks
from modules import shared
from scripts.civsfz_color import BaseModelColors
from scripts.civsfz_api import APIInformation


def on_ui_settings():
    from scripts.civsfz_shared import platform

    civsfz_section = 'Civsfz_Browser', 'CivBrowser'
    # OptionInfo params
    # default=None, label="", component=None, component_args=None, onchange=None, section=None, refresh=None, comment_before='', comment_after='', infotext=None, restrict_api=False, category_id=None
    # SD.Next dose not have OptionHTML
    dict_api_info = (
        {
            "civsfz_msg_html1": shared.OptionHTML(
                "The command line option `--civsfz-api-key` is deprecated. "
                "We felt that this was a risk because some users might not notice the API Key being displayed on the console."
                "The API key here is saved in the `settings.json` file. "
                "If you do not know this, there is a risk of your API key being leaked."
            ),
        }
        if not platform == "SD.Next"
        else {}
    )
    dict_options1 = {
        "civsfz_api_key": shared.OptionInfo(
            "",
            label="API Key",
            component=gr.Textbox,
            component_args={"type": "password"},
        ).info("Note: API key is stored in the `settings.json` file."),
        "civsfz_browsing_level": shared.OptionInfo(
            [1],
            label="Browsing level",
            component=gr.CheckboxGroup,
            component_args={
                "choices": list(APIInformation.nsfwLevel.items()),
            },
        ),
        "civsfz_number_of_tabs": shared.OptionInfo(
            3,
            label="Number of tabs",
            component=gr.Slider,
            component_args={"minimum": 1, "maximum": 8, "step": 1},
        ).needs_reload_ui(),
        "civsfz_number_of_cards": shared.OptionInfo(
            12,
            label="Number of cards per page",
            component=gr.Slider,
            component_args={"minimum": 8, "maximum": 48, "step": 1},
        ),
        "civsfz_card_size_width": shared.OptionInfo(
            8,
            label="Card width (unit:1em)",
            component=gr.Slider,
            component_args={"minimum": 5, "maximum": 30, "step": 1},
        ),
        "civsfz_card_size_height": shared.OptionInfo(
            12,
            label="Card height (unit:1em)",
            component=gr.Slider,
            component_args={"minimum": 5, "maximum": 30, "step": 1},
        ),
        "civsfz_hover_zoom_magnification": shared.OptionInfo(
            1.5,
            label="Zoom magnification when hovering",
            component=gr.Slider,
            component_args={"minimum": 1, "maximum": 2.4, "step": 0.1},
        ),
        "civsfz_treat_x_as_nsfw": shared.OptionInfo(
            True,
            label='If the first image is of type "X", treat the model as nsfw',
            component=gr.Checkbox,
        ),
        "civsfz_treat_slash_as_folder_separator": shared.OptionInfo(
            False,
            label=r'Treat "/" as folder separator. If you change this, some models may not be able to confirm the existence of the file.',
            component=gr.Checkbox,
        ),
        "civsfz_background_opacity": shared.OptionInfo(
            0.75,
            label="Background opacity for model names",
            component=gr.Slider,
            component_args={"minimum": 0.0, "maximum": 1.0, "step": 0.05},
        ),
        "civsfz_length_of_conditions_history": shared.OptionInfo(
            5,
            label="Length of conditions history",
            component=gr.Slider,
            component_args={"minimum": 5, "maximum": 10, "step": 1},
        ),
        "civsfz_length_of_search_history": shared.OptionInfo(
            5,
            label="Length of search term history",
            component=gr.Slider,
            component_args={"minimum": 5, "maximum": 15, "step": 1},
        ),
    }

    dict_modelColor = {}
    for item in BaseModelColors().colors:
        dict_modelColor[item["key"]] = shared.OptionInfo(
            item["color"],
            label=item["label"],
            component=gr.ColorPicker,
        )

    dict_shadow_color = {
        "civsfz_shadow_color_default": shared.OptionInfo(
            "#798a9f",
            label="Frame color for cards",
            component=gr.ColorPicker,
        ),
        "civsfz_shadow_color_alreadyhave": shared.OptionInfo(
            "#7fffd4",
            label="Frame color for cards you already have",
            component=gr.ColorPicker,
        ),
        "civsfz_shadow_color_alreadyhad": shared.OptionInfo(
            "#caff7f",
            label="Frame color for cards with updates",
            component=gr.ColorPicker,
        ),
    }
    dict_folder_info = {
            "civsfz_msg_html2": shared.OptionHTML(
                "Click <a href='https://github.com/SignalFlagZ/sd-webui-civbrowser/wiki'>here(Wiki|GitHub)</a> to learn how to specify the model folder and subfolders."
            ),
        } if not platform == "SD.Next" else {}

    label = 'Save folders for Types. Set JSON Key-Value pair. The folder separator is "/" not "\\". The path is relative from models folder or absolute.'
    info = 'Example for Stability Matrix: {"Checkpoint":"Stable-diffusion/sd"}'
    placefolder = '{\n\
                "Checkpoint": "MY_SUBFOLDER",\n\
                "VAE": "",\n\
                "TextualInversion": "",\n\
                "LORA": "",\n\
                "LoCon": "",\n\
                "Hypernetwork": "",\n\
                "AestheticGradient": "",\n\
                "Controlnet": "ControlNet",\n\
                "Upscaler": "OtherModels/Upscaler",\n\
                "MotionModule": "OtherModels/MotionModule",\n\
                "Poses": "OtherModels/Poses",\n\
                "Wildcards": "OtherModels/Wildcards",\n\
                "Workflows": "OtherModels/Workflows",\n\
                "Other": "OtherModels/Other"\n\
                }'

    dict_folders = {
        "civsfz_save_type_folders": (
            shared.OptionInfo(
                "",
                label=label + " " + info,
                comment_after=None,
                component=gr.Code,
                component_args=lambda: {
                    "language": "python",
                    "interactive": True,
                    "lines": 4,
                },
            )
            if platform == "Forge"
            else shared.OptionInfo(
                "",
                label=label,
                component=gr.Textbox,
                component_args={
                    "lines": 4,
                    "info": info,
                    "placeholder": placefolder,
                },
            )
        ),
        "civsfz_save_subfolder": shared.OptionInfo(
            "",
            label='Subfolders under type folders. Model information can be referenced by the key name enclosed in double curly brachets "{{}}". Available key names are "BASEMODELbkCmpt", "BASEMODEL", "NSFW", "USERNAME", "MODELNAME", "MODELID", "VERSIONNAME" and "VERSIONID". Folder separator is "/".',
            component=gr.Textbox,
            component_args={
                "lines": 1,
                "placeholder": "_{{BASEMODEL}}/.{{NSFW}}/{{MODELNAME}}",
            },
        ),
    }

    for key, opt in {
        **dict_api_info,
        **dict_options1,
        **dict_modelColor,
        **dict_shadow_color,
        **dict_folder_info,
        **dict_folders,
    }.items():
        opt.section = civsfz_section
        shared.opts.add_option(key, opt)

script_callbacks.on_ui_settings(on_ui_settings)
