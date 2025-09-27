'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import LiveVideoStream from '../../../components/LiveVideoStream';

export default function LiveFeedPage() {
  const [selectedCamera, setSelectedCamera] = useState('FF-001');
  const [isRecording, setIsRecording] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [objectCount, setObjectCount] = useState(0);
  const [poseCount, setPoseCount] = useState(0);
  const [detectedObjects, setDetectedObjects] = useState([]);
  const [detectedPoses, setDetectedPoses] = useState([]);
  const [detectionData, setDetectionData] = useState(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Simulated camera data for mesh network
  const cameras = [
    { id: 'FF-001', name: 'Firefighter Alpha (Mac Camera)', status: 'online', battery: 85, signal: 'strong', resolution: '1080p', fps: 30, type: 'mac-camera' },
    { id: 'FF-002', name: 'Firefighter Beta', status: 'online', battery: 72, signal: 'good', resolution: '720p', fps: 30, type: 'helmet' },
    { id: 'FF-003', name: 'Firefighter Gamma', status: 'offline', battery: 0, signal: 'none', resolution: 'N/A', fps: 0, type: 'helmet' },
    { id: 'FF-004', name: 'Firefighter Delta', status: 'online', battery: 91, signal: 'strong', resolution: '1080p', fps: 60, type: 'helmet' },
    { id: 'FF-005', name: 'Firefighter Echo', status: 'online', battery: 68, signal: 'weak', resolution: '480p', fps: 15, type: 'helmet' }
  ];

  const selectedCameraData = cameras.find(cam => cam.id === selectedCamera);

  // Simulate audio level changes
  useEffect(() => {
    const interval = setInterval(() => {
      setAudioLevel(Math.random() * 100);
    }, 100);
    return () => clearInterval(interval);
  }, []);

  // Handle detection updates from video stream
  const handleDetectionUpdate = (data) => {
    setDetectedObjects(data.detections || []);
    setDetectedPoses(data.poses || []);
    setObjectCount(data.detections.length);
    setPoseCount(data.poses.length);
    setDetectionData({
      timestamp: data.timestamp,
      object_detections: data.detections,
      pose_detections: data.poses,
      object_count: data.detections.length,
      pose_count: data.poses.length
    });
  };

  // Fetch detection data for non-Mac cameras
  useEffect(() => {
    const fetchDetectionData = async () => {
      try {
        const response = await fetch(`/api/object-detection?camera_id=${selectedCamera}&limit=1`);
        const data = await response.json();
        if (data.success && data.results.length > 0) {
          const latest = data.results[0];
          setDetectionData(latest);
          setObjectCount(latest.object_count || 0);
          setPoseCount(latest.pose_count || 0);
          setDetectedObjects(latest.object_detections || []);
          setDetectedPoses(latest.pose_detections || []);
        }
      } catch (error) {
        console.error('Error fetching detection data:', error);
      }
    };

    // Only fetch for non-Mac cameras (they use WebSocket)
    if (isDetecting && selectedCamera !== 'FF-001') {
      const interval = setInterval(fetchDetectionData, 1000);
      return () => clearInterval(interval);
    }
  }, [selectedCamera, isDetecting]);

  const toggleRecording = () => {
    setIsRecording(!isRecording);
  };

  const startDetection = async () => {
    setIsDetecting(true);
    // The Mac camera detector will start automatically when this state changes
    console.log('Starting detection for Mac camera...');
  };

  const stopDetection = () => {
    setIsDetecting(false);
    setObjectCount(0);
    setPoseCount(0);
    setDetectedObjects([]);
    setDetectedPoses([]);
    setDetectionData(null);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 p-6 h-[calc(100vh-80px)]">
        
        {/* Main Video Feed - Takes up 3 columns */}
        <div className="lg:col-span-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 relative">
          {selectedCameraData?.status === 'online' ? (
            <>
              {/* Live Video Stream */}
              <LiveVideoStream 
                cameraId={selectedCamera}
                isDetecting={isDetecting}
                onDetectionUpdate={handleDetectionUpdate}
              />
              
              {/* HUD Overlays */}
              <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded text-sm font-bold z-20">
                {isRecording ? 'REC' : 'LIVE'}
              </div>
              <div className="absolute top-4 right-4 bg-green-600 text-white px-3 py-1 rounded text-sm z-20">
                {selectedCameraData.resolution}
              </div>
              
              {/* Detection Overlays */}
              <div className="absolute bottom-4 left-4 bg-black bg-opacity-70 text-white px-3 py-2 rounded z-20">
                <div className="text-sm font-semibold">Objects: {objectCount} | Poses: {poseCount}</div>
                <div className="text-xs">
                  {detectedObjects.length > 0 ? `Nearest: ${detectedObjects[0]?.class_name || 'Unknown'}` : 'No objects detected'}
                </div>
              </div>
              
              {/* Audio Level Indicator */}
              <div className="absolute bottom-4 right-4 bg-black bg-opacity-70 text-white px-3 py-2 rounded z-20">
                <div className="text-sm font-semibold">Audio Level</div>
                <div className="w-20 h-2 bg-gray-600 rounded mt-1">
                  <div 
                    className="h-full bg-green-500 rounded transition-all duration-100"
                    style={{ width: `${audioLevel}%` }}
                  ></div>
                </div>
              </div>
            </>
          ) : (
            <div className="w-full h-full bg-gray-700 rounded-lg flex items-center justify-center">
              <div className="text-center text-gray-500">
                <div className="text-6xl mb-4">📹</div>
                <p className="text-lg">Camera Offline</p>
                <p className="text-sm text-gray-400 mt-2">No signal from {selectedCameraData?.id}</p>
              </div>
            </div>
          )}
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
          
          {/* Detection Controls */}
          <div className="bg-white/5 p-4 rounded-lg border border-white/10">
            <h3 className="text-sm font-semibold mb-3 text-white">Detection Controls</h3>
            {selectedCameraData?.type === 'mac-camera' ? (
              <div className="space-y-2">
                <button
                  onClick={isDetecting ? stopDetection : startDetection}
                  disabled={selectedCameraData?.status !== 'online'}
                  className={`w-full py-3 px-4 rounded-lg font-semibold transition-all duration-200 ${
                    isDetecting 
                      ? 'bg-red-500 hover:bg-red-600' 
                      : 'bg-blue-500 hover:bg-blue-600'
                  } ${selectedCameraData?.status !== 'online' ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {isDetecting ? 'Stop Detection' : 'Start Detection'}
                </button>
                <div className="mt-2 text-xs text-gray-300">
                  Status: {selectedCameraData?.status !== 'online' ? 'Camera Offline' : (isDetecting ? 'Detecting...' : 'Ready')}
                </div>
              </div>
            ) : (
              <div className="space-y-2">
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
            )}
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

          {/* Detection Results */}
          <div className="bg-white/5 p-4 rounded-lg border border-white/10">
            <h3 className="text-sm font-semibold mb-3 text-white">Detection Results</h3>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {detectedObjects.map((obj, index) => (
                <div key={`obj-${index}`} className="bg-white/10 p-2 rounded-lg text-xs">
                  <div className="font-semibold text-white">{obj.class_name}</div>
                  <div className="text-gray-300">Confidence: {Math.round(obj.confidence * 100)}%</div>
                  <div className="text-gray-300">Priority: {obj.priority}</div>
                </div>
              ))}
              {detectedPoses.map((pose, index) => (
                <div key={`pose-${index}`} className="bg-white/10 p-2 rounded-lg text-xs">
                  <div className="font-semibold text-white">{pose.action}</div>
                  <div className="text-gray-300">Confidence: {Math.round(pose.confidence * 100)}%</div>
                  <div className="text-gray-300">Priority: {pose.priority}</div>
                </div>
              ))}
              {detectedObjects.length === 0 && detectedPoses.length === 0 && (
                <div className="text-gray-400 text-xs text-center py-4">
                  {isDetecting ? 'No detections yet...' : 'Start detection to see results'}
                </div>
              )}
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
                <span className="text-gray-400">Detection:</span>
                <span className={isDetecting ? 'text-emerald-400' : 'text-red-400'}>
                  {isDetecting ? 'Active' : 'Offline'}
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
