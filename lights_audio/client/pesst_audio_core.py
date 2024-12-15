import asyncio
from random import choice
from re import Pattern, compile, Match
from urllib.parse import urlparse
from pathlib import Path
from os.path import splitext # type: ignore
from os import remove
from subprocess import run, CalledProcessError
from typing import Iterable, Literal, Optional
from config import AUDIO_FORMAT, COLOR_FILE_EXTENSION, EMPTY_FILE, LIGHTS_LOCAL_IP, LIGHTS_REMOTE_IP, LIGHTS_PORT, SONG_DIRECTORY, SYN_INTERVAL, YOUTUBE_SECRETS_FILE, log
from protocol import DEFAULT_BRIGHTNESS
from pesst_audio_player import MPVWrapper
from pesst_light_client import LightClient
from pesst_audio_to_color import audio_to_colors_with_timestamps
from pesst_youtube_client import YoutubeAPIV3Client, Song

AUTOPLAY = Path("Autoplay")
YOUTUBE_CLIENT = YoutubeAPIV3Client(YOUTUBE_SECRETS_FILE, False)
# Current State: Used by Tick 
QUEUE: list[Path] = []
BRIGHTNESS = DEFAULT_BRIGHTNESS
PLAYING: bool = True
NEXT_SONG = False

PREVIOUS_QUEUE = []
PREVIOUS_PLAYING = True
PREVIOUS_BRIGHTNESS = DEFAULT_BRIGHTNESS

MUSIC: Optional[MPVWrapper] = None
LIGHTS: LightClient

SYN_COUNTDOWN = 0

async def setup(lights: Literal["local", "remote", "none"] = "local"):
    global LIGHTS
    ip = LIGHTS_REMOTE_IP
    if lights == "local":
        ip = LIGHTS_LOCAL_IP
    LIGHTS = LightClient(ip, LIGHTS_PORT, lights != "none")
    await LIGHTS.connect() 
    await LIGHTS.set_brightness(DEFAULT_BRIGHTNESS)
    YOUTUBE_CLIENT.initalize_session()

async def queue_handler():
    """
    Compares Current State to Previous State and dispatches events to ffplay and raspberry PI
    NOTE: Only 1 event can happen a tick
    1. Next song
    2. Pause/Unpause
    """
    global QUEUE
    global PLAYING
    global NEXT_SONG
    global PREVIOUS_QUEUE
    global PREVIOUS_PLAYING
    global MUSIC
    global LIGHTS
    global SYN_COUNTDOWN
    global BRIGHTNESS
    global PREVIOUS_BRIGHTNESS

    while True:
        await asyncio.sleep(0.1)
        SYN_COUNTDOWN = (SYN_COUNTDOWN + 1) % (SYN_INTERVAL*10) # Synchronize every 10 seconds
        if MUSIC and MUSIC.ended:
            QUEUE.pop(0)
            NEXT_SONG = True
        
        if SYN_COUNTDOWN == 0 and MUSIC:
            await LIGHTS.start(await MUSIC.get_timestamp() or 0)

        pause: bool = not PLAYING and PREVIOUS_PLAYING
        unpause: bool = PLAYING and not PREVIOUS_PLAYING
        next_song: bool = bool((not PREVIOUS_QUEUE and QUEUE) or (QUEUE and NEXT_SONG))
        no_songs: bool = bool(PREVIOUS_QUEUE and not QUEUE)
        brightness_changed: bool = BRIGHTNESS != PREVIOUS_BRIGHTNESS

        NEXT_SONG = False

        if pause and MUSIC:
            await MUSIC.pause()
            await LIGHTS.pause()
        elif unpause and MUSIC:
            await MUSIC.play()
            await LIGHTS.start(await MUSIC.get_timestamp() or 0)
        elif next_song:
            await play_next_song(QUEUE[0])
        elif no_songs and MUSIC:
            await MUSIC.stop()
            await LIGHTS.upload(EMPTY_FILE)
            MUSIC = None
        elif brightness_changed:
            await LIGHTS.set_brightness(BRIGHTNESS)
        
        PREVIOUS_QUEUE = QUEUE
        PREVIOUS_PLAYING = PLAYING
        QUEUE = QUEUE.copy()
        PREVIOUS_BRIGHTNESS = BRIGHTNESS

