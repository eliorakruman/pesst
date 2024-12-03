import asyncio
import re

"""
TODO: Pause and Resume are NOT WORING AGH
"""

class AudioPlayer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.process = None
        self._paused = False
        self._current_time = 0.0
        self._task = None

    async def start(self):
        """Start the ffplay process."""
        if self.process:
            raise RuntimeError("Playback already started.")
        
        self.process = await asyncio.create_subprocess_exec(
            'ffplay', '-autoexit', '-nodisp', '-i', self.filepath,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE  # Capture stderr for timestamps
        )

        self._task = asyncio.create_task(self._read_stderr())
    
    async def _read_stderr(self):
        """Read and parse ffplay's stderr for timestamp updates."""
        if not self.process or not self.process.stderr:
            return
        
        timestamp_pattern = re.compile(r"time=(\d+:\d+:\d+\.\d+)")
        
        while True:
            line = await self.process.stderr.readline()
            if not line:
                break
            decoded_line = line.decode('utf-8').strip()
            
            match = timestamp_pattern.search(decoded_line)
            if match:
                time_str = match.group(1)
                self._current_time = self._parse_timestamp(time_str)
    
    def _parse_timestamp(self, time_str):
        """Convert timestamp string (hh:mm:ss.ms) to seconds."""
        h, m, s = map(float, time_str.split(':'))
        return h * 3600 + m * 60 + s
    
    async def send_command(self, command):
        """Send a command to the ffplay process."""
        if not self.process or self.process.stdin is None:
            raise RuntimeError("Playback process is not running.")
        self.process.stdin.write(f'{command}\n'.encode())
        await self.process.stdin.drain()
    
    async def play(self):
        """Start playback (resume if paused)."""
        if not self.process:
            await self.start()
        elif self._paused:
            await self.send_command('p')  # 'p' toggles play/pause in ffplay
            self._paused = False
    
    async def pause(self):
        """Pause playback."""
        if self.process and not self._paused:
            await self.send_command('p')  # 'p' toggles play/pause in ffplay
            self._paused = True
    
    async def stop(self):
        """Stop playback and terminate the process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
            self._paused = False
            self._current_time = 0.0
            if self._task:
                self._task.cancel()
    
    async def get_timestamp(self):
        """Get the current playback timestamp in seconds."""
        return self._current_time
    
    async def wait(self):
        """Wait for the playback to finish."""
        if self.process:
            await self.process.wait()

# Usage example
async def main():
    player = AudioPlayer("./songs/VIOLENCE [ZZTXFr6lowI].mp3")
    
    await player.play()
    print("Playing...")
    await asyncio.sleep(2)  # Let it play for 2 seconds
    
    current_time = await player.get_timestamp()
    print(f"Current timestamp: {current_time:.2f} seconds")
    
    await player.pause()
    print("Paused...")
    await asyncio.sleep(10)
    
    await player.play()
    print("Resumed...")
    await asyncio.sleep(2)
    
    current_time = await player.get_timestamp()
    print(f"Current timestamp: {current_time:.2f} seconds")
    
    await player.stop()
    print("Stopped.")

# Run the example
if __name__ == '__main__':
    asyncio.run(main())
