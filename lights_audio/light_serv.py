import socket
from enum import Enum


def check_recv(val: str, client):
    if val is not None:
        client.send(val.encode())


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(("", 1234))
sock.listen(5)
color: str = "blue"
rec_flag: bool = False
sens_flag: bool = False
light_flag: bool = False
clients: list = [None]*3
while not rec_flag and not (rec_flag == sens_flag == light_flag):
    # Establish connection with client.
    c, addr = sock.accept()
    handshake: str = c.recv(1024).decode()
    if handshake == "face_rec":
        rec_flag = True
        clients[0] = c
    elif handshake == "motion_sensor":
        sens_flag = True
        clients[1] = c
    elif handshake == "light_system":
        light_flag = True
        clients[2] = c
    print('Got connection from', addr)
while True:
    check_recv(clients[0].recv(1024).decode(), clients[2])
    check_recv(clients[1].recv(1024).decode(), clients[2])

