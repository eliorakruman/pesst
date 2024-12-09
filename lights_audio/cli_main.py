import asyncio
from client.pesst_audio_cli import cli
from client.pesst_audio_core import setup, queue_handler
from asyncio import gather, run

async def main():
    await setup()
    cli_task = asyncio.create_task(cli())
    queue_handler_task = asyncio.create_task(queue_handler())

    try:
        await asyncio.gather(cli_task, queue_handler_task)
    except asyncio.CancelledError:
        print("Tasks were cancelled.")
        await cli_task
        await queue_handler_task
    print(cli_task.exception())

if __name__ == '__main__':
    run(main())
