import wave
import numpy as np
import pyaudio

# Define audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
BITS_PER_SAMPLE = 16
RECORD_TIME = 5  # seconds
FILENAME = "test_audio.wav"

# Create a PyAudio object
p = pyaudio.PyAudio()

# Open an audio stream for recording
stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=1024)

print(f"Recording for {RECORD_TIME} seconds...")

# Store audio data in a list
frames = []

# Record audio for the specified time
for i in range(0, int(SAMPLE_RATE / 1024 * RECORD_TIME)):
    data = stream.read(1024)
    frames.append(data)

# Stop the recording
stream.stop_stream()
stream.close()
p.terminate()

# Write the audio data to a WAV file
print(f"Saving audio to {FILENAME}...")

with wave.open(FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))

print("Recording complete.")
