'use client';

import { useState, useEffect, useRef } from 'react';
import RadarHUD from './RadarHUD';

const LiveVideoStream = ({ cameraId, isDetecting, onDetectionUpdate, showObjectDetection = true, showGestureDetection = true, showHUDOverlays = true, showRadarHUD = true }) => {
  const [videoSrc, setVideoSrc] = useState(null);
  const [detections, setDetections] = useState([]);
  const [gestures, setGestures] = useState([]);
  const [roomClassification, setRoomClassification] = useState(null);
  const [radarData, setRadarData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const videoRef = useRef(null);
  const wsRef = useRef(null);
  const canvasRef = useRef(null);

  // WebSocket connection management
  useEffect(() => {
    if (isDetecting && cameraId === 'FF-001') {
      connectWebSocket();
    } else {
      disconnectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [isDetecting, cameraId]);

  // Canvas drawing when detections or toggle states change
  useEffect(() => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      
      // Set canvas size to match video container
      if (videoRef.current) {
        canvas.width = videoRef.current.offsetWidth;
        canvas.height = videoRef.current.offsetHeight;
      }
      
      // Always redraw (or clear) when detections, gestures, or toggle states change
      drawDetections(ctx, detections, gestures);
    }
  }, [detections, gestures, showObjectDetection, showGestureDetection]);

  const connectWebSocket = () => {
    if (wsRef.current) return; // Already connected

    try {
      wsRef.current = new WebSocket('ws://localhost:8765');
      setIsConnected(false);
      setError(null);

      wsRef.current.onopen = () => {
        console.log('Connected to video stream server');
        setIsConnected(true);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'frame') {
            // Create blob URL from base64 data
            const byteCharacters = atob(data.data);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
              byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'image/jpeg' });
            const imageUrl = URL.createObjectURL(blob);
            
            setVideoSrc(imageUrl);
            setDetections(data.detections || []);
            setGestures(data.gestures || []);
            setRoomClassification(data.room_classification || null);
            setRadarData(data.radar_data || null);
            
            // Notify parent component of detection updates
            if (onDetectionUpdate) {
              onDetectionUpdate({
                detections: data.detections || [],
                gestures: data.gestures || [],
                roomClassification: data.room_classification || null,
                radarData: data.radar_data || null,
                timestamp: data.timestamp
              });
            }
            
            // Clean up previous blob URL
            setTimeout(() => {
              URL.revokeObjectURL(imageUrl);
            }, 100);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      wsRef.current.onclose = () => {
        console.log('Disconnected from video stream server');
        setIsConnected(false);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Failed to connect to video stream');
        setIsConnected(false);
      };
    } catch (err) {
      console.error('Error connecting to WebSocket:', err);
      setError('Failed to connect to video stream');
    }
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setVideoSrc(null);
    setDetections([]);
    setGestures([]);
    setRadarData(null);
  };

  const drawDetections = (ctx, detections, gestures) => {
    // Clear previous drawings
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  
    console.log('drawDetections called with:', { 
      showObjectDetection, 
      showGestureDetection, 
      detectionsCount: detections.length, 
      gesturesCount: gestures.length,
      canvasSize: { width: ctx.canvas.width, height: ctx.canvas.height }
    });
  
    // Calculate letterbox-aware scaling
    const backendWidth = 640;
    const backendHeight = 480;
    const scale = Math.min(ctx.canvas.width / backendWidth, ctx.canvas.height / backendHeight);
    const displayWidth = backendWidth * scale;
    const displayHeight = backendHeight * scale;
    const offsetX = (ctx.canvas.width - displayWidth) / 2;
    const offsetY = (ctx.canvas.height - displayHeight) / 2;
  
    console.log('Scaling:', { scale, offsetX, offsetY, displayWidth, displayHeight });
  
    // Draw object detection boxes (only if enabled)
    if (showObjectDetection && detections.length > 0) {
      detections.forEach((detection) => {
        if (detection.type === 'object') {
          const [x1, y1, x2, y2] = detection.bbox;
  
          // Scale with letterbox offsets
          const scaledX1 = offsetX + x1 * scale;
          const scaledY1 = offsetY + y1 * scale;
          const scaledX2 = offsetX + x2 * scale;
          const scaledY2 = offsetY + y2 * scale;
  
          const confidence = detection.confidence;
          const class_name = detection.class_name;
          const priority = detection.priority;
  
          // Color coding for objects
          let color;
          if (priority >= 8) {
            color = '#ef4444'; // Red - High priority
          } else if (priority >= 5) {
            color = '#eab308'; // Yellow - Medium priority
          } else {
            color = '#3b82f6'; // Blue - Low priority
          }
  
          // Draw bounding box
          ctx.strokeStyle = color;
          ctx.lineWidth = 2;
          ctx.strokeRect(scaledX1, scaledY1, scaledX2 - scaledX1, scaledY2 - scaledY1);
  
          // Draw label
          ctx.fillStyle = color;
          ctx.font = '12px Arial';
          ctx.fillText(`${class_name}: ${Math.round(confidence * 100)}%`, scaledX1, scaledY1 - 5);
        }
      });
    }
  
    // Draw gesture detection boxes (only if enabled)
    if (showGestureDetection && gestures.length > 0) {
      gestures.forEach((gesture) => {
        if (gesture.bbox) {
          const [x1, y1, x2, y2] = gesture.bbox;
  
          // Scale with letterbox offsets
          const scaledX1 = offsetX + x1 * scale;
          const scaledY1 = offsetY + y1 * scale;
          const scaledX2 = offsetX + x2 * scale;
          const scaledY2 = offsetY + y2 * scale;
  
          const gesture_name = gesture.gesture;
          const confidence = gesture.confidence;
  
          // Color coding for gestures
          let color;
          if (gesture_name.includes('emergency')) {
            color = '#dc2626'; // Red - Emergency
          } else if (gesture_name.includes('affirmative')) {
            color = '#7c3aed'; // Magenta - High priority
          } else {
            color = '#06b6d4'; // Cyan - Normal
          }
  
          // Draw bounding box
          ctx.strokeStyle = color;
          ctx.lineWidth = 2;
          ctx.strokeRect(scaledX1, scaledY1, scaledX2 - scaledX1, scaledY2 - scaledY1);
  
          // Draw label
          ctx.fillStyle = color;
          ctx.font = '12px Arial';
          ctx.fillText(`${gesture_name}: ${Math.round(confidence * 100)}%`, scaledX1, scaledY1 - 5);
  
          // Draw center point if available
          if (gesture.center && gesture.center.length >= 2) {
            const [cx, cy] = gesture.center;
            const scaledCx = offsetX + cx * scale;
            const scaledCy = offsetY + cy * scale;
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(scaledCx, scaledCy, 3, 0, 2 * Math.PI);
            ctx.fill();
          }
        }
      });
    }
  };
  
  if (cameraId !== 'FF-001') {
    return (
      <div className="w-full h-full bg-gray-700 rounded-lg flex items-center justify-center relative overflow-hidden">
        <div className="text-center text-gray-300">
          <div className="text-6xl mb-4">📹</div>
          <p className="text-lg">Camera Feed</p>
          <p className="text-sm text-gray-400 mt-2">Live video from {cameraId}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-gray-700 rounded-lg relative overflow-hidden">
      {isDetecting ? (
        <>
          {videoSrc ? (
            <>
              <img
                ref={videoRef}
                src={videoSrc}
                alt="Live video feed"
                className="w-full h-full object-contain bg-black"
                style={{ imageRendering: 'pixelated' }}
              />
              
              <canvas
                ref={canvasRef}
                className="absolute top-0 left-0 w-full h-full pointer-events-none"
                style={{ zIndex: 10 }}
              />
              
              {showHUDOverlays && (
                <div className="absolute top-2 right-2 bg-green-600 text-white px-2 py-1 rounded text-xs">
                  {isConnected ? 'LIVE' : 'CONNECTING...'}
                </div>
              )}
              
              {showHUDOverlays && (
                <div className="absolute bottom-2 left-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs">
                  Objects: {detections.length} | Gestures: {gestures.length}
                </div>
              )}
              
              {showHUDOverlays && roomClassification && roomClassification.confidence > 0.3 && (
                <div className="absolute top-2 left-2 bg-purple-600 bg-opacity-90 text-white px-3 py-2 rounded text-sm">
                  <div className="font-semibold">🏠 {roomClassification.type}</div>
                  <div className="text-xs opacity-80">
                    Confidence: {Math.round(roomClassification.confidence * 100)}% | 
                    Objects: {roomClassification.objects_count}
                  </div>
                </div>
              )}
              
              {/* Radar HUD Overlay */}
              {showRadarHUD && radarData && (
                <RadarHUD radarData={radarData} isVisible={showHUDOverlays} />
              )}
            </>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-300">
                <div className="text-4xl mb-2">📹</div>
                <p className="text-sm">Connecting to camera...</p>
                {error && (
                  <p className="text-red-400 text-xs mt-1">{error}</p>
                )}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-gray-300">
            <div className="text-6xl mb-4">📹</div>
            <p className="text-lg">Mac Camera Ready</p>
            <p className="text-sm text-gray-400 mt-2">Click "Start Detection" to begin</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveVideoStream;
