

import face_recognition
import cv2
import numpy as np
from picamera2 import Picamera2

# Initialize the Picamera2
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

image = "./photoes/paras_1.jpg"


# Load a sample picture and learn how to recognize it.
paras = face_recognition.load_image_file(image)
paras_face_encoding = face_recognition.face_encodings(paras)[0]

# Load a second sample picture and learn how to recognize it.
#efren = face_recognition.load_image_file(image2)
#efren_face_encoding = face_recognition.face_encodings(efren)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    paras_face_encoding,
    #efren_face_encoding
]
known_face_names = [
    "Paras",
    #"Efren"
]


# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

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
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # Use the known face with the smallest distance
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
    
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
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Label the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Show the resulting image
    cv2.imshow('Video', frame)

    # Break the loop on 'Esc' key press
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Stop the camera and close windows
picam2.stop()
cv2.destroyAllWindows()
