#!/usr/bin/env python3
"""
Test the complete transcription pipeline
1. Simulate Arduino recording (create test WAV file)
2. Convert WAV to MP3
3. Send to Jetson TX2 transcription script
4. Verify transcription appears in web dashboard
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def create_test_wav_file(duration=5, sample_rate=16000):
    """
    Create a test WAV file using ffmpeg (sine wave with speech simulation)
    
    Args:
        duration (int): Duration in seconds
        sample_rate (int): Sample rate in Hz
    
    Returns:
        str: Path to created WAV file
    """
    
    output_file = "test_audio.wav"
    
    print(f"Creating test WAV file: {output_file}")
    
    try:
        # Create a test audio file with ffmpeg
        # This creates a sine wave that simulates speech
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', f'sine=frequency=440:duration={duration}',
            '-ar', str(sample_rate),
            '-ac', '1',
            '-y',
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Created test WAV file: {output_file}")
            return output_file
        else:
            print(f"❌ Failed to create WAV file: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating WAV file: {e}")
        return None

def convert_wav_to_mp3(wav_file):
    """
    Convert WAV to MP3 using the conversion script
    
    Args:
        wav_file (str): Path to WAV file
    
    Returns:
        str: Path to MP3 file
    """
    
    print(f"Converting {wav_file} to MP3...")
    
    try:
        # Use the conversion script
        result = subprocess.run([
            sys.executable, 'convert_wav_to_mp3.py', wav_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            mp3_file = wav_file.replace('.wav', '.mp3')
            if os.path.exists(mp3_file):
                print(f"✅ Converted to MP3: {mp3_file}")
                return mp3_file
            else:
                print("❌ MP3 file not found after conversion")
                return None
        else:
            print(f"❌ Conversion failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return None

def test_transcription_api():
    """
    Test the transcription API endpoint
    
    Returns:
        bool: True if API is working
    """
    
    print("Testing transcription API...")
    
    try:
        # Test with a sample transcription
        test_data = {
            "transcription": "Test message from pipeline",
            "source": "test-pipeline"
        }
        
        response = requests.post(
            "http://localhost:3000/api/transcribe",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ API is working")
            return True
        else:
            print(f"❌ API error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed: {e}")
        return False

def run_jetson_transcription(mp3_file):
    """
    Run the Jetson transcription script
    
    Args:
        mp3_file (str): Path to MP3 file
    
    Returns:
        bool: True if transcription succeeded
    """
    
    print(f"Running Jetson transcription on {mp3_file}...")
    
    try:
        # Run the Jetson transcription script
        result = subprocess.run([
            sys.executable, '../jetson-transcribe/main.py', mp3_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Transcription completed")
            print("Output:", result.stdout)
            return True
        else:
            print(f"❌ Transcription failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running transcription: {e}")
        return False

def check_transcriptions_in_dashboard():
    """
    Check if transcriptions appear in the dashboard
    
    Returns:
        bool: True if transcriptions are found
    """
    
    print("Checking transcriptions in dashboard...")
    
    try:
        response = requests.get("http://localhost:3000/api/transcribe", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('transcriptions'):
                transcriptions = data['transcriptions']
                print(f"✅ Found {len(transcriptions)} transcriptions in dashboard")
                
                # Show recent transcriptions
                for i, trans in enumerate(transcriptions[:3]):
                    print(f"  {i+1}. [{trans['source']}] {trans['text']}")
                
                return True
            else:
                print("❌ No transcriptions found in dashboard")
                return False
        else:
            print(f"❌ Failed to fetch transcriptions: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking dashboard: {e}")
        return False

def main():
    print("🔥 Firefighter Helmet Transcription Pipeline Test")
    print("=" * 50)
    
    # Step 1: Test API
    if not test_transcription_api():
        print("\n❌ API test failed. Make sure the Next.js server is running on port 3000")
        return
    
    # Step 2: Create test WAV file
    wav_file = create_test_wav_file()
    if not wav_file:
        print("\n❌ Failed to create test WAV file")
        return
    
    # Step 3: Convert to MP3
    mp3_file = convert_wav_to_mp3(wav_file)
    if not mp3_file:
        print("\n❌ Failed to convert to MP3")
        return
    
    # Step 4: Run transcription
    if not run_jetson_transcription(mp3_file):
        print("\n❌ Transcription failed")
        return
    
    # Step 5: Check dashboard
    time.sleep(2)  # Wait a moment for the transcription to be processed
    if not check_transcriptions_in_dashboard():
        print("\n❌ Transcription not found in dashboard")
        return
    
    print("\n🎉 Pipeline test completed successfully!")
    print("\nNext steps:")
    print("1. Upload the Arduino sketch to your ESP32")
    print("2. Record audio using the Arduino")
    print("3. Convert WAV to MP3")
    print("4. Run transcription script")
    print("5. Check dashboard for results")
    
    # Cleanup
    try:
        os.remove(wav_file)
        os.remove(mp3_file)
        print(f"\n🧹 Cleaned up test files")
    except:
        pass

if __name__ == "__main__":
    main()
