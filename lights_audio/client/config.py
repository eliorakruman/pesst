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
YOUTUBE_SECRETS_FILE = Path("./client_secret_251006524266-bp7ejcoqlqk03ml9o789cn84sl90nk3k.apps.googleusercontent.com.json")

def log(s: str):
    if DEBUG:
        print(s)

