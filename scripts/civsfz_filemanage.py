import os
import gradio as gr
import time
import threading
import requests
import urllib.parse
import shutil
import json
import re
from pathlib import Path
import platform
import subprocess as sp
from collections import deque
from modules import shared, sd_models
from colorama import Fore, Back, Style
from requests.exceptions import ConnectionError
from tqdm import tqdm
from modules.shared import opts, cmd_opts
from modules.paths import models_path
from modules.hashes import calculate_sha256
try:
    from send2trash import send2trash
    send2trash_installed = True
except ImportError:
    print("Recycle bin cannot be used.")
    send2trash_installed = False

print_ly = lambda  x: print(Fore.LIGHTYELLOW_EX + "CivBrowser: " + x + Style.RESET_ALL )
print_lc = lambda  x: print(Fore.LIGHTCYAN_EX + "CivBrowser: " + x + Style.RESET_ALL )
print_n = lambda  x: print("CivBrowser: " + x )

isDownloading = False
ckpt_dir = shared.cmd_opts.ckpt_dir or sd_models.model_path
pre_opt_folder = None

def extensionFolder() -> Path:
    return Path(__file__).parent

def escaped_filename(model_name):
    MAX_LENGTH = 254
    escapechars = str.maketrans({   " ": r"_",
                                    "(": r"",
                                    ")": r"",
                                    "|": r"",
                                    ":": r"",
                                    ",": r"_",
                                    "<": r"",
                                    ">": r"",
                                    "!": r"",
                                    "?": r"",
                                    ".": r"_",
                                    "&": r"_and_",
                                    "*": r"_",
                                    "\"": r"",
                                    "\\": r"",
                                    "/": r"/" if opts.civsfz_treat_slash_as_folder_separator else r"_"
                                })
    new_name = model_name.translate(escapechars)
    if len(new_name) > MAX_LENGTH:
        new_name = re.sub('_+', '_', new_name)
        if len(new_name) > MAX_LENGTH:
            new_name = new_name[0:MAX_LENGTH-1]

    return new_name

def type_path(type: str) -> Path:
    global pre_opt_folder, ckpt_dir
    if opts.civsfz_save_type_folders != "":
        try:
            folderSetting = json.loads(opts.civsfz_save_type_folders)
        except json.JSONDecodeError as e:
            if pre_opt_folder != opts.civsfz_save_type_folders:
                print_ly(f'Check subfolder setting: {e}')
            folderSetting = {}
    else:
        folderSetting = {}       
    pre_opt_folder = opts.civsfz_save_type_folders
        
    if type == "Checkpoint":
        base = ckpt_dir
        folder = ckpt_dir
    elif type == "Hypernetwork":
        base = cmd_opts.hypernetwork_dir
        folder = base
    elif type == "TextualInversion":
        base = cmd_opts.embeddings_dir
        folder = base
    elif type == "AestheticGradient":
        base = "extensions/stable-diffusion-webui-aesthetic-gradients/aesthetic_embeddings"
        folder = base
    elif type == "LORA":
        base = cmd_opts.lora_dir  # "models/Lora"
        folder = base
    elif type == "LoCon":
        if "lyco_dir" in cmd_opts:
            base = f"{cmd_opts.lyco_dir}"
        elif "lyco_dir_backcompat" in cmd_opts:  # A1111 V1.5.1
            base = f"{cmd_opts.lyco_dir_backcompat}"
        else:
            base = os.path.join(models_path, "LyCORIS")
        folder = base
    elif type == "VAE":
        if cmd_opts.vae_dir:
            base = cmd_opts.vae_dir  # "models/VAE"
        else:
            base = os.path.join(models_path, "VAE")
        folder = base
    elif type == "Controlnet":
        base = models_path
        folder = os.path.join(models_path, "ControlNet")
    elif type == "Poses":
        base = models_path
        folder = os.path.join(models_path, "OtherModels/Poses")
    elif type == "Upscaler":
        base = models_path
        folder = os.path.join(models_path, "OtherModels/Upscaler")
    elif type == "MotionModule":
        base = models_path
        folder = os.path.join(models_path, "OtherModels/MotionModule")
    elif type == "Wildcards":
        base = models_path
        folder = os.path.join(models_path, "OtherModels/Wildcards")
    elif type == "Workflows":
        base = models_path
        folder = os.path.join(models_path, "OtherModels/Workflows")
    elif type == "Other":
        base = models_path
        folder = os.path.join(models_path, "OtherModels/Other")

    optFolder = folderSetting.get(type, "")
    if optFolder == "":
        pType = Path(folder)
    else:
        pType = Path(base) / Path(optFolder)
    return pType

