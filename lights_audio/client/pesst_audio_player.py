import asyncio
from config import log
import os
from typing import Optional
import json

class MPVWrapper:
    def __init__(self, filepath, socket_path="/tmp/mpvsocket"):
        self.filepath = filepath
        self.socket_path = socket_path
        self.process = None
        self.event_task = None
        self.ended = False

    async def start(self):
        """Start the mpv player with IPC enabled."""
        self.process = await asyncio.create_subprocess_exec(
            'mpv', f'--input-ipc-server={self.socket_path}', self.filepath,
            '--idle', '--quiet',  # Enable idle mode after playback ends
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        # Wait until the IPC server socket is ready
        for _ in range(10):  # Retry up to 10 times
            if os.path.exists(self.socket_path):
                break
            await asyncio.sleep(0.1)
        else:
            raise RuntimeError("Failed to start mpv IPC server.")

        # Start listening for events
        self.event_task = asyncio.create_task(self._listen_for_events())

    async def send_command(self, command):
        """Send a JSON command to the mpv IPC socket."""
        if not os.path.exists(self.socket_path):
            raise RuntimeError(f"Socket {self.socket_path} does not exist.")
        
        try:
            reader, writer = await asyncio.open_unix_connection(self.socket_path)
            writer.write((command + '\n').encode())
            await writer.drain()
            response = await reader.read(1024)
            writer.close()
            await writer.wait_closed()
            return response.decode().strip()
        except Exception as e:
            log(f"Failed to send command: {e}")
            return None

    async def _listen_for_events(self):
        """Listen for events from mpv's IPC."""
        retries = 5  # Number of connection retries
        while retries > 0:
            try:
                reader, writer = await asyncio.open_unix_connection(self.socket_path)
                log("Connected to audio socket")
                while True:
                    line = await reader.readline()
                    if not line:
                        break
                    try:
                        event = json.loads(line.decode())
                        log(event)
                        if event.get("event") == "end-file":
                            self.ended = True
                    except json.JSONDecodeError as e:
                        log(f"Failed to decode event: {e}")
                writer.close()
                await writer.wait_closed()
                break
            except (ConnectionRefusedError, FileNotFoundError) as e:
                log(f"Failed to connect to socket: {e}. Retrying...")
                retries -= 1
                await asyncio.sleep(0.5)
        else:
            print("Max retries reached. Could not connect to the mpv socket.")

    async def play(self):
        """Resume playback."""
        await self.send_command('{"command": ["set_property", "pause", false]}')

    async def pause(self):
        """Pause playback."""
        await self.send_command('{"command": ["set_property", "pause", true]}')

    async def stop(self):
        """Stop playback."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
        if self.event_task:
            self.event_task.cancel()

    async def get_timestamp(self) -> Optional[int]:
        """Retrieve the current playback timestamp in seconds."""
        response = await self.send_command('{"command": ["get_property", "time-pos"]}')
        if response:
            try:
                result = json.loads(response)
                return result.get("data", None)  # Return the timestamp if available
            except json.JSONDecodeError as e:
                log(f"Error decoding JSON response: {e}")
        return None


# Example usage
async def main():
    player = MPVWrapper("./songs/Playboi Carti - Evil Jordan⧸EVILJ0RDAN (Official Lyric Video) [Y_tXa6IT3i4].mp3")
    await player.start()
    print("Playing...")
    await asyncio.sleep(5)  # Let it play for 5 seconds
    
    timestamp = await player.get_timestamp()
    print(f"Current timestamp: {timestamp} seconds")
    
    print("Pausing...")
    await player.pause()
    await asyncio.sleep(2)  # Wait while paused
    
    timestamp = await player.get_timestamp()
    print(f"Current timestamp: {timestamp} seconds (paused)")
    
    print("Resuming...")
    await player.play()
    await asyncio.sleep(5)  # Let it play for 5 more seconds
    
    timestamp = await player.get_timestamp()
    print(f"Current timestamp: {timestamp} seconds (resumed)")

    while not player.ended:
        await asyncio.sleep(1)
    
    await player.stop()
    print("Stopped.")

if __name__ == '__main__':
    asyncio.run(main())
