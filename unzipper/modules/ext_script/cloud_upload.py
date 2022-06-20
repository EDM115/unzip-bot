import os
import subprocess
# import requests
from pathlib import Path
from requests import get, post, ConnectionError, head
from requests.exceptions import MissingSchema
import json
import sys

async def terminal(command):
    run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    shell_ouput = run.stdout.read()[:-1].decode("utf-8")
    return shell_ouput

async def bayfiles(file, url):
    try:
        temp_upload = await terminal(f"curl -F 'file=@{file}' {url}")
        uploaded = json.loads(temp_upload)
    except:
        uploaded = "Error happened"
    return uploaded

"""
# https://github.com/gamingdy/Anonfiles-Bayfiles-UPLOAD
class Error(BaseException):
    pass

class UploadFile:
    def __init__(self, url):
        self.based_url = url

    def upload(self, filepath):
        # Upload files on Anonfiles or Bayfiles, with a Size limit to 5 Go/Gb by files.
        # You must be specified files path(relative or absolute)
        with open(filepath, "rb") as a_file:
            filename = os.path.basename(filepath)
            _files = {"file": (filename, a_file)}
            r = requests.post(self.based_url, files=_files).json()
        if r["status"]:
            file = r["data"]["file"]
            final_file = {"url": file["url"], "metadata": file["metadata"]}
            return final_file
        else:
            r_error = r["error"]
            error_message = f"{r_error['type']} : {r_error['message']}"
            raise Error(error_message)

class Anonfiles(UploadFile):
    def __init__(self):
        UploadFile.__init__(self, "https://api.anonfiles.com/upload")

class Bayfiles(UploadFile):
    def __init__(self):
        UploadFile.__init__(self, "https://api.bayfiles.com/upload")
"""

"""
# https://github.com/redevil1/bayfiles
async def bayfiles_upload(file):
    url = "https://api.bayfiles.com/upload"
    try:
        r = post(url, file=file)
    except ConnectionError:
        return "[Error]: No internet"
    resp = json.loads(r.text)
    if resp["status"]:
        urlshort = resp['data']['file']['url']['short']
        urllong = resp['data']['file']['url']['full']
        print(f'[SUCCESS]: Your file has been succesfully uploaded:\nFull URL: {urllong}\nShort URL: {urlshort}')
        return urllong
    else:
        message = resp['error']['message']
        errtype = resp['error']['type']
        print(f'[ERROR]: {message}\n{errtype}')
        return message
"""
