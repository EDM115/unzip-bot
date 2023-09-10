import requests
from unzipper import LOGGER


anonfilesBaseSites = ["anonfiles.com", "hotfile.io", "bayfiles.com", "megaupload.nz", "letsupload.cc", "filechan.org", "myfile.is", "vshare.is", "rapidshare.nu", "lolabits.se", "openload.cc", "share-online.is", "upvid.cc"]


async def get_gdrive_id(gdrive_url):
    gdrive_url = gdrive_url.strip().rstrip('/')

    if "drive.google.com" in gdrive_url:
        if "/file/d/" in gdrive_url:
            start_index = gdrive_url.find("/file/d/") + len("/file/d/")
            end_index = gdrive_url.find("/", start_index)
            file_id = gdrive_url[start_index:end_index]
            return file_id

        if "/open?id=" in gdrive_url:
            start_index = gdrive_url.find("/open?id=") + len("/open?id=")
            file_id = gdrive_url[start_index:]
            return file_id

        if "/file/d/" in gdrive_url and "/view" in gdrive_url:
            start_index = gdrive_url.find("/file/d/") + len("/file/d/")
            end_index = gdrive_url.find("/view", start_index)
            file_id = gdrive_url[start_index:end_index]
            return file_id

        if "/uc?id=" in gdrive_url:
            start_index = gdrive_url.find("/uc?id=") + len("/uc?id=")
            end_index = gdrive_url.find("&", start_index)
            file_id = gdrive_url[start_index:end_index]
            return file_id

        if "/uc?export=download&id=" in gdrive_url:
            start_index = gdrive_url.find("/uc?export=download&id=") + len("/uc?export=download&id=")
            end_index = gdrive_url.find("&", start_index)
            file_id = gdrive_url[start_index:end_index]
            return file_id

    raise ValueError("Invalid or unrecognized Google Drive URL format")


async def gdrive_dl(url):
    try:
        file_id = await get_gdrive_id(url)
        downloadable_link = f"https://drive.google.com/uc?id={file_id}&export=download"
        return downloadable_link
    except ValueError as e:
        LOGGER.warning(e)
        return None


async def yandisk_dl(url):
    try:
        file_id = url.split("/")[-1]
        downloadable_link = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={file_id}"
        r = requests.get(downloadable_link)
        download_link = r.json()["href"]
        return download_link
    except Exception as e:
        LOGGER.warning(e)
        return None


async def onedrive_dl(url):
    try:
        file_id = url.split("/")[-2]
        downloadable_link = f"https://api.onedrive.com/v1.0/shares/u!{file_id}/root/content"
        return downloadable_link
    except Exception as e:
        LOGGER.warning(e)
        return None


async def mediafire_dl(url):
    try:
        file_id = url.split("/")[-2]
        downloadable_link = f"https://download{file_id}.mediafire.com/file/{file_id}/file"
        return downloadable_link
    except Exception as e:
        LOGGER.warning(e)
        return None


async def anonfiles_dl(url):
    basesite = url.split("/")[2].replace("www.", "")
    if basesite not in anonfilesBaseSites:
        return None
    try:
        file_id = url.split("/")[-1]
        downloadable_link = f"https://api.anonfiles.com/v2/file/{file_id}/info"
        r = requests.get(downloadable_link)
        download_link = r.json()["data"]["file"]["url"]["full"]
        return download_link
    except Exception as e:
        LOGGER.warning(e)
        return None


async def krakenfiles_dl(url):
    try:
        file_id = url.split("/")[-1]
        downloadable_link = f"https://krakenfiles.com/view/{file_id}"
        r = requests.get(downloadable_link)
        download_link = r.url
        return download_link
    except Exception as e:
        LOGGER.warning(e)
        return None


async def wetransfer_dl(url):
    try:
        file_id = url.split("/")[-1]
        downloadable_link = f"https://wetransfer.com/api/ui/transfers/{file_id}/download"
        r = requests.get(downloadable_link)
        download_link = r.json()["direct_link"]
        return download_link
    except Exception as e:
        LOGGER.warning(e)
        return None