def basemodel_path(baseModel: str) -> Path:
    basemodelPath = ""
    if not 'SD 1' in baseModel:
        basemodelPath = '_' + baseModel.replace(' ', '_').replace('.', '_')
    return Path(basemodelPath)

def basemodel_path_all(baseModel: str) -> Path:
    basemodelPath = baseModel.replace(' ', '_').replace('.', '_')
    return Path(basemodelPath)

def generate_model_save_path(type, modelName:str = "",baseModel:str="", nsfw:bool=False) -> Path:
    typePath = type_path(type)
    basemodelPath = basemodel_path(baseModel)
    modelPath = typePath / basemodelPath
    if nsfw:
        modelPath = typePath / basemodelPath / Path('.nsfw')
    filename = escaped_filename(modelName)
    modelPath = modelPath / Path(filename)
    return modelPath


def generate_model_save_path2(type, modelName: str = "", baseModel: str = "", nsfw: bool = False, userName=None, mID=None, vID=None, versionName=None) -> Path:
    # TYPE, MODELNAME, BASEMODEL, NSFW, UPNAME, MODEL_ID, VERSION_ID
    subfolders = {
        # "TYPE": type_path(type).as_posix(),
        "BASEMODELbkCmpt": basemodel_path(baseModel).as_posix(),
        "BASEMODEL": basemodel_path_all(baseModel).as_posix(),
        "NSFW": "nsfw" if nsfw else None,
        "USERNAME": escaped_filename(userName) if userName is not None else None,
        "MODELNAME": escaped_filename(modelName),
        "MODELID": str(mID) if mID is not None else None,
        "VERSIONNAME": escaped_filename(versionName),
        "VERSIONID": str(vID) if vID is not None else None,
    }
    if not str.strip(opts.civsfz_save_subfolder):
        subTree = "{{BASEMODELbkCmpt}}/.{{NSFW}}/{{MODELNAME}}"
    else:
        subTree = str.strip(opts.civsfz_save_subfolder)
    subTreeList = subTree.split("/")
    newTreeList = []
    for i, sub in enumerate(subTreeList):
        if sub:
            subKeys = re.findall("(\{\{(.+?)\}\})", sub)
            newSub = ""
            replaceSub = sub
            for subKey in subKeys:
                if subKey[1] is not None:
                    if subKey[1] in subfolders:
                        folder = subfolders[subKey[1]]
                        if folder is not None:
                            replaceSub = re.sub(
                                "\{\{" + subKey[1] + "\}\}", folder, replaceSub)
                        else:
                            replaceSub = re.sub(
                                "\{\{" + subKey[1] + "\}\}", "", replaceSub)
                    else:
                        print_ly(f'"{subKey[1]}" is not defined')
                        replaceSub = "ERROR"
            newSub += replaceSub if replaceSub is not None else ""

            if newSub != "":
                newTreeList.append(newSub)
        else:
            if i != 0:
                print_lc(f"Empty subfolder:{i}")
    modelPath = type_path(type).joinpath(
        "/".join(newTreeList))
    return modelPath

def save_text_file(folder, filename, trained_words):
    makedirs(folder)
    filepath = os.path.join(folder, filename.replace(".ckpt",".txt")\
                                        .replace(".safetensors",".txt")\
                                        .replace(".pt",".txt")\
                                        .replace(".yaml",".txt")\
                                        .replace(".zip",".txt")\
                        )
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='UTF-8') as f:
            f.write(trained_words)
    print_n('Save text.')
    return "Save text"

