from protocol import DONE, PAUSE, START, UPLOAD, OK, ERR
from asyncio import StreamReader, StreamWriter, start_server, gather, sleep

try:
    from time import ticks_ms, ticks_diff
except ImportError:
    ticks_ms = None
    ticks_diff = None
    from time import time_ns

def gettime():
    if ticks_ms:
        return ticks_ms()
    else:
        return time_ns() * 1_000_000

def gettimediff(t1, t2):
    if ticks_diff:
        return ticks_diff(t1, t2)
    return t1 - t2

SOUND: list[tuple[float, int, int, int]] = [(0, 255, 255, 255)]  # timestamp, r, g, b
DELAY = 0

class AudioServer:
    def __init__(self, host: str, port: int):
        self.sound_index = 0
        self.host = host
        self.port = port
        self.paused = False
        self.timestamp = 0
        self.last_time = gettime()

    async def run(self):
        await gather(
            start_server(self.listen, self.host, self.port),
            self.update_lights()
            )
    
    async def listen(self, reader: StreamReader, writer: StreamWriter):
        print("Listening...")
        while True:
            tokens = (await reader.read(1024)).decode().split()
            if not tokens:
                return
            print(tokens)
            if tokens:
                cmd = tokens[0]
                if cmd == DONE:
                    writer.close()
                    await writer.wait_closed()
                    return
                elif cmd == PAUSE:
                    self.paused = True
                    await self.send_ok(writer)
                elif cmd == START:
                    if len(tokens) != 2:
                        await self.send_err(writer)
                        continue
                    self.paused = False
                    self.sound_index = 0
                    self.timestamp = float(tokens[1])
                    self.last_time = gettime()
                    await self.send_ok(writer)
                elif cmd == UPLOAD:
                    SOUND.clear()
                    SOUND.append((0, 255, 255, 255))
                    await self.send_ok(writer)
                    error = False
                    
                    while tokens := (await reader.readline()).decode().split():
                        if len(tokens) != 4:
                            error = True
                            break
                        SOUND.append((float(tokens[0]), int(tokens[1]), int(tokens[2]), int(tokens[3])))
                    if error:
                        await self.send_err(writer)
                    else:
                        await self.send_ok(writer)
                else:
                    await self.send_err(writer)
                
    async def update_lights(self):
        while True:
            if not self.paused:
                time = gettime()
                time_diff = gettimediff(time, self.last_time) / 1000
                self.timestamp += time_diff
                self.last_time = time

            color = self.find_color_from_timestamp()
            if not self.paused and self.sound_index != 0:
                self.display_color(color)

            await sleep(0.001)
    
    def find_color_from_timestamp(self) -> tuple[int, int, int]:
        while self.sound_index < len(SOUND)-1 and SOUND[self.sound_index][0] < self.timestamp:
            self.sound_index += 1
        _, r, g, b = SOUND[self.sound_index]
        return (r, g, b)
    
    def display_color(self, rgb_color: tuple[int, int, int]):
        print(f"{{ .red={rgb_color[0]}, .green={rgb_color[1]}, .blue={rgb_color[2]} }}")
    
    
    async def send_err(self, writer: StreamWriter):
        writer.write(ERR.encode())
        await writer.drain()

    async def send_ok(self, writer: StreamWriter):
        writer.write(OK.encode())
        await writer.drain()