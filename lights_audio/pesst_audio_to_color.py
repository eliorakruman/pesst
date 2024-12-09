import librosa
import numpy as np
import matplotlib.pyplot as plt

def audio_to_colors_with_timestamps(file_path):
    # Load the audio file
    y, sr = librosa.load(file_path)  # Load the first 30 seconds for demo

    # Extract audio features
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)  # Chroma (pitch class)
    rms = librosa.feature.rms(y=y)  # Root Mean Square (intensity)

    # Generate timestamps (in seconds)
    times = librosa.frames_to_time(np.arange(len(rms[0])), sr=sr)

    with open(file_path + ".color", "w") as f:
        # Generate colors based on features
        for i, time in enumerate(times):
            # Map chroma to hue
            hue = np.mean(chroma[:, i]) * 360  # Scale chroma to 360 degrees
            # Map RMS (loudness) to brightness
            brightness = min(1, rms[0, i] / max(rms[0]))  # Normalize to [0, 1]
            # Convert hue and brightness to RGB
            color = plt.cm.hsv(hue / 360)[:3]  # HSV colormap, discard alpha
            color = tuple(int(c * brightness * 255) for c in color)  # Scale to 0-255

            f.write(f"{round(float(time), 3)} {color[0]} {color[1]} {color[2]}\n")

# Example usage
audio_file = "./songs/Playboi Carti - Evil Jordan⧸EVILJ0RDAN (Official Lyric Video) [Y_tXa6IT3i4].mp3"  # Replace with your audio file
audio_to_colors_with_timestamps(audio_file)
