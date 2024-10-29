import gradio as gr
import itertools
import json
import math
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone
from modules import script_callbacks
from colorama import Fore, Back, Style
# from modules.shared import opts
from scripts.civsfz_color import BaseModelColors
from scripts.civsfz_shared import VERSION, cmd_opts, opts

import scripts as scripts
from scripts.civsfz_api import CivitaiModels
from scripts.civsfz_filemanage import open_folder, SearchHistory, ConditionsHistory
from scripts.civsfz_downloader import Downloader

print_ly = lambda  x: print(Fore.LIGHTYELLOW_EX + "CivBrowser: " + x + Style.RESET_ALL )
print_lc = lambda  x: print(Fore.LIGHTCYAN_EX + "CivBrowser: " + x + Style.RESET_ALL )
print_n = lambda  x: print("CivBrowser: " + x )

class Components():
    newid = itertools.count()
    sHistory = SearchHistory()
    cHistory = ConditionsHistory()
    downloader = None
    def __init__(self, downloader:Downloader, tab=None):
        '''id: Event ID for javascrypt'''
        from scripts.civsfz_filemanage import generate_model_save_path2, isExistFile, \
            save_text_file, saveImageFiles
        Components.downloader = downloader
        self.gr_version = gr.__version__
        # print_ly(f"{self.gr_version}")
        self.tab = tab
        # Set the URL for the API endpoint
        self.civitai = CivitaiModels()
        self.id = next(Components.newid)
        contentTypes = self.civitai.getTypeOptions()
        self.APIKey = ""
        if cmd_opts.civsfz_api_key:
            self.APIKey = cmd_opts.civsfz_api_key[0:32]
            print_ly(
                "Command line option `--civsfz_api_key` is deprecated. Instead, use Settings."
            )
        if opts.civsfz_api_key:
            self.APIKey = opts.civsfz_api_key[0:32]
        def defaultContentType():
            value = contentTypes[self.id % len(contentTypes)]
            return value
        def defaultPeriod():
            return "Month"
        def cmdoptsAPIKey():
            return self.APIKey
        def browsingLevelChoices():
            return list(self.civitai.nsfwLevel.items())

        with gr.Column() as self.components:
            with gr.Row():
                with gr.Column(scale=1):
                    grChkbxGrpContentType = gr.CheckboxGroup(
                        label='Types:', choices=contentTypes, value=defaultContentType)
                with gr.Column(scale=1):
                    with gr.Row():
                        grDrpdwnSortType = gr.Dropdown(
                            label='Sort List by:', choices=self.civitai.getSortOptions(), value="Newest", type="value")
                        with gr.Accordion(label="Sensitive", open=False):
                            grChkboxShowNsfw = gr.Checkbox(
                                label="nsfw", info="WARNING", value=False)
                    with gr.Row():
                        grDrpdwnPeriod = gr.Dropdown(label='Period', choices=self.civitai.getPeriodOptions(
                        ), value=defaultPeriod, type="value")
                        grDrpdwnBasemodels = gr.Dropdown(label="Base Models", choices=self.civitai.getBasemodelOptions(
                        ), value=None, type="value", multiselect=True)
                    with gr.Row():
                        grDrpdwnCHistory = gr.Dropdown(label="Conditions History", choices=Components.cHistory.getAsChoices(), type="value")

            with gr.Row():
                grRadioSearchType = gr.Radio(scale=2, label="Search", choices=self.civitai.getSearchTypes(),value="No")
                grDropdownSearchTerm = gr.Dropdown( scale=1,
                    label="Search Term", choices=Components.sHistory.getAsChoices(), type="value",  interactive=True, allow_custom_value=True)
            with gr.Column(elem_id=f"civsfz_model-navigation{self.id}"):
                with gr.Row(elem_id=f"civsfz_apicontrol{self.id}", elem_classes="civsfz-navigation-buttons civsfz-sticky-element"):
                    with gr.Column(scale=3):
                        grBtnGetListAPI = gr.Button(value="GET cards")
                    with gr.Column(scale=2,min_width=80):
                        grBtnPrevPage = gr.Button(value="PREV", interactive=False)
                    with gr.Column(scale=2,min_width=80):
                        grBtnNextPage = gr.Button(value="NEXT", interactive=False)
                    with gr.Column(scale=1,min_width=80):
                        grTxtPages = gr.Textbox(label='Pages',show_label=False)
                with gr.Row():
                    grHtmlCards = gr.HTML()
                    grTxtPropaties = gr.Textbox(elem_id="civsfz_css-properties", label="CSS Properties", value="", visible=False, interactive=False, lines=1)
                with gr.Row(elem_classes="civsfz-jump-page-control civsfz-sticky-element"):
                    with gr.Column(scale=3):
                        grSldrPage = gr.Slider(label="Page", minimum=1, maximum=10,value = 1, step=1, interactive=False, scale=3)
                    with gr.Column(scale=1,min_width=80):
                        grBtnGoPage = gr.Button(value="JUMP", interactive=False, scale=1)
                    with gr.Accordion(label="Browsing Level", open=False):
                        with gr.Column(min_width=80):
                            grChkbxgrpLevel = gr.CheckboxGroup(label='Browsing Level', choices=list(self.civitai.nsfwLevel.items()) ,value=opts.civsfz_browsing_level, interactive=True, show_label=False)

            with gr.Column(elem_id=f"civsfz_model-data{self.id}"):
                grHtmlBackToTop = gr.HTML(
                    elem_classes="civsfz-back-to-top",
                    value=f"<div onclick='civsfz_scroll_to(\"#civsfz_model-navigation{self.id}\");'><span style='font-size:200%;color:transparent;text-shadow:0 0 0 orange;cursor: pointer;pointer-events: auto;'>&#x1F51D;</span></div>",
                )  # 🔝
                with gr.Row():
                    grHtmlModelName = gr.HTML(
                        elem_id=f"civsfz_modellist{self.id}",
                        value=None,
                        visible=True,
                    )
                    grTxtJsEvent = gr.Textbox(label="Event text", value=None, elem_id=f"civsfz_eventtext{self.id}", visible=False, interactive=True, lines=1)
                    txt_list = ""
                    grTxtTrainedWords = gr.Textbox(
                        label='Trained Tags (if any)', value=f'{txt_list}', interactive=False, lines=1, visible=False)
                with gr.Row(elem_classes="civsfz-save-buttons civsfz-sticky-element"):
                    with gr.Column(scale=2):
                        with gr.Row():
                            # grBtnSaveText = gr.Button(value="Save trained tags",interactive=False, min_width=80)
                            grBtnSaveImages = gr.Button(
                                value="Save model infos",
                                interactive=False,
                                min_width=80,
                            )
                            grBtnDownloadModel = gr.Button(
                                value="Download model",
                                interactive=False,
                                elem_id=f"civsfz_downloadbutton{self.id}",
                                min_width=80,
                            )
                    with gr.Column(scale=1):
                        with gr.Row():
                            grTextProgress = gr.Textbox(
                                label="Download status", show_label=False
                            )
                            # deprecated grBtnCancel = gr.Button(value="Cancel",interactive=False, variant='stop', min_width=80)

                with gr.Row():
                    grRadioVersions = gr.Radio(label="Version", choices=[], interactive=True, elem_id=f"civsfz_versionlist{self.id}", value=None)
                with gr.Row():
                    grTxtBaseModel = gr.Textbox(scale=1, label='Base Model', value='', interactive=True, lines=1, visible=False)
                    grDrpdwnSelectFile = gr.Dropdown(scale=3, label="File select", choices=[], interactive=True, value=None)
                with gr.Row(equal_height=False):
                    grBtnFolder = gr.Button(value="\N{Open file folder}", interactive=True, elem_classes="civsfz-small-buttons")  # 📂
                    grTxtSaveFolder = gr.Textbox(label="Save folder", interactive=True, value="", lines=1)
                    grMrkdwnFileMessage = gr.Markdown(value="**<span style='color:Aquamarine;'>You have</span>**", elem_classes ="civsfz-msg", visible=False)
                    grtxtSaveFilename = gr.Textbox(label="Save file name", interactive=True, value=None)
                with gr.Row():
                    grTxtDlUrl = gr.Textbox(label="Download Url", interactive=False, value=None)
                    grTxtEarlyAccess = gr.Textbox(label='Early Access', interactive=False, value=None, visible=False)
                    grTxtHash = gr.Textbox(label="File hash", interactive=False, value="", visible=False)
                    grTxtApiKey = gr.Textbox(
                        label="API Key",
                        value=lambda: self.APIKey,
                        type="password",
                        lines=1,
                    )
                with gr.Row():
                    grHtmlModelInfo = gr.HTML(elem_id=f"civsfz_model-info{self.id}")

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

            def save_text(grTxtSaveFolder, grtxtSaveFilename, trained_words):
                return 
            # grBtnSaveText.click(
            #    fn=save_text,
            #    inputs=[
            #        grTxtSaveFolder,
            #        grtxtSaveFilename,
            #        grTxtTrainedWords,
            #        ],
            #   outputs=[grTextProgress]
            #    )

            def save_image_files(grTxtSaveFolder, grtxtSaveFilename, grTxtTrainedWords, grHtmlModelInfo):
                res1 = save_text_file(grTxtSaveFolder, grtxtSaveFilename, grTxtTrainedWords)
                res2 = saveImageFiles(
                    grTxtSaveFolder,
                    grtxtSaveFilename,
                    grHtmlModelInfo,
                    self.civitai.getSelectedModelType(),
                    self.civitai.getModelVersionInfo(),
                )
                return res1 + " / " + res2

            grBtnSaveImages.click(
                fn=save_image_files,
                inputs=[
                    grTxtSaveFolder,
                    grtxtSaveFilename,
                    grTxtTrainedWords,
                    grHtmlModelInfo,
                ],
                outputs=[grTextProgress],
            )
            grBtnDownloadModel.click(
                fn=Components.downloader.add,
                inputs=[
                    grTxtSaveFolder,
                    grtxtSaveFilename,
                    grTxtDlUrl,
                    grTxtHash,
                    grTxtApiKey,
                    grTxtEarlyAccess
                    ],
                outputs=[grTextProgress]
                )

            def selectSHistory(grDropdownSearchTerm):
                if grDropdownSearchTerm == None:
                    return (gr.Dropdown.update(),
                            gr.Radio.update())
                m = re.match(rf'(.+){self.sHistory.getDelimiter()}(.+)$', grDropdownSearchTerm)
                if m is None:
                    return (gr.Dropdown.update(),
                            gr.Radio.update())
                if len(m.groups()) < 2:
                    return ( gr.Dropdown.update(),
                        gr.Radio.update())
                return (gr.Dropdown.update(value=m.group(1)),
                        gr.Radio.update(value=m.group(2)))
            grDropdownSearchTerm.select(
                fn=selectSHistory,
                inputs=[grDropdownSearchTerm],
                outputs=[grDropdownSearchTerm,
                        grRadioSearchType]
            )
            def selectCHistory(grDrpdwnHistory):
                if grDrpdwnHistory:
                    conditions = grDrpdwnHistory.split(self.cHistory.getDelimiter())
                    return (gr.Dropdown.update(value=conditions[0]),
                            gr.Dropdown.update(value=conditions[1]),
                            gr.Dropdown.update(value=json.loads(conditions[2])),
                            gr.Checkbox.update(value=conditions[3].lower() in 'true')
                            )
                else:
                    return (#gr.CheckboxGroup.update(),
                            gr.Dropdown.update(),
                            gr.Dropdown.update(),
                            gr.Dropdown.update(),
                            gr.Checkbox.update()
                            )
            grDrpdwnCHistory.select(fn=selectCHistory,
                                   inputs=[grDrpdwnCHistory],
                                   outputs=[#grChkbxGrpContentType,
                                            grDrpdwnSortType,
                                            grDrpdwnPeriod,
                                            grDrpdwnBasemodels,
                                            grChkboxShowNsfw]
                                   )
            def CHistoryUpdate():
                return gr.Dropdown.update(choices=Components.cHistory.getAsChoices())
            self.tab.select(fn=CHistoryUpdate,
                                inputs=[],
                                outputs=[grDrpdwnCHistory]
                            )

            def updatePropertiesText():
                opacity = f"{int(opts.civsfz_background_opacity*255):02x}"
                propertiesText = ";".join(
                    [
                        str(opts.civsfz_background_color_figcaption) + opacity,
                        str(opts.civsfz_background_color_sd1),
                        str(opts.civsfz_background_color_sd2),
                        str(opts.civsfz_background_color_sd3),
                        str(opts.civsfz_background_color_sd35),
                        str(opts.civsfz_background_color_sdxl),
                        str(opts.civsfz_background_color_pony),
                        str(opts.civsfz_background_color_illustrious),
                        str(opts.civsfz_background_color_flux1),
                        str(opts.civsfz_shadow_color_default),
                        str(opts.civsfz_shadow_color_alreadyhave),
                        str(opts.civsfz_shadow_color_alreadyhad),
                        str(opts.civsfz_hover_zoom_magnification),
                        str(opts.civsfz_card_size_width),
                        str(opts.civsfz_card_size_height),
                    ]
                )
                BaseModelColors().updateColor()
                return gr.Textbox.update(value=propertiesText)

            # https://github.com/SignalFlagZ/sd-webui-civbrowser/issues/59
            # grHtmlCards.change(
            #    fn=updatePropertiesText,
            #    inputs=[],
            #    outputs=[grTxtPropaties]
            #    ).then(
            #    _js='(x) => civsfz_overwriteProperties(x)',
            #    fn = None,
            #    inputs=[grTxtPropaties],
            #    outputs=[]
            #    )

            def update_model_list(grChkbxGrpContentType, grDrpdwnSortType, grRadioSearchType, grDropdownSearchTerm, grChkboxShowNsfw, grDrpdwnPeriod, grDrpdwnBasemodels, grChkbxgrpLevel:list):
                response = None
                self.civitai.clearRequestError()
                query = self.civitai.makeRequestQuery(
                    grChkbxGrpContentType, grDrpdwnSortType, grDrpdwnPeriod, grRadioSearchType, grDropdownSearchTerm, grDrpdwnBasemodels, grChkboxShowNsfw)
                if query == "":
                    gr.Warning(f'Enter a number')
                vIdAsmId = False # 
                if grRadioSearchType == "Version ID":
                    if query != "":
                        url = self.civitai.getVersionsApiUrl(query)
                        response = self.civitai.requestApi(url=url)
                        if self.civitai.getRequestError() is None:
                            # Some key is not included in the response
                            vIdAsmId = True
                            query = str(response["modelId"])
                if grRadioSearchType == "Hash":
                    if query != "":
                        url = self.civitai.getVersionsByHashUrl(query)
                        response = self.civitai.requestApi(url=url)
                        if self.civitai.getRequestError() is None:
                            # Some key is not included in the response
                            vIdAsmId = True
                            query = str(response["modelId"])
                if grRadioSearchType == "Model ID" or vIdAsmId:
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
                elif grRadioSearchType not in ("Version ID", "Hash"):
                    response = self.civitai.requestApi(
                        query=query) 
                err = self.civitai.getRequestError()
                if err is not None:
                    gr.Warning(str(err))
                if response is None:
                    return gr.HTML.update(choices=[], value=None),\
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=None),\
                        gr.Button.update(interactive=False),\
                        gr.Button.update(interactive=False),\
                        gr.Button.update(interactive=False),\
                        gr.Slider.update(interactive=False),\
                        gr.Textbox.update(value=None),\
                        gr.Dropdown.update(),\
                        gr.Dropdown.update()
                Components.sHistory.add(grRadioSearchType, grDropdownSearchTerm)
                Components.cHistory.add(grDrpdwnSortType,
                             grDrpdwnPeriod,
                             grDrpdwnBasemodels,
                             grChkboxShowNsfw)
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
                HTML = self.civitai.modelCardsHtml(models, jsID=self.id, nsfwLevel=sum(grChkbxgrpLevel))
                return  gr.HTML.update(value=""), \
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=HTML),\
                        gr.Button.update(interactive=hasPrev),\
                        gr.Button.update(interactive=hasNext),\
                        gr.Button.update(interactive=enableJump),\
                        gr.Slider.update(interactive=enableJump, value=int(self.civitai.getCurrentPage()),maximum=int(self.civitai.getTotalPages())),\
                        gr.Textbox.update(value=grTxtPages),\
                        gr.Dropdown.update(choices=Components.sHistory.getAsChoices()),\
                        gr.Dropdown.update(choices=Components.cHistory.getAsChoices(),value=Components.cHistory.getAsChoices()[0])
            def preload_nextpage():
                hasNext = not self.civitai.nextPage() is None
                if hasNext:
                    url = self.civitai.nextPage()
                    response = self.civitai.requestApi(url, timeout=(10,10))

            grBtnGetListAPI.click(
                fn=update_model_list,
                inputs=[
                    grChkbxGrpContentType,
                    grDrpdwnSortType,
                    grRadioSearchType,
                    grDropdownSearchTerm,
                    grChkboxShowNsfw,
                    grDrpdwnPeriod,
                    grDrpdwnBasemodels,
                    grChkbxgrpLevel,
                ],
                outputs=[
                    grHtmlModelName,
                    grRadioVersions,
                    grHtmlCards,
                    grBtnPrevPage,
                    grBtnNextPage,
                    grBtnGoPage,
                    grSldrPage,
                    grTxtPages,
                    grDropdownSearchTerm,
                    grDrpdwnCHistory,
                ],
            ).then(  # for custum settings
                fn=updatePropertiesText, inputs=[], outputs=[grTxtPropaties]
            ).then(
                fn=preload_nextpage,
                inputs=[],
                outputs=[],
            ).then(
                _js=f'() => {{civsfz_scroll_to("#civsfz_model-navigation{self.id}");}}',
                fn=None,
                inputs=[],
                outputs=[],
            )

            # for custum settings
            grTxtPropaties.change(
                _js='(x) => civsfz_overwriteProperties(x)',
                fn = None,
                inputs=[grTxtPropaties],
                outputs=[]
            )

            def  update_model_info(model_version=None, grChkbxgrpLevel=[0]):
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
                    dict = self.civitai.makeModelInfo2(nsfwLevel=sum(grChkbxgrpLevel))
                    if dict['modelVersions'][0]["files"] == []:
                        drpdwn =  gr.Dropdown.update(choices=[], value="")
                        grtxtSaveFilename = gr.Textbox.update(value="")
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
                        grtxtSaveFilename = gr.Textbox.update(value=filename)
                    return (
                        gr.HTML.update(value=dict["html"]),
                        gr.Textbox.update(value=", ".join(dict["trainedWords"])),
                        drpdwn,
                        gr.Textbox.update(value=dict["baseModel"]),
                        gr.Textbox.update(value=path),
                        gr.Textbox.update(
                            value=self.civitai.getSelectedVersionEarlyAccessDeadline()
                        ),
                        grtxtSaveFilename,
                    )
                else:
                    return (
                        gr.HTML.update(value=None),
                        gr.Textbox.update(value=None),
                        gr.Dropdown.update(choices=[], value=None),
                        gr.Textbox.update(value=None),
                        gr.Textbox.update(value=None),
                        gr.Textbox.update(value=None),
                        gr.Textbox.update(value=None),
                    )
            grRadioVersions.change(
                fn=update_model_info,
                inputs=[grRadioVersions, grChkbxgrpLevel],
                outputs=[
                    grHtmlModelInfo,
                    grTxtTrainedWords,
                    grDrpdwnSelectFile,
                    grTxtBaseModel,
                    grTxtSaveFolder,
                    grTxtEarlyAccess,
                    grtxtSaveFilename,
                ],
            )

            def save_folder_changed(folder, filename):
                self.civitai.setSaveFolder(folder)
                isExist = None
                if filename is not None:
                    isExist = file_exist_check(folder, filename)
                return gr.Markdown.update(visible = True if isExist else False)
            grTxtSaveFolder.blur(
                fn=save_folder_changed,
                inputs={grTxtSaveFolder,grDrpdwnSelectFile},
                outputs=[grMrkdwnFileMessage])

            grTxtSaveFolder.change(
                fn=self.civitai.setSaveFolder,
                inputs={grTxtSaveFolder},
                outputs=[])

            def updateDlUrl(grDrpdwnSelectFile):
                return (
                    gr.Textbox.update(
                        value=self.civitai.getUrlByName(grDrpdwnSelectFile)
                    ),
                    gr.Textbox.update(
                        value=self.civitai.getHashByName(grDrpdwnSelectFile)
                    ),
                    gr.Button.update(interactive=True if grDrpdwnSelectFile else False),
                    gr.Button.update(interactive=True if grDrpdwnSelectFile else False),
                    gr.Textbox.update(value=""),
                    gr.Textbox.update(value=grDrpdwnSelectFile),
                )

            def checkEarlyAccess(grTxtEarlyAccess):
                return gr.Textbox.update(value="" if grTxtEarlyAccess == "" else "Early Access")
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

            grDrpdwnSelectFile.change(
                fn=updateDlUrl,
                inputs=[grDrpdwnSelectFile],
                outputs=[
                    grTxtDlUrl,
                    grTxtHash,
                    # grBtnSaveText,
                    grBtnSaveImages,
                    grBtnDownloadModel,
                    grTextProgress,
                    grtxtSaveFilename,
                ],
            ).then(
                fn=checkEarlyAccess, inputs=[grTxtEarlyAccess], outputs=[grTextProgress]
            )

            def file_exist_check(grTxtSaveFolder, grDrpdwnSelectFile):
                isExist = isExistFile(grTxtSaveFolder, grDrpdwnSelectFile)            
                return gr.Markdown.update(visible = True if isExist else False)
            grTxtDlUrl.change(
                fn=file_exist_check,
                inputs=[grTxtSaveFolder,
                        grDrpdwnSelectFile
                        ],
                outputs=[
                        grMrkdwnFileMessage
                        ]
                )

            def update_next_page(grChkboxShowNsfw, grChkbxgrpLevel, isNext=True):
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
                HTML = self.civitai.modelCardsHtml(models, self.id, nsfwLevel=sum(grChkbxgrpLevel))
                return  gr.HTML.update(value=None),\
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=HTML),\
                        gr.Button.update(interactive=hasPrev),\
                        gr.Button.update(interactive=hasNext),\
                        gr.Slider.update(value=self.civitai.getCurrentPage(), maximum=self.civitai.getTotalPages()),\
                        gr.Textbox.update(value=grTxtPages)

            grBtnNextPage.click(
                fn=update_next_page,
                inputs=[grChkboxShowNsfw, grChkbxgrpLevel],
                outputs=[
                    grHtmlModelName,
                    grRadioVersions,
                    grHtmlCards,
                    grBtnPrevPage,
                    grBtnNextPage,
                    grSldrPage,
                    grTxtPages,
                    # grTxtSaveFolder
                ],
            ).then(
                fn=preload_nextpage,
                inputs=[],
                outputs=[],
            )
            def update_prev_page(grChkboxShowNsfw, grChkbxgrpLevel):
                return update_next_page(grChkboxShowNsfw, grChkbxgrpLevel, isNext=False)
            grBtnPrevPage.click(
                fn=update_prev_page,
                inputs=[grChkboxShowNsfw, grChkbxgrpLevel],
                outputs=[
                    grHtmlModelName,
                    grRadioVersions,
                    grHtmlCards,
                    grBtnPrevPage,
                    grBtnNextPage,
                    grSldrPage,
                    grTxtPages,
                    # grTxtSaveFolder
                ],
            )

            def jump_to_page(grChkboxShowNsfw, grSldrPage, grChkbxgrpLevel):
                # url = self.civitai.nextPage()
                # if url is None:
                #    url = self.civitai.prevPage()
                # addQuery =  {'page': grSldrPage }
                # newURL = self.civitai.updateQuery(url, addQuery)
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
                HTML = self.civitai.modelCardsHtml(models, jsID=self.id, nsfwLevel=sum(grChkbxgrpLevel))
                return  gr.HTML.update(value=None),\
                        gr.Radio.update(choices=[], value=None),\
                        gr.HTML.update(value=HTML),\
                        gr.Button.update(interactive=hasPrev),\
                        gr.Button.update(interactive=hasNext),\
                        gr.Slider.update(value = self.civitai.getCurrentPage()),\
                        gr.Textbox.update(value=grTxtPages)
            grBtnGoPage.click(
                fn=jump_to_page,
                inputs=[grChkboxShowNsfw, grSldrPage, grChkbxgrpLevel],
                outputs=[
                    grHtmlModelName,
                    grRadioVersions,
                    grHtmlCards,
                    grBtnPrevPage,
                    grBtnNextPage,
                    grSldrPage,
                    grTxtPages,
                ],
            )

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
            def eventTextUpdated(grTxtJsEvent, grChkbxgrpLevel):
                if grTxtJsEvent is not None:
                    grTxtJsEvent = grTxtJsEvent.split(':')
                    # print(Fore.LIGHTYELLOW_EX + f'{grTxtJsEvent=}' + Style.RESET_ALL)
                    if grTxtJsEvent[0].startswith('Index'):
                        index = int(grTxtJsEvent[1]) # str: 'Index:{index}:{id}'
                        self.civitai.selectModelByIndex(index)
                        grRadioVersions = updateVersionsByModelID(self.civitai.getSelectedModelID())
                        (
                            grHtmlModelInfo,
                            grTxtTrainedWords,
                            grDrpdwnSelectFile,
                            grTxtBaseModel,
                            grTxtSaveFolder,
                            grTxtEarlyAccess,
                            grtxtSaveFilename,
                        ) = update_model_info(grRadioVersions["value"], grChkbxgrpLevel)
                        # grTxtDlUrl = gr.Textbox.update(value=self.civitai.getUrlByName(grDrpdwnSelectFile['value']))
                        grTxtHash = gr.Textbox.update(value=self.civitai.getHashByName(grDrpdwnSelectFile['value']))
                        grHtmlModelName = gr.HTML.update(
                            value=self.civitai.modelNameTitleHtml(self.civitai.getSelectedModelName(), grTxtBaseModel['value']),
                        )
                        return (
                            grHtmlModelName,
                            grRadioVersions,
                            grHtmlModelInfo,
                            grTxtEarlyAccess,
                            grTxtHash,
                            grTxtTrainedWords,
                            grDrpdwnSelectFile,
                            grTxtBaseModel,
                            grTxtSaveFolder,
                            grtxtSaveFilename,
                        )
                    else:
                        return (
                            gr.HTML.update(value=None),
                            gr.Radio.update(value=None),
                            gr.HTML.update(value=None),
                            gr.Textbox.update(value=None),
                            gr.Textbox.update(value=""),
                            gr.Textbox.update(value=None),
                            gr.Dropdown.update(value=None),
                            gr.Textbox.update(value=None),
                            gr.Textbox.update(value=None),
                            gr.Textbox.update(value=None),
                        )
                else:
                    return (
                        gr.HTML.update(value=None),
                        gr.Radio.update(value=None),
                        gr.HTML.update(value=None),
                        gr.Textbox.update(value=None),
                        gr.Textbox.update(value=""),
                        gr.Textbox.update(value=None),
                        gr.Dropdown.update(value=None),
                        gr.Textbox.update(value=None),
                        gr.Textbox.update(value=None),
                        gr.Textbox.update(value=None),
                    )

            grTxtJsEvent.change(
                fn=eventTextUpdated,
                inputs=[grTxtJsEvent, grChkbxgrpLevel],
                outputs=[
                    grHtmlModelName,
                    grRadioVersions,
                    grHtmlModelInfo,
                    grTxtEarlyAccess,
                    grTxtHash,
                    grTxtTrainedWords,
                    grDrpdwnSelectFile,
                    grTxtBaseModel,
                    grTxtSaveFolder,
                    grtxtSaveFilename,
                ],
            ).then(
                _js=f'() => {{civsfz_scroll_to("#civsfz_model-data{self.id}");}}',
                fn=None,
                inputs=[],
                outputs=[],
            )

            grBtnFolder.click(
                fn=open_folder,
                inputs=[grTxtSaveFolder],
                outputs=[]
                )

    def getComponents(self):
        return self.components

