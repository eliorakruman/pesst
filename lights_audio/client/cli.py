from pesst_audio_cli import cli
from pesst_audio_core import setup, queue_handler
from asyncio import gather, run, create_task, CancelledError

async def main():
    await setup()
    cli_task = create_task(cli())
    queue_handler_task = create_task(queue_handler())

    try:
        await gather(cli_task, queue_handler_task)
    except CancelledError:
        print("Tasks were cancelled.")
        await cli_task
        await queue_handler_task
    print(cli_task.exception())

if __name__ == '__main__':
    run(main())
