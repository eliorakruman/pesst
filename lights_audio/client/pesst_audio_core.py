from pathlib import Path
from os.path import splitext
from subprocess import run, CalledProcessError
from typing import Optional
from pesst_audio_player import AudioPlayer
from pesst_audio_client import AudioClient

SONG_DIRECTORY = "songs/"
AUDIO_FORMAT = "mp3"

# Current State: Used by Tick 
QUEUE: list[Path] = []
PLAYING: bool = True

PREVIOUS_QUEUE = []
PREVIOUS_PLAYING = True

FFPLAY: Optional[AudioPlayer] = None
LIGHTS: AudioClient = AudioClient("127.0.0.1", 8080)
LIGHTS.connect() # TODO: Do I need to await this? 

async def tick():
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
    global FFPLAY

    toggle_pause: bool = PLAYING != PREVIOUS_PLAYING
    next_song = QUEUE != PREVIOUS_QUEUE
    
    if not FFPLAY:
        return

    if toggle_pause:
        # TODO: How much of this do I need to await? Several don't have dependencies between eachother
        if PLAYING:
            FFPLAY.play()
            await FFPLAY.get_timestamp()
            LIGHTS.start(await FFPLAY.get_timestamp())
        else:
            FFPLAY.pause()
    elif next_song:
        if QUEUE:
            FFPLAY.stop()
            FFPLAY = AudioPlayer(QUEUE[0])
            FFPLAY.start()
        else: # No songs left
            FFPLAY.stop()
            FFPLAY = None
    else:
        return
    
    PREVIOUS_QUEUE = QUEUE
    PREVIOUS_PLAYING = PLAYING
    QUEUE = QUEUE.copy()
        

def add_songs(url: list[str]) -> list[Path]:
    command = [
        "yt-dlp",
        "-P", SONG_DIRECTORY,
        "--extract-audio",  # Optional: Extract only audio
        "--audio-format", AUDIO_FORMAT,  # Optional: Convert to mp3 format
        *url
    ]

    # Run the command
    try:
        result = run(command, check=True, text=True, capture_output=True)
    except CalledProcessError as e:
        return [f"Error occurred while downloading: {e}"]

    # Parse the yt-dlp output
    yt_dlp_output = result.stdout.splitlines()
    add_to_queue: list[Path] = [clean_downloaded(line, "."+AUDIO_FORMAT) for line in yt_dlp_output if line.startswith("[download] Destination")]
    add_to_queue.extend([clean_already_downloaded(line) for line in yt_dlp_output if "has already been downloaded" in line])
    
    QUEUE.extend(add_to_queue)
    return add_to_queue
    
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
    return [str(song) for song in QUEUE]

def delete_songs(songs: list[str]) -> list[str]:
    try:
        song_indeces: list[int] = map(int, songs)
    except ValueError:
        return ["Not a list of integers"]
    
    removed_songs = [song for i, song in enumerate(QUEUE) if i in song_indeces]
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