async def play_next_song(path: Path):
    global MUSIC
    global PLAYING
    PLAYING = True
    if MUSIC:
        # Upload the music file to LIGHTS
        await MUSIC.stop()
    if path == AUTOPLAY:
        path = choice(__list_downloads())[1]
        QUEUE.insert(0, path)
    await LIGHTS.upload(SONG_DIRECTORY / Path(str(path)+ COLOR_FILE_EXTENSION))
    MUSIC = MPVWrapper(SONG_DIRECTORY / path)
    await MUSIC.start()
    await asyncio.sleep(0.1)

LAST_SEARCH: list[tuple[str, str]] = [] # song_name, song_url
def search(song_name: str) -> list[str]:
    global LAST_SEARCH
    results = YOUTUBE_CLIENT.search_for_song(song_name)
    LAST_SEARCH = [(f"{result.title}: {result.channel_title}", result.get_url()) for result in results]
    return [f"{i}: {r[0]}" for i, r in enumerate(LAST_SEARCH)]
        
        
def download(songs: Iterable[str]) -> list[Path]:
    urls_to_download: set[str] = set()
    urls = [url for url in songs if uri_validator(url)]
    indeces = [int(index) for index in songs if index.isdigit()]
    names = [name for name in songs if not uri_validator(name) and not name.isdigit()]

    urls_to_download.update(urls)
    urls_to_download.update(url for url in find_songs_by_name(names, LAST_SEARCH))
    urls_to_download.update(result[1] for i, result in enumerate(LAST_SEARCH) if i in indeces)

    return __download(urls_to_download)

def __download(urls: Iterable[str]) -> list[Path]:
    if not urls:
        return []

    command = [
        "yt-dlp",
        "-P", SONG_DIRECTORY,
        "--extract-audio",  # Optional: Extract only audio
        "--audio-format", AUDIO_FORMAT,  # Optional: Convert to mp3 format
        *urls
    ]

    try:
        result = run(command, check=True, text=True, capture_output=True)
    except CalledProcessError as e:
        log(f"Error occurred while downloading: {e}")
        return []

    # Parse the yt-dlp output
    yt_dlp_output = result.stdout.splitlines() # type: ignore
    out = []
    out.extend([clean_downloaded(line, "."+AUDIO_FORMAT) for line in yt_dlp_output if line.startswith("[download] Destination")])
    out.extend([clean_already_downloaded(line) for line in yt_dlp_output if "has already been downloaded" in line])

    for path in out:
        if not (SONG_DIRECTORY / Path(str(path)+COLOR_FILE_EXTENSION)).exists():
            audio_to_colors_with_timestamps(SONG_DIRECTORY / path, "unknown")
        else:
            log("Already generated song file")
    
    return out

def uninstall(songs: list[str]) -> list[Path]:
    indeces = [int(index) for index in songs if index.isdigit()]
    names = [song for song in songs if not song.isdigit()]

    downloaded_songs = __list_downloads()

    songs_to_remove: set[Path] = set()
    songs_to_remove.update(song_tuple[1] for i, song_tuple in enumerate(downloaded_songs) if i in indeces)
    songs_to_remove.update(find_songs_by_name(names, downloaded_songs))

    for song_to_remove in songs_to_remove:
        remove(SONG_DIRECTORY / song_to_remove)
        remove(SONG_DIRECTORY / Path(str(song_to_remove) + COLOR_FILE_EXTENSION))
    return [song_to_remove for song_to_remove in songs_to_remove]

