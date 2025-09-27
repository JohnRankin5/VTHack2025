'use client';

import { useState } from 'react';

const LiveFeed = () => {
  const [selectedCamera, setSelectedCamera] = useState('FF-001');
  
  // Simulated camera data for mesh network
  const cameras = [
    { id: 'FF-001', name: 'Firefighter Alpha', status: 'online', battery: 85, signal: 'strong' },
    { id: 'FF-002', name: 'Firefighter Beta', status: 'online', battery: 72, signal: 'good' },
    { id: 'FF-003', name: 'Firefighter Gamma', status: 'offline', battery: 0, signal: 'none' },
    { id: 'FF-004', name: 'Firefighter Delta', status: 'online', battery: 91, signal: 'strong' },
    { id: 'FF-005', name: 'Firefighter Echo', status: 'online', battery: 68, signal: 'weak' }
  ];

  const selectedCameraData = cameras.find(cam => cam.id === selectedCamera);

  return (
    <div className="w-full">
      {/* Camera Selector */}
      <div className="mb-4">
        <div className="text-sm text-gray-400 font-medium mb-2">Select Camera Feed</div>
        <div className="grid grid-cols-1 gap-2 max-h-32 overflow-y-auto">
          {cameras.map((camera) => (
            <button
              key={camera.id}
              onClick={() => setSelectedCamera(camera.id)}
              className={`p-2 rounded-lg text-left transition-all duration-200 ${
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
                  <div className="text-xs">
                    {camera.battery}%
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Camera Feed Display */}
      <div className="w-full h-64 bg-gray-700 rounded-lg flex items-center justify-center relative overflow-hidden">
        {selectedCameraData?.status === 'online' ? (
          <>
            <div className="text-center text-gray-300">
              <div className="text-4xl mb-2">📹</div>
              <p className="text-sm">{selectedCameraData.name}</p>
              <p className="text-xs text-gray-400 mt-1">Live video from {selectedCameraData.id}</p>
            </div>
            
            {/* Simulated HUD Overlay Elements */}
            <div className="absolute top-2 left-2 bg-red-600 text-white px-2 py-1 rounded text-xs font-bold">
              REC
            </div>
            <div className="absolute top-2 right-2 bg-green-600 text-white px-2 py-1 rounded text-xs">
              LIVE
            </div>
            <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
              LiDAR: Active
            </div>
            <div className="absolute bottom-2 right-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
              IMU: Connected
            </div>
          </>
        ) : (
          <div className="text-center text-gray-500">
            <div className="text-4xl mb-2">📹</div>
            <p className="text-sm">Camera Offline</p>
            <p className="text-xs text-gray-400 mt-1">No signal from {selectedCameraData?.id}</p>
          </div>
        )}
      </div>
      
      {/* Status Indicators */}
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
        <div className={`text-white p-2 rounded text-center ${
          selectedCameraData?.status === 'online' ? 'bg-emerald-500' : 'bg-red-500'
        }`}>
          <div className="font-bold">Camera</div>
          <div>{selectedCameraData?.status === 'online' ? 'Online' : 'Offline'}</div>
        </div>
        <div className={`text-white p-2 rounded text-center ${
          selectedCameraData?.status === 'online' ? 'bg-emerald-500' : 'bg-red-500'
        }`}>
          <div className="font-bold">Audio</div>
          <div>{selectedCameraData?.status === 'online' ? 'Recording' : 'No Signal'}</div>
        </div>
      </div>

      {/* Camera Details */}
      {selectedCameraData && (
        <div className="mt-3 p-3 bg-white/5 rounded-lg border border-white/10">
          <div className="text-xs text-gray-400 mb-2">Camera Details</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-gray-400">Battery:</span>
              <span className="text-white ml-1">{selectedCameraData.battery}%</span>
            </div>
            <div>
              <span className="text-gray-400">Signal:</span>
              <span className="text-white ml-1 capitalize">{selectedCameraData.signal}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveFeed;
  