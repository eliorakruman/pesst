import asyncio
from pathlib import Path
from os.path import splitext # type: ignore
from subprocess import run, CalledProcessError
from typing import Optional
from client.pesst_audio_player import MPVWrapper
from client.pesst_audio_client import AudioClient

SONG_DIRECTORY = "songs/"
AUDIO_FORMAT = "mp3"

# Current State: Used by Tick 
QUEUE: list[Path] = []
PLAYING: bool = True

PREVIOUS_QUEUE = []
PREVIOUS_PLAYING = True

MUSIC: Optional[MPVWrapper] = None
LIGHTS: AudioClient = AudioClient("127.0.0.1", 8080)

async def setup():
    await LIGHTS.connect() 

async def queue_handler():
    """
    Compares Current State to Previous State and dispatches events to ffplay and raspberry PI
    NOTE: Only 1 event can happen a tick
    1. Next song
    2. Pause/Unpause
    """
    global QUEUE
    global PLAYING
    global PREVIOUS_QUEUE
    global PREVIOUS_PLAYING
    global MUSIC
    global LIGHTS

    while True:
        await asyncio.sleep(0.1)
        if MUSIC and MUSIC.ended:
            print("ENDED")
            QUEUE.pop(0)

        pause: bool = not PLAYING and PREVIOUS_PLAYING
        unpause: bool = PLAYING and not PREVIOUS_PLAYING
        next_song: bool = bool((not PREVIOUS_QUEUE and QUEUE) or (QUEUE and PREVIOUS_QUEUE[0] != QUEUE[0]))
        no_songs: bool = bool(PREVIOUS_QUEUE and not QUEUE)

        if pause and MUSIC:
            await MUSIC.pause()
        elif unpause and MUSIC:
            await MUSIC.play()
        elif next_song:
            await play_next_song(QUEUE[0])
        elif no_songs and MUSIC:
            await MUSIC.stop()
            MUSIC = None
        
        PREVIOUS_QUEUE = QUEUE
        PREVIOUS_PLAYING = PLAYING
        QUEUE = QUEUE.copy()

async def play_next_song(path: Path):
    global MUSIC
    global PLAYING
    PLAYING = True
    if MUSIC:
        await MUSIC.stop()
    MUSIC = MPVWrapper(SONG_DIRECTORY / path)
    await MUSIC.start()
    await asyncio.sleep(0.1)
        

def add_songs(urls: list[str]) -> list[str]:
    command = [
        "yt-dlp",
        "-P", SONG_DIRECTORY,
        "--extract-audio",  # Optional: Extract only audio
        "--audio-format", AUDIO_FORMAT,  # Optional: Convert to mp3 format
        *urls
    ]

    # Run the command
    try:
        result = run(command, check=True, text=True, capture_output=True)
    except CalledProcessError as e:
        return [f"Error occurred while downloading: {e}"]

    # Parse the yt-dlp output
    yt_dlp_output = result.stdout.splitlines() # type: ignore
    add_to_queue: list[Path] = [clean_downloaded(line, "."+AUDIO_FORMAT) for line in yt_dlp_output if line.startswith("[download] Destination")]
    add_to_queue.extend([clean_already_downloaded(line) for line in yt_dlp_output if "has already been downloaded" in line])
    
    QUEUE.extend(add_to_queue)
    return [str(s) for s in add_to_queue]
    
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
    return [f"{i}: {str(song)}" for i, song in enumerate(QUEUE)]

def delete_songs(songs: list[str]) -> list[str]:
    global QUEUE
    try:
        song_indeces: list[int] = list(map(int, songs))
    except ValueError:
        return ["Not a list of integers"]
    
    removed_songs = [str(song) for i, song in enumerate(QUEUE) if i in song_indeces]
    QUEUE = [song for i, song in enumerate(QUEUE) if i not in song_indeces]
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