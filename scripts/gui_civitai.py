import requests
import json
import gradio as gr
import urllib.parse
import shutil
from html import escape
from modules import script_callbacks
import modules.scripts as scripts
from scripts.civitai_api import *
from scripts.file_manage import *

# Set the URL for the API endpoint
json_data = civitaiData("https://civitai.com/api/v1/models?limit=10")

def save_image_files(preview_image_html, model_filename, list_models, content_type, use_new_folder,base_model):
    print("Save Images Clicked")

    model_folder = extranetwork_folder(content_type, use_new_folder, list_models, base_model)
    img_urls = re.findall(r'src=[\'"]?([^\'" >]+)', preview_image_html)
    
    name = os.path.splitext(model_filename)[0]
    #model_folder = os.path.join("models\Stable-diffusion",list_models.replace(" ","_").replace("(","").replace(")","").replace("|","").replace(":","-"))

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    HTML = preview_image_html
    for i, img_url in enumerate(img_urls):
        filename = f'{name}_{i}.png'
        filenamethumb = f'{name}.png'
        if content_type == "TextualInversion":
            filename = f'{name}_{i}.preview.png'
            filenamethumb = f'{name}.preview.png'
        HTML = HTML.replace(img_url,f'"{filename}"')
        img_url = urllib.parse.quote(img_url,  safe=':/=')   #img_url.replace("https", "http").replace("=","%3D")
        print(img_url, model_folder, filename)
        try:
            with urllib.request.urlopen(img_url) as url:
                with open(os.path.join(model_folder, filename), 'wb') as f:
                    f.write(url.read())
                    if i == 0 and not os.path.exists(os.path.join(model_folder, filenamethumb)):
                        shutil.copy2(os.path.join(model_folder, filename),os.path.join(model_folder, filenamethumb))
                    print("\t\t\tDownloaded")
            #with urllib.request.urlretrieve(img_url, os.path.join(model_folder, filename)) as dl:
                    
        except urllib.error.URLError as e:
            print(f'Error: {e.reason}')
    path_to_new_file = os.path.join(model_folder, f'{name}.html')
    #if not os.path.exists(path_to_new_file):
    with open(path_to_new_file, 'wb') as f:
        f.write(HTML.encode('utf8'))
    #Save json_info
    path_to_new_file = os.path.join(model_folder, f'{name}.civitai.info')
    with open(path_to_new_file, mode="w", encoding="utf-8") as f:
        json.dump(json_data.getModelVersionInfo(), f, indent=2, ensure_ascii=False)
    
    print(f"Done.")

def api_next_page(next_page_url:str=""):
    if not next_page_url:
        next_page_url = json_data.nextPage()
    return json_data.requestApi(next_page_url)

def update_prev_page(show_nsfw, content_type):
    return update_next_page(show_nsfw, content_type, False)

def update_next_page(show_nsfw, content_type, isNext=True, ):
    if isNext:
        json_data.updateJsondata(api_next_page(json_data.nextPage()), content_type)
    else:
        json_data.updateJsondata(api_next_page(json_data.prevPage()), content_type)
    json_data.setShowNsfw(show_nsfw)
    pages = json_data.getPages()
    hasPrev = not json_data.prevPage() == ""
    hasNext = not json_data.nextPage() == ""
    model_dict = json_data.getModelNames() if (show_nsfw) else json_data.getModelNamesSfw()
    HTML = json_data.modelCardsHtml(model_dict)
    return  gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value=None),\
            gr.Dropdown.update(choices=[], value=None),\
            gr.HTML.update(value=HTML),\
            gr.Button.update(interactive=hasPrev),\
            gr.Button.update(interactive=hasNext),\
            gr.Textbox.update(value=pages)

def update_model_list(content_type, sort_type, use_search_term, search_term, show_nsfw):
    query = json_data.makeRequestQuery(content_type, sort_type, use_search_term, search_term)
    data = json_data.requestApi(json_data.getBaseUrl(), query)
    json_data.updateJsondata(data, content_type)
    if json_data.getJsonData() is None:
        return
    json_data.setShowNsfw(show_nsfw)
    pages = json_data.getPages()
    hasPrev = not json_data.prevPage() == ""
    hasNext = not json_data.nextPage() == ""
    model_dict = json_data.getModelNames() if (show_nsfw) else json_data.getModelNamesSfw()
    HTML = json_data.modelCardsHtml(model_dict)
    return  gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value=None),\
            gr.Dropdown.update(choices=[], value=None),\
            gr.HTML.update(value=HTML),\
            gr.Button.update(interactive=hasPrev),\
            gr.Button.update(interactive=hasNext),\
            gr.Textbox.update(value=pages)

def update_model_versions(model_name=None):
    dict = json_data.getModelVersions(model_name)
    return gr.Dropdown.update(choices=[k for k, v in dict.items()], value=f'{next(iter(dict.keys()), None)}')

def  update_model_info(model_name=None, model_version=None):
    if model_name and model_version:
        dict = json_data.getModelInfo(model_name, model_version)             
        return  gr.HTML.update(value=dict['html']),\
                gr.Textbox.update(value=dict['trainedWords']),\
                gr.Dropdown.update(choices=[k for k, v in dict['files'].items()], value=next(iter(dict['files'].keys()), None)),\
                gr.Textbox.update(value=dict['baseModel'])
    else:
        return  gr.HTML.update(value=None),\
                gr.Textbox.update(value=None),\
                gr.Dropdown.update(choices=[], value=None),\
                gr.Textbox.update(value='')


def request_civit_api(api_url=None, payload=None):
    if payload is not None:
        payload = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
    # Make a GET request to the API
    try:
        response = requests.get(api_url, params=payload, timeout=(10,15))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Request error: ", e)
        #print(f"Query: {payload} URL: {response.url}")
        exit() #return None
    else:
        response.encoding  = "utf-8" # response.apparent_encoding
        data = json.loads(response.text)
    # Check the status code of the response
    #if response.status_code != 200:
    #  print("Request failed with status code: {}".format(response.status_code))
    #  exit()
    return data


def update_everything(list_models, list_versions, dl_url):
    (a, d, f, base_model) = update_model_info(list_models, list_versions)
    dl_url = gr.Textbox.update(value=json_data.updateDlUrl(list_models, list_versions, f['value']))
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

        save_text.click(
            fn=save_text_file,
            inputs=[
            model_filename,
            content_type,
            save_model_in_new,
            dummy,
            list_models,
            base_model
            ],
            outputs=[]
        )
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
        download_model.click(
            fn=download_file_thread,
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
            fn=json_data.updateDlUrl,
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
            dl_url = gr.Textbox.update(value=json_data.updateDlUrl(list_models, list_versions, f['value']))
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
