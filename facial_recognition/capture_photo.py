from picamera2 import Picamera2
import cv2
import os
import time

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

user_input = input("Enter name for photos: ")
output_path = "/home/pi/Raspberrypi_workshop/Face_Detection_System"

number_photos = 5  # Set the number of photos to capture
photo_count = 0  # Start at 0

# Ensure the output directory exists
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Print instructions for the user
print(f"Press the ENTER button to take {number_photos} photos, one at a time.")

while photo_count < number_photos:
    # Display a preview (optional)
    frame = picam2.capture_array()  # Capture an image as a NumPy array
    cv2.imshow('Preview', frame)

    # Check if the Enter key was pressed (ASCII value 13)
    if cv2.waitKey(1) == 13:  # 13 is the ASCII code for Enter
        # Create the output file path with a unique name
        output = f"{output_path}/{user_input}_{photo_count + 1}.jpg"

        # Check if the file already exists
        if os.path.exists(output):
            print(f"Error: {output} already exists.")
            choice = input("Do you want to overwrite it? (y/n): ")
            if choice.lower() != 'y':
                # Prompt for a new name or modify the existing one
                user_input_second = input("Enter a new base name for the photo: ")
                output = f"{output_path}/{user_input_second}_{photo_count + 1}.jpg"

        # Save the captured frame to a file
        cv2.imwrite(output, frame)
        print(f"Image {photo_count + 1} saved to {output}")
        photo_count += 1

# Clean up resources
picam2.stop()
cv2.destroyAllWindows()
