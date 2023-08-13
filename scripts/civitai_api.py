import os
from html import escape
import json
import urllib.parse
from colorama import Fore, Back, Style
from scripts.file_manage import *

class civitaimodels:
# Handle the response data of civitai api.
    def __init__(self, url:str, json_data:dict={}, content_type:str=""):
        self.jsonData = json_data
        self.contentType = content_type
        self.showNsfw = False
        self.baseUrl = url
        self.selectedItemID = None

    def setBaseUrl(self,url:str):
           self.url = url
    def getBaseUrl(self) -> str:
            return self.baseUrl
    def getJsonData(self) -> dict:
        return self.jsonData
    def updateJsondata(self, json_data:dict={}, content_type:str=""):
        self.jsonData = json_data
        self.contentType = content_type
        self.showNsfw = False
    def setShowNsfw(self, showNsfw:bool):
        self.showNsfw = showNsfw
    def getShowNsfw(self) -> bool:
        return self.showNsfw
    def setContentType(self, content_type:str):
        self.contentType = content_type
    def getContentType(self) -> str:
        return self.contentType
    
    # Items
    def getItemNames(self) -> dict: #include nsfw models
        model_dict = {}
        for item in self.jsonData['items']:
            model_dict[item['name']] = item['name']
        return model_dict
    def getItemNamesSfw(self) -> dict: #sfw models
        model_dict = {}
        for item in self.jsonData['items']:
            if not item['nsfw']:
                model_dict[item['name']] = item['name']
        return model_dict   
    def getItemIDs(self) -> dict:
        IDs = {}
        for item in self.jsonData['items']:
            IDs[item['id']] = item['name']
        return IDs
    def getItemnameByID(self, id:int) -> str:
        name = None
        for item in self.jsonData['items']:
            if item['id'] == id:
                name = item['name']
        return name
    def getIDByItemname(self, name:str) -> str:
        id = None
        for item in self.jsonData['items']:
            if item['name'] == name:
                id = item['id']
        return id
    def isNsfw(self, id:int) -> bool:
        nsfw = None
        for item in self.jsonData['items']:
            if item['id'] == id:
                nsfw = item['name']
        return nsfw
    
    # Model
    def selectItem(self, id:int):
        for item in self.jsonData['items']:
            if item['id'] == id:
                self.selectedItemID = id
        return self.selectedItemID
    def getSelectedItemID(self) -> int:
        return self.selectedItemID
    def getModelVersions(self):
        modelVersions=None
        if self.selectedItemID is None:
            print('Select item first.')
        else:
            for item in self.jsonData['items']:
                if item['id'] == self.selectedItemID:
                    modelVersions = item['modelVersions']
        return modelVersions

    def setModelVersionInfo(self, modelInfo:str):
        self.modelVersionInfo = modelInfo
    def getModelVersionInfo(self) -> str:
        return self.modelVersionInfo

    def getModelVersions(self, modelName:str) -> dict:
        versions_dict = {}
        if modelName is not None:
            versions_dict = {}
            for item in self.jsonData['items']:
                if item['name'] == modelName:
                    for model in item['modelVersions']:
                        versions_dict[model['name']] = item["name"]
        return versions_dict


    def getModelInfo(self, modelName:str, modelVersion:str) -> dict:
        modelInfo = {
            'description':"",
            'trainedWords':"",
            'files':{},
            'allow':{},
        }
        for item in self.jsonData['items']:
            if item['name'] == modelName:
                modelInfo['creator'] = item['creator']['username']
                modelInfo['tags'] = item['tags']
                if item['description']:
                    modelInfo['description'] = item['description']
                if item['allowNoCredit']:
                    modelInfo['allow']['allowNoCredit'] = item['allowNoCredit']
                if item['allowCommercialUse']:
                    modelInfo['allow']['allowCommercialUse'] = item['allowCommercialUse']
                if item['allowDerivatives']:
                    modelInfo['allow']['allowDerivatives'] = item['allowDerivatives']
                if item['allowDifferentLicense']:
                    modelInfo['allow']['allowDifferentLicense'] = item['allowDifferentLicense']
                for model in item['modelVersions']:
                    if model['name'] == modelVersion:
                        if model['trainedWords']:
                            modelInfo['trainedWords'] = ", ".join(model['trainedWords'])
                        if model['baseModel']:
                            modelInfo['baseModel'] = model['baseModel']
                        for file in model['files']:
                            modelInfo['files'][file['name']] = file['downloadUrl']

                        modelInfo['downloadUrl'] = model['downloadUrl']
                        #model_filename = model['files']['name']

                        img_html = '<div class="sampleimgs">'
                        for pic in model['images']:
                            nsfw = None
                            if pic['nsfw'] != "None" and not self.showNsfw:
                                nsfw = 'class="civnsfw"'
                            img_html = img_html + f'<div {nsfw} style="display:flex;align-items:flex-start;"><img src={pic["url"]} style="width:20em;"></img>'
                            if pic['meta']:
                                img_html = img_html + '<div style="text-align:left;line-height: 1.5em;">'
                                for key, value in pic['meta'].items():
                                    img_html = img_html + f'{escape(str(key))}: {escape(str(value))}</br>'
                                img_html = img_html + '</div>'
                            img_html = img_html + '</div>'
                        img_html = img_html + '</div>'
                        output_html = '<p>' \
                            f'<b>Model</b>: {escape(str(modelName))}<br>'\
                            f'<b>Version</b>: {escape(str(modelVersion))}<br>'\
                            f'<b>Uploaded by</b>: {escape(str(modelInfo["creator"]))}<br>'\
                            f'<b>Base Model</b>: {escape(str(modelInfo["baseModel"]))}</br>'\
                            f'<b>Tags</b>: {escape(str(modelInfo["tags"]))}<br>'\
                            f'<b>Trained Tags</b>: {escape(str(modelInfo["trainedWords"]))}<br>'\
                            f'{escape(str(modelInfo["allow"]))}<br>'\
                            f'<a href={modelInfo["downloadUrl"]}><b>'\
                            'Download Here</b></a>'\
                            '</p><br><br><p>'\
                            f'{modelInfo["description"]}</p><br>'\
                            f'<div align=center>{img_html}</div>'
                        modelInfo['html'] = output_html
        return modelInfo

    def updateDlUrl(self, model_name=None, model_version=None, model_filename=None):
        if model_filename:
            dl_url = None
            #model_version = model_version.replace(f' - {model_name}','').strip()
            for item in self.jsonData['items']:
                if item['name'] == model_name:
                    for model in item['modelVersions']:
                        if model['name'] == model_version:
                            for file in model['files']:
                                if file['name'] == model_filename:
                                    dl_url = file['downloadUrl']
                                    self.setModelVersionInfo(model)
            return dl_url
        else:
            return None
    # Pages
    def getCurrentPage(self) -> str:
        return f"{self.jsonData['metadata']['currentPage']}"
    def getTotalPages(self) -> str:
        return f"{self.jsonData['metadata']['totalPages']}"
    def getPages(self) -> str:
        return f"{self.getCurrentPage()}/{self.getTotalPages()}"
    def nextPage(self) -> str:
        return self.jsonData['metadata']['nextPage'] if 'nextPage' in self.jsonData['metadata'] else ""
    def prevPage(self) -> str:
        return self.jsonData['metadata']['prevPage'] if 'prevPage' in self.jsonData['metadata'] else ""

    # HTML
    # Make model cards html
    def modelCardsHtml(self, model_dict):
        HTML = '<div class="column civmodellist">'
        for item in self.jsonData['items']:
            for k,model in model_dict.items():
                if model_dict[k] == item['name']:
                    #print(f'Item:{item["modelVersions"][0]["images"]}')
                    model_name = escape(item["name"].replace("'","\\'"),quote=True)
                    #print(f'{model_name}')
                    #print(f'Length: {len(item["modelVersions"][0]["images"])}')
                    nsfw = ""
                    alreadyhave = ""
                    if any(item['modelVersions']):
                        if len(item['modelVersions'][0]['images']) > 0:
                            if item["modelVersions"][0]["images"][0]['nsfw'] != "None" and not self.getShowNsfw():
                                nsfw = 'civcardnsfw'
                            imgtag = f'<img src={item["modelVersions"][0]["images"][0]["url"]}"></img>'
                        else:
                            imgtag = f'<img src="./file=html/card-no-preview.png"></img>'
                            
                        for file in item['modelVersions'][0]['files']:
                            file_name = file['name']
                            base_model = item["modelVersions"][0]['baseModel']
                            folder = extranetwork_folder(self.getContentType(),False,item["name"],base_model, False)
                            path_file = os.path.join(folder, file_name)
                            #print(f"{path_file}")
                            if os.path.exists(path_file):
                                alreadyhave = "civmodelcardalreadyhave"
                                break
                    HTML = HTML +  f'<figure class="civmodelcard {nsfw} {alreadyhave}" onclick="select_model(\'{model_name}\')">'\
                                    +  imgtag \
                                    +  f'<figcaption>{item["name"]}</figcaption></figure>'
        HTML = HTML + '</div>'
        return HTML
    
    #REST API
    def makeRequestQuery(self, content_type, sort_type, use_search_term, search_term=None):
        query = {'types': content_type, 'sort': sort_type}
        if use_search_term != "No" and search_term:
            #search_term = search_term.replace(" ","%20")
            match use_search_term:
                case "User name":
                    query |= {'username': search_term }
                case "Tag":
                    query |= {'tag': search_term }
                case _:
                    query |= {'query': search_term }
        return query

    def requestApi(self, url=None, query=None):
        if url is None:
            url = self.getBaseUrl()
        if query is not None:
            query = urllib.parse.urlencode(query, quote_via=urllib.parse.quote)
        # Make a GET request to the API
        try:
            response = requests.get( url, params=query, timeout=(10,15))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(Fore.YELLOW + "Request error: " , e)
            print(Style.RESET_ALL)
            #print(f"Query: {payload} URL: {response.url}")
            data = self.jsonData # exit() #return None
        else:
            response.encoding  = "utf-8" # response.apparent_encoding
            data = json.loads(response.text)
        # Check the status code of the response
        #if response.status_code != 200:
        #  print("Request failed with status code: {}".format(response.status_code))
        #  exit()            
        return data