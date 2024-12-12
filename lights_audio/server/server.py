from asyncio import run
try:
    import machine # type: ignore
    import network # type: ignore
    import neopixel # type: ignore
    ON_PICO = True
    IP = "10.42.0.100"
    PORT = 8080
    WLAN_USERNAME = "bob"
except ImportError:
    ON_PICO = False
    IP = "127.0.0.1"
    PORT = 8080
    
DEBUG = True

from protocol import DONE, PAUSE, START, UPLOAD, OK, ERR
from asyncio import StreamReader, StreamWriter, start_server, gather, sleep

# Prints timestamps and prints colors instead of using hardware lights

def log(s: str):
    if DEBUG:
        print(s)

try:
    from time import ticks_ms, ticks_diff # type: ignore
except ImportError:
    ticks_ms = None
    ticks_diff = None
    from time import time_ns

def gettime():
    if ticks_ms:
        return ticks_ms()
    else:
        return time_ns() / 1_000_000

def gettimediff(t1, t2):
    if ticks_diff:
        return ticks_diff(t1, t2) / 1000
    return (t1 - t2) / 1000

SOUND: bytearray = bytearray([0, 0, 255, 255, 255])  # timestamp, r, g, b
DELAY = 0

class AudioServer:
    def __init__(self, pin_number: int = 1, led_count: int = 60):
        try:
            pin = machine.Pin(pin_number)
            self.led_count = led_count
            self.np = neopixel.NeoPixel(pin, led_count)
        except:
            if ON_PICO:
                raise
        self.sound_index = 0
        self.prev_index = -1
        self.paused = False
        self.timestamp = 0
        self.last_time = gettime()
        self.wlan = None

    async def run(self):
        if ON_PICO:
            ip = await self.wlan_connect()
        else:
            ip = "127.0.0.1"
        print(ip)
        await gather(
            start_server(self.listen, ip, PORT),
            self.update_lights()
            )

    async def wlan_connect(self) -> str:
        wlan = network.WLAN(network.STA_IF)
        self.wlan = wlan
        wlan.active(True)
        wlan.connect(WLAN_USERNAME)
        while True:
            print('Waiting for connection...', wlan.status() )
            await sleep(1)
            if wlan.isconnected():
                ip = wlan.ifconfig()[0]
                print(f'Connected on {ip}')
                return ip
    
    async def listen(self, reader: StreamReader, writer: StreamWriter):
        global SOUND
        print("Listening...")
        while True:
            tokens = (await reader.read(1024)).decode().split()
            if not tokens:
                return
            print(tokens)
            if tokens:
                cmd = tokens[0]
                log(cmd)
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
                    self.reset(float(tokens[1]))
                    await self.send_ok(writer)
                elif cmd == UPLOAD:
                    if len(tokens) != 2 or not tokens[1].isdigit():
                        await self.send_err(writer)
                        continue
                    self.reset(0)
                    num_bytes = int(tokens[1])
                    SOUND = bytearray([0, 0, 255, 255, 255])
                    await self.send_ok(writer)
                    SOUND.extend(await reader.readexactly(num_bytes))
                    await self.send_ok(writer)
                else:
                    await self.send_err(writer)
    
    def reset(self, time: float):
        self.paused = False
        self.sound_index = 0
        self.timestamp = time
        self.last_time = gettime()
                
    async def update_lights(self):
        while True:
            if not self.paused:
                time = gettime()
                time_diff = gettimediff(time, self.last_time)
                self.timestamp += time_diff
                self.last_time = time

            color = self.find_color_from_timestamp()
            if not self.paused and self.sound_index != 0 and self.sound_index != self.prev_index:
                self.prev_index = self.sound_index
                if ON_PICO:
                    self.display_color(color)
                else:
                    self.display_color_dbg(color)

            await sleep(0.05)
    
    def find_color_from_timestamp(self) -> tuple[int, int, int]:
        while self.sound_index < len(SOUND)-5:
            timestamp = int.from_bytes(SOUND[self.sound_index:self.sound_index+2], "big") / 10
            if timestamp >= self.timestamp:
                break
            self.sound_index += 5
        r = SOUND[self.sound_index+2]
        g = SOUND[self.sound_index+3]
        b = SOUND[self.sound_index+4]
        return r, g, b
    
    def display_color_dbg(self, rgb_color: tuple[int, int, int]):
        print(f"T:{self.timestamp}: {{ .red={rgb_color[0]}, .green={rgb_color[1]}, .blue={rgb_color[2]} }}")
    
    def display_color(self, rgb_color: tuple[int, int, int]):
        for i in range(self.led_count):
            self.np[i] = rgb_color # type: ignore
            self.np.write()
    
    
    async def send_err(self, writer: StreamWriter):
        writer.write(ERR.encode())
        await writer.drain()

    async def send_ok(self, writer: StreamWriter):
        writer.write(OK.encode())
        await writer.drain()
    
if __name__ == '__main__':
    run(AudioServer().run())