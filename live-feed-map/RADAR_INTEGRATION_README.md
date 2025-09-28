# 🔥 FireGuard Radar Integration System

## Overview

This system integrates radar distance measurements with the existing object detection video feed to provide real-time collision avoidance and distance monitoring for firefighters. The radar data is overlaid on the video stream as a HUD (Heads-Up Display) with visual and audio alerts for obstacle avoidance.

## 🚀 Quick Start

### 1. Start the Integrated System

```bash
cd live-feed-map
python3 start_radar_integrated_system.py
```

This will start both:
- WebSocket Data Bridge (port 5003) - for receiving radar data
- Enhanced Video Stream Server (port 8765) - with radar HUD overlay

### 2. Send Radar Data

Send radar distance data to the WebSocket endpoint:
```
ws://10.42.0.117:65431
```

**Data Format:**
```json
{
  "type": "radar_distance",
  "distance_m": 5.5,
  "t_sec": 1234567890.123
}
```

### 3. View the Enhanced Video Feed

Access the Next.js frontend at `http://localhost:3000` to see the video feed with radar HUD overlay.

## 📡 System Components

### 1. Radar Avoidance System (`radar_avoidance_system.py`)

**Core Features:**
- Real-time distance filtering and noise reduction
- Multi-level collision detection (SAFE, WARNING, CRITICAL, EMERGENCY)
- Movement recommendations based on distance
- Historical data tracking and trend analysis

**Safety Zones:**
- **SAFE**: > 2.0m (default warning distance)
- **WARNING**: 1.0m - 2.0m 
- **CRITICAL**: 0.5m - 1.0m
- **EMERGENCY**: < 0.5m

### 2. Enhanced Video Stream Server

**New Features:**
- Radar data integration with existing object detection
- Real-time HUD overlay drawing on video frames
- Collision warning display (center screen alerts)
- Mini radar visualization (bottom-left corner)
- Distance display (top-right corner)

### 3. React HUD Component (`components/RadarHUD.js`)

**HUD Elements:**
- **Distance Display**: Current distance with color-coded status
- **Collision Warnings**: Center-screen alerts for dangerous situations
- **Radar Visualization**: Circular radar display with zones
- **System Status**: Connection health and alert counters

### 4. API Integration

**New Endpoints:**
- `GET /api/radar-data` - Fetch recent radar measurements
- WebSocket data bridge integration for real-time processing

## 🎯 HUD Features

### Distance Display (Top-Right)
```
🎯 Distance: 3.2m
Status: SAFE ➡️
Recommend: PROCEED NORMAL
```

### Collision Warnings (Center Screen)
- **EMERGENCY**: Red flashing alert with "STOP IMMEDIATELY"
- **CRITICAL**: Orange alert with "REVERSE SLOWLY"  
- **WARNING**: Yellow alert with "SLOW DOWN"

### Radar Visualization (Bottom-Left)
- Circular radar display with distance zones
- Real-time distance indicator line
- Color-coded zones (Red/Orange/Yellow/Green)

### System Status (Bottom-Right)
```
📊 Readings: 45
⚠️ Alerts: 3
💓 HEALTHY
```

## ⚙️ Configuration

### Radar Avoidance Parameters

You can customize the safety distances in `radar_avoidance_system.py`:

```python
RadarAvoidanceSystem(
    min_safe_distance=1.0,    # Minimum safe distance (meters)
    warning_distance=2.0,     # Warning threshold (meters)
    critical_distance=0.5     # Critical threshold (meters)
)
```

### HUD Display Options

Control HUD elements in the React component:

```jsx
<LiveVideoStream 
  showRadarHUD={true}
  showHUDOverlays={true}
  // ... other props
/>
```

## 🔧 Data Processing Pipeline

1. **Radar Data Reception**: WebSocket receives distance measurements
2. **Noise Filtering**: Median filter + smoothing applied
3. **Status Classification**: Distance categorized into safety zones
4. **Movement Recommendations**: Generated based on current status
5. **HUD Rendering**: Real-time overlay on video stream
6. **Alert System**: Visual/audio warnings for critical situations

## 📊 Data Formats

### Input Radar Data
```json
{
  "type": "radar_distance",
  "distance_m": 6.43,
  "t_sec": 1759042869.924203
}
```

### Processed HUD Data
```json
{
  "hud_data": {
    "distance_m": 6.4,
    "status": "SAFE",
    "movement_recommendation": "PROCEED_NORMAL",
    "distance_trend": "STABLE"
  },
  "collision_warning": null,
  "distance_visualization": {
    "current_distance": 6.4,
    "max_range": 10.0,
    "zones": [...]
  }
}
```

## 🚨 Safety Features

### Multi-Level Alert System
- **Visual Alerts**: Color-coded HUD elements
- **Screen Warnings**: Full-screen collision alerts
- **Trend Analysis**: Monitors if obstacles are approaching
- **Data Validation**: Filters out invalid/noisy readings

### Collision Avoidance Logic
- **Consecutive Alert Tracking**: Prevents false positives
- **Movement Recommendations**: Clear action guidance
- **Emergency Override**: Immediate stop commands for critical situations

## 🔍 Troubleshooting

### Common Issues

1. **No Radar Data Showing**
   - Check WebSocket connection to `ws://10.42.0.117:65431`
   - Verify radar data format matches expected JSON structure
   - Check console logs for connection errors

2. **HUD Not Displaying**
   - Ensure `showRadarHUD={true}` in LiveVideoStream component
   - Check browser console for React component errors
   - Verify video stream is active (camera FF-001)

3. **Stale Data Warnings**
   - Check radar device is actively sending data
   - Verify network connectivity between radar and system
   - Look for "STALE_DATA" in system status display

### Debug Commands

```bash
# Check WebSocket data bridge status
curl http://localhost:5003/api/health

# Get recent radar data
curl http://localhost:5003/api/device-data?device_type=laptop

# View system logs
tail -f /path/to/your/logs
```

## 🎮 Usage in Firefighting Operations

### Deployment Scenarios
- **Search and Rescue**: Distance from walls/obstacles during navigation
- **Structural Assessment**: Measuring distances to unstable elements
- **Equipment Positioning**: Safe distance maintenance from hazards
- **Team Coordination**: Visual distance feedback for tactical movements

### Tactical Advantages
- **Hands-Free Operation**: HUD overlay doesn't require looking away from scene
- **Real-Time Feedback**: Immediate distance and collision warnings
- **Environmental Awareness**: Enhanced spatial understanding in low visibility
- **Safety Enhancement**: Proactive obstacle avoidance vs reactive collision response

## 📈 Future Enhancements

- **Multi-Directional Radar**: Support for 360° radar arrays
- **Object Classification**: Combine radar with computer vision for object identification
- **Audio Alerts**: Spoken distance announcements and warnings
- **Historical Mapping**: Build real-time maps of scanned environments
- **Team Integration**: Share radar data between multiple firefighters

---

## 🤝 Integration with Existing System

This radar integration seamlessly works with your existing FireGuard system:
- ✅ Object detection continues to work normally
- ✅ Gesture recognition remains functional  
- ✅ Room classification still operates
- ✅ All existing HUD elements preserved
- ✅ WebSocket architecture maintained
- ✅ Next.js frontend compatibility

The radar system adds a new layer of safety without disrupting existing functionality!
