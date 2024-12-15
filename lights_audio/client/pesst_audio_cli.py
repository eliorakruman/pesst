import asyncio
from os import system, name
from sys import argv
from platform import system as system_
from shlex import split
import pesst_audio_core as pesst_audio_core

# Requirements
# yt-dlp : https://github.com/yt-dlp/yt-dlp
# mpv : https://mpv.io/

REPL_HELP_MESSAGE = \
f"""\
Description: REPL to download and play music from youtube
Overview: command [options...]
Commands:
add song... : Adds a song to the queue by url or songname if downloaded
skip : Skips a song
queue : Lists songs in the queue
search song : Searches for a song on youtube. Download it via download index/name
download url... : Downloads songs by url. Supports youtube and soundcloud
uninstall song : Uninstall a song by index or name
downloads : List downloaded songs
brightness <percent> : Sets brightness to percent
brightness +|-<percent> : Increments or decrements brightness by percent
autoplay : Auto queues songs from downloads. Must clear queue to exit autoplay. Skipping will proceed to the next random song
delete id... : Deletes songs from the queue by id
play : Plays queue
pause : Pauses queue
clear : Clear the queue
exit : Exits the program

cls : Clear display
help : Display help message
credits : Display credits\
"""

REPL_INTRO_MESSAGE = \
f"""\
{argv[0]} 0.1.0 (main, Oct  1 2024, 02:05:46) on {system_()}
Type "help" or "credits" for more information.\
"""

CREDITS = \
f"""\
Thanks to Archer, Daniel, Efren, Eliora, Nathan, and Paras for being wonderful teammates.\
"""

async def ainput(prompt: str) -> str:
    """Asynchronous version of input() using a thread executor."""
    try:
        return await asyncio.get_running_loop().run_in_executor(None, input, prompt)
    except:
        return ""

async def cli():
    print(REPL_INTRO_MESSAGE)
    while True:
        output: list[str] = []
        input_ = await ainput(">>> ")
        tokens: list[str] = list(map(str.strip, split(input_)))
        if not tokens:
            continue

        command = tokens[0]
        args = tokens[1:]

        match command:
            case "add":
                if len(args) == 0:
                    output.append("add requires songs/urls")
                else:
                    output.extend(pesst_audio_core.add_songs(args) or ["None found"])
            case "queue":
                output.extend(pesst_audio_core.list_queue())
            case "search":
                if len(args) != 1:
                    output.append("Search accepts only 1 argument")
                else:
                    output.extend(pesst_audio_core.search(args[0]))
            case "download":
                output.extend(str(path) for path in pesst_audio_core.download(args))
            case "uninstall":
                output.extend(str(path) for path in pesst_audio_core.uninstall(args))
            case "downloads":
                output.extend(pesst_audio_core.list_downloads())
            case "brightness":
                output.extend(await pesst_audio_core.brightness(args))
            case "autoplay":
                pesst_audio_core.autoplay()
            case "delete":
                try:
                    song_indeces: list[int] = list(map(int, args))
                    output.extend(pesst_audio_core.delete_songs(song_indeces))
                except ValueError:
                    output.extend(["Not a list of integers"])
            case "skip":
                pesst_audio_core.delete_songs([0])
            case "play":
                pesst_audio_core.play()
            case "pause":
                pesst_audio_core.pause()
            case "clear":
                pesst_audio_core.clear_queue()
            case "exit":
                await pesst_audio_core.exit()
                return
            case "cls":
                system('cls' if name == 'nt' else 'clear')
            case "help":
                output.append(REPL_HELP_MESSAGE)
            case "credits":
                output.append(CREDITS)
            case _:
                output.append("Unrecognized command")
            
        if output:
            print("\n".join(output))
