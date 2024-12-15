from protocol import DONE, MIN_DIFF, PAUSE, SIG_FIGS, START, UPLOAD, OK, ERR, BRIGHTNESS, DEFAULT_BRIGHTNESS
from asyncio import StreamReader, StreamWriter, start_server, gather, sleep, run
try:
    import machine # type: ignore
    import network # type: ignore
    import neopixel # type: ignore
    from env import SSID, PASSWORD # type: ignore
    ON_PICO = True
except ImportError:
    ON_PICO = False
    

PORT = 8080
DEBUG = True # Prints timestamps and prints colors instead of using hardware lights


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

SOUND: bytearray = bytearray([0, 0, 100, 100, 100])  # timestamp, r, g, b
DELAY = 0.1

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
        self.brightness = DEFAULT_BRIGHTNESS / 100 # Brightness as a percent
        self.last_brightness = -1

    async def run(self):
        if ON_PICO:
            ip = await self.wlan_connect(SSID, PASSWORD)
        else:
            ip = "127.0.0.1"
        print(ip)
        await gather(
            start_server(self.listen, ip, PORT),
            self.update_lights()
            )

    async def wlan_connect(self, ssid: str, password: str) -> str:
        wlan = network.WLAN(network.STA_IF)
        self.wlan = wlan
        wlan.active(True)
        wlan.connect(ssid, password)
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
            log(tokens)
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
                self.reset(float(tokens[1]))
                await self.send_ok(writer)
            elif cmd == BRIGHTNESS:
                if len(tokens) != 2 or not tokens[1].isdigit():
                    await self.send_err(writer)
                    continue
                self.brightness = int(tokens[1]) / 100
                await self.send_ok(writer)
            elif cmd == UPLOAD:
                if len(tokens) != 2 or not tokens[1].isdigit():
                    await self.send_err(writer)
                    continue
                self.reset(0)
                num_bytes = int(tokens[1])
                SOUND = bytearray([0, 0, 100, 100, 100])
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
            color: tuple[int, int, int] = tuple(int(c*self.brightness) for c in color) # type: ignore
            if not self.paused and self.sound_index != 0 and self.sound_index != self.prev_index or self.last_brightness != self.brightness:
                self.prev_index = self.sound_index
                if ON_PICO:
                    self.display_color(color)
                else:
                    self.display_color_dbg(color)
                self.last_brightness = self.brightness

            await sleep(MIN_DIFF/2)
    
    def find_color_from_timestamp(self) -> tuple[int, int, int]:
        while self.sound_index < len(SOUND)-5:
            timestamp = int.from_bytes(SOUND[self.sound_index:self.sound_index+2], "big") / SIG_FIGS
            if timestamp >= self.timestamp + DELAY:
                break
            self.sound_index += 5
        r = SOUND[self.sound_index+2]
        g = SOUND[self.sound_index+3]
        b = SOUND[self.sound_index+4]
        return r, g, b
    
    def display_color_dbg(self, rgb_color: tuple[int, int, int]):
        print(f"T:{self.timestamp:.2f}: B:{self.brightness}: {{ .red={rgb_color[0]:.2f}, .green={rgb_color[1]:.2f}, .blue={rgb_color[2]:.2f} }}")
    
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