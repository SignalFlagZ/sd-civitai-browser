import gradio as gr
from html import escape
from modules import script_callbacks
import modules.scripts as scripts
from scripts.civitai_api import civitaimodels
from scripts.file_manage import extranetwork_folder, isExistFile,\
                save_text_file, saveImageFiles,makedirs
from colorama import Fore, Back, Style
#Download
import os
import re
import requests
from tqdm import tqdm
import time
#

# Set the URL for the API endpoint
civitai = civitaimodels("https://civitai.com/api/v1/models?limit=10")

def download_file2(folder, filename,  url):
    makedirs(folder)
    file_name = os.path.join(folder, filename)
    #thread = threading.Thread(target=download_file, args=(url, filepath))

    # Maximum number of retries
    max_retries = 5

    # Delay between retries (in seconds)
    retry_delay = 10

    while True:
        # Check if the file has already been partially downloaded
        if os.path.exists(file_name):
            # Get the size of the downloaded file
            downloaded_size = os.path.getsize(file_name)

            # Set the range of the request to start from the current size of the downloaded file
            headers = {"Range": f"bytes={downloaded_size}-"}
        else:
            downloaded_size = 0
            headers = {}

        # Split filename from included path
        tokens = re.split(re.escape('\\'), file_name)
        file_name_display = tokens[-1]

        # Initialize the progress bar
        progressConsole = tqdm(total=1000000000, unit="B", unit_scale=True, desc=f"Downloading {file_name_display}", initial=downloaded_size, leave=False)

        # Open a local file to save the download
        with open(file_name, "ab") as f:
            while True:
                try:
                    # Send a GET request to the URL and save the response to the local file
                    response = requests.get(url, headers=headers, stream=True)

                    # Get the total size of the file
                    total_size = int(response.headers.get("Content-Length", 0))

                    # Update the total size of the progress bar if the `Content-Length` header is present
                    if total_size == 0:
                        total_size = downloaded_size
                    progressConsole.total = total_size
                    prg = 0
                    # Write the response to the local file and update the progress bar
                    for chunk in response.iter_content(chunk_size=5*1024*1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            progressConsole.update(len(chunk))
                            prg += len(chunk)
                            yield f'{round(prg/1024/1024)}MB / {round(total_size/1024/1024)}MB'
                    downloaded_size = os.path.getsize(file_name)
                    # Break out of the loop if the download is successful
                    break
                except ConnectionError as e:
                    # Decrement the number of retries
                    max_retries -= 1

                    # If there are no more retries, raise the exception
                    if max_retries == 0:
                        raise e

                    # Wait for the specified delay before retrying
                    time.sleep(retry_delay)
        # Close the progress bar
        progressConsole.close()
        downloaded_size = os.path.getsize(file_name)
        # Check if the download was successful
        if downloaded_size >= total_size:
            print(Fore.LIGHTCYAN_EX + f"Save: {file_name_display}" + Style.RESET_ALL)
            yield 'Downloaded'

        else:
            print(f"Error: File download failed. Retrying... {file_name_display}")
            yield 'Failed'
        return

def updateVersionsByModelID(model_ID=None):
    if model_ID is not None:
        civitai.selectModelByID(model_ID)
        if civitai.getSelectedModelIndex() is not None:
            dict = civitai.getModelVersionsList()
            civitai.selectVersionByName(next(iter(dict.keys()), None))
        return gr.Dropdown.update(choices=[k for k, v in dict.items()], value=f'{next(iter(dict.keys()), None)}')
    else:
        return gr.Dropdown.update(choices=[],value = None)

def on_ui_tabs():
    with gr.Blocks() as civitai_interface:
        with gr.Row():
            with gr.Column(scale=4):
                grRadioContentType = gr.Radio(label='Content type:', choices=["Checkpoint","TextualInversion","LORA","LoCon","Poses","Controlnet","Hypernetwork","AestheticGradient", "VAE"], value="Checkpoint", type="value")
            with gr.Column(scale=1, max_width=100, min_width=100):
                grDrpdwnSortType = gr.Dropdown(label='Sort List by:', choices=["Newest","Most Downloaded","Highest Rated","Most Liked"], value="Newest", type="value")
            with gr.Column(scale=1, max_width=100, min_width=100):
                grDrpdwnPeriod = gr.Dropdown(label='Period', choices=["AllTime", "Year", "Month", "Week", "Day"], value="AllTime", type="value")
            with gr.Column(scale=1, max_width=100, min_width=80):
                grChkboxShowNsfw = gr.Checkbox(label="NSFW content", value=False)
        with gr.Row():
            grRadioSearchType = gr.Radio(label="Search", choices=["No", "Model name", "User name", "Tag"],value="No")
            grTxtSearchTerm = gr.Textbox(label="Search Term", interactive=True, lines=1)
        with gr.Row():
            with gr.Column(scale=4):
                grBtnGetListAPI = gr.Button(label="Get List", value="Get List")
            with gr.Column(scale=2,min_width=80):
                grBtnPrevPage = gr.Button(value="Prev. Page", interactive=False)
            with gr.Column(scale=2,min_width=80):
                grBtnNextPage = gr.Button(value="Next Page", interactive=False)
            with gr.Column(scale=1,min_width=80):
                grTxtPages = gr.Textbox(label='Pages',show_label=False)
        with gr.Row():
            grHtmlCards = gr.HTML()
        with gr.Row():
            with gr.Column(scale=3):
                grSldrPage = gr.Slider(label="Page", minimum=1, maximum=10,value = 1, step=1, interactive=False, scale=3)
            with gr.Column(scale=1,min_width=80):
                grBtnGoPage = gr.Button(value="Jump page", interactive=False, scale=1)

        with gr.Row():
            with gr.Column(scale=1):
                grDrpdwnModels = gr.Dropdown(label="Model", choices=[], interactive=True, elem_id="modellist", value=None)
                grTxtJsEvent = gr.Textbox(label="Event text", value=None, elem_id="eventtext1", visible=False, interactive=True, lines=1)
            with gr.Column(scale=5):
                grRadioVersions = gr.Radio(label="Version", choices=[], interactive=True, elem_id="versionlist", value=None)
        with gr.Row().style(equal_height=False):
            grBtnFolder = gr.Button(value='📁',interactive=False, elem_classes ="civitaibuttons")
            grTxtSaveFolder = gr.Textbox(label="Save folder", interactive=True, value="", lines=1)
            grMrkdwnFileMessage = gr.Markdown(value="**<span style='color:Aquamarine;'>You have</span>**", elem_classes ="civitaimsg", visible=False)
            grDrpdwnFilenames = gr.Dropdown(label="Model Filename", choices=[], interactive=True, value=None)
        with gr.Row():
            txt_list = ""
            grTxtTrainedWords = gr.Textbox(label='Trained Tags (if any)', value=f'{txt_list}', interactive=True, lines=1)
            grTxtBaseModel = gr.Textbox(label='Base Model', value='', interactive=True, lines=1)
            grTxtDlUrl = gr.Textbox(label="Download Url", interactive=False, value=None)
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Row():
                    grBtnSaveText = gr.Button(value="Save trained tags",interactive=False, min_width=80)
                    grBtnSaveImages = gr.Button(value="Save model infos",interactive=False, min_width=80)
            with gr.Column(scale=1):
                with gr.Row():
                    grBtnDownloadModel = gr.Button(value="Download model",interactive=False, elem_id='downloadbutton1',min_width=80)
                    grBtnCancel = gr.Button(value="Cancel",interactive=False, min_width=80)
                grTextProgress = gr.Textbox(label='Progress')
        with gr.Row():
            grHtmlModelInfo = gr.HTML()
        
        def save_text(grTxtSaveFolder, grDrpdwnFilenames, trained_words):
            save_text_file(grTxtSaveFolder, grDrpdwnFilenames, trained_words)
        grBtnSaveText.click(
            fn=save_text,
            inputs=[
                grTxtSaveFolder,
                grDrpdwnFilenames,
                grTxtTrainedWords,
            ],
            outputs=[]
        )

        def save_image_files(grTxtSaveFolder, grDrpdwnFilenames, grHtmlModelInfo, grRadioContentType):
            saveImageFiles(grTxtSaveFolder, grDrpdwnFilenames, grHtmlModelInfo, grRadioContentType, civitai.getModelVersionInfo() )
        grBtnSaveImages.click(
            fn=save_image_files,
            inputs=[
                grTxtSaveFolder,
                grDrpdwnFilenames,
                grHtmlModelInfo,
                grRadioContentType,
            ],
            outputs=[]
        )
        #def model_download(grTxtSaveFolder, grDrpdwnFilenames, grTxtDlUrl): # progress=gr.Progress()
        #    ret = download_file_thread2(grTxtSaveFolder, grDrpdwnFilenames, grTxtDlUrl)
        #    print(Fore.LIGHTYELLOW_EX + f'{ret=}' + Style.RESET_ALL)
        #    return ret
        download = grBtnDownloadModel.click(
            fn=download_file2,
            inputs=[
                grTxtSaveFolder,
                grDrpdwnFilenames,
                grTxtDlUrl
            ],
            outputs=[grTextProgress,
                    ]
        )
        def test():
            return gr.Textbox.update(value="Canceled")
        grBtnCancel.click(
            fn=test,
            inputs=None,
            outputs=[grTextProgress],
            cancels=[download]
            )
      
        def update_model_list(grRadioContentType, grDrpdwnSortType, grRadioSearchType, grTxtSearchTerm, grChkboxShowNsfw, grDrpdwnPeriod):
            query = civitai.makeRequestQuery(grRadioContentType, grDrpdwnSortType, grDrpdwnPeriod, grRadioSearchType, grTxtSearchTerm)
            response = civitai.requestApi(query=query)
            if response is None:
                return gr.Dropdown.update(choices=[], value=None),\
                    gr.Radio.update(choices=[], value=None),\
                    gr.HTML.update(value=None),\
                    gr.Button.update(interactive=False),\
                    gr.Button.update(interactive=False),\
                    gr.Button.update(interactive=False),\
                    gr.Slider.update(interactive=False),\
                    gr.Textbox.update(value=None)
            civitai.updateJsonData(response, grRadioContentType)
            civitai.setShowNsfw(grChkboxShowNsfw)
            grTxtPages = civitai.getPages()
            hasPrev = not civitai.prevPage() is None
            hasNext = not civitai.nextPage() is None
            enableJump = hasPrev or hasNext
            model_names = civitai.getModelNames() if (grChkboxShowNsfw) else civitai.getModelNamesSfw()
            HTML = civitai.modelCardsHtml(model_names)
            return  gr.Dropdown.update(choices=[v for k, v in model_names.items()], value=None),\
                    gr.Radio.update(choices=[], value=None),\
                    gr.HTML.update(value=HTML),\
                    gr.Button.update(interactive=hasPrev),\
                    gr.Button.update(interactive=hasNext),\
                    gr.Button.update(interactive=enableJump),\
                    gr.Slider.update(interactive=enableJump, value=int(civitai.getCurrentPage()),maximum=int(civitai.getTotalPages())),\
                    gr.Textbox.update(value=grTxtPages)
        grBtnGetListAPI.click(
            fn=update_model_list,
            inputs=[
                grRadioContentType,
                grDrpdwnSortType,
                grRadioSearchType,
                grTxtSearchTerm,
                grChkboxShowNsfw,
                grDrpdwnPeriod
            ],
            outputs=[
                grDrpdwnModels,
                grRadioVersions,
                grHtmlCards,            
                grBtnPrevPage,
                grBtnNextPage,
                grBtnGoPage,
                grSldrPage,
                grTxtPages
            ]
        )
        
        #def update_everything(grDrpdwnModels, grRadioVersions, grTxtDlUrl):
        #    civitai.selectModelByName(grDrpdwnModels)
        #    civitai.selectVersionByName(grRadioVersions)
        #    grHtmlModelInfo, grTxtTrainedWords, grDrpdwnFilenames, grTxtBaseModel, grTxtSaveFolder = update_model_info(grRadioVersions)
        #    grTxtDlUrl = gr.Textbox.update(value=civitai.getUrlByName(grDrpdwnFilenames['value']))
        #    return  grHtmlModelInfo,\
        #            grTxtTrainedWords,\
        #            grDrpdwnFilenames,\
        #            grRadioVersions,\
        #            grDrpdwnModels,\
        #            grTxtDlUrl,\
        #            grTxtBaseModel,\
        #            grTxtSaveFolder
        #grBtnUpdateInfo.click(
        #    #deprecated
        #    fn=update_everything,
        #    #fn=update_model_info,
        #    inputs=[
        #        grDrpdwnModels,
        #        grRadioVersions,
        #        grTxtDlUrl
        #    ],
        #    outputs=[
        #        grHtmlModelInfo,
        #        grTxtTrainedWords,
        #        grDrpdwnFilenames,
        #        grRadioVersions,
        #        grDrpdwnModels,
        #        grTxtDlUrl,
        #        grTxtBaseModel,
        #        grTxtSaveFolder
        #    ]
        #)

        def UpdatedModels(grDrpdwnModels):
            index = civitai.getIndexByModelName(grDrpdwnModels)
            eventText = None
            if grDrpdwnModels is not None:
                eventText = 'Index:' + str(index)
            return gr.Textbox.update(value=eventText)
        grDrpdwnModels.change(
            fn=UpdatedModels,
            inputs=[
                grDrpdwnModels,
            ],
            outputs=[
                #grRadioVersions,
                grTxtJsEvent
            ]
        )
        
        def  update_model_info(model_version=None):
            if model_version is not None and civitai.selectVersionByName(model_version) is not None:
                path = extranetwork_folder( civitai.getContentType(),
                                            civitai.getSelectedModelName(),
                                            civitai.getSelectedVersionBaeModel(),
                                            civitai.isNsfwModel()
                                        )
                dict = civitai.makeModelInfo()             
                return  gr.HTML.update(value=dict['html']),\
                        gr.Textbox.update(value=dict['trainedWords']),\
                        gr.Dropdown.update(choices=[k for k, v in dict['files'].items()], value=next(iter(dict['files'].keys()), None)),\
                        gr.Textbox.update(value=dict['baseModel']),\
                        gr.Textbox.update(value=path)
            else:
                return  gr.HTML.update(value=None),\
                        gr.Textbox.update(value=None),\
                        gr.Dropdown.update(choices=[], value=None),\
                        gr.Textbox.update(value=None),\
                        gr.Textbox.update(value=None)
        grRadioVersions.change(
            fn=update_model_info,
            inputs=[
            grRadioVersions,
            ],
            outputs=[
                grHtmlModelInfo,
                grTxtTrainedWords,
                grDrpdwnFilenames,
                grTxtBaseModel,
                grTxtSaveFolder
            ]
            )
        
        def save_folder_changed(folder, filename):
            civitai.setSaveFolder(folder)
            isExist = None
            if filename is not None:
                isExist = file_exist_check(folder, filename)
            return gr.Markdown.update(visible = True if isExist else False)
            
        grTxtSaveFolder.blur(
            fn=save_folder_changed,
            inputs={grTxtSaveFolder,grDrpdwnFilenames},
            outputs=[grMrkdwnFileMessage])
        
        def updateDlUrl(grDrpdwnFilenames):
            return  gr.Textbox.update(value=civitai.getUrlByName(grDrpdwnFilenames)),\
                    gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                    gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                    gr.Button.update(interactive=True if grDrpdwnFilenames else False)
        
        grTxtSaveFolder.change(
            fn=civitai.setSaveFolder,
            inputs={grTxtSaveFolder},
            outputs=[])
        
        def updateDlUrl(grDrpdwnFilenames):
            return  gr.Textbox.update(value=civitai.getUrlByName(grDrpdwnFilenames)),\
                    gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                    gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                    gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                    gr.Button.update(interactive=True if grDrpdwnFilenames else False)
        grDrpdwnFilenames.change(
            fn=updateDlUrl,
            inputs=[grDrpdwnFilenames],
            outputs=[
                grTxtDlUrl,
                grBtnSaveText,
                grBtnSaveImages,
                grBtnDownloadModel,
                grBtnCancel
                ]
            )   
        
        def file_exist_check(grTxtSaveFolder, grDrpdwnFilenames):
            isExist = isExistFile(grTxtSaveFolder, grDrpdwnFilenames)            
            return gr.Markdown.update(visible = True if isExist else False)
        grTxtDlUrl.change(
            fn=file_exist_check,
            inputs=[grTxtSaveFolder,
                    grDrpdwnFilenames
                    ],
            outputs=[
                    grMrkdwnFileMessage
                    ]
            )
        
        def update_next_page(grChkboxShowNsfw, isNext=True):
            url = civitai.nextPage() if isNext else civitai.prevPage()
            response = civitai.requestApi(url)
            if response is None:
                return None, None,  gr.HTML.update(),None,None,gr.Slider.update(),gr.Textbox.update()
            civitai.updateJsonData(response)
            civitai.setShowNsfw(grChkboxShowNsfw)
            grTxtPages = civitai.getPages()
            hasPrev = not civitai.prevPage() is None
            hasNext = not civitai.nextPage() is None
            model_names = civitai.getModelNames() if (grChkboxShowNsfw) else civitai.getModelNamesSfw()
            HTML = civitai.modelCardsHtml(model_names)
            return  gr.Dropdown.update(choices=[v for k, v in model_names.items()], value=None),\
                    gr.Radio.update(choices=[], value=None),\
                    gr.HTML.update(value=HTML),\
                    gr.Button.update(interactive=hasPrev),\
                    gr.Button.update(interactive=hasNext),\
                    gr.Slider.update(value=civitai.getCurrentPage()),\
                    gr.Textbox.update(value=grTxtPages)
       
        grBtnNextPage.click(
            fn=update_next_page,
            inputs=[
                grChkboxShowNsfw,
            ],
            outputs=[
                grDrpdwnModels,
                grRadioVersions,
                grHtmlCards,
                grBtnPrevPage,
                grBtnNextPage,
                grSldrPage,
                grTxtPages,
                #grTxtSaveFolder
            ]
        )
        def update_prev_page(grChkboxShowNsfw):
            return update_next_page(grChkboxShowNsfw, isNext=False)
        grBtnPrevPage.click(
            fn=update_prev_page,
            inputs=[
                grChkboxShowNsfw,
            ],
            outputs=[
                grDrpdwnModels,
                grRadioVersions,
                grHtmlCards,
                grBtnPrevPage,
                grBtnNextPage,
                grSldrPage,
                grTxtPages,
                #grTxtSaveFolder
            ]
            )

        def jump_to_page(grChkboxShowNsfw, grSldrPage):
            url = civitai.nextPage()
            if url is None:
                url = civitai.prevPage()
            addQuery =  {'page': grSldrPage }
            newURL = civitai.updateQuery(url, addQuery)
            #print(f'{newURL}')
            response = civitai.requestApi(newURL)
            if response is None:
                return None, None,  gr.HTML.update(),None,None,gr.Slider.update(),gr.Textbox.update()
            civitai.updateJsonData(response)
            civitai.setShowNsfw(grChkboxShowNsfw)
            grTxtPages = civitai.getPages()
            hasPrev = not civitai.prevPage() is None
            hasNext = not civitai.nextPage() is None
            model_names = civitai.getModelNames() if (grChkboxShowNsfw) else civitai.getModelNamesSfw()
            HTML = civitai.modelCardsHtml(model_names)
            return  gr.Dropdown.update(choices=[v for k, v in model_names.items()], value=None),\
                    gr.Radio.update(choices=[], value=None),\
                    gr.HTML.update(value=HTML),\
                    gr.Button.update(interactive=hasPrev),\
                    gr.Button.update(interactive=hasNext),\
                    gr.Slider.update(value = civitai.getCurrentPage()),\
                    gr.Textbox.update(value=grTxtPages)
        grBtnGoPage.click(
            fn=jump_to_page,
            inputs=[
                grChkboxShowNsfw,
                grSldrPage
            ],
            outputs=[
                grDrpdwnModels,
                grRadioVersions,
                grHtmlCards,
                grBtnPrevPage,
                grBtnNextPage,
                grSldrPage,
                grTxtPages,
                #grTxtSaveFolder
            ])

        def eventTextUpdated(grTxtJsEvent):
            if grTxtJsEvent is not None:
                grTxtJsEvent = grTxtJsEvent.split(':')
                # print(Fore.LIGHTYELLOW_EX + f'{grTxtJsEvent=}' + Style.RESET_ALL)
                if grTxtJsEvent[0] == 'Index':
                    index = int(grTxtJsEvent[1]) # str: 'Index:{index}:{id}'
                    civitai.selectModelByIndex(index)
                    grRadioVersions = updateVersionsByModelID(civitai.getSelectedModelID())
                    grHtmlModelInfo,grTxtTrainedWords, grDrpdwnFilenames, grTxtBaseModel, grTxtSaveFolder = update_model_info(grRadioVersions['value'])
                    grTxtDlUrl = gr.Textbox.update(value=civitai.getUrlByName(grDrpdwnFilenames['value']))
                    grDrpdwnModels = gr.Dropdown.update(value=civitai.getSelectedModelName())
                    return  grDrpdwnModels,\
                            grRadioVersions,\
                            grHtmlModelInfo,\
                            grTxtDlUrl,\
                            grTxtTrainedWords,\
                            grDrpdwnFilenames,\
                            grTxtBaseModel,\
                            grTxtSaveFolder
                else:
                    return  gr.Dropdown.update(value=None),\
                            gr.Radio.update(value=None),\
                            gr.HTML.update(value=None),\
                            gr.Textbox.update(value=None),\
                            gr.Textbox.update(value=None),\
                            gr.Dropdown.update(value=None),\
                            gr.Textbox.update(value=None),\
                            gr.Textbox.update(value=None)
            else:
                return  gr.Dropdown.update(value=None),\
                        gr.Radio.update(value=None),\
                        gr.HTML.update(value=None),\
                        gr.Textbox.update(value=None),\
                        gr.Textbox.update(value=None),\
                        gr.Dropdown.update(value=None),\
                        gr.Textbox.update(value=None),\
                        gr.Textbox.update(value=None)
        grTxtJsEvent.change(
            fn=eventTextUpdated,
            inputs=[
                grTxtJsEvent,
            ],
            outputs=[
                grDrpdwnModels,
                grRadioVersions,
                grHtmlModelInfo,
                grTxtDlUrl,
                grTxtTrainedWords,
                grDrpdwnFilenames,
                grTxtBaseModel,
                grTxtSaveFolder
            ]
            )

    return (civitai_interface, "CivitAi Browser", "civitai_interface_sfz"),

script_callbacks.on_ui_tabs(on_ui_tabs)
