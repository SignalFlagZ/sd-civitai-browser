import os
import time
import threading
import requests
import urllib.parse
import shutil
import json
import re
import platform
import sys
import subprocess as sp
from modules import shared
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


print_ly = lambda  x: print(Fore.LIGHTYELLOW_EX + "Civitai-Browser: " + x + Style.RESET_ALL )
print_lc = lambda  x: print(Fore.LIGHTCYAN_EX + "Civitai-Browser: " + x + Style.RESET_ALL )
print_n = lambda  x: print("Civitai-Browser: " + x )

isDownloading = False

def contenttype_folder(content_type):
    if content_type == "Checkpoint":
        if cmd_opts.ckpt_dir:
            folder = cmd_opts.ckpt_dir #"models/Stable-diffusion"
        else:            
            folder = os.path.join(models_path,"Stable-diffusion") 
    elif content_type == "Hypernetwork":
        folder = cmd_opts.hypernetwork_dir #"models/hypernetworks"
    elif content_type == "TextualInversion":
        folder = cmd_opts.embeddings_dir #"embeddings"
    elif content_type == "AestheticGradient":
        folder = "extensions/stable-diffusion-webui-aesthetic-gradients/aesthetic_embeddings"
    elif content_type == "LORA":
        folder = cmd_opts.lora_dir #"models/Lora"
    elif content_type == "LoCon":
        if "lyco_dir" in cmd_opts:
            folder = f"{cmd_opts.lyco_dir}"
        elif "lyco_dir_backcompat" in cmd_opts: #A1111 V1.5.1
            folder = f"{cmd_opts.lyco_dir_backcompat}"
        else:
            folder = os.path.join(models_path,"LyCORIS")
    elif content_type == "VAE":
        if cmd_opts.vae_dir:
            folder = cmd_opts.vae_dir #"models/VAE"
        else:
            folder = os.path.join(models_path,"VAE")
    elif content_type == "Controlnet":
        if cmd_opts.ckpt_dir:
            folder = os.path.join(os.path.join(cmd_opts.ckpt_dir, os.pardir), "ControlNet")
        else:            
            folder = os.path.join(models_path,"ControlNet")
    elif content_type == "Poses":
        if cmd_opts.ckpt_dir:
            folder = os.path.join(os.path.join(cmd_opts.ckpt_dir, os.pardir), "Poses")
        else:            
            folder = os.path.join(models_path,"Poses")
    return folder

def escaped_modelpath(folder, model_name):
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
                                    "\\": r""
                                })
    return os.path.join(folder,model_name.translate(escapechars))

def extranetwork_folder(content_type, model_name:str = "",base_model:str="", nsfw:bool=False):
    folder = contenttype_folder(content_type)
#    if use_new_folder:
        #model_folder = os.path.join(new_folder,model_name.replace(" ","_").replace("(","").replace(")","").replace("|","").replace(":","-").replace(",","_").replace("\\",""))
