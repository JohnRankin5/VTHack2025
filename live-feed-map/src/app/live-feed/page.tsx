'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';

export default function LiveFeedPage() {
  const [selectedCamera, setSelectedCamera] = useState('FF-001');
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [objectCount, setObjectCount] = useState(3);
  const [detectedObjects, setDetectedObjects] = useState([
    { id: 1, type: 'Door', distance: '2.3m', confidence: 95 },
    { id: 2, type: 'Window', distance: '4.1m', confidence: 87 },
    { id: 3, type: 'Obstacle', distance: '1.8m', confidence: 92 }
  ]);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Simulated camera data for mesh network
  const cameras = [
    { id: 'FF-001', name: 'Firefighter Alpha', status: 'online', battery: 85, signal: 'strong', resolution: '1080p', fps: 30 },
    { id: 'FF-002', name: 'Firefighter Beta', status: 'online', battery: 72, signal: 'good', resolution: '720p', fps: 30 },
    { id: 'FF-003', name: 'Firefighter Gamma', status: 'offline', battery: 0, signal: 'none', resolution: 'N/A', fps: 0 },
    { id: 'FF-004', name: 'Firefighter Delta', status: 'online', battery: 91, signal: 'strong', resolution: '1080p', fps: 60 },
    { id: 'FF-005', name: 'Firefighter Echo', status: 'online', battery: 68, signal: 'weak', resolution: '480p', fps: 15 }
  ];

  const selectedCameraData = cameras.find(cam => cam.id === selectedCamera);

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
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 p-6 h-[calc(100vh-80px)]">
        
        {/* Main Video Feed - Takes up 3 columns */}
        <div className="lg:col-span-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 relative">
          <div className="w-full h-full bg-gray-700 rounded-lg flex items-center justify-center relative overflow-hidden">
            {selectedCameraData?.status === 'online' ? (
              <>
                {/* Video Feed Placeholder */}
                <div className="text-center text-gray-300">
                  <div className="text-6xl mb-4">📹</div>
                  <p className="text-lg">{selectedCameraData.name}</p>
                  <p className="text-sm text-gray-400 mt-2">Live video from {selectedCameraData.id}</p>
                </div>
                
                {/* HUD Overlays */}
                <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded text-sm font-bold">
                  {isRecording ? 'REC' : 'LIVE'}
                </div>
                <div className="absolute top-4 right-4 bg-green-600 text-white px-3 py-1 rounded text-sm">
                  {selectedCameraData.resolution}
                </div>
              </>
            ) : (
              <div className="text-center text-gray-500">
                <div className="text-6xl mb-4">📹</div>
                <p className="text-lg">Camera Offline</p>
                <p className="text-sm text-gray-400 mt-2">No signal from {selectedCameraData?.id}</p>
              </div>
            )}
            
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
        <div className="lg:col-span-1 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 flex flex-col space-y-6">
          
          {/* Camera Selector */}
          <div className="bg-white/5 p-4 rounded-lg border border-white/10">
            <h3 className="text-sm font-semibold mb-3 text-white">Camera Selection</h3>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {cameras.map((camera) => (
                <button
                  key={camera.id}
                  onClick={() => setSelectedCamera(camera.id)}
                  className={`w-full p-2 rounded-lg text-left transition-all duration-200 ${
                    selectedCamera === camera.id
                      ? 'bg-blue-500 text-white'
                      : 'bg-white/10 hover:bg-white/20 text-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium">{camera.name}</div>
                      <div className="text-xs opacity-75">{camera.id}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${
                        camera.status === 'online' ? 'bg-emerald-500' : 'bg-red-500'
                      }`}></div>
                      <div className="text-xs">{camera.battery}%</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
          
          {/* Recording Controls */}
          <div className="bg-white/5 p-4 rounded-lg border border-white/10">
            <h3 className="text-sm font-semibold mb-3 text-white">Recording Controls</h3>
            <button
              onClick={toggleRecording}
              disabled={selectedCameraData?.status !== 'online'}
              className={`w-full py-3 px-4 rounded-lg font-semibold transition-all duration-200 ${
                isRecording 
                  ? 'bg-red-500 hover:bg-red-600' 
                  : 'bg-emerald-500 hover:bg-emerald-600'
              } ${selectedCameraData?.status !== 'online' ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isRecording ? 'Stop Recording' : 'Start Recording'}
            </button>
            <div className="mt-2 text-xs text-gray-300">
              Status: {selectedCameraData?.status !== 'online' ? 'Camera Offline' : (isRecording ? 'Recording...' : 'Ready')}
            </div>
          </div>

          {/* Camera Settings */}
          <div className="bg-white/5 p-4 rounded-lg border border-white/10">
            <h3 className="text-sm font-semibold mb-3 text-white">Camera Settings</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Resolution:</span>
                <span className="text-white">{selectedCameraData?.resolution || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Frame Rate:</span>
                <span className="text-white">{selectedCameraData?.fps || 0} FPS</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Night Vision:</span>
                <span className="text-emerald-400">ON</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Stabilization:</span>
                <span className="text-emerald-400">Active</span>
              </div>
            </div>
          </div>

          {/* Object Detection */}
          <div className="bg-white/5 p-4 rounded-lg border border-white/10">
            <h3 className="text-sm font-semibold mb-3 text-white">Object Detection</h3>
            <div className="space-y-2">
              {detectedObjects.map((obj) => (
                <div key={obj.id} className="bg-white/10 p-3 rounded-lg text-sm">
                  <div className="font-semibold text-white">{obj.type}</div>
                  <div className="text-gray-300">Distance: {obj.distance}</div>
                  <div className="text-gray-300">Confidence: {obj.confidence}%</div>
                </div>
              ))}
            </div>
          </div>

          {/* System Status */}
          <div className="bg-white/5 p-4 rounded-lg border border-white/10">
            <h3 className="text-sm font-semibold mb-3 text-white">System Status</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Camera:</span>
                <span className={selectedCameraData?.status === 'online' ? 'text-emerald-400' : 'text-red-400'}>
                  {selectedCameraData?.status === 'online' ? 'Online' : 'Offline'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Audio:</span>
                <span className={selectedCameraData?.status === 'online' ? 'text-emerald-400' : 'text-red-400'}>
                  {selectedCameraData?.status === 'online' ? 'Recording' : 'No Signal'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">LiDAR:</span>
                <span className={selectedCameraData?.status === 'online' ? 'text-emerald-400' : 'text-red-400'}>
                  {selectedCameraData?.status === 'online' ? 'Active' : 'Offline'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Battery:</span>
                <span className={selectedCameraData?.battery && selectedCameraData.battery > 20 ? 'text-emerald-400' : 'text-red-400'}>
                  {selectedCameraData?.battery || 0}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Signal:</span>
                <span className="text-white capitalize">{selectedCameraData?.signal || 'none'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
