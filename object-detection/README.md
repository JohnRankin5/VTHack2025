# Object Detection System for Firefighter Helmet

This system provides real-time object detection using YOLOv5 for the firefighter helmet mesh network.

## System Architecture

```
Mac Camera → YOLOv5 Processing → Web Server → Dashboard
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd object-detection
pip install -r requirements.txt
```

### 2. Download YOLOv5 Model

The system will automatically download the YOLOv5s model on first run.

### 3. Start the Web Server

```bash
cd ../live-feed-map
npm run dev
```

The server will run on `http://localhost:3000`

## Usage

### Option 1: Integrated Detection (Recommended for Testing)

This combines camera capture and YOLOv5 processing in one script:

```bash
python integrated_detection.py --duration 60
```

**Features:**
- Uses Mac camera directly
- Real-time YOLOv5 processing
- Visual display with bounding boxes
- Sends results to web server
- Press 'q' to quit early

### Option 2: Separate Components (For Hardware Testing)

#### Mac Camera Simulator
Simulates Arduino camera data capture:

```bash
python mac_camera_simulator.py --duration 60
```

#### Jetson Processor
Processes frames with YOLOv5 (simulated):

```bash
python jetson_processor.py --duration 60
```

## Command Line Options

All scripts support these options:

- `--server`: Server URL (default: http://localhost:3000)
- `--camera-id`: Camera ID (default: FF-001)
- `--duration`: Duration in seconds (default: 60)

## Dashboard Integration

The object detection results are automatically displayed in the dashboard:

1. **Object Detection Panel**: Shows recent detections with confidence scores
2. **Detection Stats**: Total detections and unique object types
3. **Real-time Updates**: Updates every 2 seconds
4. **Visual Indicators**: Green for active detection, gray for inactive

## Detected Objects

The system can detect 80 different object types from the COCO dataset, including:

- **People**: person
- **Furniture**: chair, couch, bed, dining table
- **Doors/Windows**: door, window
- **Electronics**: laptop, tv, cell phone
- **Common Objects**: bottle, book, clock, etc.

## API Endpoints

### POST /api/object-detection
Receives detection results from processing systems.

**Request Body:**
```json
{
  "camera_id": "FF-001",
  "timestamp": "2025-01-27T10:30:00Z",
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.85,
      "bbox": [100, 150, 200, 300],
      "center": [150, 225]
    }
  ],
  "detection_count": 1,
  "source": "integrated-system"
}
```

### GET /api/object-detection
Retrieves recent detection results.

**Query Parameters:**
- `camera_id`: Filter by camera ID
- `limit`: Maximum number of results (default: 50)

## Testing

### 1. Basic Test
```bash
python integrated_detection.py --duration 30
```

### 2. Check Dashboard
Open `http://localhost:3000` and verify:
- Object Detection panel shows activity
- Detection stats update
- Recent detections appear

### 3. Test Different Scenarios
- Point camera at different objects
- Test in different lighting conditions
- Verify confidence scores and bounding boxes

## Troubleshooting

### Camera Issues
- Ensure camera permissions are granted
- Try different camera indices (0, 1, 2)
- Check if camera is being used by another application

### Model Loading Issues
- Ensure internet connection for model download
- Check available disk space
- Verify PyTorch installation

### Server Connection Issues
- Ensure web server is running on port 3000
- Check firewall settings
- Verify server URL in script parameters

## Performance Notes

- **Frame Rate**: 2-5 FPS for real-time processing
- **Confidence Threshold**: 0.5 (50%)
- **Model**: YOLOv5s (small, fast)
- **Input Resolution**: 640x640 pixels

## Future Enhancements

1. **LiDAR Integration**: Add depth information for 3D object detection
2. **Custom Training**: Fine-tune model for firefighter-specific objects
3. **Real-time Streaming**: WebRTC for live video feed
4. **Edge Optimization**: TensorRT for Jetson TX2 optimization
5. **Multi-camera Support**: Process multiple camera feeds simultaneously

## Hardware Requirements

### Development (Mac)
- macOS with camera access
- Python 3.8+
- 4GB+ RAM
- Webcam

### Production (Jetson TX2)
- NVIDIA Jetson TX2
- Camera module (e.g., OV7670, ESP32-CAM)
- Serial communication
- 8GB+ RAM recommended

## License

This project is part of the FireGuard tactical command system for firefighter safety.
