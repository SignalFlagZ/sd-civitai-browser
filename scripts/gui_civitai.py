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

def update_prev_page(grChkboxShowNsfw, grRadioContentType):
    return update_next_page(grChkboxShowNsfw, grRadioContentType, False)

def update_next_page(grChkboxShowNsfw, grRadioContentType, isNext=True, ):
    if isNext:
        civitai.updateJsonData(api_next_page(civitai.nextPage()), grRadioContentType)
    else:
        civitai.updateJsonData(api_next_page(civitai.prevPage()), grRadioContentType)
    civitai.setShowNsfw(grChkboxShowNsfw)
    grTxtPages = civitai.getPages()
    hasPrev = not civitai.prevPage() == ""
    hasNext = not civitai.nextPage() == ""
    model_names = civitai.getModelNames() if (grChkboxShowNsfw) else civitai.getModelNamesSfw()
    HTML = civitai.modelCardsHtml(model_names)
    return  gr.Dropdown.update(choices=[v for k, v in model_names.items()], value=None),\
            gr.Dropdown.update(choices=[], value=None),\
            gr.HTML.update(value=HTML),\
            gr.Button.update(interactive=hasPrev),\
            gr.Button.update(interactive=hasNext),\
            gr.Textbox.update(value=grTxtPages)

def update_model_list(grRadioContentType, grDrpdwnSortType, grRadioSearchType, grTxtSearchTerm, grChkboxShowNsfw):
    query = civitai.makeRequestQuery(grRadioContentType, grDrpdwnSortType, grRadioSearchType, grTxtSearchTerm)
    response = civitai.requestApi(query=query)
    if response is None:
        return {}
    civitai.updateJsonData(response, grRadioContentType)
    civitai.setShowNsfw(grChkboxShowNsfw)
    grTxtPages = civitai.getPages()
    hasPrev = not civitai.prevPage() == ""
    hasNext = not civitai.nextPage() == ""
    model_names = civitai.getModelNames() if (grChkboxShowNsfw) else civitai.getModelNamesSfw()
    HTML = civitai.modelCardsHtml(model_names)
    return  gr.Dropdown.update(choices=[v for k, v in model_names.items()], value=None),\
            gr.Dropdown.update(choices=[], value=None),\
            gr.HTML.update(value=HTML),\
            gr.Button.update(interactive=hasPrev),\
            gr.Button.update(interactive=hasNext),\
            gr.Textbox.update(value=grTxtPages)

def update_model_versions(model_name=None):
    if model_name is not None:
        civitai.selectModelByName(model_name)
    if civitai.getSelectedModelIndex() is not None:
        dict = civitai.getModelVersionsList()
        civitai.selectVersionByName(next(iter(dict.keys()), None))
        return gr.Dropdown.update(choices=[k for k, v in dict.items()], value=f'{next(iter(dict.keys()), None)}')

def  update_model_info(model_version=None):
    civitai.selectVersionByName(model_version)
    if model_version:
        dict = civitai.makeModelInfo()             
        return  gr.HTML.update(value=dict['html']),\
                gr.Textbox.update(value=dict['trainedWords']),\
                gr.Dropdown.update(choices=[k for k, v in dict['files'].items()], value=next(iter(dict['files'].keys()), None)),\
                gr.Textbox.update(value=dict['baseModel'])
    else:
        return  gr.HTML.update(value=None),\
                gr.Textbox.update(value=None),\
                gr.Dropdown.update(choices=[], value=None),\
                gr.Textbox.update(value='')

def update_everything(grDrpdwnModels, grDrpdwnVersions, grTxtDlUrl):
    civitai.selectModelByName(grDrpdwnModels)
    civitai.selectVersionByName(grDrpdwnVersions)
    grHtmlModelInfo, grTxtTrainedWords, grDrpdwnFilenames, grTxtBaseModel = update_model_info(grDrpdwnVersions)
    grTxtDlUrl = gr.Textbox.update(value=civitai.getUrlbyName(f['value']))
    return  grHtmlModelInfo,\
            grTxtTrainedWords,\
            grDrpdwnFilenames,\
            grDrpdwnVersions,\
            grDrpdwnModels,\
            grTxtDlUrl,\
            grTxtBaseModel

   