def makedirs(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        print_lc(f'Make folder: {folder}')

def isExistFile(folder, file):
    isExist = False
    if folder != "" and folder is not None:
        path = os.path.join(folder, file)
        isExist = os.path.exists(path)
    return isExist


def saveImageFiles(folder, versionName, html, content_type, versionInfo):
    html = versionInfo['html0']
    makedirs(folder)
    img_urls = re.findall(r'src=[\'"]?([^\'" >]+)', html)
    basename = os.path.splitext(versionName)[0]  # remove extension
    preview_url = versionInfo["modelVersions"][0]["images"][0]["url"]
    preview_url = urllib.parse.quote(preview_url,  safe=':/=')
    if 'images' in versionInfo:
        for img in versionInfo['images']:
            if img['type'] == 'image':
                preview_url = img['url']
                preview_url = urllib.parse.quote(preview_url,  safe=':/=')
                break
    with requests.Session() as session:
        HTML = html
        for i, img_url in enumerate(img_urls):
            isVideo = False
            for img in versionInfo["modelVersions"][0]["images"]:
                if img['url'] == img_url:
                    if img['type'] == 'video':
                        isVideo = True
            # print(Fore.LIGHTYELLOW_EX + f'URL: {img_url}'+ Style.RESET_ALL)
            if isVideo:
                if content_type == "TextualInversion":
                    filename = f'{basename}_{i}.preview.webm'
                    filenamethumb = f'{basename}.preview.webm'
                else:
                    filename = f'{basename}_{i}.webm'
                    filenamethumb = f'{basename}.webm'
            else:
                if content_type == "TextualInversion":
                    filename = f'{basename}_{i}.preview.png'
                    filenamethumb = f'{basename}.preview.png'
                else:
                    filename = f'{basename}_{i}.png'
                    filenamethumb = f'{basename}.png'

            HTML = HTML.replace(img_url, f'"{filename}"')
            url_parse = urllib.parse.urlparse(img_url)
            if url_parse.scheme:
                # img_url.replace("https", "http").replace("=","%3D")
                img_url = urllib.parse.quote(img_url,  safe=':/=')
                try:
                    response =  session.get(img_url, timeout=5)
                    with open(os.path.join(folder, filename), 'wb') as f:
                        f.write(response.content)
                        if img_url == preview_url:
                            shutil.copy2(os.path.join(folder, filename),
                                        os.path.join(folder, filenamethumb))
                        print_n(f"Save {filename}")
                    # with urllib.request.urlretrieve(img_url, os.path.join(model_folder, filename)) as dl:
                except requests.exceptions.Timeout as e:
                    print_ly(f'Error: {e.reason}')
                    print_ly(f'URL: {img_url}')
                    # return "Err: Save infos"
                except requests.exceptions.RequestException as e:
                    print_ly(f'Error: {e.reason}')
                    print_ly(f'URL: {img_url}')
    filepath = os.path.join(folder, f'{basename}.html')
    with open(filepath, 'wb') as f:
        f.write(HTML.encode('utf8'))
        print_n(f"Save {basename}.html")
    # Save json_info
    filepath = os.path.join(folder, f'{basename}.civitai.json')
    with open(filepath, mode="w", encoding="utf-8") as f:
        json.dump(versionInfo, f, indent=2, ensure_ascii=False)
        print_n(f"Save {basename}.civitai.json")
    return "Save infos"

# def download_file_thread(url, file_name, content_type, model_name,base_model, nsfw:bool=False):
def download_file_thread(folder, filename,  url):
    global isDownloading
    if isDownloading:
        isDownloading = False
        return
    isDownloading = True
    makedirs(folder)
    filepath = os.path.join(folder, filename)
    thread = threading.Thread(target=download_file, args=(url, filepath))
    # Start the thread
    thread.start()
    #download_file(url,filepath)

def download_file(folder, filename,  url, hash, api_key, early_access):
    makedirs(folder)
    file_name = os.path.join(folder, filename)
    #thread = threading.Thread(target=download_file, args=(url, filepath))

    # Maximum number of retries
    max_retries = 3

    # Delay between retries (in seconds)
    retry_delay = 3

    exitGenerator=False
    while not exitGenerator:
        # Check if the file has already been partially downloaded
        downloaded_size = 0
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
            }
        if early_access:
            print_lc("Early Access model")
            if len(api_key) == 32:
                headers.update({"Authorization": f"Bearer {api_key}"})
                print_lc("Apply API key")
        mode = "wb" #Open file mode
        if os.path.exists(file_name):
            yield "Overwrite?"
            #if not overWrite:
            #    print_n(f"Continue: {file_name}")
            #    mode = "ab"
            #    # Get the size of the downloaded file
            #    downloaded_size = os.path.getsize(file_name)
            #    # Set the range of the request to start from the current size of the downloaded file
            #    headers = {"Range": f"bytes={downloaded_size}-"}

        # Split filename from included path
        tokens = re.split(re.escape('\\'), file_name)
        file_name_display = tokens[-1]

        # Initialize the progress bar
        try:
            yield "Connecting..."
        except Exception as e:
            exitGenerator=True
            return
        # Open a local file to save the download

        while not exitGenerator:
        # Send a GET request to the URL and save the response to the local file
            try:
                with requests.Session() as session:
                    #session.headers['Connection'] = 'close'
                    #session.headers['Connection'] = 'keep-alive'
                    #session.headers.update(headers)
                    #headers.update({'Cache-Control': 'no-cache'})
                    response = session.get(url, headers=headers, stream=True, timeout=(10, 10))  # Get the total size of the file
                    response.raise_for_status()
                    #print_lc(f"{response.headers=}")
                    if 'Content-Length' in response.headers:
                        total_size = int(response.headers.get("Content-Length", 0))
                        # Update the total size of the progress bar if the `Content-Length` header is present
                        if total_size == 0:
                            total_size = downloaded_size
                        with tqdm(total=1000000000, unit="B", unit_scale=True, desc=f"Downloading {file_name_display}", initial=downloaded_size, leave=True) as progressConsole:
                            prg = 0 #downloaded_size
                            progressConsole.total = total_size
                            with open(file_name, mode) as file:
                                for chunk in response.iter_content(chunk_size=4*1024*1024):
                                    if chunk:  # filter out keep-alive new chunks
                                        file.write(chunk)
                                        progressConsole.update(len(chunk))
                                        prg += len(chunk)
                                        try:
                                            yield f'{round(prg/1048576)}MB / {round(total_size/1048576)}MB'
                                        except Exception as e:
                                            response.close()
                                            exitGenerator=True
                                            progressConsole.close()
                                            break
                        downloaded_size = os.path.getsize(file_name)
                        # Break out of the loop if the download is successful
                        break
                    else:
                        if early_access:
                            print_ly(
                                "Download canceled. Early Access!")
                            yield "Early Access!"
                            exitGenerator=True
                            return
                        else:
                            print_lc("May need API key")
                            yield "May need API key"
                            if len(api_key) == 32:
                                headers.update({"Authorization": f"Bearer {api_key}"})
                                print_lc("Apply API key")
                                yield "Apply API key"
                            else:
                                exitGenerator=True
                                return

            except requests.exceptions.Timeout as e:
                print_ly(f"{e}")
                exitGenerator = True
                yield "Timeout Error"
            except ConnectionError as e:
                print_ly(f"{e}")
                exitGenerator = True
                yield "Connection Error"
            except requests.exceptions.RequestException as e:
                print_ly(f"{e}")
                exitGenerator=True
                yield "Request Error"
            except Exception as e:
                print_ly(e)
                exitGenerator=True
                return
            # Decrement the number of retries
            max_retries -= 1
            # If there are no more retries, raise the exception
            if max_retries == 0:
                exitGenerator = True
                yield "Retry limit"
                return
            # Wait for the specified delay before retrying
            print_lc(f"Retry wait {retry_delay}s")
            yield f"Retry wait {retry_delay}s"
            time.sleep(retry_delay)

        downloaded_size = os.path.getsize(file_name)
        # Check if the download was successful
        sha256 = calculate_sha256(file_name).upper()
        #print_lc(f'Model file hash : {hash}')
        if hash != "":
            if sha256[:len(hash)] == hash.upper():
                print_n(f"Save: {file_name_display}")
                gr.Info(f"Success: {file_name_display}")
                yield 'Downloaded'
                exitGenerator=True
                return
            else:
                print_ly(f"Error: File download failed. {file_name_display}")
                print_lc(f'Model file hash : {hash}')
                print_lc(f'Downloaded hash : {sha256}')
                gr.Warning(f"Hash mismatch: {file_name_display}")
                exitGenerator = True
                removeFile(file_name)
                yield 'Failed.'
                return
        else:
                print_n(f"Save: {file_name_display}")
                print_ly("No hash value provided. Unable to confirm file.")
                gr.Info(f"No hash: {file_name_display}")
                yield 'Downloaded. No hash.'
                exitGenerator=True
                return

