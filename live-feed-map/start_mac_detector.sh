#!/bin/bash

# Start Mac Camera Detector for Live Feed Map
# This script starts the Mac camera detector as one of the firefighter helmets

echo "🚒 Starting Mac Camera Detector for Live Feed Map..."
echo "📹 Camera will act as Firefighter Alpha (FF-001)"
echo "🔍 Running object detection and pose detection"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if required packages are installed
echo "🔧 Checking dependencies..."
python3 -c "import cv2, ultralytics, requests, websockets" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing required packages. Installing..."
    pip install opencv-python ultralytics requests numpy websockets
fi

# Check if Next.js server is running
echo "🌐 Checking if Next.js server is running..."
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "⚠️  Next.js server not detected on localhost:3000"
    echo "   Please start the Next.js server first:"
    echo "   cd live-feed-map && npm run dev"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🚀 Starting Mac Camera Video Stream Server..."
echo "   - Camera ID: FF-001 (Firefighter Alpha)"
echo "   - WebSocket Server: ws://localhost:8765"
echo "   - Next.js Server: http://localhost:3000"
echo "   - Press Ctrl+C to quit"
echo ""

# Start the video stream server
python3 video_stream_server.py

echo ""
echo "✅ Mac Camera Detector stopped"
