from pathlib import Path


DEBUG = False
LIGHTS_LOCAL_IP = "127.0.0.1"
LIGHTS_REMOTE_IP = "172.20.10.4"
LIGHTS_PORT = 8080
SYN_INTERVAL = 10 # Seconds
SONG_DIRECTORY = "songs/"
AUDIO_FORMAT = "mp3"
EMPTY_FILE = Path("./empty_file")
COLOR_FILE_EXTENSION = ".color"

def log(s: str):
    if DEBUG:
        print(s)

