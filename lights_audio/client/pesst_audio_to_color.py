from typing import Literal
from math import sqrt, e as E
import colorsys
from pathlib import Path
import librosa
import numpy as np
import matplotlib.pyplot as plt
from protocol import DECIMAL_PLACES, SIG_FIGS, MIN_DIFF

def audio_to_colors_with_timestamps(file_path: Path, emotion: Literal["unknown", "hype"]):
    # Load the audio file
    y, sr = librosa.load(str(file_path))  # Load the first 30 seconds for demo

    # Extract audio features
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)  # Chroma (pitch class)
    rms = librosa.feature.rms(y=y)  # Root Mean Square (intensity)

    # Generate timestamps (in seconds)
    times = librosa.frames_to_time(np.arange(len(rms[0])), sr=sr)
    prev_time = -1

    mx_loudness = rms[0, 0]
    mn_loudness = rms[0, 0]
    average_loudness = 0
    for i, time in enumerate(times):
        loudness = rms[0, i]
        mx_loudness = max(mx_loudness, loudness)
        mn_loudness = min(mn_loudness, loudness)
        average_loudness = (average_loudness * i + loudness) / (i+1)
    loudness_std_top = 0
    for i, time in enumerate(times):
        loudness = rms[0, i]
        loudness_std_top += pow(loudness - average_loudness, 2)
    loudness_std = sqrt(loudness_std_top / len(times))

    print(average_loudness, loudness_std)

    with open(str(file_path) + ".color", "wb") as f:
        # Generate colors based on features
        for i, time in enumerate(times):
            # Map chroma to hue
            if emotion == "hype":
                # Red shift for hype songs
                loudness = rms[0, i]
                chroma_strength = np.mean(chroma[:, i])
                color = hype_color(mx_loudness, mn_loudness, average_loudness, loudness_std, loudness, chroma_strength, loudness_std/average_loudness)
            else:
                hue = np.mean(chroma[:, i]) * 360  # Scale chroma to 360 degrees
                # Map RMS (loudness) to brightness
                brightness = min(1, rms[0, i] / max(rms[0]))  # Normalize to [0, 1]
                # Convert hue and brightness to RGB
                color = plt.cm.hsv(hue / 360)[:3]  # HSV colormap, discard alpha # type: ignore
                color = tuple(int(c * brightness * 255) for c in color)  # Scale to 0-255

            timestamp = round(float(time), DECIMAL_PLACES)
            if timestamp - prev_time >= MIN_DIFF:
                f.write(encode_line(timestamp, color[0], color[1], color[2]))
                prev_time = timestamp
        if times.any():
            f.write(encode_line(timestamp+0.1, 0, 0, 0)) # End with black

def encode_line(timestamp: float, r: int, g: int, b: int):
    timestamp = int(timestamp * SIG_FIGS)
    return bytearray([*timestamp.to_bytes(2, "big"), r, g, b])

def norm(x, mn, mx):
    # normalise x to range [-1,1]
    nom = (x - mn) * 2.0
    denom = mx- mn
    return  nom/denom - 1.0

def sigmoid(x, k=0.1):
    # sigmoid function
    # use k to adjust the slope
    s = 1 / (1 + np.exp(-x / k)) 
    return s

i = 0
def hype_color(mx_loudness: float, mn_loudness: float, average_loudness: float, loudness_stdev: float, loudness, chroma_strength, cv) -> tuple[int, int, int]:
    global i
    i+=1
    if i == 100:
        exit()
    # Determine color based on energy and chroma
    # if loudness < average_loudness - loudness_stdev*1.5:
    #     return (0, 0, 0)  # Black for very low loudness
    # elif loudness > average_loudness + loudness_stdev * 1.5:
    #     return (255, 255, 255)  # White for very high energy and chroma
    #     # Black - RED - WHITE
    # else:
    x = norm(loudness, mn_loudness, mx_loudness)
    rx = norm(loudness+loudness_stdev/2, mn_loudness, mx_loudness)
    r = sigmoid(rx)
    g = sigmoid(x)
    b = sigmoid(x)
    print(r, g, b)
    # G, B: Sigmoid * 255
    # x = (loudness - average_loudness) / CV
    # R: (Sigmoid(x-10)) * 255
    return (int(r * 255), int(g * 255), int(b * 255))  # Scale RGB to 0-255
# Example usage
if __name__ == '__main__':
    audio_file = Path("./songs/Ken Carson - overseas (Official Music Video) [80M6sAU9DY4].mp3")  # Replace with your audio file
    audio_to_colors_with_timestamps(audio_file, "hype")
