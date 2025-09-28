# Mac Camera Live Feed Map Setup

This setup allows your Mac camera to act as one of the firefighter helmets in the live feed map, running object detection with real-time video streaming.

## Features

- **Live Video Streaming**: Real-time video feed from your Mac camera displayed in the web interface
- **Object Detection**: Uses YOLOv8 to detect objects relevant to firefighters (doors, windows, people, etc.)
- **Hand Gesture Recognition**: Custom OpenCV-based gesture detection for firefighter signals
- **Overlay Controls**: Toggle object detection, gesture detection, and HUD overlays independently
- **Real-time Integration**: Live detection results are displayed as overlays on the video stream
- **Priority System**: Objects and gestures are prioritized based on firefighter relevance
- **WebSocket Streaming**: Low-latency video streaming via WebSocket connection

## Prerequisites

1. **Python 3.8+** installed
2. **Next.js server** running on localhost:3000
3. **Mac camera** access permissions

## Installation

### 1. Test the Setup

First, run the test script to verify everything is working:

```bash
cd live-feed-map
source venv/bin/activate
python test_setup.py
```

This will test all dependencies and camera access.

### 2. Check System Status

After starting the servers, you can check if everything is working:

```bash
python check_status.py
```

This will verify that both the Next.js server and video stream server are running correctly.

### 3. Start the Next.js Server

```bash
npm run dev
```

The server should be running on http://localhost:3000

### 4. Grant Camera Permissions

Make sure your Mac has granted camera permissions to Terminal or your Python environment.

## Usage

### Quick Start

1. **Start the Video Stream Server**:
   ```bash
   ./start_mac_detector.sh
   ```

2. **Open the Live Feed Map**:
   - Go to http://localhost:3000/live-feed
   - Select "Firefighter Alpha (Mac Camera)" from the camera list
   - Click "Start Detection"

### Manual Start

If you prefer to run manually:

```bash
source venv/bin/activate
python3 video_stream_server.py
```

## Detection Capabilities

### Object Detection
- **High Priority** (Red): People, doors, windows, fire hydrants
- **Medium Priority** (Yellow): Chairs, beds, sinks, knives
- **Low Priority** (Blue): Books, clocks, decorative items

### Hand Gesture Recognition
- **Emergency Gestures** (Red): Stop, Help, Fist
- **Direction Gestures** (Purple): Point
- **Communication Gestures** (Cyan): OK, Thumbs Up/Down, Wave, Open Hand

### Video Streaming
- **Real-time video**: Live feed from your Mac camera
- **Detection overlays**: Object detection boxes drawn on video
- **Low latency**: WebSocket streaming for smooth performance
- **Automatic scaling**: Video adapts to web interface size

## Interface Features

### Live Feed Display
- Real-time object detection boxes with confidence scores
- Hand gesture recognition with action classification
- Color-coded priority system for both objects and gestures
- Detection statistics overlay

### Control Panel
- **Detection Controls**: Start/Stop detection for Mac camera
- **Overlay Controls**: Toggle object detection, gesture detection, and HUD overlays
- **Detection Results**: Real-time display of detected objects and gestures
- **Camera Status**: Battery, signal strength, resolution, FPS
- **System Status**: Connection status and performance indicators

### Overlay Controls
- **Object Detection Toggle**: Show/hide object detection boxes and labels
- **Gesture Detection Toggle**: Show/hide gesture detection boxes and labels  
- **HUD Overlays Toggle**: Show/hide status indicators, counters, and audio level
- **Quick Actions**: "Show All" and "Hide All" buttons for convenience

## Troubleshooting

### Camera Not Working
- Check camera permissions in System Preferences > Security & Privacy > Camera
- Make sure no other applications are using the camera
- Try restarting Terminal/Python environment

### Detection Not Starting
- Verify all dependencies are installed: `pip3 list | grep -E "(opencv|ultralytics|mediapipe)"`
- Check if Next.js server is running: `curl http://localhost:3000`
- Look for error messages in the terminal output

### Poor Detection Performance
- Ensure good lighting conditions
- Make sure you're visible in the camera frame
- Try different poses or objects to test detection

### API Connection Issues
- Verify Next.js server is running on port 3000
- Check browser console for network errors
- Ensure no firewall blocking localhost connections

## Customization

### Adding New Object Classes
Edit the `get_firefighter_object_priority()` function in `mac_camera_detector.py` to add new object types and priorities.

### Modifying Pose Analysis
Edit the `analyze_firefighter_pose()` function to add new pose detection logic.

### Changing Camera Settings
Modify camera properties in the `initialize_system()` method:
- Resolution: `cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)`
- Frame rate: `cap.set(cv2.CAP_PROP_FPS, 30)`

## Performance Tips

- Close other camera-using applications
- Ensure good lighting for better detection accuracy
- Use a stable camera position
- Monitor system resources if detection is slow

## Stopping Detection

- Press 'q' in the camera window to quit
- Or click "Stop Detection" in the web interface
- Use Ctrl+C in the terminal as a last resort

## Integration with Other Cameras

This Mac camera detector integrates seamlessly with the existing live feed map system. You can run multiple detectors simultaneously by using different camera IDs:

```bash
python3 mac_camera_detector.py --camera-id FF-002 --server http://localhost:3000
```

The web interface will automatically detect and display all active camera feeds.
