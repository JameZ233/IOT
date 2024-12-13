import requests
import sounddevice as sd
import numpy as np
import webrtcvad
import wave
from io import BytesIO
# import os

# Audio and VAD configuration
SAMPLE_RATE = 16000  # Whisper works best at 16000 Hz
FRAME_DURATION = 30  # ms (10, 20, or 30 ms supported by webrtcvad)
CHANNELS = 1
SERVER_URL = "http://34.46.155.222:5000/process-audio"
VAD_MODE = 0  # 0 (very low sensitivity) to 3 (high sensitivity)
SILENCE_THRESHOLD = 1  # Time in seconds of silence before triggering transcription

# Initialize VAD
vad = webrtcvad.Vad()
vad.set_mode(VAD_MODE)

def record_and_detect():
    """Record audio and detect speech using VAD."""
    print("Listening for voice commands...")
    buffer = []
    silence_frames = 0
    max_silence_frames = int(SILENCE_THRESHOLD * 1000 / FRAME_DURATION)  # 1 second of silence

    def callback(indata, frames, time, status):
        nonlocal buffer, silence_frames
        if status:
            print(f"Audio input error: {status}")

        audio_frame = indata[:, 0].tobytes()
        if vad.is_speech(audio_frame, SAMPLE_RATE):
            buffer.append(audio_frame)
            silence_frames = 0
        elif buffer:
            silence_frames += 1
            if silence_frames > max_silence_frames:
                # Speech ended
                sd.stop()
                send_audio(b"".join(buffer))
                buffer = []
                silence_frames = 0

    with sd.InputStream(callback=callback, channels=CHANNELS, samplerate=SAMPLE_RATE, blocksize=int(SAMPLE_RATE * FRAME_DURATION / 1000), dtype="int16"):
        while True:
            sd.sleep(1000)
            
def send_audio(audio_data):
    """Send audio data to the server and play back the response."""
    try:
        print("Sending audio to server...")
        wave_io = BytesIO()
        with wave.open(wave_io, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data)
        wave_io.seek(0)

        response = requests.post(SERVER_URL, files={"audio": ("speech.wav", wave_io, "audio/wav")})
        if response.status_code == 200:
            print("Response received from server.")
            play_audio(response.content)
        else:
            print(f"Server error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
        
def play_audio(audio_data):
    """Play audio response."""
    with wave.open(BytesIO(audio_data), "rb") as wf:
        sample_rate = wf.getframerate()
        audio_data = wf.readframes(wf.getnframes())
        sd.play(np.frombuffer(audio_data, dtype=np.int16), samplerate=sample_rate)
        sd.wait()

if __name__ == "__main__":
    try:
        record_and_detect()
    except KeyboardInterrupt:
        print("Stopped by user.")