def removeFile(file):
    if send2trash_installed:
        send2trash(file.replace('/','\\'))
        print_lc('Move file to trash')
    else:
        print_lc('File is not deleted. send2trash module is missing.')
    return

def open_folder(f):
    '''
    [reference](https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/5ef669de080814067961f28357256e8fe27544f4/modules/ui_common.py#L109)
    '''
    if not f:
        return
    count = 0
    while not os.path.isdir(f):
        count += 1
        print_lc(f'Not found "{f}"')
        newf = os.path.abspath(os.path.join(f, os.pardir))
        if newf == f:
            break
        if count >5:
            print_lc(f'Not found the folder')
            return
        f = newf
    path = os.path.normpath(f)
    if os.path.isdir(path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            sp.Popen(["open", path])
        elif "microsoft-standard-WSL2" in platform.uname().release:
            sp.Popen(["wsl-open", path])
        else:
            sp.Popen(["xdg-open", path])
    else:
        print_lc(f'Not found "{path}"')

class History():
    def __init__(self, path=None):
        self._path = Path.joinpath(
            extensionFolder(), Path("../history.json"))
        if path != None:
            self._path = path
        self._history: deque = self.load()
    def load(self) -> dict:
        try:
            with open(self._path, 'r', encoding="utf-8") as f:
                ret = json.load(f)
        except:
            ret = []
        return deque(ret,maxlen=20)
    def save(self):
        try:
            with open(self._path, 'w', encoding="utf-8") as f:
                json.dump(list(self._history), f, indent=4, ensure_ascii=False)
        except Exception as e:
            #print_lc(e)
            pass
    def len(self) -> int:
        return len(self._history) if self._history is not None else None
    def getAsChoices(self):
        ret = [
            json.dumps(h, ensure_ascii=False) for h in self._history]
        return ret

class SearchHistory(History):
    def __init__(self):
        super().__init__(Path.joinpath(
            extensionFolder(), Path("../search_history.json")))
        self._delimiter = "_._"
    def add(self, type, word):
        if type == "No" or word == "" or word == None:
            return
        dict = { "type" : type,
                "word": word }  
        try:                  
            self._history.remove(dict)
        except:
            pass
        self._history.appendleft(dict)
        while self.len() > opts.civsfz_length_of_search_history:
            self._history.pop()
        self.save()
    def getAsChoices(self):
        ret = [f'{w["word"]}{self._delimiter}{w["type"]}' for w in self._history]
        return ret
    def getDelimiter(self) -> str:
        return self._delimiter

class ConditionsHistory(History):
    def __init__(self):
        super().__init__(Path.joinpath(
            extensionFolder(), Path("../conditions_history.json")))
        self._delimiter = "_._"
    def add(self, sort, period, baseModels, nsfw ):
        dict = {
            "sort": sort,
            "period": period,
            "baseModels": baseModels,
            "nsfw": nsfw
        }
        try:                  
            self._history.remove(dict)
        except:
            pass
        self._history.appendleft(dict)
        while self.len() > opts.civsfz_length_of_conditions_history:
            self._history.pop()
        self.save()
    def getAsChoices(self):
        ret = [self._delimiter.join(
                [ str(v) if k != 'baseModels' else json.dumps(v, ensure_ascii=False) for k, v in h.items()]
                ) for h in self._history]
        return ret
    def getDelimiter(self) -> str:
        return self._delimiter
    