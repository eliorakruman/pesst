import socket
import threading
import networkx

from enum import Enum


def recv_send(client_thread, receiver_elem):
    while True:
        # print(client_thread)
        try:
            text = client_thread.recv(1024).decode()
        except KeyboardInterrupt:
            exit()
        # print(text)
        receiver_elem.send(text.encode())


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(("", 1234))
try:
    sock.listen(5)
except KeyboardInterrupt:
    exit()
print("server started on port 1234")

color: str = "blue"
rec_flag: bool = False
sens_flag: bool = False
light_flag: bool = False
clients: list = []
receiver = None

while True:
    if rec_flag and rec_flag == sens_flag == light_flag:
        break

    # Establish connection with client.
    c, addr = sock.accept()
    handshake: str = c.recv(1024).decode()
    if handshake == "face_rec":
        rec_flag = True
        clients.append(c)
    elif handshake == "motion_sensor":
        sens_flag = True
        clients.append(c)
    elif handshake == "light_system":
        light_flag = True
        receiver = c
    print('Got connection from', addr)

print("fully connected")

for client in clients:
    thread = threading.Thread(target=recv_send, args=[client, receiver])
    thread.start()
