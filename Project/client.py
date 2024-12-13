import sys
sys.path.append('/home/zwz/proj/lib/python3.11/site-packages')
from requests import post
import time
# from threading import Thread
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import numpy as np
from webrtcvad import Vad
import wave
import cv2
import alsaaudio
# import ffmpeg
from io import BytesIO
import RPi.GPIO as GPIO

SERVER_URL = f"http://34.46.155.222:5000/upload"

# Pin configuration
BUTTON_PIN = 17

# Set up GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set pin as input with pull-up resistor

# Add event detection with debounce time
DEBOUNCE_TIME = 200  # Debounce time in milliseconds

# Set up video configuration
picam2 = Picamera2()
video_config=picam2.create_video_configuration()
picam2.configure(video_config)

# Audio configuration
SAMPLE_RATE = 16000  # Whisper works best at 16000 Hz
FRAME_DURATION = 30  # ms (10, 20, or 30 ms supported by webrtcvad)
CHANNELS = 1
PERIOD_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)
RECORD_TIME=100 # Time in ms for recording

# Initialization microphone
pcm = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, channels=CHANNELS, 
                    rate=SAMPLE_RATE, format=alsaaudio.PCM_FORMAT_S16_LE, periodsize=PERIOD_SIZE)

# Interrupt
def capture_data(channel):
    """Record video & audio & detect speech using VAD."""
    global pcm, picam2
    print("Listening for voice commands...")
    # Start Recording Video
    picam2.start()
    picam2.start_recording(H264Encoder(),output='video.mp4')
    record_time = RECORD_TIME
    start_time = time.time()
    # Start Recording Audio
    while time.time()-start_time <=5:
        frames, data = pcm.read()
        # print(frames, len(data))
        if data:
            audio_frame = np.frombuffer(data, dtype=np.int16).tobytes()
            audio_buffer.write(audio_frame)
        # print('record', time.time()-start_time)
    # Stop both Audio and Video Recording
    picam2.stop_recording()
    picam2.stop()
    print('recording done')
    # Send both to the server
    send_data(audio_buffer)
    # Reset the pointer and content of the buffer
    audio_buffer.seek(0)
    audio_buffer.truncate(0)
          
def send_data(audio_buffer):
    """Send both audio and video data to the server, and play back the response."""
    try:
        print("Sending audio and video to server...")
        
        # Writing buffer to the audio file for transferring
        wave_io = BytesIO()
        with wave.open(wave_io, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_buffer.getvalue())
        wave_io.seek(0)
        
        print('2')
        files = {
            "audio": ("speech.wav", wave_io, "audio/wav"),
            "video": ("video.mp4", open('video.mp4','rb'), "video/mp4")
        }
        print('0')
        # Sending Audio and Video to the server
        response = post(SERVER_URL, files=files)
        print('1')
        if response.status_code == 200:
            print("Response received from server.")
            play_audio(response.content)
        else:
            print(f"Server error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
# Receive and Play the Audio
def play_audio(audio_data):
    """Play audio response."""

    # Open the WAV audio data from BytesIO
    with wave.open(BytesIO(audio_data), "rb") as wf:
        periodsize = wf.getframerate() // 2
        print('width',wf.getsampwidth())
        pcm_out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NONBLOCK, channels=wf.getnchannels(), 
                            rate=wf.getframerate(), format=alsaaudio.PCM_FORMAT_S16_LE, periodsize=periodsize, device='default')
        print('wfchannel', wf.getnchannels())
        data = wf.readframes(periodsize)
        print('audio_data',len(audio_data))
        print("Playing audio response...")
        while data:
        # Play the audio response
            pcm_out.write(data)
            data = wf.readframes(periodsize)
        pcm_out.close()
# Interrupt Enabled
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=capture_data, bouncetime=DEBOUNCE_TIME)  

if __name__ == "__main__":
    """Main function to manage video and audio streaming."""
    
    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
            print('Waiting for Interrupt')
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        picam2.close()
        pcm.close()
        GPIO.cleanup()