def on_ui_tabs():
    ver = VERSION
    tabNames = []
    downloader = Downloader()
    for i in range(1, opts.civsfz_number_of_tabs + 1):
        tabNames.append(f'Browser{i}')
    with gr.Blocks() as civitai_interface:
        with gr.Accordion(label="Update information", open=False):
            gr.Markdown(
                value=(
                    "# Recent changes"
                    "\n"
                    "- Command line option `--civsfz_api_key` is deprecated. Instead, use Settings."
                    "\n"
                    "- The default color has been changed due to code corrections related to background color settings."
                    "\n"
                    "- Change the layout of save buttons to reduce mouse movement"
                    "\n"
                    "- Model name and base model are displayed in large size"
                    "\n"
                    "- Add background color for Illustrious"
                    "\n"
                    "- Add background color for SD3 and SD3.5"
                    "\n"
                    "- Change the position of Back-to-Top button to reduce mouse movement"
                    "\n"
                    "- Preload next page"
                    "\n\n"
                    "For more information, please click [here(CivBrowser|GitHub)](https://github.com/SignalFlagZ/sd-webui-civbrowser)"
                )
            )
        downloader.uiDlList(gr)
        # Use the Timer component because there are problems with `every` on HTML component.
        # grHtmlDlQueue = gr.HTML(elem_id=f"civsfz_download_queue", value=None)
        # grTimer = gr.Timer(value=10.0)
        # def updateDlList():
        #    ret = gr.HTML.update(value=Downloader.uiDlList)
        #    return ret
        # grTimer.tick(
        #    fn=updateDlList,
        #    inputs=[],
        #    outputs=[grHtmlDlQueue],
        # )
        with gr.Tabs(elem_id='civsfz_tab-element', elem_classes="civsfz-custom-property"):
            for i,name in enumerate(tabNames):
                with gr.Tab(label=name, id=f"tab{i}", elem_id=f"civsfz_tab{i}") as tab:
                    Components(downloader, tab)  # (tab)
        with gr.Row():
            gr.Markdown(value=f'<div style="text-align:center;">{ver}</div>')
            downloader.uiJsEvent(gr)
    return [(civitai_interface, "CivBrowser", "civsfz_interface")]

script_callbacks.on_ui_tabs(on_ui_tabs)
