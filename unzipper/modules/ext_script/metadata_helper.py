import os

import mutagen.id3 as id3

from mutagen.aac import AAC
from mutagen.aiff import AIFF
from mutagen.asf import ASF
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.oggopus import OggOpus
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE

from unzipper.modules.ext_script.ext_helper import __run_cmds_unzipper, run_cmds_on_cr


async def get_audio_metadata(file_path):
    file_ext = file_path.split(".")[-1].lower()
    audio_meta = {"performer": None, "title": None, "duration": None}

    try:
        if file_ext in ["mp3"]:
            audio = MP3(file_path, ID3=EasyID3)
        elif file_ext in ["m4a", "alac"]:
            audio = MP4(file_path)
        elif file_ext in ["flac"]:
            audio = FLAC(file_path)
        elif file_ext in ["aif", "aiff"]:
            audio = AIFF(file_path)
        elif file_ext in ["ogg"]:
            audio = OggVorbis(file_path)
        elif file_ext in ["opus"]:
            audio = OggOpus(file_path)
        elif file_ext in ["wav"]:
            audio = WAVE(file_path)
        elif file_ext in ["wma"]:
            audio = ASF(file_path)
        elif file_ext in ["aac"]:
            audio = AAC(file_path)
        else:
            return audio_meta

        audio_meta["duration"] = int(audio.info.length)

        if file_ext == "mp3":
            audio_meta["performer"] = audio.get("artist", [None])[0]
            audio_meta["title"] = audio.get("title", [None])[0]

        elif file_ext in ["m4a", "alac"]:
            audio_meta["performer"] = audio.tags.get("\xa9ART", [None])[0]
            audio_meta["title"] = audio.tags.get("\xa9nam", [None])[0]

        elif file_ext == "flac":
            audio_meta["performer"] = audio.get("artist", [None])[0]
            audio_meta["title"] = audio.get("title", [None])[0]

        elif file_ext in ["aif", "aiff"]:
            audio_meta["performer"] = audio.get("artist", [None])[0]
            audio_meta["title"] = audio.get("title", [None])[0]

        elif file_ext == "ogg":
            audio_meta["performer"] = audio.get("artist", [None])[0]
            audio_meta["title"] = audio.get("title", [None])[0]

        elif file_ext == "opus":
            audio_meta["performer"] = audio.get("artist", [None])[0]
            audio_meta["title"] = audio.get("title", [None])[0]

        elif file_ext == "wav":
            # WAV doesn't have a standard tagging system, handling might vary
            pass

        elif file_ext == "wma":
            audio_meta["performer"] = audio.tags.get("Author", [None])[0]
            audio_meta["title"] = audio.tags.get("WM/AlbumTitle", [None])[0]

        elif file_ext == "aac":
            # AAC tagging is not standardized, handling might vary
            pass

    except Exception:
        return audio_meta

    return audio_meta


async def convert_and_save(file_path, target_format, metadata):
    directory, filename = os.path.split(file_path)
    basename, _ = os.path.splitext(filename)
    new_file = os.path.join(directory, f"{basename}.{target_format}")

    cmd = ["ffmpeg", "-i", file_path, "-vn", new_file]
    await run_cmds_on_cr(__run_cmds_unzipper, cmd=cmd)

    if target_format == "mp3":
        audio = MP3(new_file, ID3=EasyID3)
        audio["artist"] = metadata["performer"]
        audio["title"] = metadata["title"]
        audio.save()
    elif target_format in ["m4a", "alac"]:
        audio = MP4(new_file)
        audio.tags["\xa9ART"] = metadata["performer"]
        audio.tags["\xa9nam"] = metadata["title"]
        audio.save()
    elif target_format == "flac":
        audio = FLAC(new_file)
        audio["artist"] = metadata["performer"]
        audio["title"] = metadata["title"]
        audio.save()
    elif target_format in ["aif", "aiff"]:
        audio = AIFF(new_file)
        # The metadata have to be a Frame instance
        audio["artist"] = id3.TextFrame(encoding=3, text=[metadata["performer"]])
        audio["title"] = id3.TextFrame(encoding=3, text=[metadata["title"]])
        audio.save()
    elif target_format == "ogg":
        audio = OggVorbis(new_file)
        audio["artist"] = metadata["performer"]
        audio["title"] = metadata["title"]
        audio.save()
    elif target_format == "opus":
        audio = OggOpus(new_file)
        audio["artist"] = metadata["performer"]
        audio["title"] = metadata["title"]
        audio.save()
    elif target_format == "wav":
        audio = WAVE(new_file)
        audio.save()
    elif target_format == "wma":
        audio = ASF(new_file)
        audio.tags["Author"] = metadata["performer"]
        audio.tags["WM/AlbumTitle"] = metadata["title"]
        audio.save()
    elif target_format == "aac":
        audio = AAC(new_file)
        audio.save()

    return new_file
