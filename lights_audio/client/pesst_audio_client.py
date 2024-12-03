from protocol import START, PAUSE, UPLOAD, OK, ERR, InvalidFormatError

from asyncio import open_connection, IncompleteReadError

class AudioClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
    
    async def connect(self):
        reader, writer = await open_connection(self.host, self.port)
        self.reader = reader
        self.writer = writer
    
    async def start(self, seconds: float = 0) -> bool:
        self.writer.write(START.encode())
        self.writer.write(f" {round(seconds, 3)}".encode())
        await self.writer.drain()
        return await self.is_ok()
    
    async def pause(self) -> bool:
        self.writer.write(PAUSE.encode())
        await self.writer.drain()
        return await self.is_ok()
    
    async def upload(self, file_path) -> bool:
        self.writer.write(UPLOAD.encode())
        await self.writer.drain()
        # Give server time to delete previous file
        if not await self.is_ok():
            return False
        with open(file_path, "rb") as f:
            self.writer.writelines(f)
        return await self.is_ok()
    
    async def is_ok(self) -> bool:
        res = (await self.reader.readexactly(2)).decode()
        try:
            extra_data = await self.reader.read(1)  # Attempt to read one more byte
            if extra_data:
                raise InvalidFormatError(f"Unexpected extra data received: {extra_data}")
        except IncompleteReadError:
            pass 
        if res == OK:
            return True
        if res == ERR:
            return False
        raise InvalidFormatError
    
