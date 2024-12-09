from asyncio import run
from server.pesst_audio_server import AudioServer

if __name__ == '__main__':
    run(AudioServer("127.0.0.1", 8080).run())