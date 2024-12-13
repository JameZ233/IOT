from flask import Flask, request, send_file, jsonify
from whisper import load_model
from io import BytesIO
from gtts import gTTS
from pydub import AudioSegment
# from pymongo import MongoClient
import soundfile as sf
import numpy as np
from llm import interpret_command
import json
from colorRecognition import process_video
import subprocess

H264_FILE = 'raw_video.h264'
MP4_FILE = 'output_video.mp4'

# Initialize Flask app
app = Flask(__name__)

# Load whisper model
whisper_model = load_model('tiny.en')

# Initialize MongoDB client
# client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
# try:
#     client.admin.command('ping')
#     print('MongoDB connection is successful.')
# except Exception as e:
#     print('Error:', e)

# db = client.stereo_camera
# print('Databases:', client.list_database_names())
# print('Stereo Camera Collections:', db.list_collection_names())

def bad_request_handler(text):
    return text

# Map commands to ColorSense functions
command_map = {
    "detect_color": process_video,
    "unknown_cmd": bad_request_handler
}

def convert_to_speech(text):
    print("Converting response to speech...")
    tts = gTTS(text, lang="en")
    mp3_audio = BytesIO()
    tts.write_to_fp(mp3_audio)
    mp3_audio.seek(0)

    # Convert the MP3 to WAV using pydub
    audio_segment = AudioSegment.from_mp3(mp3_audio)
    
    # Convert audio to WAV format and save to a BytesIO object
    wav_audio = BytesIO()
    audio_segment.export(wav_audio, format="wav")
    wav_audio.seek(0)
    return wav_audio

def raw_h264_to_mp4(raw_data):
    """Save raw H.264 byte data to a .h264 file"""
    with open(H264_FILE, 'wb') as f:
        f.write(raw_data)
    print(f"Raw H.264 data saved to {H264_FILE}")
    """Convert raw H.264 file to MP4 using ffmpeg"""
    try:
        subprocess.run(['ffmpeg', '-y', '-f', 'h264', '-i', H264_FILE, '-c:v', 'copy', MP4_FILE], check=True)
        print(f"Conversion successful: {MP4_FILE}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting to MP4: {e}")

@app.post("/upload")
def process_audio():
    """Receive audio, transcribe, process command, and return speech."""
    try:
        # Receive audio file
        audio_file = request.files["audio"]
        audio_data = audio_file.read()
        # print("audio_data:", len(audio_data))

        # Read audio data from BytesIO and convert to numpy array
        with BytesIO(audio_data) as audio_io:
            audio_np, sample_rate = sf.read(audio_io, dtype="float32")
            # print("audio_np:", len(audio_np))
        
        # Ensure the sample rate matches Whisper's requirement
        if sample_rate != 16000:
            raise ValueError("Audio must be sampled at 16 kHz for Whisper.")
        
        # Transcribe audio
        print("Transcribing audio...")
        transcription = whisper_model.transcribe(audio_np)
        text = transcription["text"]
        print(f"Transcription: {text}")
        
        response_text = "Cannot identify color."
        # Process command
        # if 'color' in text:
        llm_res = interpret_command(text)
        cmd = json.loads(llm_res)
        func_name = cmd.get("name")
        args = cmd.get("args", [])
        print(func_name, args)
        if func_name in command_map:
            video_file = request.files["video"]
            video_data = video_file.read()
            raw_h264_to_mp4(video_data)
            if func_name == 'detect_color':
                response_text = command_map[func_name](MP4_FILE, *args)
            else:
                response_text = command_map[func_name](*args)
        
        print(f"Response: {response_text}")

        # Convert response to speech
        audio_res = convert_to_speech(response_text)
        
        # Send back audio response
        return send_file(audio_res, mimetype="audio/wav")
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        del audio_data
        del video_data

# Run the server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
