from protocol import PAUSE, START, UPLOAD, OK, ERR
from asyncio import open_connection

SOUND_FILE = "sound"
DELAY = 0

class AudioServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.paused = False
        self.timestamp = 0
    
    async def listen(self):
        reader, writer = await open_connection(self.host, self.port)
        self.reader = reader
        self.writer = writer

        while True:
            tokens = (await reader.read()).split()
            if not tokens:
                await self.send_err()
                continue

            cmd = tokens[0]
            if cmd == PAUSE:
                self.paused = True
            elif cmd == START:
                self.paused = False
                self.timestamp = float(tokens[1])
            elif cmd == UPLOAD:
                ...  # Delete existing sound file
                self.send_ok()
                # Read a file and store to SOUND_FILE
                self.send_ok()
            else:
                writer.write(ERR.encode())
            
            # TODO: Process existing song stuffs
            # Increment timestamp if unpaused
    
    async def send_err(self):
        await self.writer.write(ERR.encode())

    async def send_ok(self):
        await self.writer.write(OK.encode())