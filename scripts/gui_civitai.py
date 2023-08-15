import gradio as gr
from html import escape
from modules import script_callbacks
import modules.scripts as scripts
from scripts.civitai_api import civitaimodels
from scripts.file_manage import save_text_file, download_file_thread, saveImageFiles
from colorama import Fore, Back, Style

# Set the URL for the API endpoint
civitai = civitaimodels("https://civitai.com/api/v1/models?limit=10")

def api_next_page(next_page_url:str=""):
    if not next_page_url:
        next_page_url = civitai.nextPage()
    return civitai.requestApi(next_page_url)

def update_prev_page(show_nsfw, content_type):
    return update_next_page(show_nsfw, content_type, False)

def update_next_page(show_nsfw, content_type, isNext=True, ):
    if isNext:
        civitai.updateJsonData(api_next_page(civitai.nextPage()), content_type)
    else:
        civitai.updateJsonData(api_next_page(civitai.prevPage()), content_type)
    civitai.setShowNsfw(show_nsfw)
    pages = civitai.getPages()
    hasPrev = not civitai.prevPage() == ""
    hasNext = not civitai.nextPage() == ""
    model_dict = civitai.getModelNames() if (show_nsfw) else civitai.getModelNamesSfw()
    HTML = civitai.modelCardsHtml(model_dict)
    return  gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value=None),\
            gr.Dropdown.update(choices=[], value=None),\
            gr.HTML.update(value=HTML),\
            gr.Button.update(interactive=hasPrev),\
            gr.Button.update(interactive=hasNext),\
            gr.Textbox.update(value=pages)

def update_model_list(content_type, sort_type, use_search_term, search_term, show_nsfw):
    query = civitai.makeRequestQuery(content_type, sort_type, use_search_term, search_term)
    response = civitai.requestApi(query=query)
    if response is None:
        return {}
    civitai.updateJsonData(response, content_type)
    civitai.setShowNsfw(show_nsfw)
    pages = civitai.getPages()
    hasPrev = not civitai.prevPage() == ""
    hasNext = not civitai.nextPage() == ""
    model_dict = civitai.getModelNames() if (show_nsfw) else civitai.getModelNamesSfw()
    HTML = civitai.modelCardsHtml(model_dict)
    return  gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value=None),\
            gr.Dropdown.update(choices=[], value=None),\
            gr.HTML.update(value=HTML),\
            gr.Button.update(interactive=hasPrev),\
            gr.Button.update(interactive=hasNext),\
            gr.Textbox.update(value=pages)

def update_model_versions(model_name=None):
    if model_name is not None:
        civitai.selectModelByName(model_name)
        dict = civitai.getModelVersionsList()
        return gr.Dropdown.update(choices=[k for k, v in dict.items()], value=f'{next(iter(dict.keys()), None)}')
    else:
        return gr.Dropdown.update(choices=[], value=None)

def  update_model_info(model_name=None, model_version=None):
    if model_name and model_version:
        dict = civitai.makeModelInfo(model_name, model_version)             
        return  gr.HTML.update(value=dict['html']),\
                gr.Textbox.update(value=dict['trainedWords']),\
                gr.Dropdown.update(choices=[k for k, v in dict['files'].items()], value=next(iter(dict['files'].keys()), None)),\
                gr.Textbox.update(value=dict['baseModel'])
    else:
        return  gr.HTML.update(value=None),\
                gr.Textbox.update(value=None),\
                gr.Dropdown.update(choices=[], value=None),\
                gr.Textbox.update(value='')

def update_everything(list_models, list_versions, dl_url):
    (a, d, f, base_model) = update_model_info(list_models, list_versions)
    dl_url = gr.Textbox.update(value=civitai.updateDlUrl(list_models, list_versions, f['value']))
    return (a, d, f, list_versions, list_models, dl_url, base_model)

   
