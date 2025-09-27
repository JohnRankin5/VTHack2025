#!/usr/bin/env python3
"""
Convert WAV files to MP3 for testing the transcription pipeline
This script converts Arduino-recorded WAV files to MP3 format
"""

import os
import sys
import subprocess
from pathlib import Path

def convert_wav_to_mp3(wav_file_path, output_dir=None):
    """
    Convert WAV file to MP3 using ffmpeg
    
    Args:
        wav_file_path (str): Path to the WAV file
        output_dir (str): Output directory (optional)
    
    Returns:
        str: Path to the converted MP3 file
    """
    
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ffmpeg is not installed or not in PATH")
        print("Install ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/")
        return None
    
    # Validate input file
    if not os.path.exists(wav_file_path):
        print(f"Error: File {wav_file_path} not found")
        return None
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.dirname(wav_file_path)
    
    # Create output filename
    wav_name = Path(wav_file_path).stem
    mp3_file_path = os.path.join(output_dir, f"{wav_name}.mp3")
    
    print(f"Converting {wav_file_path} to {mp3_file_path}")
    
    try:
        # Convert WAV to MP3 using ffmpeg
        cmd = [
            'ffmpeg',
            '-i', wav_file_path,
            '-acodec', 'mp3',
            '-ab', '128k',  # 128 kbps bitrate
            '-ar', '16000', # 16 kHz sample rate
            '-ac', '1',     # Mono
            '-y',           # Overwrite output file
            mp3_file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully converted to {mp3_file_path}")
            return mp3_file_path
        else:
            print(f"❌ Conversion failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return None

def batch_convert_wav_files(directory):
    """
    Convert all WAV files in a directory to MP3
    
    Args:
        directory (str): Directory containing WAV files
    """
    
    if not os.path.exists(directory):
        print(f"Error: Directory {directory} not found")
        return
    
    wav_files = list(Path(directory).glob("*.wav"))
    
    if not wav_files:
        print(f"No WAV files found in {directory}")
        return
    
    print(f"Found {len(wav_files)} WAV files to convert")
    
    converted_files = []
    for wav_file in wav_files:
        mp3_file = convert_wav_to_mp3(str(wav_file))
        if mp3_file:
            converted_files.append(mp3_file)
    
    print(f"\n✅ Converted {len(converted_files)} files successfully")
    return converted_files

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python convert_wav_to_mp3.py <wav_file>")
        print("  python convert_wav_to_mp3.py <directory>")
        print("\nExamples:")
        print("  python convert_wav_to_mp3.py audio_12345.wav")
        print("  python convert_wav_to_mp3.py /path/to/wav/files/")
        return
    
    input_path = sys.argv[1]
    
    if os.path.isfile(input_path):
        # Convert single file
        if input_path.lower().endswith('.wav'):
            convert_wav_to_mp3(input_path)
        else:
            print("Error: Input file must be a WAV file")
    elif os.path.isdir(input_path):
        # Convert all WAV files in directory
        batch_convert_wav_files(input_path)
    else:
        print(f"Error: {input_path} is not a valid file or directory")

if __name__ == "__main__":
    main()
