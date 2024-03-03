import os
import datetime
from dateutil import tz
from html import escape
import json
import urllib.parse
from pathlib import Path
import requests
from colorama import Fore, Back, Style
from scripts.civsfz_filemanage import generate_model_save_path
from modules.shared import opts
from jinja2 import Environment, FileSystemLoader

print_ly = lambda  x: print(Fore.LIGHTYELLOW_EX + "CivBrowser: " + x + Style.RESET_ALL )
print_lc = lambda  x: print(Fore.LIGHTCYAN_EX + "CivBrowser: " + x + Style.RESET_ALL )
print_n = lambda  x: print("CivBrowser: " + x )

baseUrl = "https://civitai.com"
modelsApi = "/api/v1/models"
imagesApi = "/api/v1/images"
versionsAPI = "/api/v1/model-versions"
typeOptions = None
sortOptions = None
basemodelOptions = None
periodOptions = None
searchTypes = ["No", "Model name", "User name",
               "Tag", "Model ID", "Version ID"]

templatesPath = Path.joinpath(
    Path(__file__).parent, Path("../templates"))
environment = Environment(loader=FileSystemLoader(templatesPath.resolve()))

class civitaimodels:
    '''civitaimodels: Handle the response of civitai models api v1.'''
    def __init__(self, url:str=None, json_data:dict=None, content_type:str=None):
        global typeOptions
        self.jsonData = json_data
        # self.contentType = content_type
        self.showNsfw = False
        self.baseUrl = baseUrl if url is None else url
        self.modelIndex = None
        self.versionIndex = None
        self.modelVersionInfo = None
        self.requestError = None
        self.saveFolder = None
        if typeOptions is None:
            self.getOptions()

    def updateJsonData(self, json_data:dict=None, content_type:str=None):
        '''Update json data.'''
        self.jsonData = json_data
        # self.contentType = self.contentType if content_type is None else content_type
        self.showNsfw = False
        self.modelIndex = None
        self.versionIndex = None
        self.modelVersionInfo = None
        self.requestError = None
        self.saveFolder = None
    def setBaseUrl(self,url:str):
        self.url = url
    def getBaseUrl(self) -> str:
        return self.baseUrl
    def getModelsApiUrl(self, id=None):
        url = self.baseUrl + modelsApi
        url += f'/{id}' if id is not None else ""
        return url
    def getImagesApiUrl(self):
        return self.baseUrl + imagesApi
    def getVersionsApiUrl(self, id=None):
        url = self.baseUrl + versionsAPI
        url += f'/{id}' if id is not None else ""
        return url
    def getJsonData(self) -> dict:
        return self.jsonData

    def setShowNsfw(self, showNsfw:bool):
        self.showNsfw = showNsfw
    def isShowNsfw(self) -> bool:
        return self.showNsfw
    # def setContentType(self, content_type:str):
    #    self.contentType = content_type
    # def getContentType(self) -> str:
    #    return self.contentType
    def getRequestError(self) -> requests.exceptions.RequestException:
        return self.requestError
    def clearRequestError(self):
        self.requestError = None
    def setSaveFolder(self, path):
        self.saveFolder = path
    def getSaveFolder(self):
        return self.saveFolder
    def getTypeOptions(self) -> list:
        # global typeOptions, sortOptions, basemodelOptions
        return typeOptions
    def getSortOptions(self) -> list:
        # global typeOptions, sortOptions, basemodelOptions
        return sortOptions
    def getBasemodelOptions(self) -> list:
        # global typeOptions, sortOptions, basemodelOptions
        return basemodelOptions
    def getPeriodOptions(self) -> list:
        return periodOptions
    def getSearchTypes(self) -> list:
        return searchTypes

    # Models
    def getModels(self, showNsfw = False) -> list:
        '''Return: [(str: Model name, str: index)]'''
        model_list = [] 
        for index, item in enumerate(self.jsonData['items']):
            if showNsfw :
                model_list.append((item['name'], index))
            elif not self.treatAsNsfw(modelIndex=index):  #item['nsfw']:
                model_list.append((item['name'], index))
        return model_list

    # def getModelNames(self) -> dict: #include nsfw models
    #    model_dict = {}
    #    for item in self.jsonData['items']:
    #        model_dict[item['name']] = item['name']
    #    return model_dict
    # def getModelNamesSfw(self) -> dict: #sfw models
    #    '''Return SFW items names.'''
    #    model_dict = {}
    #    for item in self.jsonData['items']:
    #        if not item['nsfw']:
    #            model_dict[item['name']] = item['name']
    #    return model_dict

    # Model
    def getModelNameByID(self, id:int) -> str:
        name = None
        for item in self.jsonData['items']:
            if int(item['id']) == int(id):
                name = item['name']
        return name
    def getIDByModelName(self, name:str) -> str:
        id = None
        for item in self.jsonData['items']:
            if item['name'] == name:
                id = int(item['id'])
        return id
    def getModelNameByIndex(self, index:int) -> str:
        return self.jsonData['items'][index]['name']
    def isNsfwModelByID(self, id:int) -> bool:
        nsfw = None
        for item in self.jsonData['items']:
            if int(item['id']) == int(id):
                nsfw = item['nsfw']
        return nsfw
    def selectModelByIndex(self, index:int):
        if index >= 0 and index < len(self.jsonData['items']):
            self.modelIndex = index
        return self.modelIndex
    def selectModelByID(self, id:int):
        for index, item in enumerate(self.jsonData['items']):
            if int(item['id']) == int(id):
                self.modelIndex = index
        return self.modelIndex
    def selectModelByName(self, name:str) -> int:
        if name is not None:
            for index, item in enumerate(self.jsonData['items']):
                if item['name'] == name:
                    self.modelIndex = index
            # print(f'{name} - {self.modelIndex}')
        return self.modelIndex
    def isNsfwModel(self) -> bool:
        return self.jsonData['items'][self.modelIndex]['nsfw']
    def treatAsNsfw(self, modelIndex=None, versionIndex=None):
        modelIndex = self.modelIndex if modelIndex is None else modelIndex
        modelIndex = 0 if modelIndex is None else modelIndex
        versionIndex = self.versionIndex if versionIndex is None else versionIndex
        versionIndex = 0 if versionIndex is None else versionIndex
        ret = self.jsonData['items'][modelIndex]['nsfw']
        if opts.civsfz_treat_x_as_nsfw:
            try:
                picNsfw = self.jsonData['items'][modelIndex]['modelVersions'][versionIndex]['images'][0]['nsfw']
            except Exception as e:
                # print_ly(f'{e}')
                pass
            else:
                # print_lc(f'{picNsfw}')
                if picNsfw == 'X':
                    ret = True
        return ret
    def getIndexByModelName(self, name:str) -> int:
        retIndex = None
        if name is not None:
            for index, item in enumerate(self.jsonData['items']):
                if item['name'] == name:
                    retIndex = index
        return retIndex
    def getSelectedModelIndex(self) -> int:
        return self.modelIndex
    def getSelectedModelName(self) -> str:
        item = self.jsonData['items'][self.modelIndex]
        return item['name']
    def getSelectedModelID(self) -> str:
        item = self.jsonData['items'][self.modelIndex]
        return int(item['id'])
    def getSelectedModelType(self) -> str:
        item = self.jsonData['items'][self.modelIndex]
        return item['type']
    def getModelTypeByIndex(self, index:int) -> str:
        item = self.jsonData['items'][index]
        return item['type'] 
    def allows2permissions(self) -> dict:
        '''Convert allows to permissions. Select model first.
            [->Reference](https://github.com/civitai/civitai/blob/main/src/components/PermissionIndicator/PermissionIndicator.tsx#L15)'''
        permissions = {}
        if self.modelIndex is None:
            print_ly('Select item first.')
        else:
            if self.modelIndex is not None:
                canSellImagesPermissions = {
                    'Image', 'Rent', 'RentCivit', 'Sell'}
                canRentCivitPermissions = {'RentCivit', 'Rent', 'Sell'}
                canRentPermissions = {'Rent', 'Sell'}
                canSellPermissions = {'Sell'}

                item = self.jsonData['items'][self.modelIndex]
                allowCommercialUse = set(item['allowCommercialUse'])
                allowNoCredit = item['allowNoCredit']
                allowDerivatives = item['allowDerivatives']
                allowDifferentLicense = item['allowDifferentLicense']

                canSellImages = len(allowCommercialUse & canSellImagesPermissions) > 0 
                canRentCivit = len(allowCommercialUse & canRentCivitPermissions) > 0
                canRent = len(allowCommercialUse & canRentPermissions) > 0
                canSell = len(allowCommercialUse & canSellPermissions) > 0
                
                permissions['allowNoCredit'] = allowNoCredit
                permissions['canSellImages'] = canSellImages
                permissions['canRentCivit'] = canRentCivit
                permissions['canRent'] = canRent
                permissions['canSell'] = canSell
                permissions['allowDerivatives'] = allowDerivatives
                permissions['allowDifferentLicense'] = allowDifferentLicense
        return permissions
    def getModelVersionsList(self) -> list:
        '''Return modelVersions list. Select item before.'''
        versionNames = []
        if self.modelIndex is None:
            print_ly('Select item first.')
        else:
            item = self.jsonData['items'][self.modelIndex]
            versionNames = [ (version['name'],i) for i,version in enumerate(item['modelVersions'])]
                #versionNames[version['name']] = version["name"]
        return versionNames

    # Version
    def selectVersionByIndex(self, index:int) -> int:
        numVersions = len(self.jsonData['items'][self.modelIndex]['modelVersions'])
        index = 0 if index < 0 else index
        index = numVersions -1 if index > numVersions-1 else index
        self.versionIndex = index
        return self.versionIndex
    def selectVersionByID(self, ID:int) -> int:
        item = self.jsonData['items'][self.modelIndex]
        for index, model in enumerate(item['modelVersions']):
            if int(model['id']) == int(ID):
                self.versionIndex = index
        return self.versionIndex
    def selectVersionByName(self, name:str) -> int:
        '''Select model version by name. Select model first.
        
        Args:
            ID (int): version ID
        Returns:
            int: index number of the version
        '''
        if name is not None:
            item = self.jsonData['items'][self.modelIndex]
            for index, model in enumerate(item['modelVersions']):
                if model['name'] == name:
                    self.versionIndex = index
        return self.versionIndex
    def getSelectedVersionName(self):
        return self.jsonData['items'][self.modelIndex]['modelVersions'][self.versionIndex]['name']
    def getSelectedVersionBaseModel(self):
        # print(f"{self.jsonData['items'][self.modelIndex]['modelVersions']}")
        return self.jsonData['items'][self.modelIndex]['modelVersions'][self.versionIndex]['baseModel']
    def getSelectedVersionEarlyAccessTimeFrame(self):
        return self.jsonData['items'][self.modelIndex]['modelVersions'][self.versionIndex]['earlyAccessTimeFrame']
    def setModelVersionInfo(self, modelInfo:str):
        self.modelVersionInfo = modelInfo
    def getModelVersionInfo(self) -> str:
        return self.modelVersionInfo
    def getVersionDict(self) -> dict:
        version_dict = {}
        item = self.jsonData['items'][self.modelIndex]
        version_dict = item['modelVersions'][self.versionIndex]
        return version_dict

    def getCreatedDatetime(self) -> datetime.datetime :
        item = self.jsonData['items'][self.modelIndex]
        version_dict = item['modelVersions'][self.versionIndex]
        strCreatedAt = version_dict['createdAt'].replace('Z', '+00:00') # < Python 3.11
        dtCreatedAt = datetime.datetime.fromisoformat(strCreatedAt)
        # print_lc(f'{dtCreatedAt} {dtCreatedAt.tzinfo}')
        return dtCreatedAt
    def getUpdatedDatetime(self) -> datetime.datetime:
        item = self.jsonData['items'][self.modelIndex]
        version_dict = item['modelVersions'][self.versionIndex]
        strUpdatedAt = version_dict['updatedAt'].replace(
            'Z', '+00:00')  # < Python 3.11
        dtUpdatedAt = datetime.datetime.fromisoformat(strUpdatedAt)
        # print_lc(f'{dtUpdatedAt} {dtUpdatedAt.tzinfo}')
        return dtUpdatedAt
    def getPublishedDatetime(self) -> datetime.datetime:
        item = self.jsonData['items'][self.modelIndex]
        version_dict = item['modelVersions'][self.versionIndex]
        strPublishedAt = version_dict['publishedAt'].replace(
            'Z', '+00:00')  # < Python 3.11
        dtPublishedAt = datetime.datetime.fromisoformat(strPublishedAt)
        # print_lc(f'{dtPublishedAt} {dtPublishedAt.tzinfo}')
        return dtPublishedAt

    def makeModelInfo2(self, modelIndex=None, versionIndex=None) -> dict:
        """make selected version info"""
        modelIndex = self.modelIndex if modelIndex is None else modelIndex
        versionIndex = self.versionIndex if versionIndex is None else versionIndex
        item = self.jsonData["items"][modelIndex]
        version = item["modelVersions"][versionIndex]
        modelInfo = {"infoVersion": "2.0"}
        for key, value in item.items():
            if key not in ("modelVersions"):
                modelInfo[key] = value
        modelInfo["allow"] = {}
        modelInfo["allow"]["allowNoCredit"] = item["allowNoCredit"]
        modelInfo["allow"]["allowCommercialUse"] = item["allowCommercialUse"]
        modelInfo["allow"]["allowDerivatives"] = item["allowDerivatives"]
        modelInfo["allow"]["allowDifferentLicense"] = item["allowDifferentLicense"]
        modelInfo["modelVersions"] = [version]
        modelInfo["modelVersions"][0]["files"] = version["files"]
        modelInfo["modelVersions"][0]["images"] = version["images"]
        # add version info
        modelInfo['versionId'] = version['id']
        modelInfo['versionName'] = version['name']
        modelInfo['createdAt'] = version['createdAt']
        modelInfo['updatedAt'] = version['updatedAt']
        modelInfo['publishedAt'] = version['publishedAt']
        modelInfo['trainedWords'] = version['trainedWords']
        modelInfo['baseModel'] = version['baseModel']
        modelInfo['versionDescription'] = version['description']
        modelInfo["downloadUrl"] = (
            version["downloadUrl"] if "downloadUrl" in version else None
        )
        versionRes = self.requestVersionByVersionID(version["id"])
        if versionRes is not None:
            for i, img in enumerate(versionRes["images"]):
                modelInfo["modelVersions"][0]["images"][i]["meta"] = img['meta']
        html = self.modelInfoHtml(modelInfo)
        modelInfo["html"] = html
        self.setModelVersionInfo(modelInfo)
        return modelInfo

    def getUrlByName(self, model_filename=None):
        if self.modelIndex is None:
            # print(Fore.LIGHTYELLOW_EX + f'getUrlByName: Select model first. {model_filename}' + Style.RESET_ALL )
            return
        if self.versionIndex is None:
            # print(Fore.LIGHTYELLOW_EX + f'getUrlByName: Select version first. {model_filename}' + Style.RESET_ALL )
            return
        # print(Fore.LIGHTYELLOW_EX + f'File name . {model_filename}' + Style.RESET_ALL )
        item = self.jsonData['items'][self.modelIndex]
        version = item['modelVersions'][self.versionIndex]
        dl_url = None
        for file in version['files']:
            if file['name'] == model_filename:
                dl_url = file['downloadUrl']
        return dl_url
    def getHashByName(self, model_filename=None):
        if self.modelIndex is None:
            # print(Fore.LIGHTYELLOW_EX + f'getUrlByName: Select model first. {model_filename}' + Style.RESET_ALL )
            return
        if self.versionIndex is None:
            # print(Fore.LIGHTYELLOW_EX + f'getUrlByName: Select version first. {model_filename}' + Style.RESET_ALL )
            return
        # print(Fore.LIGHTYELLOW_EX + f'File name . {model_filename}' + Style.RESET_ALL )
        item = self.jsonData['items'][self.modelIndex]
        version = item['modelVersions'][self.versionIndex]
        sha256 = ""
        for file in version['files']:
            # print_lc(f'{file["hashes"]=}')
            if file['name'] == model_filename and 'SHA256' in file['hashes']:
                sha256 = file['hashes']['SHA256']
        return sha256

    # Pages
    def getCurrentPage(self) -> str:
        return f"{self.jsonData['metadata']['currentPage']}"
    def getTotalPages(self) -> str:
        return f"{self.jsonData['metadata']['totalPages']}"
    def getPages(self) -> str:
        return f"{self.getCurrentPage()}/{self.getTotalPages()}"
    def nextPage(self) -> str:
        return self.jsonData['metadata']['nextPage'] if 'nextPage' in self.jsonData['metadata'] else None
    def prevPage(self) -> str:
        return self.jsonData['metadata']['prevPage'] if 'prevPage' in self.jsonData['metadata'] else None

    # HTML
    # Make model cards html
    def modelCardsHtml(self, models, jsID=0):
        '''Generate HTML of model cards.'''
        cards = []
        for model in models:
            index = model[1]
            item = self.jsonData['items'][model[1]]
            base_model = ""
            param = {
                'name':     item['name'],
                'index':    index,
                'jsId':     jsID,
                'id':       item['id'],
                'isNsfw':   False,
                'type':     item['type'],
                'have':     "",
                'ea':       "",
                'imgType':  ""
                }
            if any(item['modelVersions']):
                if len(item['modelVersions'][0]['images']) > 0:
                    img  = item['modelVersions'][0]['images'][0]
                    param['imgType'] = img['type']
                    param['imgsrc'] = img["url"]
                    if img['nsfw'] != "None" and not self.isShowNsfw():
                        param['isNsfw'] = True
                base_model = item["modelVersions"][0]['baseModel']
                param['baseModel'] = base_model
                    
                folder = generate_model_save_path(self.getModelTypeByIndex(
                    index), item["name"], base_model, self.treatAsNsfw(modelIndex=index))  # item['nsfw'])
                for i,ver in enumerate(item['modelVersions']):
                    for file in ver['files']:
                        file_name = file['name']
                        path_file = folder / Path(file_name)
                        if path_file.exists():
                            if i == 0:
                                param['have'] = 'new'
                                break
                            else:
                                param['have'] = 'old'
                                break
                    if param['have'] != "":
                        break
                ea = item["modelVersions"][0]['earlyAccessTimeFrame']
                if ea > 0:
                    strPub = item["modelVersions"][0]['publishedAt'].replace('Z', '+00:00')  # < Python 3.11
                    dtPub = datetime.datetime.fromisoformat(strPub)
                    dtNow = datetime.datetime.now(datetime.timezone.utc)
                    dtDiff = dtNow - dtPub
                    if ea <= int(dtDiff.days):
                        param['ea'] = 'out'
                    else:
                        param['ea'] = 'in'
            cards.append(param)
            
        forTrigger = f'<!-- {datetime.datetime.now()} -->'  # for trigger event
        template = environment.get_template("cardlist.jinja")
        content = template.render(forTrigger=forTrigger, cards=cards)
        return content

    def meta2html(self, meta:dict) -> str:
        # convert key name as infotext
        renameKey = {
            'prompt':'Prompt',
            'negativePrompt': 'Negative prompt',
            'steps': 'Steps',
            'seed': 'Seed',
            'sampler': 'Sampler',
            'cfgScale': 'CFG scale',
            'clipSkip': 'Clip skip'
                }
        infotext = {renameKey.get(key, key): value for key, value in meta.items()} if meta is not None else None
        template = environment.get_template("infotext.jinja")
        content = template.render({'infotext': infotext})
        return content

    def modelInfoHtml(self, modelInfo:dict) -> str:
        '''Generate HTML of model info'''
        samples = ""
        for pic in modelInfo["modelVersions"][0]["images"]:
            nsfw = pic['nsfw'] != "None" and not self.showNsfw
            infotext = self.meta2html(pic['meta']) if pic['meta'] is not None else ""
            template = environment.get_template("sampleImage.jinja")
            samples += template.render(
                pic=pic,
                nsfw=nsfw,
                infotext=infotext
                )

        created = self.getCreatedDatetime().astimezone(
            tz.tzlocal()).replace(microsecond=0).isoformat()
        published = self.getPublishedDatetime().astimezone(
            tz.tzlocal()).replace(microsecond=0).isoformat()
        updated = self.getUpdatedDatetime().astimezone(
            tz.tzlocal()).replace(microsecond=0).isoformat()
        template = environment.get_template("modelbasicinfo.jinja")
        basicInfo = template.render(
            modelInfo=modelInfo, created=created, published=published, updated=updated)
        
        permissions = self.permissionsHtml(self.allows2permissions())
        # function:copy to clipboard
        js = ('<script>''function civsfz_copyInnerText(node) {'
            'if (node.nextSibling != null) {'
              'return navigator.clipboard.writeText(node.nextElementSibling.innerText).then('
			'function () {'
				'alert("Copied infotext");'
			'}).catch('
			    'function (error) {'
				'alert((error && error.message) || "Failed to copy infotext");'
			'})} }'
            '</script>')
        template = environment.get_template("modelInfo.jinja")
        content = template.render(
            modelInfo=modelInfo, basicInfo=basicInfo, permissions=permissions,
            samples=samples, js=js)
            
        return content

    def permissionsHtml(self, premissions:dict, msgType:int=3) -> str:
        template = environment.get_template("permissions.jinja")
        content = template.render(premissions)
        return content

    # REST API
    def makeRequestQuery(self, content_type, sort_type, period, use_search_term, search_term=None, base_models=None):
        if use_search_term == "Model ID" or use_search_term == "Version ID":
            if not search_term.isdecimal():
                query = ""
                print_ly(f'"{search_term}" is not a numerical value')
            else:
                query = str.strip(search_term)
        else:
            query = {'types': content_type, 'sort': sort_type, 'limit': opts.civsfz_number_of_cards }
            if not period == "AllTime":
                query |= {'period': period}   
            if use_search_term != "No" and search_term:
                # search_term = search_term.replace(" ","%20")
                if use_search_term == "User name":
                    query |= {'username': search_term }
                elif use_search_term == "Tag":
                    query |= {'tag': search_term }
                else:
                    query |= {'query': search_term }
            if base_models:
                query |= {'baseModels': base_models }
        return query

    def updateQuery(self, url:str , addQuery:dict) -> str:
        parse = urllib.parse.urlparse(url)
        strQuery = parse.query
        dictQuery = urllib.parse.parse_qs(strQuery)
        query = dictQuery | addQuery
        newURL = parse._replace(query=urllib.parse.urlencode(query,  doseq=True, quote_via=urllib.parse.quote))
        return urllib.parse.urlunparse(newURL)

    def requestApi(self, url=None, query=None):
        self.requestError = None
        if url is None:
            url = self.getModelsApiUrl()
        if query is not None:
            query = urllib.parse.urlencode(query, doseq=True, quote_via=urllib.parse.quote)
        # print_lc(f'{query=}')

        # Make a GET request to the API
        try:
            with requests.Session() as request:
                response = request.get( url, params=query, timeout=(10,15))
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # print(Fore.LIGHTYELLOW_EX + "Request error: " , e)
            # print(Style.RESET_ALL)
            print_ly(f"Request error: {e}")
            # print(f"{response=}")
            data = self.jsonData # No update data
            self.requestError = e
        else:
            response.encoding  = "utf-8" # response.apparent_encoding
            data = json.loads(response.text)
        # Check the status code of the response
        # if response.status_code != 200:
        #  print("Request failed with status code: {}".format(response.status_code))
        #  exit()
        return data

    def requestImagesByVersionId(self, versionId=None, limit=None):
        if versionId == None:
            return None
        params = {"modelVersionId": versionId,
                  "sort": "Oldest"}
        if limit is not None:
            params |= {"limit": limit}
        return self.requestApi(self.getImagesApiUrl(), params)
    def requestVersionByVersionID(self, versionID=None):
        if versionID == None:
            return None
        url = self.getVersionsApiUrl(versionID)
        return self.requestApi(url)
    def requestApiOptions(self, url=None, query=None):
        self.requestError = None
        if url is None:
            url = self.getModelsApiUrl()
        if query is not None:
            query = urllib.parse.urlencode(
                query, doseq=True, quote_via=urllib.parse.quote)
        # print_lc(f'{query=}')

        # Make a GET request to the API
        try:
            with requests.Session() as request:
                response = request.get(url, params=query, timeout=(10, 15))
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # print(f"{response=}")
            response.encoding = "utf-8"
            data = json.loads(response.text)
        else:
            data = ""
        # Check the status code of the response
        # if response.status_code != 200:
        #  print("Request failed with status code: {}".format(response.status_code))
        #  exit()
        return data

    def getOptions(self):
        '''Get choices from Civitai'''
        global typeOptions, sortOptions, basemodelOptions, periodOptions
        url = self.getModelsApiUrl()
        query = { 'types': ""}
        data = self.requestApiOptions(url, query)
        try:
            types = data[0]['unionErrors'][0]['issues'][0]['options']
        except KeyError:
            typeOptions = [
                "Checkpoint",
                "TextualInversion",
                "LORA",
                "LoCon",
                "Hypernetwork",
                "AestheticGradient",
                "Controlnet",
                "Upscaler",
                "MotionModule",
                "VAE",
                "Poses",
                "Wildcards",
                "Workflows",
                "Other"
            ]
        else:
            print_lc(f'Set types')
            priorityTypes = [
                "Checkpoint",
                "TextualInversion",
                "LORA",
                "LoCon"
            ]
            dictPriority = {
                priorityTypes[i]: priorityTypes[i] for i in range(0, len(priorityTypes))}
            dict_types = dictPriority | {types[i]: types[i]
                                         for i in range(0, len(types))}
            typeOptions = [dictPriority.get(
                key, key) for key, value in dict_types.items()]

        query = {'baseModels': ""}
        data = self.requestApiOptions(url, query)
        try:
            basemodelOptions = data[0]['unionErrors'][0]['issues'][0]['options']
        except KeyError:
            basemodelOptions = [
                "SD 1.4",
                "SD 1.5",
                "SD 1.5 LCM",
                "SD 2.0",
                "SD 2.0 768",
                "SD 2.1",
                "SD 2.1 768",
                "SD 2.1 Unclip",
                "SDXL 0.9",
                "SDXL 1.0",
                "Pony",
                "SDXL 1.0 LCM",
                "SDXL Distilled",
                "SDXL Turbo",
                "SDXL Lightning",
                "Stable Cascade",
                "SVD",
                "SVD XT",
                "Playground v2",
                "PixArt a",
                "Other"
            ]
        else:
            print_lc(f'Set base models')
        query = {'sort': ""}
        data = self.requestApiOptions(url, query)
        try:
            sortOptions = data[0]['options']
        except KeyError:
            sortOptions = [
                "Highest Rated",
                "Most Downloaded",
                "Most Liked",
                "Most Buzz",
                "Most Discussed",
                "Most Collected",
                "Most Images",
                "Newest"
            ]
        else:
            print_lc(f'Set sorts')
        query = {'period': ""}
        data = self.requestApiOptions(url, query)
        try:
            periodOptions = data[0]['options']
        except KeyError:
            periodOptions = [
                "Day",
                "Week",
                "Month",
                "Year",
                "AllTime"
            ]
        else:
            print_lc(f'Set periods')
