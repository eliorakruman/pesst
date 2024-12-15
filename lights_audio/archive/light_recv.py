import socket
import machine
import neopixel
import network
from utime import sleep

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('bob')
while not wlan.isconnected():
    print('Waiting for connection...', wlan.status())
    sleep(3)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')


n = 60  # Number of LEDs
pin = machine.Pin(1)
np = neopixel.NeoPixel(pin, n)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

color_codes: dict[str, tuple[int, int, int]] = {"red": (255, 0, 0), "white": (255, 255, 255), "green": (0, 255, 0), "blue": (0, 0, 255)}

for i in range(n):
    np[i] = (255, 255, 255)
np.write()


wait_steps = -1
wait_color = False
client.connect(("10.42.0.241", 1234))
client.send("light_system".encode())
while True:
    for i in range(n):
        np[i] = (255, 255, 255)
        np.write()
    color = client.recv(1024).decode()
    if wait_color and color == "white":
        wait_color = False
    if color is not None and color in color_codes and not wait_color:
        for i in range(n):
            np[i] = color_codes[color]
            np.write()
        if color == "blue":
            wait_color = True

