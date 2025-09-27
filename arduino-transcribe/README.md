# Arduino Microphone Recording for Firefighter Helmet

This directory contains Arduino code and utilities for recording microphone data and testing the complete transcription pipeline.

## Files

- `arduino_microphone.ino` - Arduino sketch for recording audio
- `convert_wav_to_mp3.py` - Script to convert WAV files to MP3
- `test_pipeline.py` - Complete pipeline test script
- `README.md` - This file

## Hardware Requirements

### For ESP32 (Recommended)
- ESP32 development board
- I2S microphone (e.g., INMP441, SPH0645LM4H)
- SD card module
- SD card (formatted as FAT32)

### Pin Connections (ESP32)
```
I2S Microphone:
- VCC → 3.3V
- GND → GND
- WS → GPIO 25
- SCK → GPIO 32
- SD → GPIO 33

SD Card Module:
- VCC → 3.3V
- GND → GND
- MISO → GPIO 19
- MOSI → GPIO 23
- SCK → GPIO 18
- CS → GPIO 5
```

## Software Requirements

### Arduino IDE
1. Install ESP32 board support:
   - File → Preferences → Additional Board Manager URLs
   - Add: `https://dl.espressif.com/dl/package_esp32_index.json`
   - Tools → Board → Boards Manager → Search "ESP32" → Install

2. Install required libraries:
   - Tools → Manage Libraries → Search and install:
     - "SD" (built-in)
     - "SPI" (built-in)

### Python Dependencies
```bash
pip install requests
```

### FFmpeg (for audio conversion)
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/
```

## Usage

### 1. Upload Arduino Sketch
1. Connect ESP32 to computer via USB
2. Select board: Tools → Board → ESP32 Dev Module
3. Select port: Tools → Port → (your ESP32 port)
4. Upload the sketch

### 2. Record Audio
1. Open Serial Monitor (115200 baud)
2. Send commands:
   - `t` - Test microphone
   - `r` - Start recording (5 seconds)
   - `s` - Stop recording manually

### 3. Convert WAV to MP3
```bash
# Convert single file
python convert_wav_to_mp3.py audio_12345.wav

# Convert all WAV files in directory
python convert_wav_to_mp3.py /path/to/wav/files/
```

### 4. Test Complete Pipeline
```bash
# Make sure Next.js server is running on port 3000
python test_pipeline.py
```

### 5. Run Transcription
```bash
# From jetson-transcribe directory
python main.py /path/to/audio.mp3
```

## Testing the Pipeline

### Quick Test
1. Start Next.js server: `cd live-feed-map && npm run dev`
2. Run pipeline test: `python test_pipeline.py`
3. Check dashboard at `http://localhost:3000`

### Manual Test
1. Record audio with Arduino
2. Convert WAV to MP3
3. Run transcription script
4. Check dashboard for results

## Troubleshooting

### Arduino Issues
- **SD card not detected**: Check connections, format SD card as FAT32
- **No audio**: Check microphone connections, test with `t` command
- **Recording fails**: Ensure SD card has enough space

### Python Issues
- **FFmpeg not found**: Install FFmpeg and ensure it's in PATH
- **API connection failed**: Check if Next.js server is running on port 3000
- **Transcription fails**: Check if Whisper is installed on Jetson TX2

### Audio Quality
- **Poor transcription**: Ensure good microphone placement
- **Noise**: Use noise-canceling microphone or add filtering
- **Volume**: Adjust microphone gain or add automatic gain control

## File Formats

### WAV Format (Arduino Output)
- Sample Rate: 16 kHz
- Bit Depth: 16-bit
- Channels: Mono
- Format: PCM

### MP3 Format (Transcription Input)
- Sample Rate: 16 kHz
- Bitrate: 128 kbps
- Channels: Mono
- Format: MP3

## Integration with Firefighter Helmet

### Real-time Recording
- Modify `RECORD_TIME` for different durations
- Add voice activity detection (VAD)
- Implement automatic recording triggers

### Wireless Transmission
- Add WiFi module for wireless file transfer
- Implement FTP or HTTP file upload
- Add encryption for secure transmission

### Power Management
- Add battery monitoring
- Implement sleep modes
- Optimize for long-term operation

## Next Steps

1. **Hardware Integration**: Mount microphone in helmet
2. **Real-time Processing**: Stream audio directly to Jetson TX2
3. **Voice Commands**: Add keyword detection
4. **Noise Reduction**: Implement audio filtering
5. **Battery Life**: Optimize power consumption

## Support

For issues or questions:
1. Check this README
2. Review Arduino Serial Monitor output
3. Check Python script error messages
4. Verify hardware connections
5. Test individual components

---

**Happy coding! 🔥👨‍🚒**
