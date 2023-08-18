import os
import time
import threading
import requests
import urllib.parse
import shutil
import json
import re
from colorama import Fore, Back, Style
from requests.exceptions import ConnectionError
from tqdm import tqdm
from modules.shared import opts, cmd_opts
from modules.paths import models_path

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
        with open(filepath, 'w') as f:
            f.write(trained_words)
    print(Fore.LIGHTCYAN_EX + f'Save text.' + Style.RESET_ALL)

def makedirs(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(Fore.LIGHTCYAN_EX + f'Make folder: {folder}' + Style.RESET_ALL)
        
def saveImageFiles(folder, versionName, html, content_type, versionInfo):
    makedirs(folder)
    img_urls = re.findall(r'src=[\'"]?([^\'" >]+)', html)
    basename = os.path.splitext(versionName)[0] # remove extension
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    urllib.request.install_opener(opener)
    HTML = html
    for i, img_url in enumerate(img_urls):
        filename = f'{basename}_{i}.png'
        filenamethumb = f'{basename}.png'
        if content_type == "TextualInversion":
            filename = f'{basename}_{i}.preview.png'
            filenamethumb = f'{basename}.preview.png'
        HTML = HTML.replace(img_url,f'"{filename}"')
        img_url = urllib.parse.quote(img_url,  safe=':/=')   #img_url.replace("https", "http").replace("=","%3D")
        try:
            with urllib.request.urlopen(img_url) as url:
                with open(os.path.join(folder, filename), 'wb') as f:
                    f.write(url.read())
                    if i == 0 and not os.path.exists(os.path.join(folder, filenamethumb)):
                        shutil.copy2(os.path.join(folder, filename),os.path.join(folder, filenamethumb))
                    print(Fore.LIGHTCYAN_EX + f"Save {filename}" + Style.RESET_ALL)
            #with urllib.request.urlretrieve(img_url, os.path.join(model_folder, filename)) as dl:
                    
        except urllib.error.URLError as e:
            print(f'Error: {e.reason}')
    
    filepath = os.path.join(folder, f'{basename}.html')
    with open(filepath, 'wb') as f:
        f.write(HTML.encode('utf8'))
    #Save json_info
    filepath = os.path.join(folder, f'{basename}.civitai.info')
    with open(filepath, mode="w", encoding="utf-8") as f:
        json.dump(versionInfo, f, indent=2, ensure_ascii=False)
    print(Fore.LIGHTCYAN_EX + f"Done." + Style.RESET_ALL)

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
            print (Fore.LIGHTYELLOW_EX + f'Canceled!' + Style.RESET_ALL)
            break
        isDownloading = False
        downloaded_size = os.path.getsize(file_name)
        # Check if the download was successful
        if downloaded_size >= total_size:
            print(Fore.LIGHTCYAN_EX + f"Success: {file_name_display}" + Style.RESET_ALL)
            break
        else:
            print(f"Error: File download failed. Retrying... {file_name_display}")

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
