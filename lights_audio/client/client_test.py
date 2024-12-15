from pathlib import Path
from asyncio import run
from pesst_light_client import LightClient

# url =["https://youtube.com/playlist?list=PLt6HwsGlQ-seA3-e9c54MDA6Vtkt88niD&si=os9sxzUCc_3yzrWJ", "https://www.youtube.com/watch?v=859u6uiZdds&ab_channel=Spinnin%27Records"]

async def main():
    client = LightClient("127.0.0.1", 8080)
    await client.connect()
    await client.start()
    await client.pause()
    await client.upload(Path("./songs/Playboi Carti - Evil Jordan⧸EVILJ0RDAN (Official Lyric Video) [Y_tXa6IT3i4].mp3.color"))
    await client.start()

if __name__ == '__main__':
    run(main())
