import os
import gradio as gr
from modules import script_callbacks
from colorama import Fore, Back, Style
import itertools
from modules.shared import opts
import re
from scripts.civitai_api import civitaimodels

print_ly = lambda  x: print(Fore.LIGHTYELLOW_EX + "Civitai-Browser: " + x + Style.RESET_ALL )
print_lc = lambda  x: print(Fore.LIGHTCYAN_EX + "Civitai-Browser: " + x + Style.RESET_ALL )
print_n = lambda  x: print("Civitai-Browser: " + x )

class components():
    newid = itertools.count()
    
    def __init__(self, tab=None):
        '''id: Event ID for javascrypt'''
        from scripts.file_manage import extranetwork_folder, isExistFile,\
                save_text_file, saveImageFiles,download_file2
        #self.tab = tab
        # Set the URL for the API endpoint
        self.civitai = civitaimodels("https://civitai.com/api/v1/models")
        self.id = next(components.newid)
        contentType = ["Checkpoint","TextualInversion","LORA","LoCon","Poses","Controlnet","Hypernetwork","AestheticGradient", "VAE"]
        def defaultContentType():
            value = contentType[self.id % len(contentType)]
            return value

        with gr.Column() as self.components:
            with gr.Row():
                with gr.Column(scale=4):
                    grRadioContentType = gr.Radio(label='Content type:', choices=contentType, value=defaultContentType)
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
                grMrkdwnErr = gr.Markdown(value=None, visible=False)
            with gr.Row():
                grHtmlCards = gr.HTML()
                grTxtColors = gr.Textbox(label="HTML Colors", value="", visible=False, interactive=False, lines=1)
            with gr.Row():
                with gr.Column(scale=3):
                    grSldrPage = gr.Slider(label="Page", minimum=1, maximum=10,value = 1, step=1, interactive=False, scale=3)
                with gr.Column(scale=1,min_width=80):
                    grBtnGoPage = gr.Button(value="Jump page", interactive=False, scale=1)

            with gr.Row():
                with gr.Column(scale=1):
                    grDrpdwnModels = gr.Dropdown(label="Model", choices=[], interactive=True, elem_id="modellist", value=None)
                    grTxtJsEvent = gr.Textbox(label="Event text", value=None, elem_id=f"eventtext{self.id}", visible=False, interactive=True, lines=1)
                with gr.Column(scale=5):
                    grRadioVersions = gr.Radio(label="Version", choices=[], interactive=True, elem_id="versionlist", value=None)
            with gr.Row(equal_height=False):
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
                with gr.Column(scale=2):
                    with gr.Row():
                        grBtnSaveText = gr.Button(value="Save trained tags",interactive=False, min_width=80)
                        grBtnSaveImages = gr.Button(value="Save model infos",interactive=False, min_width=80)
                        grBtnDownloadModel = gr.Button(value="Download model",interactive=False, elem_id='downloadbutton1',min_width=80)
                with gr.Column(scale=1):
                    with gr.Row():
                        grTextProgress = gr.Textbox(label='Download status',show_label=False)
                        grBtnCancel = gr.Button(value="Cancel",interactive=False, min_width=80)
            with gr.Row():
                grHtmlModelInfo = gr.HTML()
                
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

            def save_image_files(grTxtSaveFolder, grDrpdwnFilenames, grHtmlModelInfo, grRadioContentType):
                return saveImageFiles(grTxtSaveFolder, grDrpdwnFilenames, grHtmlModelInfo, grRadioContentType, self.civitai.getModelVersionInfo() )
            grBtnSaveImages.click(
                fn=save_image_files,
                inputs=[
                    grTxtSaveFolder,
                    grDrpdwnFilenames,
                    grHtmlModelInfo,
                    grRadioContentType,
                    ],
                outputs=[grTextProgress]
                )
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
            
            def cancel_download():
                return gr.Textbox.update(value="Canceled")
            grBtnCancel.click(
                fn=cancel_download,
                inputs=None,
                outputs=[grTextProgress],
                cancels=[download]
                )
        
            def update_model_list(grRadioContentType, grDrpdwnSortType, grRadioSearchType, grTxtSearchTerm, grChkboxShowNsfw, grDrpdwnPeriod):
                query = self.civitai.makeRequestQuery(grRadioContentType, grDrpdwnSortType, grDrpdwnPeriod, grRadioSearchType, grTxtSearchTerm)
                response = self.civitai.requestApi(query=query)
                err = self.civitai.getRequestError()
                if err is None:
                    grMrkdwnErr = gr.Markdown.update(value=None, visible=False)
                else:
                    grMrkdwnErr = gr.Markdown.update(value=f"**<span style='color:Gold;'>{str(err)}**", visible=True)
                colorText = f'{opts.civsfz_figcaption_background_color};'\
                            f'{opts.civsfz_default_shadow_color};'\
                            f'{opts.civsfz_alreadyhave_shadow_color}'
                if response is None:
                    return gr.Dropdown.update(choices=[], value=None),\
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=None),\
                        gr.Button.update(interactive=False),\
                        gr.Button.update(interactive=False),\
                        gr.Button.update(interactive=False),\
                        gr.Slider.update(interactive=False),\
                        gr.Textbox.update(value=None),\
                        grMrkdwnErr,\
                        gr.Textbox.update(value=colorText)
                self.civitai.updateJsonData(response, grRadioContentType)
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
                        grMrkdwnErr,\
                        gr.Textbox.update(value=colorText)
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
                    grTxtPages,
                    grMrkdwnErr,
                    grTxtColors
                ]
            )

            def UpdatedModels(grDrpdwnModels):
                #print_ly(f"{grDrpdwnModels=}")
                eventText = None
                if grDrpdwnModels is not None:
                    match = re.match(r'(.*)\:\((\d+)\)$',grDrpdwnModels)
                    if match:
                        index = match.group(2)
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
                if model_version is not None and self.civitai.selectVersionByName(model_version) is not None:
                    path = extranetwork_folder( self.civitai.getContentType(),
                                                self.civitai.getSelectedModelName(),
                                                self.civitai.getSelectedVersionBaeModel(),
                                                self.civitai.isNsfwModel()
                                            )
                    dict = self.civitai.makeModelInfo()             
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
                self.civitai.setSaveFolder(folder)
                isExist = None
                if filename is not None:
                    isExist = file_exist_check(folder, filename)
                return gr.Markdown.update(visible = True if isExist else False)
                
            grTxtSaveFolder.blur(
                fn=save_folder_changed,
                inputs={grTxtSaveFolder,grDrpdwnFilenames},
                outputs=[grMrkdwnFileMessage])
            
            def updateDlUrl(grDrpdwnFilenames):
                return  gr.Textbox.update(value=self.civitai.getUrlByName(grDrpdwnFilenames)),\
                        gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                        gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                        gr.Button.update(interactive=True if grDrpdwnFilenames else False)
            
            grTxtSaveFolder.change(
                fn=self.civitai.setSaveFolder,
                inputs={grTxtSaveFolder},
                outputs=[])
            
            def updateDlUrl(grDrpdwnFilenames):
                return  gr.Textbox.update(value=self.civitai.getUrlByName(grDrpdwnFilenames)),\
                        gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                        gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                        gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                        gr.Button.update(interactive=True if grDrpdwnFilenames else False),\
                        gr.Textbox.update(value="")
            grDrpdwnFilenames.change(
                fn=updateDlUrl,
                inputs=[grDrpdwnFilenames],
                outputs=[
                    grTxtDlUrl,
                    grBtnSaveText,
                    grBtnSaveImages,
                    grBtnDownloadModel,
                    grBtnCancel,
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
                        grHtmlModelInfo,grTxtTrainedWords, grDrpdwnFilenames, grTxtBaseModel, grTxtSaveFolder = update_model_info(grRadioVersions['value'])
                        grTxtDlUrl = gr.Textbox.update(value=self.civitai.getUrlByName(grDrpdwnFilenames['value']))
                        grDrpdwnModels = gr.Dropdown.update(value=f'{self.civitai.getSelectedModelName()}:({index})')
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
            grHtmlCards.change(
                _js = '(x) => overwriteColors(x)',
                fn = None,
                inputs=[grTxtColors],
                outputs=[]                
                )
            
    def getComponents(self):
        return self.components

def on_ui_tabs():
    ver = 'v1.7.1'
    #ver += '' if tk else ' Cloud mode. No tkinter found.'
    tabNames = []
    for i in range(1, opts.civsfz_number_of_tabs + 1):
        tabNames.append(f'Browser{i}')
    #print_lc(f'{opts.civsfz_figcaption_background_color}')
    #customCss = f'.civmodelcard figcaption {{background-color:{opts.civsfz_figcaption_background_color} !important;}}'
    #print_lc(f'{customCss}')
    with gr.Blocks() as civitai_interface:
        with gr.Tabs():
            for i,name in enumerate(tabNames):
                with gr.TabItem(label=name, id=f"tab{i}", elem_id=f"civtab{i}") as tab:
                    components() #(tab)
        gr.Markdown(value=f'<div style="text-align:center;">{ver}</div>')
    return [(civitai_interface, "CivitAi Browser", "civitai_interface_sfz")]

script_callbacks.on_ui_tabs(on_ui_tabs)