#        model_folder = escaped_modelpath(new_folder, model_name)
#        if not os.path.exists(new_folder):
#            if make_dir: os.makedirs(new_folder)
#        if not os.path.exists(model_folder):
#            if make_dir: os.makedirs(model_folder)
#    else:
        #model_folder = os.path.join(folder,model_name.replace(" ","_").replace("(","").replace(")","").replace("|","").replace(":","-").replace(",","_").replace("\\",""))
    if not 'SD 1' in base_model:
        folder = os.path.join(folder, '_' + base_model.replace(' ','_').replace('.','_'))
    if nsfw:
        folder = os.path.join(folder, '.nsfw')
    model_folder = escaped_modelpath(folder, model_name)
    return model_folder

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
    makedirs(folder)
    img_urls = re.findall(r'src=[\'"]?([^\'" >]+)', html)
    basename = os.path.splitext(versionName)[0] # remove extension
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    preview_url = versionInfo['images'][0]['url']
    preview_url = urllib.parse.quote(preview_url,  safe=':/=')
    if 'images' in versionInfo:
        for img in versionInfo['images']:
            if img['type'] == 'image':
                preview_url = img['url']
                preview_url = urllib.parse.quote(preview_url,  safe=':/=')
                break

    urllib.request.install_opener(opener)
    HTML = html
    for i, img_url in enumerate(img_urls):
        isVideo = False
        for img in versionInfo['images']:
            if img['url'] == img_url:
                if img['type'] == 'video':
                    isVideo = True
        #print(Fore.LIGHTYELLOW_EX + f'URL: {img_url}'+ Style.RESET_ALL)
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

        HTML = HTML.replace(img_url,f'"{filename}"')
        url_parse = urllib.parse.urlparse(img_url)
        if url_parse.scheme:
            img_url = urllib.parse.quote(img_url,  safe=':/=')   #img_url.replace("https", "http").replace("=","%3D")
            try:
                with urllib.request.urlopen(img_url) as url:
                    with open(os.path.join(folder, filename), 'wb') as f:
                        f.write(url.read())
                        if img_url == preview_url:
                            shutil.copy2(os.path.join(folder, filename),os.path.join(folder, filenamethumb))
                        print_n(f"Save {filename}")
                #with urllib.request.urlretrieve(img_url, os.path.join(model_folder, filename)) as dl:
            except urllib.error.URLError as e:
                print_ly(f'Error: {e.reason}')
                print_ly(f'URL: {img_url}')
                #return "Err: Save infos"
            except urllib.error.HTTPError as err:
                print_ly(f'Error: {e.reason}')
                print_ly(f'URL: {img_url}')
    filepath = os.path.join(folder, f'{basename}.html')
    with open(filepath, 'wb') as f:
        f.write(HTML.encode('utf8'))
        print_n(f"Save {basename}.html")
    #Save json_info
    filepath = os.path.join(folder, f'{basename}.civitai.info')
    with open(filepath, mode="w", encoding="utf-8") as f:
        json.dump(versionInfo, f, indent=2, ensure_ascii=False)
        print_n(f"Save {basename}.civitai.info")
    return "Save infos"

#def download_file_thread(url, file_name, content_type, model_name,base_model, nsfw:bool=False):
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


def download_file(url, file_name):
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
        progress = tqdm(total=1000000000, unit="B", unit_scale=True, desc=f"Downloading {file_name_display}", initial=downloaded_size, leave=False)
        # Open a local file to save the download
        global isDownloading
        with open(file_name, "ab") as f:
            while isDownloading:
                try:
                    # Send a GET request to the URL and save the response to the local file
                    response = requests.get(url, headers=headers, stream=True)

                    # Get the total size of the file
                    total_size = int(response.headers.get("Content-Length", 0))

                    # Update the total size of the progress bar if the `Content-Length` header is present
                    if total_size == 0:
                        total_size = downloaded_size
                    progress.total = total_size 

                    # Write the response to the local file and update the progress bar
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            progress.update(len(chunk))
                        if (isDownloading == False):
                            response.close
                            break
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
        progress.close()
        if (isDownloading == False):
            print_ly(f'Canceled!')
            break
        isDownloading = False
        downloaded_size = os.path.getsize(file_name)
        # Check if the download was successful
        if downloaded_size >= total_size:
            print_n(f"Save: {file_name_display}")
            break
        else:
            print_ly(f"Error: File download failed. Retrying... {file_name_display}")

#def download_file(url, file_name):
#    # Download the file and save it to a local file
#    response = requests.get(url, stream=True)
#
#    # Get the total size of the file
#    total_size = int(response.headers.get("Content-Length", 0))
#
#    # Split filename from included path
#    tokens = re.split(re.escape('\\'), file_name)
#    file_name_display = tokens[-1]
#
#    # Initialize the progress bar
#    progress = tqdm(total=total_size, unit="B", unit_scale=True, desc=f"Downloading {file_name_display}")
#
#    # Open a local file to save the download
#    with open(file_name, "wb") as f:
#        # Iterate over the response chunks and update the progress bar
#        for chunk in response.iter_content(chunk_size=1024):
#            if chunk:  # filter out keep-alive new chunks
#                f.write(chunk)
#                progress.update(len(chunk))
#
#    # Close the progress bar
#    progress.close()

