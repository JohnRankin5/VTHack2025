'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';

export default function LiveFeedPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [objectCount, setObjectCount] = useState(3);
  const [detectedObjects, setDetectedObjects] = useState([
    { id: 1, type: 'Door', distance: '2.3m', confidence: 95 },
    { id: 2, type: 'Window', distance: '4.1m', confidence: 87 },
    { id: 3, type: 'Obstacle', distance: '1.8m', confidence: 92 }
  ]);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Simulate audio level changes
  useEffect(() => {
    const interval = setInterval(() => {
      setAudioLevel(Math.random() * 100);
    }, 100);
    return () => clearInterval(interval);
  }, []);

  const toggleRecording = () => {
    setIsRecording(!isRecording);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 p-4 h-[calc(100vh-80px)]">
        
        {/* Main Video Feed - Takes up 3 columns */}
        <div className="lg:col-span-3 bg-gray-800 rounded-lg p-4 relative">
          <div className="w-full h-full bg-gray-700 rounded-lg flex items-center justify-center relative overflow-hidden">
            {/* Video Feed Placeholder */}
            <div className="text-center text-gray-300">
              <div className="text-6xl mb-4">📹</div>
              <p className="text-lg">Live Camera Feed</p>
              <p className="text-sm text-gray-400 mt-2">High-resolution video from helmet camera</p>
            </div>
            
            {/* HUD Overlays */}
            <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded text-sm font-bold">
              {isRecording ? 'REC' : 'LIVE'}
            </div>
            <div className="absolute top-4 right-4 bg-green-600 text-white px-3 py-1 rounded text-sm">
              HD 1080p
            </div>
            
            {/* Object Detection Overlays */}
            <div className="absolute bottom-4 left-4 bg-black bg-opacity-70 text-white px-3 py-2 rounded">
              <div className="text-sm font-semibold">Objects Detected: {objectCount}</div>
              <div className="text-xs">Nearest: 1.8m</div>
            </div>
            
            {/* Audio Level Indicator */}
            <div className="absolute bottom-4 right-4 bg-black bg-opacity-70 text-white px-3 py-2 rounded">
              <div className="text-sm font-semibold">Audio Level</div>
              <div className="w-20 h-2 bg-gray-600 rounded mt-1">
                <div 
                  className="h-full bg-green-500 rounded transition-all duration-100"
                  style={{ width: `${audioLevel}%` }}
                ></div>
              </div>
            </div>

            {/* Simulated Object Detection Boxes */}
            <div className="absolute top-1/4 left-1/4 w-16 h-16 border-2 border-red-500 rounded">
              <div className="absolute -top-6 left-0 text-xs bg-red-500 text-white px-1 rounded">
                Door 95%
              </div>
            </div>
            <div className="absolute top-1/3 right-1/3 w-12 h-12 border-2 border-yellow-500 rounded">
              <div className="absolute -top-6 left-0 text-xs bg-yellow-500 text-black px-1 rounded">
                Window 87%
              </div>
            </div>
            <div className="absolute bottom-1/3 left-1/3 w-14 h-14 border-2 border-orange-500 rounded">
              <div className="absolute -top-6 left-0 text-xs bg-orange-500 text-white px-1 rounded">
                Obstacle 92%
              </div>
            </div>
          </div>
        </div>

        {/* Control Panel - Takes up 1 column */}
        <div className="lg:col-span-1 bg-gray-800 rounded-lg p-4 flex flex-col space-y-4">
          
          {/* Recording Controls */}
          <div className="bg-gray-700 p-3 rounded">
            <h3 className="text-sm font-semibold mb-2">Recording Controls</h3>
            <button
              onClick={toggleRecording}
              className={`w-full py-2 px-4 rounded font-semibold ${
                isRecording 
                  ? 'bg-red-600 hover:bg-red-700' 
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {isRecording ? 'Stop Recording' : 'Start Recording'}
            </button>
            <div className="mt-2 text-xs text-gray-300">
              Status: {isRecording ? 'Recording...' : 'Ready'}
            </div>
          </div>

          {/* Camera Settings */}
          <div className="bg-gray-700 p-3 rounded">
            <h3 className="text-sm font-semibold mb-2">Camera Settings</h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span>Resolution:</span>
                <span className="text-green-400">1080p</span>
              </div>
              <div className="flex justify-between">
                <span>Frame Rate:</span>
                <span className="text-green-400">30 FPS</span>
              </div>
              <div className="flex justify-between">
                <span>Night Vision:</span>
                <span className="text-green-400">ON</span>
              </div>
              <div className="flex justify-between">
                <span>Stabilization:</span>
                <span className="text-green-400">Active</span>
              </div>
            </div>
          </div>

          {/* Object Detection */}
          <div className="bg-gray-700 p-3 rounded">
            <h3 className="text-sm font-semibold mb-2">Object Detection</h3>
            <div className="space-y-2">
              {detectedObjects.map((obj) => (
                <div key={obj.id} className="bg-gray-600 p-2 rounded text-xs">
                  <div className="font-semibold">{obj.type}</div>
                  <div className="text-gray-300">Distance: {obj.distance}</div>
                  <div className="text-gray-300">Confidence: {obj.confidence}%</div>
                </div>
              ))}
            </div>
          </div>

          {/* System Status */}
          <div className="bg-gray-700 p-3 rounded">
            <h3 className="text-sm font-semibold mb-2">System Status</h3>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span>Camera:</span>
                <span className="text-green-400">Online</span>
              </div>
              <div className="flex justify-between">
                <span>Audio:</span>
                <span className="text-green-400">Recording</span>
              </div>
              <div className="flex justify-between">
                <span>LiDAR:</span>
                <span className="text-green-400">Active</span>
              </div>
              <div className="flex justify-between">
                <span>Battery:</span>
                <span className="text-green-400">87%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
