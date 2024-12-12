from pathlib import Path


DEBUG = False
LIGHTS_IP = "127.0.0.1"
LIGHTS_IP = "10.42.0.108"
LIGHTS_PORT = 8080
SYN_INTERVAL = 10 # Seconds
SONG_DIRECTORY = "songs/"
AUDIO_FORMAT = "mp3"
EMPTY_FILE = Path("./empty_file")

def log(s: str):
    if DEBUG:
        print(s)