def on_ui_tabs():
    with gr.Blocks() as civitai_interface:
        with gr.Row():
            with gr.Column(scale=2):
                grRadioContentType = gr.Radio(label='Content type:', choices=["Checkpoint","TextualInversion","LORA","LoCon","Poses","Controlnet","Hypernetwork","AestheticGradient", "VAE"], value="Checkpoint", type="value")
            with gr.Column(scale=1,min_width=100):
                    grDrpdwnSortType = gr.Dropdown(label='Sort List by:', choices=["Newest","Most Downloaded","Highest Rated","Most Liked"], value="Newest", type="value")
                    grChkboxShowNsfw = gr.Checkbox(label="NSFW content", value=False)
        with gr.Row():
            grRadioSearchType = gr.Radio(label="Search", choices=["No", "Model name", "User name", "Tag"],value="No")
            grTxtSearchTerm = gr.Textbox(label="Search Term", interactive=True, lines=1)
        with gr.Row():
            with gr.Column(scale=4):
                grBtnGetListAPI = gr.Button(label="Get List", value="Get List")
            with gr.Column(scale=2,min_width=80):
                grBtnPrevPage = gr.Button(value="Prev. Page")
            with gr.Column(scale=2,min_width=80):
                grBtnNextPage = gr.Button(value="Next Page")
            with gr.Column(scale=1,min_width=80):
                grTxtPages = gr.Textbox(label='Pages',show_label=False)
        with gr.Row():
            grHtmlCards = gr.HTML()
        with gr.Row():
            grDrpdwnModels = gr.Dropdown(label="Model", choices=[], interactive=True, elem_id="quicksettings1", value=None)
            grTxtJsEvent = gr.Textbox(label="Event text",elem_id="eventtext1", visible=False, interactive=True, lines=1)
            grDrpdwnVersions = gr.Dropdown(label="Version", choices=[], interactive=True, elem_id="quicksettings", value=None)
        with gr.Row():
            txt_list = ""
            grTxtTrainedWords = gr.Textbox(label='Trained Tags (if any)', value=f'{txt_list}', interactive=True, lines=1)
            grTxtBaseModel = gr.Textbox(label='Base Model', value='', interactive=True, lines=1)
            grDrpdwnFilenames = gr.Dropdown(label="Model Filename", choices=[], interactive=True, value=None)
            grTxtDlUrl = gr.Textbox(label="Download Url", interactive=False, value=None)
        with gr.Row():
            grBtnUpdateInfo = gr.Button(value='1st - Get Model Info')
            grBtnSaveText = gr.Button(value="2nd - Save Text")
            grBtnSaveImages = gr.Button(value="3rd - Save Images")
            grBtnDownloadModel = gr.Button(value="4th - Download Model")
            #save_model_in_new = gr.Checkbox(label="Save Model to new folder", value=False)
        with gr.Row():
            grHtmlModelInfo = gr.HTML()
        
        def save_text(file_name, grRadioContentType, trained_words, grDrpdwnModels, grTxtBaseModel):
            save_text_file(file_name, grRadioContentType, trained_words, grDrpdwnModels, grTxtBaseModel,civitai.isNsfwModel() )
        grBtnSaveText.click(
            fn=save_text,
            inputs=[
            grDrpdwnFilenames,
            grRadioContentType,
            #save_model_in_new,
            grTxtTrainedWords,
            grDrpdwnModels,
            grTxtBaseModel,
            ],
            outputs=[]
        )

        def save_image_files(grHtmlModelInfo, grDrpdwnFilenames, grDrpdwnModels, grRadioContentType, grTxtBaseModel):
            saveImageFiles(grHtmlModelInfo, grDrpdwnFilenames, grDrpdwnModels, grRadioContentType, grTxtBaseModel, civitai.getModelVersionInfo(), civitai.isNsfwModel() )
        grBtnSaveImages.click(
            fn=save_image_files,
            inputs=[
            grHtmlModelInfo,
            grDrpdwnFilenames,
            grDrpdwnModels,
            grRadioContentType,
            #save_model_in_new,
            grTxtBaseModel
            ],
            outputs=[]
        )
        def model_download(url, file_name, grRadioContentType, grDrpdwnModels,grTxtBaseModel):
            download_file_thread(url, file_name, grRadioContentType, grDrpdwnModels,grTxtBaseModel, civitai.isNsfwModel() )
        grBtnDownloadModel.click(
            fn=model_download,
            inputs=[
            grTxtDlUrl,
            grDrpdwnFilenames,
            grRadioContentType,
            #save_model_in_new,
            grDrpdwnModels,
            grTxtBaseModel
            ],
            outputs=[]
        )
        grBtnGetListAPI.click(
            fn=update_model_list,
            inputs=[
            grRadioContentType,
            grDrpdwnSortType,
            grRadioSearchType,
            grTxtSearchTerm,
            grChkboxShowNsfw
            ],
            outputs=[
            grDrpdwnModels,
            grDrpdwnVersions,
            grHtmlCards,            
            grBtnPrevPage,
            grBtnNextPage,
            grTxtPages
            ]
        )
        grBtnUpdateInfo.click(
            fn=update_everything,
            #fn=update_model_info,
            inputs=[
            grDrpdwnModels,
            grDrpdwnVersions,
            grTxtDlUrl
            ],
            outputs=[
            grHtmlModelInfo,
            grTxtTrainedWords,
            grDrpdwnFilenames,
            grDrpdwnVersions,
            grDrpdwnModels,
            grTxtDlUrl,
            grTxtBaseModel
            ]
        )
        grDrpdwnModels.change(
            fn=update_model_versions,
            inputs=[
            grDrpdwnModels,
            ],
            outputs=[
            grDrpdwnVersions,
            ]
        )
        grDrpdwnVersions.change(
            fn=update_model_info,
            inputs=[
            grDrpdwnVersions,
            ],
            outputs=[
            grHtmlModelInfo,
            grTxtTrainedWords,
            grDrpdwnFilenames,
            grTxtBaseModel
            ]
        )
        def updateDlUrl(grDrpdwnFilenames):
            return civitai.getUrlbyName(grDrpdwnFilenames)
        grDrpdwnFilenames.change(
            fn=updateDlUrl,
            inputs=[grDrpdwnFilenames,],
            outputs=[grTxtDlUrl,]
        )
        grBtnNextPage.click(
            fn=update_next_page,
            inputs=[
            grChkboxShowNsfw,
            grRadioContentType,
            ],
            outputs=[
            grDrpdwnModels,
            grDrpdwnVersions,
            grHtmlCards,
            grBtnPrevPage,
            grBtnNextPage,
            grTxtPages
            ]
        )
        grBtnPrevPage.click(
            fn=update_prev_page,
            inputs=[
            grChkboxShowNsfw,
            grRadioContentType,
            ],
            outputs=[
            grDrpdwnModels,
            grDrpdwnVersions,
            grHtmlCards,
            grBtnPrevPage,
            grBtnNextPage,
            grTxtPages
            ]
        )
        def update_models_dropdown(grTxtJsEvent):
            index = grTxtJsEvent.split(':')[1] # str: 'Index:{index}:{id}'
            civitai.selectModelByIndex(int(index))
            ret_versions=update_model_versions()
            html,grTxtTrainedWords, grDrpdwnFilenames, grTxtBaseModel = update_model_info(ret_versions['value'])
            grTxtDlUrl = gr.Textbox.update(value=civitai.getUrlbyName(['value']))
            grDrpdwnModels = gr.Dropdown.update(value=civitai.getSelectedModelName())
            return grDrpdwnModels, ret_versions ,html,grTxtDlUrl,grTxtTrainedWords,grDrpdwnFilenames,grTxtBaseModel
        grTxtJsEvent.change(
            fn=update_models_dropdown,
            inputs=[
                grTxtJsEvent,
            ],
            outputs=[
                grDrpdwnModels,
                grDrpdwnVersions,
                grHtmlModelInfo,
                grTxtDlUrl,
                grTxtTrainedWords,
                grDrpdwnFilenames
            ]
        )

    return (civitai_interface, "CivitAi", "civitai_interface"),

script_callbacks.on_ui_tabs(on_ui_tabs)