def on_ui_tabs():
    with gr.Blocks() as civitai_interface:
        with gr.Row():
            with gr.Column(scale=2):
                content_type = gr.Radio(label='Content type:', choices=["Checkpoint","TextualInversion","LORA","LoCon","Poses","Controlnet","Hypernetwork","AestheticGradient", "VAE"], value="Checkpoint", type="value")
            with gr.Column(scale=1,min_width=100):
                    sort_type = gr.Dropdown(label='Sort List by:', choices=["Newest","Most Downloaded","Highest Rated","Most Liked"], value="Newest", type="value")
                    show_nsfw = gr.Checkbox(label="NSFW content", value=False)
        with gr.Row():
            use_search_term = gr.Radio(label="Search", choices=["No", "Model name", "User name", "Tag"],value="No")
            search_term = gr.Textbox(label="Search Term", interactive=True, lines=1)
        with gr.Row():
            with gr.Column(scale=4):
                get_list_from_api = gr.Button(label="Get List", value="Get List")
            with gr.Column(scale=2,min_width=80):
                get_prev_page = gr.Button(value="Prev. Page")
            with gr.Column(scale=2,min_width=80):
                get_next_page = gr.Button(value="Next Page")
            with gr.Column(scale=1,min_width=80):
                pages = gr.Textbox(label='Pages',show_label=False)
        with gr.Row():
            list_html = gr.HTML()
        with gr.Row():
            list_models = gr.Dropdown(label="Model", choices=[], interactive=True, elem_id="quicksettings1", value=None)
            event_text = gr.Textbox(label="Event text",elem_id="eventtext1", visible=False, interactive=True, lines=1)
            list_versions = gr.Dropdown(label="Version", choices=[], interactive=True, elem_id="quicksettings", value=None)
        with gr.Row():
            txt_list = ""
            dummy = gr.Textbox(label='Trained Tags (if any)', value=f'{txt_list}', interactive=True, lines=1)
            base_model = gr.Textbox(label='Base Model', value='', interactive=True, lines=1)
            model_filename = gr.Dropdown(label="Model Filename", choices=[], interactive=True, value=None)
            dl_url = gr.Textbox(label="Download Url", interactive=False, value=None)
        with gr.Row():
            update_info = gr.Button(value='1st - Get Model Info')
            save_text = gr.Button(value="2nd - Save Text")
            save_images = gr.Button(value="3rd - Save Images")
            download_model = gr.Button(value="4th - Download Model")
            save_model_in_new = gr.Checkbox(label="Save Model to new folder", value=False)
        with gr.Row():
            preview_image_html = gr.HTML()
        
        def save_text_click(file_name, content_type, use_new_folder, trained_words, list_models, base_model):
            save_text_file(file_name, content_type, use_new_folder, trained_words, list_models, base_model,civitai.isNsfwModel() )
        save_text.click(
            fn=save_text_click,
            inputs=[
            model_filename,
            content_type,
            save_model_in_new,
            dummy,
            list_models,
            base_model,
            ],
            outputs=[]
        )

        def save_image_files(preview_image_html, model_filename, list_models, content_type, use_new_folder,base_model):
            saveImageFiles(preview_image_html, model_filename, list_models, content_type, use_new_folder,base_model, civitai.getModelVersionInfo(), civitai.isNsfwModel() )
        save_images.click(
            fn=save_image_files,
            inputs=[
            preview_image_html,
            model_filename,
            list_models,
            content_type,
            save_model_in_new,
            base_model
            ],
            outputs=[]
        )
        def download_model_click(url, file_name, content_type, use_new_folder, list_models,base_model):
            download_file_thread(url, file_name, content_type, use_new_folder, list_models,base_model, civitai.isNsfwModel() )
        download_model.click(
            fn=download_model_click,
            inputs=[
            dl_url,
            model_filename,
            content_type,
            save_model_in_new,
            list_models,
            base_model
            ],
            outputs=[]
        )
        get_list_from_api.click(
            fn=update_model_list,
            inputs=[
            content_type,
            sort_type,
            use_search_term,
            search_term,
            show_nsfw
            ],
            outputs=[
            list_models,
            list_versions,
            list_html,            
            get_prev_page,
            get_next_page,
            pages
            ]
        )
        update_info.click(
            fn=update_everything,
            #fn=update_model_info,
            inputs=[
            list_models,
            list_versions,
            dl_url
            ],
            outputs=[
            preview_image_html,
            dummy,
            model_filename,
            list_versions,
            list_models,
            dl_url,
            base_model
            ]
        )
        list_models.change(
            fn=update_model_versions,
            inputs=[
            list_models,
            ],
            outputs=[
            list_versions,
            ]
        )
        list_versions.change(
            fn=update_model_info,
            inputs=[
            list_models,
            list_versions,
            ],
            outputs=[
            preview_image_html,
            dummy,
            model_filename,
            base_model
            ]
        )
        model_filename.change(
            fn=civitai.updateDlUrl,
            inputs=[list_models, list_versions, model_filename,],
            outputs=[dl_url,]
        )
        get_next_page.click(
            fn=update_next_page,
            inputs=[
            show_nsfw,
            content_type,
            ],
            outputs=[
            list_models,
            list_versions,
            list_html,
            get_prev_page,
            get_next_page,
            pages
            ]
        )
        get_prev_page.click(
            fn=update_prev_page,
            inputs=[
            show_nsfw,
            content_type,
            ],
            outputs=[
            list_models,
            list_versions,
            list_html,
            get_prev_page,
            get_next_page,
            pages
            ]
        )
        def update_models_dropdown(model_name):
            ret_versions=update_model_versions(model_name)
            (html,d, f, base_model) = update_model_info(model_name,ret_versions['value'])
            dl_url = gr.Textbox.update(value=civitai.updateDlUrl(list_models, list_versions, f['value']))
            return gr.Dropdown.update(value=model_name),ret_versions ,html,dl_url,d,f,base_model
        event_text.change(
            fn=update_models_dropdown,
            inputs=[
                event_text,
            ],
            outputs=[
                list_models,
                list_versions,
                preview_image_html,
                dl_url,
                dummy,
                model_filename
            ]
        )

    return (civitai_interface, "CivitAi", "civitai_interface"),

script_callbacks.on_ui_tabs(on_ui_tabs)
