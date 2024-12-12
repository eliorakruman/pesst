from pathlib import Path
from protocol import START, PAUSE, UPLOAD, OK, ERR, InvalidFormatError

from asyncio import open_connection

class AudioClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
    
    async def connect(self):
        reader, writer = await open_connection(self.host, self.port)
        self.reader = reader
        self.writer = writer
    
    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()
    
    async def start(self, seconds: float = 0) -> bool:
        self.writer.write(START.encode())
        self.writer.write(f" {round(seconds, 3)}".encode())
        await self.writer.drain()
        return await self.is_ok()
    
    async def pause(self) -> bool:
        self.writer.write(PAUSE.encode())
        await self.writer.drain()
        return await self.is_ok()
    
    async def upload(self, file_path: Path) -> bool:
        with open(file_path, "rb") as f:
            contents = f.read()
        self.writer.write(f"{UPLOAD} {len(contents)}".encode())
        await self.writer.drain()
        # Give server time to delete previous file
        if not await self.is_ok():
            return False
        if len(contents) > 0:
            self.writer.write(contents)
            await self.writer.drain()
        ok = await self.is_ok()
        return ok
    
    async def is_ok(self) -> bool:
        res = (await self.reader.readexactly(2)).decode()
        if res == OK:
            return True
        if res == ERR:
            return False
        raise InvalidFormatError
    