from typing import Literal
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

    with open(str(file_path) + ".color", "wb") as f:
        # Generate colors based on features
        for i, time in enumerate(times):
            # Map chroma to hue
            if emotion == "hype":
                # Red shift for hype songs
                loudness = rms[0, i] / max(rms[0])
                chroma_strength = np.mean(chroma[:, i])
                color = hype_color(loudness, chroma_strength)
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

def encode_line(timestamp: float, r: int, g: int, b: int):
    timestamp = int(timestamp * SIG_FIGS)
    return bytearray([*timestamp.to_bytes(2, "big"), r, g, b])

def hype_color(loudness, chroma_strength) -> tuple[int, int, int]:
    # Determine color based on energy and chroma
            if loudness > 0.8 and chroma_strength > 0.5:
                color = (255, 255, 255)  # White for very high energy and chroma
            else:
                # Adjust hue within a close range to red
                hue = (10 + 20 * (1 - chroma_strength)) % 360  # Allows slight orange and deeper red variations

                saturation = max(0.6, 1 - chroma_strength)
                brightness = max(0.3, loudness)  # Ensure some visibility in low energy

                # Normalize hue for colorsys input
                normalized_hue = hue / 360

                # Convert hue, saturation, and brightness to RGB
                r, g, b = colorsys.hsv_to_rgb(normalized_hue, saturation, brightness)
                color = (int(r * 255), int(g * 255), int(b * 255))  # Scale RGB to 0-255
            print(color)
            return color
# Example usage
if __name__ == '__main__':
    audio_file = Path("./songs/Ken Carson - overseas (Official Music Video) [80M6sAU9DY4].mp3")  # Replace with your audio file
    audio_to_colors_with_timestamps(audio_file, "hype")
