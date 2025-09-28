// /Users/jeremyky/Documents/vthacks25/live-feed-map/src/app/hand-test/page.tsx
'use client';

import { useState, useRef, useEffect } from 'react';

export default function HandTestPage() {
  const [videoSrc, setVideoSrc] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const videoRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    // Always connect to the camera when page loads
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      wsRef.current = new WebSocket('ws://localhost:8765');
      
      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
      };
      
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'frame') {
          setVideoSrc(`data:image/jpeg;base64,${data.data}`);
        }
      };
      
      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
      };
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Failed to connect to video stream');
        setIsConnected(false);
      };
    } catch (error) {
      console.error('Connection error:', error);
      setError('Failed to connect to video stream');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-8">Hand Test - Always On Camera</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Video Display */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Live Camera Feed</h2>
          <div className="relative">
            {videoSrc ? (
              <img 
                src={videoSrc} 
                alt="Live camera feed" 
                className="w-full h-auto rounded-lg"
                ref={videoRef}
              />
            ) : (
              <div className="w-full h-96 bg-gray-700 rounded-lg flex items-center justify-center">
                {error ? (
                  <div className="text-red-400 text-center">
                    <p className="text-lg font-semibold">Error</p>
                    <p>{error}</p>
                  </div>
                ) : (
                  <div className="text-gray-400 text-center">
                    <p className="text-lg font-semibold">Loading Camera...</p>
                    <p>Connecting to video stream...</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Status Panel */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Status</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Connection Status:</span>
              <span className={`px-3 py-1 rounded-full text-sm ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span>Camera Status:</span>
              <span className={`px-3 py-1 rounded-full text-sm ${
                videoSrc ? 'bg-green-500' : 'bg-yellow-500'
              }`}>
                {videoSrc ? 'Active' : 'Loading'}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span>Server:</span>
              <span className="text-blue-400">Port 8765</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}