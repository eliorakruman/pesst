import asyncio
from os import system, name
from sys import argv
from platform import system as system_ # type: ignore
import pesst_audio_core as pesst_audio_core

# Requirements
# yt-dlp : https://github.com/yt-dlp/yt-dlp
# ffplay && ffmpeg

INVOCATION_HELP_MESSAGE = \
f"""\
Usage: python {argv[0]}
Opens up a repl\
"""

REPL_HELP_MESSAGE = \
f"""\
Description: REPL to download and play music from youtube
Overview: command [options...]
Commands:
add url... : Adds a song to the queue
skip : Skips a song
list : Lists songs in the queue
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
    if len(argv) > 1 and argv[1] in ["-help", "--help", "-h", "help"]:
        print(INVOCATION_HELP_MESSAGE)
        exit(0)

    print(REPL_INTRO_MESSAGE)
    while True:
        output: list[str] = []
        try:
            tokens: list[str] = (await ainput(">>> ")).split()
            if not tokens:
                continue

            command = tokens[0]
            args = tokens[1:]

            match command:
                case "add":
                    if len(args) == 0:
                        output.append("add requires urls")
                    else:
                        pesst_audio_core.add_songs(args)
                case "list":
                    output.extend(pesst_audio_core.list_queue())
                case "delete":
                    output.extend(pesst_audio_core.delete_songs(args))
                case "skip":
                    pesst_audio_core.delete_songs(["0"])
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
            
        except KeyboardInterrupt:
            output.append("Keyboard Interrupt")

        if output:
            print("\n".join(output))

        