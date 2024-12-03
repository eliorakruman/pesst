import socket
import machine
import neopixel

n = 60  # Number of LEDs
pin = machine.Pin(1)
np = neopixel.NeoPixel(pin, n)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

color_codes: dict[str, tuple[int, int, int]] = {"red": (255, 0, 0), "white": (255, 255, 255), "green": (0, 255, 0), "blue": (0, 0, 255)}

for i in range(n):
    np[i] = (255, 255, 255)

wait_steps = -1

client.connect(("172.20.164.94", 1234))
client.send("light_system".encode())
while True:
    color = client.recv(1024).decode()
    if wait_steps == 0:
        wait_steps = -1
        for i in range(n):
            np[i] = (255, 255, 255)
    if color is not None and color in color_codes:
        for i in range(n):
            np[i] = color_codes[color]
        if color != "blue":
            wait_steps = 20
    if wait_steps != -1:
        wait_steps -= 1
