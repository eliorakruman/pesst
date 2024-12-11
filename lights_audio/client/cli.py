from pesst_audio_cli import cli
from pesst_audio_core import setup, queue_handler
from asyncio import run, create_task, CancelledError, wait

async def main():
    await setup()
    cli_task = create_task(cli())
    queue_handler_task = create_task(queue_handler())

    try:
        await wait([cli_task])
        queue_handler_task.cancel()
    except CancelledError:
        print("Tasks were cancelled.")
        print(cli_task.exception())

if __name__ == '__main__':
    run(main())
