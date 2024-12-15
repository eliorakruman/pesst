

import face_recognition
import cv2
import numpy as np
from picamera2 import Picamera2
import os
import socket
import network
from utime import sleep
import sys

PHOTO_DIR: str = "./photos"
SERVER_ADDR: str = "<ip>"   # server address to be filled here
HOTSPOT: str = "<hotspot>"  # hotspot name to be filled here
PORT: int = 0   # port number to be filled here
ENCODINGS: list = []
NAMES: list = []


def __register_new_user(image, encoding):
    new_name = input("Type your name here or q to quit: ")
    if new_name != "q":
        cv2.imwrite(f"{PHOTO_DIR}/{new_name}", image)
        ENCODINGS.append(encoding)
        NAMES.append(new_name)
        return name
    return None

# Initialize Picamera2 camera object, configure and start video stream thread
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(HOTSPOT)
while not wlan.isconnected():
    print('Waiting for connection...', wlan.status())
    sleep(3)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((SERVER_ADDR, PORT))
except ConnectionError:
    print("Connection expired")
    sys.exit(0)
sock.send("face_rec".encode())
# load images from photo library and generate encodings
for image_file in os.listdir(PHOTO_DIR):
    image_tensor = face_recognition.load_image_file(image_file)
    ENCODINGS.append(face_recognition.face_encodings(image_tensor)[0])
    NAMES.append(image_file[:image_file.find(".")])


process_this_frame = True
border_color = (0, 0, 255)
while True:
    # Capture a frame from the camera
    frame = picam2.capture_array()

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    # Convert the image from BGR (OpenCV format) to RGB (face_recognition format)
#     rgb_small_frame = small_frame[:, :, ::-1]

    # Process every other frame for efficiency
    if process_this_frame:
        # Find all face locations and encodings
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        face_names = []
        for face_encoding in face_encodings:
            # Check for matches
            matches = face_recognition.compare_faces(ENCODINGS, face_encoding)
            name = "Unknown"

            # Use the known face with the smallest distance
            face_distances = face_recognition.face_distance(ENCODINGS, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = NAMES[best_match_index]
                if "blacklisted:" in name:
                    border_color = (255, 0, 0)

                    sock.send("red")
                else:
                    border_color = (0, 0, 255)
                    sock.send("green")
            else:
                temp = __register_new_user(frame, face_encoding)
                name = temp if temp is not None else "Unknown"
            face_names.append(name)

    process_this_frame = not process_this_frame

    # Display results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations to full size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), border_color, 2)

        # Label the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), border_color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, border_color, 1)

    # Show the resulting image
    cv2.imshow('Video', frame)

    # Break the loop on 'Esc' key press
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Stop the camera and close windows
picam2.stop()
cv2.destroyAllWindows()
