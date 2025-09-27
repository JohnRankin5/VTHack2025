import whisper
import requests
import sys
import os
import time

# Initialize the Whisper model
print("Loading Whisper model...")
model = whisper.load_model("base")
print("Model loaded successfully!")

def transcribe_audio(mp3_file_path):
    """Transcribe MP3 audio file to text."""
    try:
        print(f"Loading audio file: {mp3_file_path}")
        # Load audio file and transcribe
        audio = whisper.load_audio(mp3_file_path)
        audio = whisper.pad_or_trim(audio)
        
        print("Transcribing audio...")
        # Make prediction
        result = model.transcribe(audio)
        
        # Return the transcribed text
        return result["text"].strip()
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None

def send_transcription_to_server(transcription, server_url):
    """Send the transcription text to the Next.js API."""
    try:
        payload = {
            "transcription": transcription,
            "source": "jetson-tx2"
        }
        print(f"Sending transcription to: {server_url}")
        response = requests.post(server_url, json=payload, timeout=10)
        return response.status_code, response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending transcription: {e}")
        return None, None

def main():
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py <mp3_file_path>")
        print("Example: python main.py /path/to/audio.mp3")
        return
    
    mp3_file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(mp3_file_path):
        print(f"Error: File {mp3_file_path} not found")
        return
    
    # Server URL - updated to correct port
    server_url = "http://localhost:3000/api/transcribe"  # Next.js API route URL
    
    print(f"Processing file: {mp3_file_path}")
    print(f"Server URL: {server_url}")
    
    # Transcribe the audio
    transcription = transcribe_audio(mp3_file_path)
    
    if transcription is None:
        print("Failed to transcribe audio")
        return
        
    print(f"Transcription: {transcription}")
    
    # Send transcription to the web server
    status_code, response_data = send_transcription_to_server(transcription, server_url)
    
    if status_code == 200:
        print("✅ Transcription successfully sent to the server!")
        print(f"Response: {response_data}")
    else:
        print(f"❌ Failed to send transcription. Status code: {status_code}")
        if response_data:
            print(f"Response: {response_data}")

if __name__ == "__main__":
    main()
