'use client';

import { useState, useEffect, useRef } from 'react';

const LiveVideoStream = ({ cameraId, isDetecting, onDetectionUpdate }) => {
  const [videoSrc, setVideoSrc] = useState(null);
  const [detections, setDetections] = useState([]);
  const [poses, setPoses] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const videoRef = useRef(null);
  const wsRef = useRef(null);
  const canvasRef = useRef(null);

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

  const connectWebSocket = () => {
    try {
      // Connect to the video stream WebSocket server
      wsRef.current = new WebSocket('ws://localhost:8765');

      wsRef.current.onopen = () => {
        console.log('Connected to video stream server');
        setIsConnected(true);
        setError(null);
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
            setPoses(data.poses || []);
            
            // Notify parent component of detection updates
            if (onDetectionUpdate) {
              onDetectionUpdate({
                detections: data.detections || [],
                poses: data.poses || [],
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
    setPoses([]);
  };

  const drawDetections = (ctx, detections, poses) => {
    // Clear previous drawings
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    
    // Draw object detection boxes
    detections.forEach((detection, index) => {
      if (detection.type === 'object') {
        const [x1, y1, x2, y2] = detection.bbox;
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
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        
        // Draw label
        ctx.fillStyle = color;
        ctx.font = '12px Arial';
        ctx.fillText(`${class_name}: ${Math.round(confidence * 100)}%`, x1, y1 - 5);
      }
    });
    
    // Draw pose detection boxes
    poses.forEach((pose, index) => {
      if (pose.type === 'pose') {
        const [x1, y1, x2, y2] = pose.bbox;
        const action = pose.action;
        const confidence = pose.confidence;
        const priority = pose.priority;
        
        // Color coding for poses
        let color;
        if (priority >= 9) {
          color = '#dc2626'; // Red - Emergency
        } else if (priority >= 7) {
          color = '#7c3aed'; // Magenta - High priority
        } else {
          color = '#06b6d4'; // Cyan - Normal
        }
        
        // Draw bounding box
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        
        // Draw label
        ctx.fillStyle = color;
        ctx.font = '12px Arial';
        ctx.fillText(`${action}: ${Math.round(confidence * 100)}%`, x1, y1 - 5);
        
        // Draw key points
        Object.entries(pose.key_points || {}).forEach(([point_name, [px, py]]) => {
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(px, py, 3, 0, 2 * Math.PI);
          ctx.fill();
        });
      }
    });
  };

  useEffect(() => {
    if (canvasRef.current && (detections.length > 0 || poses.length > 0)) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      
      // Set canvas size to match video
      if (videoRef.current) {
        canvas.width = videoRef.current.offsetWidth;
        canvas.height = videoRef.current.offsetHeight;
      }
      
      drawDetections(ctx, detections, poses);
    }
  }, [detections, poses]);

  if (cameraId !== 'FF-001') {
    // Show placeholder for other cameras
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
              {/* Video element */}
              <img
                ref={videoRef}
                src={videoSrc}
                alt="Live video feed"
                className="w-full h-full object-cover"
                style={{ imageRendering: 'pixelated' }}
              />
              
              {/* Detection overlay canvas */}
              <canvas
                ref={canvasRef}
                className="absolute top-0 left-0 w-full h-full pointer-events-none"
                style={{ zIndex: 10 }}
              />
              
              {/* Connection status */}
              <div className="absolute top-2 right-2 bg-green-600 text-white px-2 py-1 rounded text-xs">
                {isConnected ? 'LIVE' : 'CONNECTING...'}
              </div>
              
              {/* Detection count overlay */}
              <div className="absolute bottom-2 left-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs">
                Objects: {detections.length} | Poses: {poses.length}
              </div>
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
