from pathlib import Path
from protocol import BRIGHTNESS, START, PAUSE, UPLOAD, OK, ERR, InvalidFormatError

from asyncio import open_connection

class LightClient:
    def __init__(self, host: str, port: int, enabled: bool = True):
        self.enabled = enabled
        self.host = host
        self.port = port
    
    async def connect(self):
        if not self.enabled:
            return
        reader, writer = await open_connection(self.host, self.port)
        self.reader = reader
        self.writer = writer
    
    async def close(self):
        if not self.enabled:
            return
        self.writer.close()
        await self.writer.wait_closed()
    
    async def __send_command(self, s: str):
        if not self.enabled:
            return True
        self.writer.write(s.encode())
        await self.writer.drain()
        return await self.is_ok()
    
    async def start(self, seconds: float = 0) -> bool:
        return await self.__send_command(f"{START} {round(seconds, 3)}")
    
    async def pause(self) -> bool:
        return await self.__send_command(f"{PAUSE}")
    
    async def set_brightness(self, percent: int):
        return await self.__send_command(f"{BRIGHTNESS} {percent}")

    async def upload(self, file_path: Path) -> bool:
        if not self.enabled:
            return True
        with open(file_path, "rb") as f:
            contents = f.read()
        if not await self.__send_command(f"{UPLOAD} {len(contents)}"):
            return False
        if len(contents) > 0:
            self.writer.write(contents)
            await self.writer.drain()
        ok = await self.is_ok()
        return ok
    
    async def is_ok(self) -> bool:
        if not self.enabled:
            return True
        res = (await self.reader.readexactly(2)).decode()
        if res == OK:
            return True
        if res == ERR:
            return False
        raise InvalidFormatError
    