pattern: Pattern = compile(r"([+-])?(\d|(?:\d\d)|100)")
needs_1_arg = "Expected 1 brightness argument"
not_a_percent = "Argument not of the form [+|-]0..100"
async def brightness(args: list[str]) -> list[str]:
    global BRIGHTNESS
    if len(args) == 0:
        return [f"Brightness: {BRIGHTNESS}"]
    if len(args) != 1:
        return [needs_1_arg]
    maybe_match: Optional[Match[str]] = pattern.fullmatch(args[0])
    if maybe_match is None:
        return [not_a_percent]
    sign = maybe_match.group(1)
    percent = int(maybe_match.group(2))
    if sign == None:
        BRIGHTNESS = percent
    elif sign == "+":
        BRIGHTNESS = min(BRIGHTNESS+percent, 100)
    elif sign == "-":
        BRIGHTNESS = max(BRIGHTNESS-percent, 0)
    else:
        raise RuntimeError("How did we get here? Bad regular expression!")
    return [f"Brightness: {BRIGHTNESS}"]

def autoplay():
    global QUEUE
    QUEUE.append(AUTOPLAY)

def add_songs(songs: list[str]) -> list[str]:
    add_to_queue: list[Path] = []

    urls = [song for song in songs if uri_validator(song)]
    indeces = [int(index) for index in songs if index.isdigit()]
    names = [song for song in songs if not uri_validator(song) and not song.isdigit()]

    downloaded_songs = __list_downloads()

    add_to_queue.extend([song[1] for i, song in enumerate(downloaded_songs) if i in indeces])
    add_to_queue.extend(find_songs_by_name(names, downloaded_songs))
    add_to_queue.extend(download(urls))

    QUEUE.extend(add_to_queue)
    return [str(s) for s in add_to_queue]
    
def find_songs_by_name[T](songs: list[str], downloads: list[tuple[str, T]]) -> list[T]:
    out: list[T] = []
    for song in songs:
        best_fit = find_song_by_name(song, downloads)
        if best_fit:
            out.append(best_fit)
    return out
            
def find_song_by_name[T](song: str, downloads: list[tuple[str, T]]) -> Optional[T]:
    song = song.lower()
    best: Optional[T] = None
    for download in downloads:
        if song in download[0].lower():
            if best:
                return None
            best = download[1]
    return best
    

def clean_already_downloaded(s: str) -> Path:
    # Input Format: [download] {SONG_DIRECTORY}/{SONG_NAME} has already been downloaded
    # Output: SONG_NAME
    return Path(s[11+len(SONG_DIRECTORY): -28])

def clean_downloaded(s: str, actual_extension: str) -> Path:
    # Input Format: [download] Destination: {SONG_DIRECTORY}/{SONG_NAME}      -> gets converted to .mp3 after
    # Output: SONG_NAME
    file = Path(s[24+len(SONG_DIRECTORY):])
    return Path(splitext(file)[0] + actual_extension)


def list_queue() -> list[str]:
    if not QUEUE:
        return []
    q = [f"{i}: {str(song)}" for i, song in enumerate(QUEUE)]
    if PLAYING:
        q[0] = q[0] + " (playing)"
    else:
        q[0] = q[0] + " (paused)"
    return q

def __list_downloads() -> list[tuple[str, Path]]:
    songs: list[tuple[str, Path]] = []
    for maybe_song in Path(SONG_DIRECTORY).iterdir():
        if not maybe_song.is_file():
            continue
        if str(maybe_song).endswith(COLOR_FILE_EXTENSION):
            continue
        song = maybe_song.name
        songs.append((song[0:song.find("[")], Path(maybe_song.name)))
    return songs

def list_downloads() -> list[str]:
    return [f"{i}: {song[0]}" for i, song in enumerate(__list_downloads())]

def delete_songs(indeces: list[int]) -> list[str]:
    global QUEUE
    global NEXT_SONG
    if 0 in indeces:
        NEXT_SONG = True
    
    removed_songs = [str(song) for i, song in enumerate(QUEUE) if i in indeces]
    QUEUE = [song for i, song in enumerate(QUEUE) if i not in indeces]
    return removed_songs
        

def play():
    global PLAYING
    PLAYING = True

def pause():
    global PLAYING
    PLAYING = False

def clear_queue():
    QUEUE.clear()

async def exit():
    if MUSIC:
        await MUSIC.stop()
    if LIGHTS:
        await LIGHTS.set_brightness(0)
        await LIGHTS.pause()
        await LIGHTS.close()

def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False

if __name__ == '__main__':
    print(find_song_by_name("oversea", __list_downloads()))