def download_file2(folder, filename,  url, hash):
    makedirs(folder)
    file_name = os.path.join(folder, filename)
    #thread = threading.Thread(target=download_file, args=(url, filepath))

    # Maximum number of retries
    max_retries = 5

    # Delay between retries (in seconds)
    retry_delay = 10

    exitGenerator=False
    while not exitGenerator:
        # Check if the file has already been partially downloaded
        downloaded_size = 0
        headers = {}
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
        progressConsole = tqdm(total=1000000000, unit="B", unit_scale=True, desc=f"Downloading {file_name_display}", initial=downloaded_size, leave=False)
        prg = 0 #downloaded_size
        # Open a local file to save the download
        with open(file_name, mode) as f:
            while not exitGenerator:
                try:
                    # Send a GET request to the URL and save the response to the local file
                    response = requests.get(url, headers=headers, stream=True)
                    # Get the total size of the file
                    total_size = int(response.headers.get("Content-Length", 0))

                    # Update the total size of the progress bar if the `Content-Length` header is present
                    if total_size == 0:
                        total_size = downloaded_size
                    progressConsole.total = total_size
                    # Write the response to the local file and update the progress bar
                    for chunk in response.iter_content(chunk_size=4*1024*1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            progressConsole.update(len(chunk))
                            prg += len(chunk)
                            try:
                                yield f'{round(prg/1048576)}MB / {round(total_size/1048576)}MB'
                            except Exception as e:
                                exitGenerator=True
                                progressConsole.close()
                                return
                    downloaded_size = os.path.getsize(file_name)
                    # Break out of the loop if the download is successful
                    break
                except GeneratorExit:
                    exitGenerator=True
                    progressConsole.close()
                    return
                except ConnectionError as e:
                    # Decrement the number of retries
                    max_retries -= 1

                    # If there are no more retries, raise the exception
                    if max_retries == 0:
                        progressConsole.close()
                        return
                    # Wait for the specified delay before retrying
                    time.sleep(retry_delay)
        # Close the progress bar
        progressConsole.close()
        downloaded_size = os.path.getsize(file_name)
        sha256 = calculate_sha256(file_name).upper()
        # Check if the download was successful
        if sha256 == hash.upper():
            print_n(f"Save: {file_name_display}")
            yield 'Downloaded'
            exitGenerator=True
            return
        else:
            print_ly(f"Error: File download failed. {file_name_display}")
            print_lc(f'Model file hash : {hash}')
            print_lc(f'Downloaded hash : {sha256}')
            exitGenerator=True
            removeFile(file_name)
            yield 'Failed.'
            return

def removeFile(file):
    if send2trash_installed:
        send2trash(file.replace('/','\\'))
        print_lc('Move file to trash')
    else:
        print_lc('File is not deleted. send2trash module is missing.')
    return

def open_folder(f):
	'''[reference](https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/5ef669de080814067961f28357256e8fe27544f4/modules/ui_common.py#L109)'''
	
	if not os.path.exists(f):
		print(f'Folder "{f}" does not exist. After you create an image, the folder will be created.')
		return
	elif not os.path.isdir(f):
		print(f"""
WARNING
An open_folder request was made with an argument that is not a folder.
This could be an error or a malicious attempt to run code on your computer.
Requested path was: {f}
""", file=sys.stderr)
		return

	if not shared.cmd_opts.hide_ui_dir_config:
		path = os.path.normpath(f)
		if platform.system() == "Windows":
			os.startfile(path)
		elif platform.system() == "Darwin":
			sp.Popen(["open", path])
		elif "microsoft-standard-WSL2" in platform.uname().release:
			sp.Popen(["wsl-open", path])
		else:
			sp.Popen(["xdg-open", path])