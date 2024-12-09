import asyncio
import os
import json

class MPVWrapper:
    def __init__(self, filepath, socket_path="/tmp/mpvsocket"):
        self.filepath = filepath
        self.socket_path = socket_path
        self.process = None

    async def start(self):
        """Start the mpv player with IPC enabled."""
        self.process = await asyncio.create_subprocess_exec(
            'mpv', f'--input-ipc-server={self.socket_path}', self.filepath,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        # Wait until the IPC server socket is ready
        for _ in range(10):  # Retry up to 10 times
            if os.path.exists(self.socket_path):
                return
            await asyncio.sleep(0.1)
        raise RuntimeError("Failed to start mpv IPC server.")

    async def send_command(self, command):
        """Send a JSON command to the mpv IPC socket and optionally receive a response."""
        if not os.path.exists(self.socket_path):
            raise RuntimeError(f"Socket {self.socket_path} does not exist.")
        
        try:
            reader, writer = await asyncio.open_unix_connection(self.socket_path)
            writer.write((command + '\n').encode())
            await writer.drain()
            response = await reader.read(1024)  # Read response if available
            writer.close()
            await writer.wait_closed()
            return response.decode().strip()
        except Exception as e:
            print(f"Failed to send command: {e}")
            return None

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

    async def get_timestamp(self):
        """Retrieve the current playback timestamp in seconds."""
        response = await self.send_command('{"command": ["get_property", "time-pos"]}')
        if response:
            try:
                result = json.loads(response)
                return result.get("data", None)  # Return the timestamp if available
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
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
    
    await player.stop()
    print("Stopped.")

asyncio.run(main())
