from pathlib import Path
import librosa
import numpy as np
import matplotlib.pyplot as plt
from protocol import DECIMAL_PLACES, SIG_FIGS, MIN_DIFF

def audio_to_colors_with_timestamps(file_path: Path):
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

# Example usage
if __name__ == '__main__':
    audio_file = Path("./songs/DISCO LINES - BABY GIRL [Lxu_9m23qHg].mp3")  # Replace with your audio file
    audio_to_colors_with_timestamps(audio_file)
