# pesst
Private Event Security System Technology: An Embedded System

COSI 142A, Fall 2024

The PESST system at a base level will have a central system that can communicate with the elements of our system
over an http server. There will be a facial recognition feature that will trigger an alarm system if a black-listed
individual attempts to enter the event. We will also have a tallying system that will be able to keep track of how
many people are in the event at one time. The system will be designed in stages. The first stage will include the
basic security features with facial recognition, the alarm, and the tallying device. The second stage will involve
advanced light features and an audio system.

## Lights and Audio
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

## Getting Started
### Requirements
- mpv : brew install mpv
- librosa : pip install librosa
- matplotlib : pip install matplotlib
- yt-dlp : pip install pt-dlp

These must be on your PATH

If you are running the server on the Pico, set :
pesst_audio_server's ON_PICO variable to true. This will attempt to connect the Pico to WAN. 
pesst_audio_core LIGHTS: AudioClient = AudioClient("127.0.0.1", 8080) IP Address

NOTE: THIS IS NOT WORKING RIGHT NOW PLEASE EFREN HELP WITH THE CONNECTING THE SERVER AND CLIENT ISSUE ON PICO
### Running: 
You MUST be in the lights_audio directory to run these!
Server first: 
`python3.12 server_main.py`

Then client + cli:
`python3.12 cli_main.py`

Type help for help, type `add <youtube url...>` to add a song or playlist to the queue.

