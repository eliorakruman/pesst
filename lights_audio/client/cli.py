from os import mkdir
from typing import Literal
from config import SONG_DIRECTORY
from pesst_audio_cli import cli
from pesst_audio_core import setup, queue_handler
from asyncio import run, create_task, CancelledError, wait
from sys import argv

INVOCATION_HELP_MESSAGE = \
f"""\
Usage: python {argv[0]} [local|remote|none]
Opens up a repl\
"""

async def main():
    lights: Literal["local", "remote", "none"] = "local"
    for arg in argv[1:]:
        match arg:
            case "-help"|"--help"|"-h"|"help":
                print(INVOCATION_HELP_MESSAGE)
                exit(0)
            case "local":
                lights = "local"
            case "remote":
                lights = "remote"
            case "none":
                lights = "none"
            case _:
                print(f"Unrecognized argument: '{arg}'")

    await setup(lights)
    try:
        mkdir(SONG_DIRECTORY)
    except: ...
    cli_task = create_task(cli())
    queue_handler_task = create_task(queue_handler())

    try:
        await wait([cli_task])
        queue_handler_task.cancel()
    except CancelledError:
        print("Tasks were cancelled.")
        print(cli_task.exception())
        print(queue_handler_task.exception())

if __name__ == '__main__':
    run(main())
