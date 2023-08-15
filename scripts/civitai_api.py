import os
from html import escape
import json
import urllib.parse
import requests
from colorama import Fore, Back, Style
from scripts.file_manage import extranetwork_folder

class civitaimodels:
    '''civitaimodels: Handle the response of civitai models api v1.'''
    def __init__(self, url:str, json_data:dict={}, content_type:str=""):
        self.jsonData = json_data
        self.contentType = content_type
        self.showNsfw = False
        self.baseUrl = url
        self.modelID = None
        self.modelNsfw = False
        self.modelVersionInfo = None
    def updateJsonData(self, json_data:dict={}, content_type:str=""):
        '''Update json data.'''
        self.jsonData = json_data
        self.contentType = content_type
        self.showNsfw = False
        self.modelID = None
        self.modelNsfw = False
        self.modelVersionInfo = None
    def setBaseUrl(self,url:str):
           self.url = url
    def getBaseUrl(self) -> str:
            return self.baseUrl
    def getJsonData(self) -> dict:
        return self.jsonData

    def setShowNsfw(self, showNsfw:bool):
        self.showNsfw = showNsfw
    def isShowNsfw(self) -> bool:
        return self.showNsfw
    def setContentType(self, content_type:str):
        self.contentType = content_type
    def getContentType(self) -> str:
        return self.contentType
    
    # Models
    def getModelNames(self) -> dict: #include nsfw models
        model_dict = {}
        for item in self.jsonData['items']:
            model_dict[item['name']] = item['name']
        return model_dict
    def getModelNamesSfw(self) -> dict: #sfw models
        '''Return SFW items names.'''
        model_dict = {}
        for item in self.jsonData['items']:
            if not item['nsfw']:
                model_dict[item['name']] = item['name']
        return model_dict   
    def getModelIDs(self) -> dict:
        IDs = {}
        for item in self.jsonData['items']:
            IDs[item['id']] = item['name']
        return IDs
    
    # Model
    def getModelNameByID(self, id:int) -> str:
        name = None
        for item in self.jsonData['items']:
            if item['id'] == id:
                name = item['name']
        return name
    def getIDByModelName(self, name:str) -> str:
        id = None
        for item in self.jsonData['items']:
            if item['name'] == name:
                id = item['id']
        return id
    def isNsfwModelByID(self, id:int) -> bool:
        nsfw = None
        for item in self.jsonData['items']:
            if item['id'] == id:
                nsfw = item['nsfw']
        return nsfw
    def selectModelByID(self, id:int):
        for item in self.jsonData['items']:
            if item['id'] == id:
                self.modelID = item['id']
                self.modelNsfw = item['nsfw']
            else:
                print(Fore.LIGHTYELLOW_EX + f'Model {id} not found. Return {self.modelID}' + Style.RESET_ALL)
        return self.modelID
    def selectModelByName(self, name:str):
        '''Serlect model by Name. Name are vaguer than IDs.'''
        if name is not None:
            for item in self.jsonData['items']:
                if item['name'] == name:
                    self.modelID = item['id']
                    self.modelNsfw = item['nsfw']
            #print(f'{name} - {self.modelID}')
        return self.modelID
    def isNsfwModel(self) -> bool:
        return self.modelNsfw
    def getModelID(self) -> int:
        return self.modelID
    def allows2permissions(self) -> dict:
        '''Convert allows to permissions.
            [->Reference](https://github.com/civitai/civitai/blob/main/src/components/PermissionIndicator/PermissionIndicator.tsx#L15)'''
        permissions = {}
        if self.modelID is None:
            print(Fore.LIGHTYELLOW_EX + 'Select item first.' + Style.RESET_ALL )
        else:
            for item in self.jsonData['items']:
                if item['id'] == self.modelID:
                    allowNoCredit = item['allowNoCredit']
                    allowCommercialUse = item['allowCommercialUse']
                    allowDerivatives = item['allowDerivatives']
                    allowDifferentLicense = item['allowDifferentLicense']
                    canSellImages = allowCommercialUse == 'Image' or allowCommercialUse == 'Rent' or allowCommercialUse == 'Sell'
                    canRent = allowCommercialUse == 'Rent' or allowCommercialUse == 'Sell'
                    canSell = allowCommercialUse == 'Sell'
                    permissions['allowNoCredit'] = allowNoCredit
                    permissions['canSellImages'] = canSellImages
                    permissions['canRent'] = canRent
                    permissions['canSell'] = canSell
                    permissions['allowDerivatives'] = allowDerivatives
                    permissions['allowDifferentLicense'] = allowDifferentLicense
        return permissions
    # Version

    def getModelVersionsList(self):
        '''Return modelVersions list.
         Select the item before. '''
        versions_dict = {}
        if self.modelID is None:
            print(Fore.LIGHTYELLOW_EX + 'Select item first.' + Style.RESET_ALL )
        else:
            for item in self.jsonData['items']:
                if item['id'] == self.modelID:
                    for model in item['modelVersions']:
                        versions_dict[model['name']] = model["name"]
        return versions_dict

    def setModelVersionInfo(self, modelInfo:str):
        self.modelVersionInfo = modelInfo
    def getModelVersionInfo(self) -> str:
        return self.modelVersionInfo

    def getVersionInfoByName(self,versionName:str) -> dict:
        model_dict = {}
        if versionName is not None:
            for index, item in enumerate(self.jsonData['items']):
                if item['id'] == self.modelID:
                    for model in item['modelVersions']:
                        if model['name'] == versionName:
                            model_dict = model
        return model_dict


    def makeModelInfo2(self, versionName:str) -> dict:
        '''not yet'''
        modelInfo = {}
        if self.modelID is None:
            print(Fore.LIGHTYELLOW_EX + f'Select item first. {self.modelID}' + Style.RESET_ALL )
        else:
            for index, item in enumerate(self.jsonData['items']):
                if item['id'] == self.modelID:
                    modelInfo = self.jsonData['items'][index]
                for version in item['modelVersions']:
                    if version['name'] == versionName:
                        modelInfo['modelVersion'] = version
        return modelInfo
    
    def makeModelInfo(self, modelName:str, modelVersion:str) -> dict:
        modelInfo = {
            'description':"",
            'trainedWords':"",
            'files':{},
            'allow':{},
        }
        for item in self.jsonData['items']:
            if item['name'] == modelName:
                modelInfo['id'] = item['id']
                modelInfo['model_name'] = item['name']
                modelInfo['type'] = item['type']
                modelInfo['nsfw'] = item['nsfw']
                modelInfo['creator'] = item['creator']['username']
                modelInfo['tags'] = item['tags']
                modelInfo['description'] = item['description']
                modelInfo['allow']['allowNoCredit'] = item['allowNoCredit']
                modelInfo['allow']['allowCommercialUse'] = item['allowCommercialUse']
                modelInfo['allow']['allowDerivatives'] = item['allowDerivatives']
                modelInfo['allow']['allowDifferentLicense'] = item['allowDifferentLicense']
                for model in item['modelVersions']:
                    if model['name'] == modelVersion:
                        modelInfo['version_name'] = model['name']
                        modelInfo['modelId'] = model['modelId']
                        modelInfo['trainedWords'] = ", ".join(model['trainedWords'])
                        modelInfo['baseModel'] = model['baseModel']
                        modelInfo['versionDescription'] = model['description']
                        for file in model['files']:
                            modelInfo['files'][file['name']] = file['downloadUrl']
                        pics = []
                        for pic in model['images']:
                            pics.append({ 'id' : pic['id'],
                                          'nsfw' : pic['nsfw'],
                                          'url': pic["url"],
                                          'meta' : pic['meta'],
                                          'type' : pic['type'],
                                         })
                        modelInfo['images'] = pics
                        modelInfo['downloadUrl'] = model['downloadUrl'] if 'downloadUrl' in model else ""
                modelInfo['html'] = self.modelInfoHtml(modelInfo)
                self.setModelVersionInfo(modelInfo)
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
        '''Generate HTML of model cards.'''
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
                            if item["modelVersions"][0]["images"][0]['nsfw'] != "None" and not self.isShowNsfw():
                                nsfw = 'civcardnsfw'
                            imgtag = f'<img src={item["modelVersions"][0]["images"][0]["url"]}"></img>'
                        else:
                            imgtag = f'<img src="./file=html/card-no-preview.png"></img>'
                            
                        for file in item['modelVersions'][0]['files']:
                            file_name = file['name']
                            base_model = item["modelVersions"][0]['baseModel']
                            folder = extranetwork_folder(self.getContentType(),False,item["name"],base_model, False, nsfw=item['nsfw'])
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

    def modelInfoHtml(self, modelInfo:dict) -> str:
        '''Generate HTML of model info'''
        img_html = '<div class="sampleimgs">'
        for pic in modelInfo['images']:
            nsfw = None
            if pic['nsfw'] != "None" and not self.showNsfw:
                nsfw = 'class="civnsfw"'
            img_html = img_html +\
                         f'<div {nsfw} style="display:flex;align-items:flex-start;">'\
                         f'<img src={pic["url"]} style="width:20em;"></img>'
            if pic['meta']:
                img_html = img_html + '<div style="text-align:left;line-height: 1.5em;">'
                for key, value in pic['meta'].items():
                    img_html = img_html + f'{escape(str(key))}: {escape(str(value))}</br>'
                img_html = img_html + '</div>'
            img_html = img_html + '</div>'
        img_html = img_html + '</div>'
        output_html = '<div>'
        if modelInfo['nsfw']:
            output_html += '<h1>NSFW</b></h1>'
        output_html += f'<h1>Model: {escape(str(modelInfo["model_name"]))}</h1>'\
            f'<b>Civitai link</b> (if exist): '\
            f'<a href="https://civitai.com/models/{escape(str(modelInfo["id"]))}" target="_blank">'\
            f'https://civitai.com/models/{str(modelInfo["id"])}</a></br>'\
            f'<b>Version</b>: {escape(str(modelInfo["version_name"]))}</br>'\
            f'<b>Uploaded by</b>: {escape(str(modelInfo["creator"]))}</br>'\
            f'<b>Base Model</b>: {escape(str(modelInfo["baseModel"]))}</br>'\
            f'<b>Tags</b>: {escape(str(modelInfo["tags"]))}</br>'\
            f'<b>Trained Tags</b>: {escape(str(modelInfo["trainedWords"]))}</br>'\
            f'<a href={modelInfo["downloadUrl"]}>'\
            '<b>Download Here</b></a>'\
            '</div>'\
            '<h2>Permissions</h2>'\
            f'<p>{self.permissionsHtml(self.allows2permissions())}'\
            f'{escape(str(modelInfo["allow"]))}</p>'\
            '<div><h2>Model description</h2>'\
            f'<p>{modelInfo["description"]}</p></div>'
        if modelInfo["versionDescription"]:
            output_html += f'<div><h2>Version description</h2>'\
            f'<p>{modelInfo["versionDescription"]}</p></div></br>'
        output_html += f'<div><h2>Images</h3>{img_html}</div>'
        return output_html
    
    def permissionsHtml(self, premissions:dict, msgType:int=2) -> str:
        html1 = '<div>'\
                f'<p><strong>Check the source license yourself.</strong></p>'\
                f'<b>{premissions["allowNoCredit"]}</b> : Use the model without crediting the creator</br>'\
                f'<b>{premissions["canSellImages"]}</b> : Sell images they generate</br>'\
                f'<b>{premissions["canRent"]}</b> : Run on services that generate images for money</br>'\
                f'<b>{premissions["allowDerivatives"]}</b> : Share merges using this model</br>'\
                f'<b>{premissions["canSell"]}</b> : Sell this model or merges using this model</br>'\
                f'<b>{premissions["allowDifferentLicense"]}<b> : Have different permissions when sharing merges</p>'\
                '</div>'
        html2 = '<div>'\
                f'<p><strong>Check the source license yourself.</strong></br>'\
                '<span style=color:red>'
        html2 += 'Creator credit required</br>' if not premissions["allowNoCredit"] else ''
        html2 += 'No selling images</br>' if not premissions["canSellImages"] else ''
        html2 += 'No generation services</br>' if not premissions["canRent"] else ''
        html2 += 'No selling models</br>' if not premissions["canSell"] else ''
        html2 += 'No sharing merges</br>' if not premissions["allowDerivatives"] else ''
        html2 += 'Same permissions required</br>' if not premissions["allowDifferentLicense"] else ''
        html2 += '</span></p></div>'
        match msgType:
            case 1:
                html = html1
            case 2:
                html = html2
            case _:
                html = html2 + html1
        return html

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
            print(Fore.LIGHTYELLOW_EX + "Request error: " , e)
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
    