from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.aiff import AIFF
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.wave import WAVE
from mutagen.asf import ASF
from mutagen.aac import AAC


def get_audio_metadata(file_path):
    file_ext = file_path.split('.')[-1].lower()
    audio_meta = {}

    try:
        if file_ext in ['mp3']:
            audio = MP3(file_path, ID3=EasyID3)
        elif file_ext in ['m4a', 'alac']:
            audio = MP4(file_path)
        elif file_ext in ['flac']:
            audio = FLAC(file_path)
        elif file_ext in ['aif', 'aiff']:
            audio = AIFF(file_path)
        elif file_ext in ['ogg']:
            audio = OggVorbis(file_path)
        elif file_ext in ['opus']:
            audio = OggOpus(file_path)
        elif file_ext in ['wav']:
            audio = WAVE(file_path)
        elif file_ext in ['wma']:
            audio = ASF(file_path)
        elif file_ext in ['aac']:
            audio = AAC(file_path)
        else:
            return None

        audio_meta['duration'] = int(audio.info.length)
        
        if file_ext == 'mp3':
            audio_meta['performer'] = audio.get('artist', [None])[0]
            audio_meta['title'] = audio.get('title', [None])[0]

        elif file_ext in ['m4a', 'alac']:
            audio_meta['performer'] = audio.tags.get('\xa9ART', [None])[0]
            audio_meta['title'] = audio.tags.get('\xa9nam', [None])[0]

        elif file_ext == 'flac':
            audio_meta['performer'] = audio.get('artist', [None])[0]
            audio_meta['title'] = audio.get('title', [None])[0]

        elif file_ext in ['aif', 'aiff']:
            audio_meta['performer'] = audio.get('artist', [None])[0]
            audio_meta['title'] = audio.get('title', [None])[0]

        elif file_ext == 'ogg':
            audio_meta['performer'] = audio.get('artist', [None])[0]
            audio_meta['title'] = audio.get('title', [None])[0]

        elif file_ext == 'opus':
            audio_meta['performer'] = audio.get('artist', [None])[0]
            audio_meta['title'] = audio.get('title', [None])[0]

        elif file_ext == 'wav':
            # WAV doesn't have a standard tagging system, handling might vary

        elif file_ext == 'wma':
            audio_meta['performer'] = audio.tags.get('Author', [None])[0]
            audio_meta['title'] = audio.tags.get('WM/AlbumTitle', [None])[0]

        elif file_ext == 'aac':
            # AAC tagging is not standardized, handling might vary

    except Exception:
        return None

    return audio_meta
