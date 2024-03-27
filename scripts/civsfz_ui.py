import gradio as gr
from datetime import datetime, timedelta, timezone
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
import math
import scripts as scripts
from scripts.civsfz_api import CivitaiModels
from scripts.civsfz_filemanage import open_folder, SearchHistory

print_ly = lambda  x: print(Fore.LIGHTYELLOW_EX + "CivBrowser: " + x + Style.RESET_ALL )
print_lc = lambda  x: print(Fore.LIGHTCYAN_EX + "CivBrowser: " + x + Style.RESET_ALL )
print_n = lambda  x: print("CivBrowser: " + x )
sHistory = SearchHistory()
class Components():
    newid = itertools.count()

    def __init__(self, tab=None):
        '''id: Event ID for javascrypt'''
        from scripts.civsfz_filemanage import generate_model_save_path2, isExistFile, \
            save_text_file, saveImageFiles, download_file
        # self.tab = tab
        # Set the URL for the API endpoint
        self.civitai = CivitaiModels()
        self.id = next(Components.newid)
        contentTypes = self.civitai.getTypeOptions()
        self.APIKey = ""
        if cmd_opts.civsfz_api_key:
            self.APIKey = cmd_opts.civsfz_api_key[0:32]
            # print(f"{self.APIKey=}")
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
                        grDrpdwnPeriod = gr.Dropdown(label='Period', choices=self.civitai.getPeriodOptions(
                        ), value=defaultPeriod, type="value")
                with gr.Column(scale=1, max_width=100, min_width=100):
                    grDrpdwnBasemodels = gr.Dropdown(label="Base Models (experimental)", choices=self.civitai.getBasemodelOptions(
                    ), value=None, type="value", multiselect=True)
                with gr.Column(scale=1, max_width=100, min_width=80):
                    grChkboxShowNsfw = gr.Checkbox(label="NSFW content", value=False)
            with gr.Row():
                grRadioSearchType = gr.Radio(scale=2, label="Search", choices=self.civitai.getSearchTypes(),value="No")
                grDropdownSearchTerm = gr.Dropdown( scale=1,
                    label="Search Term", choices=sHistory.getAsChoices(), type="value",  interactive=True, allow_custom_value=True)
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

            # def renameTab(type):
            #    return gr.TabItem.update(label=f'{self.id}:{type}')
            # grRadioContentType.change(
            #    fn = renameTab,
            #    inputs=[
            #        grRadioContentType
            #       ],
            #    outputs=[
            #            self.tab
            #        ]
            #    )
            # def check_key_length(key):
            #    return key[0:32]
            # grTxtApiKey.change(
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
                fn=download_file,
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
            
            def selectHistory(grDropdownSearchTerm):
                if grDropdownSearchTerm == None:
                    return (gr.Dropdown.update(),
                            gr.Radio.update())
                m = re.match(r'(.+):-:(.+)$', grDropdownSearchTerm)
                if len(m.groups()) < 2:
                    return ( gr.Dropdown.update(),
                        gr.Radio.update())
                return (gr.Dropdown.update(value=m.group(1)),
                        gr.Radio.update(value=m.group(2)))
            grDropdownSearchTerm.select(
                fn=selectHistory,
                inputs=[grDropdownSearchTerm],
                outputs=[grDropdownSearchTerm,
                        grRadioSearchType]
            )
            def update_model_list(grChkbxGrpContentType, grDrpdwnSortType, grRadioSearchType, grDropdownSearchTerm, grChkboxShowNsfw, grDrpdwnPeriod, grDrpdwnBasemodels):
                response = None
                self.civitai.clearRequestError()
                query = self.civitai.makeRequestQuery(
                    grChkbxGrpContentType, grDrpdwnSortType, grDrpdwnPeriod, grRadioSearchType, grDropdownSearchTerm, grDrpdwnBasemodels)
                if query == "":
                    gr.Warning(f'Enter a number')
                if grRadioSearchType == "Version ID":
                    if query != "":
                        url = self.civitai.getVersionsApiUrl(query)
                        response = self.civitai.requestApi(url=url)
                        if self.civitai.getRequestError() is None:
                            # Some key is not included in the response
                            grRadioSearchType = "Model ID"
                            query = str(response["modelId"])
                if grRadioSearchType == "Model ID":
                    if query != "":
                        url = self.civitai.getModelsApiUrl(query)
                        response = self.civitai.requestApi(url=url)
                        response = {
                            'requestUrl': response['requestUrl'],
                            "items":[response],
                            'metadata': {
                                'currentPage': "1",
                                'pageSize': "1",
                                }
                            } if self.civitai.getRequestError() is None else None
                elif grRadioSearchType != "Version ID":
                    response = self.civitai.requestApi(
                        query=query) 
                err = self.civitai.getRequestError()
                if err is not None:
                    gr.Warning(str(err))
                if response is None:
                    return gr.Dropdown.update(choices=[], value=None),\
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=None),\
                        gr.Button.update(interactive=False),\
                        gr.Button.update(interactive=False),\
                        gr.Button.update(interactive=False),\
                        gr.Slider.update(interactive=False),\
                        gr.Textbox.update(value=None),\
                        gr.Dropdown.update()
                sHistory.add(grRadioSearchType, grDropdownSearchTerm)
                self.civitai.updateJsonData(response) #, grRadioContentType)
                if err is None:
                    self.civitai.addFirstPage(response, grChkbxGrpContentType, grDrpdwnSortType, grRadioSearchType,
                                              grDropdownSearchTerm, grChkboxShowNsfw, grDrpdwnPeriod, grDrpdwnBasemodels)
                self.civitai.setShowNsfw(grChkboxShowNsfw)
                grTxtPages = self.civitai.getPages()
                hasPrev = not self.civitai.prevPage() is None
                hasNext = not self.civitai.nextPage() is None
                enableJump = hasPrev or hasNext
                # model_names = self.civitai.getModelNames() if (grChkboxShowNsfw) else self.civitai.getModelNamesSfw()
                # HTML = self.civitai.modelCardsHtml(model_names, self.id)
                models = self.civitai.getModels(grChkboxShowNsfw)
                HTML = self.civitai.modelCardsHtml(models, jsID=self.id)
                return  gr.Dropdown.update(choices=[f'{model[0]}:({model[1]})' for model in models], value=None),\
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=HTML),\
                        gr.Button.update(interactive=hasPrev),\
                        gr.Button.update(interactive=hasNext),\
                        gr.Button.update(interactive=enableJump),\
                        gr.Slider.update(interactive=enableJump, value=int(self.civitai.getCurrentPage()),maximum=int(self.civitai.getTotalPages())),\
                        gr.Textbox.update(value=grTxtPages),\
                    gr.Dropdown.update(
                        choices=sHistory.getAsChoices())
            grBtnGetListAPI.click(
                fn=update_model_list,
                inputs=[
                    grChkbxGrpContentType,
                    grDrpdwnSortType,
                    grRadioSearchType,
                    grDropdownSearchTerm,
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
                    grDropdownSearchTerm
                ]
            )

            # def UpdatedModels(grDrpdwnModels):
            #    #print_ly(f"{grDrpdwnModels=}")
            #    eventText = None
            #    if grDrpdwnModels is not None:
            #        match = re.match(r'(.*)\:\((\d+)\)$',grDrpdwnModels)
            #        if match:
            #            index = match.group(2)
            #            eventText = 'Index:' + str(index)
            #    return gr.Textbox.update(value=eventText)
            # grDrpdwnModels.change(
            #    fn=UpdatedModels,
            #    inputs=[
            #        grDrpdwnModels,
            #    ],
            #    outputs=[
            #        #grRadioVersions,
            #        grTxtJsEvent
            #    ]
            # )

            def  update_model_info(model_version=None):
                if model_version is not None and self.civitai.selectVersionByIndex(model_version) is not None:
                    path = generate_model_save_path2(self.civitai.getSelectedModelType(),
                                                self.civitai.getSelectedModelName(),
                                                self.civitai.getSelectedVersionBaseModel(),
                                                self.civitai.treatAsNsfw(), #isNsfwModel()
                                                self.civitai.getUserName(),
                                                self.civitai.getModelID(),
                                                self.civitai.getVersionID(),
                                                self.civitai.getSelectedVersionName()
                                            )
                    dict = self.civitai.makeModelInfo2()
                    if dict['modelVersions'][0]["files"] == []:
                        drpdwn =  gr.Dropdown.update(choices=[], value="")
                    else:
                        filename = dict["modelVersions"][0]["files"][0]["name"]
                        for f in dict["modelVersions"][0]["files"]:
                            if 'primary' in f:
                                if f['primary']:
                                    filename = f["name"]
                                    break
                        drpdwn = gr.Dropdown.update(
                            choices=[
                                f["name"] for f in dict["modelVersions"][0]["files"]
                            ],
                            value=filename,
                        )
                    return (
                        gr.HTML.update(value=dict["html"]),
                        gr.Textbox.update(value=", ".join(dict["trainedWords"])),
                        drpdwn,
                        gr.Textbox.update(value=dict["baseModel"]),
                        gr.Textbox.update(value=path),
                        gr.Textbox.update(
                            value=self.civitai.getSelectedVersionEarlyAccessDeadline()
                        ),
                    )
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

            def checkEarlyAccess(grTxtEarlyAccess):
                msg = ""
                if grTxtEarlyAccess != "":
                    dtPub = self.civitai.getPublishedDatetime()
                    dtNow = datetime.now(timezone.utc)
                    # dtEndat = dtPub + timedelta(days=int(grTxtEarlyAccess))
                    dtEndat = self.civitai.getEarlyAccessDeadlineDatetime()
                    tdDiff = dtNow - dtEndat
                    # print_lc(f'{tdDiff=}')
                    if tdDiff / timedelta(days=1) >= 0:
                        msg = f"Early Access: expired" # {dtDiff.days}/{grTxtEarlyAccess}
                    elif tdDiff / timedelta(hours=1) >= -1:
                        msg = f"Early Access: {math.ceil(abs(tdDiff / timedelta(minutes=1)))} minutes left"
                    elif tdDiff / timedelta(hours=1) >= -24:
                        msg = f"Early Access: {math.ceil(abs(tdDiff / timedelta(hours=1)))} hours left"
                    else:
                        msg = f"Early Access: {math.ceil(abs(tdDiff / timedelta(days=1)))} days left"
                return gr.Textbox.update(value="" if grTxtEarlyAccess == "" else f"{msg} ")

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
                fn=checkEarlyAccess,
                inputs=[
                    grTxtEarlyAccess
                ],
                outputs=[
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
                if err is not None:
                    gr.Warning(str(err))
                if response is None:
                    return None, None,  gr.HTML.update(),None,None,gr.Slider.update(),gr.Textbox.update()
                self.civitai.updateJsonData(response)
                if err is None:
                    self.civitai.addNextPage(
                        response) if isNext else self.civitai.backPage(response)
                self.civitai.setShowNsfw(grChkboxShowNsfw)
                grTxtPages = self.civitai.getPages()
                hasPrev = not self.civitai.prevPage() is None
                hasNext = not self.civitai.nextPage() is None
                # model_names = self.civitai.getModelNames() if (grChkboxShowNsfw) else self.civitai.getModelNamesSfw()
                # HTML = self.civitai.modelCardsHtml(model_names, self.id)
                models = self.civitai.getModels(grChkboxShowNsfw)
                HTML = self.civitai.modelCardsHtml(models, self.id)
                return  gr.Dropdown.update(choices=[f'{model[0]}:({model[1]})' for model in models], value=None),\
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=HTML),\
                        gr.Button.update(interactive=hasPrev),\
                        gr.Button.update(interactive=hasNext),\
                        gr.Slider.update(value=self.civitai.getCurrentPage(), maximum=self.civitai.getTotalPages()),\
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
                    grTxtPages
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
                    grTxtPages
                    #grTxtSaveFolder
                ]
                )

            def jump_to_page(grChkboxShowNsfw, grSldrPage):
                #url = self.civitai.nextPage()
                #if url is None:
                #    url = self.civitai.prevPage()
                #addQuery =  {'page': grSldrPage }
                #newURL = self.civitai.updateQuery(url, addQuery)
                newURL = self.civitai.getJumpUrl(grSldrPage)
                if newURL is None:
                    return None, None,  gr.HTML.update(), None, None, gr.Slider.update(), gr.Textbox.update()
                # print(f'{newURL}')
                response = self.civitai.requestApi(newURL)
                err = self.civitai.getRequestError()
                if err is not None:
                    gr.Warning(str(err))
                if response is None:
                    return None, None,  gr.HTML.update(),None,None,gr.Slider.update(),gr.Textbox.update()
                self.civitai.updateJsonData(response)
                if err is None:
                    self.civitai.pageJump(response,grSldrPage)
                self.civitai.setShowNsfw(grChkboxShowNsfw)
                grTxtPages = self.civitai.getPages()
                hasPrev = not self.civitai.prevPage() is None
                hasNext = not self.civitai.nextPage() is None
                # model_names = self.civitai.getModelNames() if (grChkboxShowNsfw) else self.civitai.getModelNamesSfw()
                # HTML = self.civitai.modelCardsHtml(model_names, self.id)
                models = self.civitai.getModels(grChkboxShowNsfw)
                HTML = self.civitai.modelCardsHtml(models, jsID=self.id)
                return  gr.Dropdown.update(choices=[f'{model[0]}:({model[1]})' for model in models], value=None),\
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=HTML),\
                        gr.Button.update(interactive=hasPrev),\
                        gr.Button.update(interactive=hasNext),\
                        gr.Slider.update(value = self.civitai.getCurrentPage()),\
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
                    grTxtPages
                ])

            def updateVersionsByModelID(model_ID=None):
                if model_ID is not None:
                    self.civitai.selectModelByID(model_ID)
                    if self.civitai.getSelectedModelIndex() is not None:
                        list = self.civitai.getModelVersionsList()
                        self.civitai.selectVersionByIndex(0)
                        # print(Fore.LIGHTYELLOW_EX + f'{dict=}' + Style.RESET_ALL)
                    # return gr.Dropdown.update(choices=[k for k, v in dict.items()], value=f'{next(iter(dict.keys()), None)}')
                    return gr.Radio.update(choices=list, value=0)
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
                    str(opts.civsfz_alreadyhad_shadow_color),
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
    ver = 'v1.18.0'
    tabNames = []
    for i in range(1, opts.civsfz_number_of_tabs + 1):
        tabNames.append(f'Browser{i}')
    with gr.Blocks() as civitai_interface:
        with gr.Tabs(elem_id='civsfz_tab-element'):
            for i,name in enumerate(tabNames):
                with gr.TabItem(label=name, id=f"tab{i}", elem_id=f"civsfz_tab{i}") as tab:
                    Components() #(tab)
        gr.Markdown(value=f'<div style="text-align:center;">{ver}</div>')
    return [(civitai_interface, "CivBrowser", "civsfz_interface")]

script_callbacks.on_ui_tabs(on_ui_tabs)
