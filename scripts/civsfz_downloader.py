import math
import os
import re
import requests
from colorama import Fore, Back, Style
from collections import deque
from datetime import datetime, timedelta, timezone
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from threading import Thread, local
from time import sleep
from tqdm import tqdm
from modules.hashes import calculate_sha256
from scripts.civsfz_filemanage import makedirs, removeFile, extensionFolder

def print_ly(x): return print(Fore.LIGHTYELLOW_EX +
                              "CivBrowser: " + x + Style.RESET_ALL)
def print_lc(x): return print(Fore.LIGHTCYAN_EX +
                              "CivBrowser: " + x + Style.RESET_ALL)
def print_n(x): return print("CivBrowser: " + x)

class Downloader:
    _dlQ = deque()  # Download
    _threadQ = deque() # Downloading
    _ctrlQ = deque()  # control
    #_msgQ = deque()  # msg from worker
    _thread_local = local()
    _dlResults = deque() # Download results
    _maxThreadNum = 2
    _threadNum = 0

    def __init__(self) -> None:
        Downloader._thread_local.progress = 0
    
    def get_session(self) -> requests.Session:
        if not hasattr(Downloader._thread_local, 'session'):
            Downloader._thread_local.session = requests.Session()
        return Downloader._thread_local.session


    def add(self, folder, filename,  url, hash, api_key, early_access):
        if Downloader._threadNum == 0:
            # Clear queue because garbage may remain due to errors that cannot be caught
            Downloader._threadQ.clear()
        Downloader._ctrlQ.clear() # Clear cancel request
        Downloader._dlQ.append({"folder": folder,
                             "filename": filename,
                             "url": url,
                             "hash": hash,
                             "apiKey": api_key,
                             "EarlyAccess": early_access
                             })
        if Downloader._threadNum < Downloader._maxThreadNum:
            Downloader._threadNum += 1
            worker = Thread(target=self.download)
            worker.start()
        return f"Queue {len(Downloader._dlQ)}: Threads {Downloader._threadNum}"

    def sendCancel(self, folder, filename):
        '''
            Cancel downloading by file path
        '''
        delete = None
        for dl in Downloader._dlQ:
            if len({folder, filename} & {dl["folder"], dl["filename"]}) > 0:
                delete = dl
                break
        if delete is None:
            Downloader._ctrlQ.append({"control": "cancel",
                                  "file": os.path.join(folder, filename)})
        else:
            Downloader._dlQ.remove(dl)
            print_lc(f"Canceled:{filename}")
            return f"Canceled:{filename}"

    def status(self):
        now = datetime.now(timezone.utc)
        # Discard past results
        expireQ = deque()
        remove = None
        deadline = 180
        for item in Downloader._dlResults:
            tdDiff = now - item['completedAt']
            secDiff = math.ceil(abs(tdDiff / timedelta(seconds=1)))
            item['expiration'] = secDiff / deadline
            if secDiff < deadline:
                expireQ.append(item)
            else:
                remove = item
        if remove is not None:
            Downloader._dlResults.remove(remove)
                
        templatesPath = Path.joinpath(
            extensionFolder(), Path("../templates"))
        environment = Environment(loader=FileSystemLoader(templatesPath.resolve()))
        template = environment.get_template("downloadQueue.jinja")
        content = template.render(
            threadQ=Downloader._threadQ, waitQ=Downloader._dlQ, resultQ=expireQ)
        return content
    
    def download(self) -> None:
        session = self.get_session()
        result = "" # Success or Error
        while len(Downloader._dlQ) > 0:
            q = Downloader._dlQ.popleft()
            q['progress'] = 0 # add progress info
            Downloader._threadQ.append(q)  # for download list
            url = q["url"]
            folder = q["folder"]
            filename = q["filename"]
            hash = q["hash"]
            api_key = q["apiKey"]
            early_access = q["EarlyAccess"]
            #
            makedirs(folder)
            file_name = os.path.join(folder, filename)
            # Maximum number of retries
            max_retries = 3
            # Delay between retries (in seconds)
            retry_delay = 3

            downloaded_size = 0
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
            }
            mode = "wb"  # Open file mode
            if os.path.exists(file_name):
                print_lc("Overwrite")

            # Split filename from included path
            tokens = re.split(re.escape('\\'), file_name)
            file_name_display = tokens[-1]
            cancel = False
            exitGenerator = False                
            while not exitGenerator:
                # Send a GET request to the URL and save the response to the local file
                try:
                    # Get the total size of the file
                    with session.get(url, headers=headers, stream=True, timeout=(10, 10)) as response:
                        response.raise_for_status()
                        # print_lc(f"{response.headers=}")
                        if 'Content-Length' in response.headers:
                            total_size = int(
                                response.headers.get("Content-Length", 0))
                            # Update the total size of the progress bar if the `Content-Length` header is present
                            if total_size == 0:
                                total_size = downloaded_size
                            with tqdm(total=1000000000, unit="B", unit_scale=True, desc=f"Downloading {file_name_display}", initial=downloaded_size, leave=True) as progressConsole:
                                prg = 0  # downloaded_size
                                progressConsole.total = total_size
                                with open(file_name, mode) as file:
                                    for chunk in response.iter_content(chunk_size=1*1024*1024):
                                        if chunk:  # filter out keep-alive new chunks
                                            file.write(chunk)
                                            progressConsole.update(len(chunk))
                                            prg += len(chunk)
                                            #update progress
                                            i = Downloader._threadQ.index(q)
                                            q['progress'] = prg / total_size
                                            Downloader._threadQ[i] = q
                                        # cancel
                                        if len(Downloader._ctrlQ) > 0:
                                            ctrl = Downloader._ctrlQ[0]
                                            if ctrl['control'] == "cancel" and ctrl['file'] == file_name:
                                                Downloader._ctrlQ.popleft()
                                                exitGenerator = True
                                                cancel = True
                                                result = "Canceled"
                                                print_lc(
                                                    f"Canceled:{file_name_display}:")
                                                break
                            downloaded_size = os.path.getsize(file_name)
                            # Break out of the loop if the download is successful
                            break
                        else:
                            if early_access:
                                print_ly(
                                    f"{file_name_display}:Download canceled. Early Access!")
                                exitGenerator = True
                                result = "Early Access"
                                break
                            else:
                                print_lc("May need API key")
                                if len(api_key) == 32:
                                    headers.update(
                                        {"Authorization": f"Bearer {api_key}"})
                                    print_lc(
                                        f"{file_name_display}:Apply API key")
                                else:
                                    exitGenerator = True
                                    result = "Unexpected response"
                                    break

                except requests.exceptions.Timeout as e:
                    print_ly(f"{file_name_display}:{e}")
                    result = "Timeout"
                    exitGenerator = True
                except ConnectionError as e:
                    print_ly(f"{file_name_display}:{e}")
                    result = "Connection Error"
                    exitGenerator = True
                except requests.exceptions.RequestException as e:
                    print_ly(f"{file_name_display}:{e}")
                    result = "Request exception"
                    exitGenerator = True
                except Exception as e:
                    print_ly(f"{file_name_display}:{e}")
                    result = "Exception"
                    exitGenerator = True
                # Decrement the number of retries
                max_retries -= 1
                # If there are no more retries, raise the exception
                if max_retries == 0:
                    exitGenerator = True
                    break
                # Wait for the specified delay before retrying
                print_lc(f"{file_name_display}:Retry wait {retry_delay}s")
                sleep(retry_delay)

            if cancel:
                print_lc(f'Canceled : {file_name_display}')
                #gr.Warning(f"Canceled: {file_name_display}")
                removeFile(file_name)
            else:
                if os.path.exists(file_name):
                    #downloaded_size = os.path.getsize(file_name)
                    # Check if the download was successful
                    sha256 = calculate_sha256(file_name).upper()
                    # print_lc(f'Model file hash : {hash}')
                    if hash != "":
                        if sha256[:len(hash)] == hash.upper():
                            print_n(f"Save: {file_name_display}")
                            result = "Succeeded"
                            #gr.Info(f"Success: {file_name_display}")
                        else:
                            print_ly(
                                f"Error: File download failed. {file_name_display}")
                            print_lc(f'Model file hash : {hash}')
                            print_lc(f'Downloaded hash : {sha256}')
                            #gr.Warning(f"Hash mismatch: {file_name_display}")
                            removeFile(file_name)
                            result = "Hash mismatch"
                    else:
                        print_n(f"Save: {file_name_display}")
                        print_ly("No hash value provided. Unable to confirm file.")
                        result = "No hash value"
                        #gr.Info(f"No hash: {file_name_display}")
            #Downloader._dlQ.task_done()
            Downloader._threadQ.remove(q)
            q['result'] = result
            q['completedAt'] = datetime.now(timezone.utc)
            Downloader._dlResults.append(q)
        Downloader._threadNum -= 1

