import gradio as gr
from modules import script_callbacks
from colorama import Fore, Back, Style
import itertools
from modules.shared import opts
try:
    # SD web UI >= v1.6.0-RC
    from modules.shared_cmd_options import cmd_opts
except ImportError:
    # SD web UI < v1.6.0-RC
    # SD.Next
    from modules.shared import cmd_opts
import re
import scripts as scripts
from scripts.civsfz_api import civitaimodels
from scripts.civsfz_filemanage import open_folder

print_ly = lambda  x: print(Fore.LIGHTYELLOW_EX + "CivBrowser: " + x + Style.RESET_ALL )
print_lc = lambda  x: print(Fore.LIGHTCYAN_EX + "CivBrowser: " + x + Style.RESET_ALL )
print_n = lambda  x: print("CivBrowser: " + x )

class components():
    newid = itertools.count()
    
    def __init__(self, tab=None):
        '''id: Event ID for javascrypt'''
        from scripts.civsfz_filemanage import generate_model_save_path, isExistFile, \
                save_text_file, saveImageFiles,download_file2
        #self.tab = tab
        # Set the URL for the API endpoint
        self.civitai = civitaimodels("https://civitai.com/api/v1/models")
        self.id = next(components.newid)
        contentTypes = self.civitai.getTypeOptions()
        self.APIKey = ""
        if cmd_opts.civsfz_api_key:
            self.APIKey = cmd_opts.civsfz_api_key[0:32]
            #print(f"{self.APIKey=}")
        def defaultContentType():
            value = contentTypes[self.id % len(contentTypes)]
            return value
        def defaultPeriod():
            return "Month"
        def cmdoptsAPIKey():
            return self.APIKey

        with gr.Column() as self.components:
            with gr.Row():
                with gr.Column(scale=5):
                    grChkbxGrpContentType = gr.CheckboxGroup(
                        label='Types:', choices=contentTypes, value=defaultContentType)
                with gr.Column(scale=1, max_width=100, min_width=100):
                    with gr.Row():
                        grDrpdwnSortType = gr.Dropdown(
                            label='Sort List by:', choices=self.civitai.getSortOptions(), value="Newest", type="value")
                        grDrpdwnPeriod = gr.Dropdown(label='Period', choices=["AllTime", "Year", "Month", "Week", "Day"], value=defaultPeriod, type="value")
                with gr.Column(scale=1, max_width=100, min_width=100):
                    grDrpdwnBasemodels = gr.Dropdown(label="Base Models (experimental)", choices=self.civitai.getBasemodelOptions(
                    ), value=None, type="value", multiselect=True)
                with gr.Column(scale=1, max_width=100, min_width=80):
                    grChkboxShowNsfw = gr.Checkbox(label="NSFW content", value=False)
            with gr.Row():
                grRadioSearchType = gr.Radio(label="Search", choices=["No", "Model name", "User name", "Tag"],value="No")
                grTxtSearchTerm = gr.Textbox(label="Search Term", interactive=True, lines=1)
            with gr.Column(elem_id=f"civsfz_model-navigation{self.id}"):
                with gr.Row(elem_id=f"civsfz_apicontrol{self.id}", elem_classes="civsfz-navigation-buttons civsfz-sticky-element"):
                    with gr.Column(scale=4):
                        grBtnGetListAPI = gr.Button(label="Get cards", value="GET cards")
                    with gr.Column(scale=2,min_width=80):
                        grBtnPrevPage = gr.Button(value="PREV", interactive=False)
                    with gr.Column(scale=2,min_width=80):
                        grBtnNextPage = gr.Button(value="NEXT", interactive=False)
                    with gr.Column(scale=1,min_width=80):
                        grTxtPages = gr.Textbox(label='Pages',show_label=False)
                with gr.Row():
                    grMrkdwnErr = gr.Markdown(value=None, visible=False)
                with gr.Row():
                    grHtmlCards = gr.HTML(elem_classes='civsfz-modelcardshtml')
                    grTxtPropaties = gr.Textbox(elem_id="civsfz_css-properties", label="CSS Properties", value="", visible=False, interactive=False, lines=1)
                with gr.Row(elem_classes="civsfz-jump-page-control civsfz-sticky-element"):
                    with gr.Column(scale=3):
                        grSldrPage = gr.Slider(label="Page", minimum=1, maximum=10,value = 1, step=1, interactive=False, scale=3)
                    with gr.Column(scale=1,min_width=80):
                        grBtnGoPage = gr.Button(value="JUMP", interactive=False, scale=1)

            with gr.Row(elem_id=f'civsfz_model-data{self.id}'):
                with gr.Column(scale=1):
                    grDrpdwnModels = gr.Dropdown(label="Model", choices=[], interactive=False, elem_id=f"civsfz_modellist{self.id}", value=None)
                    grTxtJsEvent = gr.Textbox(label="Event text", value=None, elem_id=f"civsfz_eventtext{self.id}", visible=False, interactive=True, lines=1)
                with gr.Column(scale=5):
                    grRadioVersions = gr.Radio(label="Version", choices=[], interactive=True, elem_id=f"civsfz_versionlist{self.id}", value=None)
            with gr.Row():
                txt_list = ""
                grTxtTrainedWords = gr.Textbox(
                    label='Trained Tags (if any)', value=f'{txt_list}', interactive=True, lines=1)
            with gr.Row(equal_height=False):
                grBtnFolder = gr.Button(value='📂',interactive=True, elem_classes ="civsfz-small-buttons")
                grTxtSaveFolder = gr.Textbox(label="Save folder", interactive=True, value="", lines=1)
                grMrkdwnFileMessage = gr.Markdown(value="**<span style='color:Aquamarine;'>You have</span>**", elem_classes ="civsfz-msg", visible=False)
                grDrpdwnFilenames = gr.Dropdown(label="Model Filename", choices=[], interactive=True, value=None)
            with gr.Row():
                grTxtBaseModel = gr.Textbox(label='Base Model', value='', interactive=True, lines=1)
                grTxtDlUrl = gr.Textbox(label="Download Url", interactive=False, value=None)
                grTxtEarlyAccess = gr.Textbox(label='Early Access', interactive=False, value=None, visible=False)
                grTxtHash = gr.Textbox(label="File hash", interactive=False, value="", visible=False)
                grTxtApiKey = gr.Textbox(
                    label='API Key', value=cmdoptsAPIKey, type="password", lines=1)
            with gr.Row(elem_classes="civsfz-save-buttons civsfz-sticky-element"):
                with gr.Column(scale=2):
                    with gr.Row():
                        grBtnSaveText = gr.Button(value="Save trained tags",interactive=False, min_width=80)
                        grBtnSaveImages = gr.Button(value="Save model infos",interactive=False, min_width=80)
                        grBtnDownloadModel = gr.Button(value="Download model",interactive=False, elem_id=f'civsfz_downloadbutton{self.id}',min_width=80)
                with gr.Column(scale=1):
                    with gr.Row():
                        grTextProgress = gr.Textbox(label='Download status',show_label=False)
                        grBtnCancel = gr.Button(value="Cancel",interactive=False, variant='stop', min_width=80)
            with gr.Row():
                with gr.Column():
                    grHtmlModelInfo = gr.HTML(elem_id=f'civsfz_model-info{self.id}')
                    with gr.Row(elem_classes='civsfz-back-to-top'):
                        grHtmlBackToTop = gr.HTML(
                            value=f"<div onclick='civsfz_scroll_to(\"#civsfz_model-navigation{self.id}\");'><span style='font-size:200%;color:transparent;text-shadow:0 0 0 orange;'>🔝</span></div>")
                
            #def renameTab(type):
            #    return gr.TabItem.update(label=f'{self.id}:{type}')
            #grRadioContentType.change(
            #    fn = renameTab,
            #    inputs=[
            #        grRadioContentType
            #       ],
            #    outputs=[
            #            self.tab
            #        ]
            #    )
            #def check_key_length(key):
            #    return key[0:32]
            #grTxtApiKey.change(
            #    fn=check_key_length,
            #    inputs=[grTxtApiKey],
            #    outputs=[grTxtApiKey],
            #    )
            
            def save_text(grTxtSaveFolder, grDrpdwnFilenames, trained_words):
                return save_text_file(grTxtSaveFolder, grDrpdwnFilenames, trained_words)
            grBtnSaveText.click(
                fn=save_text,
                inputs=[
                    grTxtSaveFolder,
                    grDrpdwnFilenames,
                    grTxtTrainedWords,
                    ],
                outputs=[grTextProgress]
                )

            def save_image_files(grTxtSaveFolder, grDrpdwnFilenames, grHtmlModelInfo):
                return saveImageFiles(grTxtSaveFolder, grDrpdwnFilenames, grHtmlModelInfo, self.civitai.getSelectedModelType(), self.civitai.getModelVersionInfo() )
            grBtnSaveImages.click(
                fn=save_image_files,
                inputs=[
                    grTxtSaveFolder,
                    grDrpdwnFilenames,
                    grHtmlModelInfo,
                    
                    ],
                outputs=[grTextProgress]
                )
            download = grBtnDownloadModel.click(
                fn=download_file2,
                inputs=[
                    grTxtSaveFolder,
                    grDrpdwnFilenames,
                    grTxtDlUrl,
                    grTxtHash,
                    grTxtApiKey,
                    grTxtEarlyAccess
                    ],
                outputs=[grTextProgress,
                        ]
                )
            
            def cancel_download():
                return gr.Textbox.update(value="Canceled")
            grBtnCancel.click(
                fn=cancel_download,
                inputs=None,
                outputs=[grTextProgress],
                cancels=[download]
                )
        
            def update_model_list(grChkbxGrpContentType, grDrpdwnSortType, grRadioSearchType, grTxtSearchTerm, grChkboxShowNsfw, grDrpdwnPeriod, grDrpdwnBasemodels):
                query = self.civitai.makeRequestQuery(
                    grChkbxGrpContentType, grDrpdwnSortType, grDrpdwnPeriod, grRadioSearchType, grTxtSearchTerm, grDrpdwnBasemodels)
                response = self.civitai.requestApi(
                    query=query) 
                err = self.civitai.getRequestError()
                if err is None:
                    grMrkdwnErr = gr.Markdown.update(value=None, visible=False)
                else:
                    grMrkdwnErr = gr.Markdown.update(value=f"**<span style='color:Gold;'>{str(err)}**", visible=True)

                if response is None:
                    return gr.Dropdown.update(choices=[], value=None),\
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=None),\
                        gr.Button.update(interactive=False),\
                        gr.Button.update(interactive=False),\
                        gr.Button.update(interactive=False),\
                        gr.Slider.update(interactive=False),\
                        gr.Textbox.update(value=None),\
                        grMrkdwnErr
                self.civitai.updateJsonData(response) #, grRadioContentType)
                self.civitai.setShowNsfw(grChkboxShowNsfw)
                grTxtPages = self.civitai.getPages()
                hasPrev = not self.civitai.prevPage() is None
                hasNext = not self.civitai.nextPage() is None
                enableJump = hasPrev or hasNext
                #model_names = self.civitai.getModelNames() if (grChkboxShowNsfw) else self.civitai.getModelNamesSfw()
                #HTML = self.civitai.modelCardsHtml(model_names, self.id)
                models = self.civitai.getModels(grChkboxShowNsfw)
                HTML = self.civitai.modelCardsHtml(models, self.id)
                return  gr.Dropdown.update(choices=[f'{model[0]}:({model[1]})' for model in models], value=None),\
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=HTML),\
                        gr.Button.update(interactive=hasPrev),\
                        gr.Button.update(interactive=hasNext),\
                        gr.Button.update(interactive=enableJump),\
                        gr.Slider.update(interactive=enableJump, value=int(self.civitai.getCurrentPage()),maximum=int(self.civitai.getTotalPages())),\
                        gr.Textbox.update(value=grTxtPages),\
                        grMrkdwnErr
            grBtnGetListAPI.click(
                fn=update_model_list,
                inputs=[
                    grChkbxGrpContentType,
                    grDrpdwnSortType,
                    grRadioSearchType,
                    grTxtSearchTerm,
                    grChkboxShowNsfw,
                    grDrpdwnPeriod,
                    grDrpdwnBasemodels
                ],
                outputs=[
                    grDrpdwnModels,
                    grRadioVersions,
                    grHtmlCards,            
                    grBtnPrevPage,
                    grBtnNextPage,
                    grBtnGoPage,
                    grSldrPage,
                    grTxtPages,
                    grMrkdwnErr
                ]
            )

            #def UpdatedModels(grDrpdwnModels):
            #    #print_ly(f"{grDrpdwnModels=}")
            #    eventText = None
            #    if grDrpdwnModels is not None:
            #        match = re.match(r'(.*)\:\((\d+)\)$',grDrpdwnModels)
            #        if match:
            #            index = match.group(2)
            #            eventText = 'Index:' + str(index)
            #    return gr.Textbox.update(value=eventText)
            #grDrpdwnModels.change(
            #    fn=UpdatedModels,
            #    inputs=[
            #        grDrpdwnModels,
            #    ],
            #    outputs=[
            #        #grRadioVersions,
            #        grTxtJsEvent
            #    ]
            #)
            
            def  update_model_info(model_version=None):
                if model_version is not None and self.civitai.selectVersionByName(model_version) is not None:
                    path = generate_model_save_path(self.civitai.getSelectedModelType(),
                                                self.civitai.getSelectedModelName(),
                                                self.civitai.getSelectedVersionBaseModel(),
                                                self.civitai.treatAsNsfw() #isNsfwModel()
                                            )
                    dict = self.civitai.makeModelInfo()
                    if dict['files'] == []:
                        drpdwn =  gr.Dropdown.update(choices=[], value="")
                    else:
                        drpdwn =  gr.Dropdown.update(choices=[f['name'] for f in dict['files']], value=dict['files'][0]['name'])  
                    return  gr.HTML.update(value=dict['html']),\
                            gr.Textbox.update(value=dict['trainedWords']),\
                            drpdwn,\
                            gr.Textbox.update(value=dict['baseModel']),\
                            gr.Textbox.update(value=path),\
                            gr.Textbox.update(value=self.civitai.getSelectedVersionEarlyAccessTimeFrame())
                else:
                    return  gr.HTML.update(value=None),\
                            gr.Textbox.update(value=None),\
                            gr.Dropdown.update(choices=[], value=None),\
                            gr.Textbox.update(value=None),\
                            gr.Textbox.update(value=None), \
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
                    grTxtSaveFolder,
                    grTxtEarlyAccess
                ]
                )
            
            def save_folder_changed(folder, filename):
                self.civitai.setSaveFolder(folder)
                isExist = None
                if filename is not None:
                    isExist = file_exist_check(folder, filename)
                return gr.Markdown.update(visible = True if isExist else False)
            grTxtSaveFolder.blur(
                fn=save_folder_changed,
                inputs={grTxtSaveFolder,grDrpdwnFilenames},
                outputs=[grMrkdwnFileMessage])
          
            grTxtSaveFolder.change(
                fn=self.civitai.setSaveFolder,
                inputs={grTxtSaveFolder},
                outputs=[])
            
            def updateDlUrl(grDrpdwnFilenames):
                return  gr.Textbox.update(value=self.civitai.getUrlByName(grDrpdwnFilenames)),\
                        gr.Textbox.update(value=self.civitai.getHashByName(grDrpdwnFilenames)),\
                        gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                        gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                        gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                        gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                        gr.Textbox.update(value="")
            def update_DownloadButoon(grTxtEarlyAccess):
                return  gr.Button.update(interactive=True if grTxtEarlyAccess == "0" else True),\
                        gr.Textbox.update(value="" if grTxtEarlyAccess == "0" else f"Early Access:{grTxtEarlyAccess}")
            grDrpdwnFilenames.change(
                fn=updateDlUrl,
                inputs=[grDrpdwnFilenames],
                outputs=[
                    grTxtDlUrl,
                    grTxtHash,
                    grBtnSaveText,
                    grBtnSaveImages,
                    grBtnDownloadModel,
                    grBtnCancel,
                    grTextProgress
                    ]
            ).then(
                fn=update_DownloadButoon,
                inputs=[
                    grTxtEarlyAccess
                ],
                outputs=[
                    grBtnDownloadModel,
                    grTextProgress
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
                url = self.civitai.nextPage() if isNext else self.civitai.prevPage()
                response = self.civitai.requestApi(url)
                err = self.civitai.getRequestError()
                if err is None:
                    grMrkdwnErr = gr.Markdown.update(value=None, visible=False)
                else:
                    grMrkdwnErr = gr.Markdown.update(value=f"**<span style='color:Gold;'>{str(err)}**", visible=True)
                if response is None:
                    return None, None,  gr.HTML.update(),None,None,gr.Slider.update(),gr.Textbox.update(), grMrkdwnErr
                self.civitai.updateJsonData(response)
                self.civitai.setShowNsfw(grChkboxShowNsfw)
                grTxtPages = self.civitai.getPages()
                hasPrev = not self.civitai.prevPage() is None
                hasNext = not self.civitai.nextPage() is None
                #model_names = self.civitai.getModelNames() if (grChkboxShowNsfw) else self.civitai.getModelNamesSfw()
                #HTML = self.civitai.modelCardsHtml(model_names, self.id)
                models = self.civitai.getModels(grChkboxShowNsfw)
                HTML = self.civitai.modelCardsHtml(models, self.id)
                return  gr.Dropdown.update(choices=[f'{model[0]}:({model[1]})' for model in models], value=None),\
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=HTML),\
                        gr.Button.update(interactive=hasPrev),\
                        gr.Button.update(interactive=hasNext),\
                        gr.Slider.update(value=self.civitai.getCurrentPage()),\
                        gr.Textbox.update(value=grTxtPages),\
                        grMrkdwnErr
        
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
                    grMrkdwnErr
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
                    grMrkdwnErr
                    #grTxtSaveFolder
                ]
                )

            def jump_to_page(grChkboxShowNsfw, grSldrPage):
                url = self.civitai.nextPage()
                if url is None:
                    url = self.civitai.prevPage()
                addQuery =  {'page': grSldrPage }
                newURL = self.civitai.updateQuery(url, addQuery)
                #print(f'{newURL}')
                response = self.civitai.requestApi(newURL)
                err = self.civitai.getRequestError()
                if err is None:
                    grMrkdwnErr = gr.Markdown.update(value=None, visible=False)
                else:
                    grMrkdwnErr = gr.Markdown.update(value=f"**<span style='color:Gold;'>{str(err)}**", visible=True)
                if response is None:
                    return None, None,  gr.HTML.update(),None,None,gr.Slider.update(),gr.Textbox.update(),grMrkdwnErr
                self.civitai.updateJsonData(response)
                self.civitai.setShowNsfw(grChkboxShowNsfw)
                grTxtPages = self.civitai.getPages()
                hasPrev = not self.civitai.prevPage() is None
                hasNext = not self.civitai.nextPage() is None
                #model_names = self.civitai.getModelNames() if (grChkboxShowNsfw) else self.civitai.getModelNamesSfw()
                #HTML = self.civitai.modelCardsHtml(model_names, self.id)
                models = self.civitai.getModels(grChkboxShowNsfw)
                HTML = self.civitai.modelCardsHtml(models, self.id)
                return  gr.Dropdown.update(choices=[f'{model[0]}:({model[1]})' for model in models], value=None),\
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=HTML),\
                        gr.Button.update(interactive=hasPrev),\
                        gr.Button.update(interactive=hasNext),\
                        gr.Slider.update(value = self.civitai.getCurrentPage()),\
                        gr.Textbox.update(value=grTxtPages),\
                        grMrkdwnErr
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
                    grMrkdwnErr
                    #grTxtSaveFolder
                ])
            
            def updateVersionsByModelID(model_ID=None):
                if model_ID is not None:
                    self.civitai.selectModelByID(model_ID)
                    if self.civitai.getSelectedModelIndex() is not None:
                        dict = self.civitai.getModelVersionsList()
                        self.civitai.selectVersionByName(next(iter(dict.keys()), None))
                        #print(Fore.LIGHTYELLOW_EX + f'{dict=}' + Style.RESET_ALL)
                    #return gr.Dropdown.update(choices=[k for k, v in dict.items()], value=f'{next(iter(dict.keys()), None)}')
                    return gr.Radio.update(choices=list(dict), value=f'{next(iter(dict.keys()), None)}')
                else:
                    return gr.Radio.update(choices=[],value = None)
            def eventTextUpdated(grTxtJsEvent):
                if grTxtJsEvent is not None:
                    grTxtJsEvent = grTxtJsEvent.split(':')
                    # print(Fore.LIGHTYELLOW_EX + f'{grTxtJsEvent=}' + Style.RESET_ALL)
                    if grTxtJsEvent[0].startswith('Index'):
                        index = int(grTxtJsEvent[1]) # str: 'Index:{index}:{id}'
                        self.civitai.selectModelByIndex(index)
                        grRadioVersions = updateVersionsByModelID(self.civitai.getSelectedModelID())
                        grHtmlModelInfo, grTxtTrainedWords, grDrpdwnFilenames, grTxtBaseModel, grTxtSaveFolder, grTxtEarlyAccess = update_model_info(
                            grRadioVersions['value'])
                        grTxtDlUrl = gr.Textbox.update(value=self.civitai.getUrlByName(grDrpdwnFilenames['value']))
                        grTxtHash = gr.Textbox.update(value=self.civitai.getHashByName(grDrpdwnFilenames['value']))
                        grDrpdwnModels = gr.Dropdown.update(value=f'{self.civitai.getSelectedModelName()}:({index})')
                        return  grDrpdwnModels,\
                                grRadioVersions,\
                                grHtmlModelInfo,\
                                grTxtDlUrl,\
                                grTxtEarlyAccess,\
                                grTxtHash,\
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
                                gr.Textbox.update(value=""),\
                                gr.Textbox.update(value=None),\
                                gr.Dropdown.update(value=None),\
                                gr.Textbox.update(value=None),\
                                gr.Textbox.update(value=None)
                else:
                    return  gr.Dropdown.update(value=None),\
                            gr.Radio.update(value=None),\
                            gr.HTML.update(value=None),\
                            gr.Textbox.update(value=None),\
                            gr.Textbox.update(value=None), \
                            gr.Textbox.update(value=""),\
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
                    grTxtEarlyAccess,
                    grTxtHash,
                    grTxtTrainedWords,
                    grDrpdwnFilenames,
                    grTxtBaseModel,
                    grTxtSaveFolder,
                    
                ]
                ).then(
                _js=f'() => {{civsfz_scroll_to("#civsfz_model-data{self.id}");}}',
                fn=None,
                inputs=[],
                outputs=[]    
                )

            def updatePropertiesText():
                propertiesText = ';'.join([
                    str(opts.civsfz_figcaption_background_color),
                    str(opts.civsfz_sd1_background_color), 
                    str(opts.civsfz_sd2_background_color),
                    str(opts.civsfz_sdxl_background_color),
                    str(opts.civsfz_default_shadow_color),
                    str(opts.civsfz_alreadyhave_shadow_color),
                    str(opts.civsfz_hover_zoom_magnification),
                    str(opts.civsfz_card_size_width),
                    str(opts.civsfz_card_size_height)
                    ])
                return gr.Textbox.update(value=propertiesText)
            grHtmlCards.change(
                fn=updatePropertiesText,
                inputs=[],
                outputs=[grTxtPropaties]
                ).then(
                _js='(x) => civsfz_overwriteProperties(x)',
                fn = None,
                inputs=[grTxtPropaties],
                outputs=[]                
                )
            
            grBtnFolder.click(
                fn=open_folder,
                inputs=[grTxtSaveFolder],
                outputs=[]
                )
            
    def getComponents(self):
        return self.components

def on_ui_tabs():
    ver = 'v1.10.1'
    tabNames = []
    for i in range(1, opts.civsfz_number_of_tabs + 1):
        tabNames.append(f'Browser{i}')
    with gr.Blocks() as civitai_interface:
        with gr.Tabs(elem_id='civsfz_tab-element'):
            for i,name in enumerate(tabNames):
                with gr.TabItem(label=name, id=f"tab{i}", elem_id=f"civsfz_tab{i}") as tab:
                    components() #(tab)
        gr.Markdown(value=f'<div style="text-align:center;">{ver}</div>')
    return [(civitai_interface, "CivBrowser", "civsfz_interface")]

script_callbacks.on_ui_tabs(on_ui_tabs)

