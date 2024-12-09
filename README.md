# pesst
Private Event Security System Technology: An Embedded System

COSI 142A, Fall 2024

The PESST system at a base level will have a central system that can communicate with the elements of our system
over an http server. There will be a facial recognition feature that will trigger an alarm system if a black-listed
individual attempts to enter the event. We will also have a tallying system that will be able to keep track of how
many people are in the event at one time. The system will be designed in stages. The first stage will include the
basic security features with facial recognition, the alarm, and the tallying device. The second stage will involve
advanced light features and an audio system.

# Requirements
## Lights and Audio
- mpv : brew install mpv
- yt-dlp : pip install pt-dlp

These must be on your PATH

This was made very last minute, so there are some quirks:
- After queuing a song, press enter to show the prompt again
- Exiting doesn't stop the program since the MUSIC and SONG player task is still running
- I have no clue why     

``` python
cli_task = asyncio.create_task(cli())
queue_handler_task = asyncio.create_task(queue_handler()) 
await asyncio.gather(cli_task, queue_handler_task)
```
works but 
``` python
await asyncio.gather(cli(), queue_handler())
```
doesn't