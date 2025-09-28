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
  const [gestureCount, setGestureCount] = useState(0);
  const [detectedObjects, setDetectedObjects] = useState([]);
  const [detectedGestures, setDetectedGestures] = useState([]);
  const [detectionData, setDetectionData] = useState(null);
  
  // Overlay visibility controls
  const [showObjectDetection, setShowObjectDetection] = useState(true);
  const [showGestureDetection, setShowGestureDetection] = useState(true);
  const [showHUDOverlays, setShowHUDOverlays] = useState(true);
  const [forceUpdate, setForceUpdate] = useState(0);
  
  // Gesture guide visibility
  const [showGestureGuide, setShowGestureGuide] = useState(false);
  
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

  // Track overlay state changes
  useEffect(() => {
    console.log('Overlay states changed:', {
      showObjectDetection,
      showGestureDetection,
      showHUDOverlays,
      forceUpdate
    });
  }, [showObjectDetection, showGestureDetection, showHUDOverlays, forceUpdate]);

  // Handle detection updates from video stream
  const handleDetectionUpdate = (data) => {
    setDetectedObjects(data.detections || []);
    setDetectedGestures(data.gestures || []);
    setObjectCount(data.detections.length);
    setGestureCount(data.gestures.length);
    setDetectionData({
      timestamp: data.timestamp,
      object_detections: data.detections,
      gesture_detections: data.gestures,
      object_count: data.detections.length,
      gesture_count: data.gestures.length
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
          setGestureCount(latest.gesture_count || 0);
          setDetectedObjects(latest.object_detections || []);
          setDetectedGestures(latest.gesture_detections || []);
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
    setGestureCount(0);
    setDetectedObjects([]);
    setDetectedGestures([]);
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
                key={`${selectedCamera}-${showObjectDetection}-${showGestureDetection}-${showHUDOverlays}-${forceUpdate}`}
                cameraId={selectedCamera}
                isDetecting={isDetecting}
                onDetectionUpdate={handleDetectionUpdate}
                showObjectDetection={showObjectDetection}
                showGestureDetection={showGestureDetection}
                showHUDOverlays={showHUDOverlays}
              />
              
              {/* HUD Overlays - Conditionally visible */}
              {showHUDOverlays && (
                <>
                  <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded text-sm font-bold z-20">
                    {isRecording ? 'REC' : 'LIVE'}
                  </div>
                  <div className="absolute top-4 right-4 bg-green-600 text-white px-3 py-1 rounded text-sm z-20">
                    {selectedCameraData.resolution}
                  </div>
                  
                  {/* Detection Overlays */}
                  <div className="absolute bottom-4 left-4 bg-black bg-opacity-70 text-white px-3 py-2 rounded z-20">
                    <div className="text-sm font-semibold">Objects: {objectCount} | Gestures: {gestureCount}</div>
                    <div className="text-xs">
                      {detectedObjects.length > 0 ? `Nearest: ${detectedObjects[0]?.class_name || 'Unknown'}` : 
                       detectedGestures.length > 0 ? `Gesture: ${detectedGestures[0]?.gesture || 'Unknown'}` : 'No detections'}
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
              )}
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

          {/* Overlay Controls */}
          <div className="bg-white/5 p-4 rounded-lg border border-white/10">
            <h3 className="text-sm font-semibold mb-3 text-white">Overlay Controls</h3>
            {/* Debug info */}
            <div className="text-xs text-gray-400 mb-2">
              Debug: Objects={showObjectDetection ? 'ON' : 'OFF'}, Gestures={showGestureDetection ? 'ON' : 'OFF'}, HUD={showHUDOverlays ? 'ON' : 'OFF'} | Update: {forceUpdate}
            </div>
            <div className="space-y-3">
              {/* Object Detection Toggle */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Object Detection</span>
                <button
                  onClick={() => {
                    console.log('Object detection toggle clicked, current state:', showObjectDetection);
                    setShowObjectDetection(!showObjectDetection);
                    setForceUpdate(prev => prev + 1);
                  }}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-200 cursor-pointer hover:scale-105 ${
                    showObjectDetection ? 'bg-blue-500 shadow-lg' : 'bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                      showObjectDetection ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              
              {/* Gesture Detection Toggle */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Gesture Detection</span>
                <button
                  onClick={() => {
                    console.log('Gesture detection toggle clicked, current state:', showGestureDetection);
                    setShowGestureDetection(!showGestureDetection);
                    setForceUpdate(prev => prev + 1);
                  }}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-200 cursor-pointer hover:scale-105 ${
                    showGestureDetection ? 'bg-purple-500 shadow-lg' : 'bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                      showGestureDetection ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              
              {/* HUD Overlays Toggle */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">HUD Overlays</span>
                <button
                  onClick={() => {
                    console.log('HUD overlays toggle clicked, current state:', showHUDOverlays);
                    setShowHUDOverlays(!showHUDOverlays);
                    setForceUpdate(prev => prev + 1);
                  }}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-200 cursor-pointer hover:scale-105 ${
                    showHUDOverlays ? 'bg-green-500 shadow-lg' : 'bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                      showHUDOverlays ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              
              {/* Test Button */}
              <div className="pt-2 border-t border-white/10">
                <button
                  onClick={() => {
                    console.log('Test button clicked!');
                    alert('Test button works! Current states: Objects=' + showObjectDetection + ', Gestures=' + showGestureDetection + ', HUD=' + showHUDOverlays);
                  }}
                  className="w-full px-2 py-1 text-xs bg-yellow-500 hover:bg-yellow-600 text-white rounded transition-colors cursor-pointer mb-2"
                >
                  🧪 Test Button
                </button>
              </div>

              {/* Quick Actions */}
              <div className="pt-2 border-t border-white/10">
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      console.log('Show All clicked');
                      setShowObjectDetection(true);
                      setShowGestureDetection(true);
                      setShowHUDOverlays(true);
                      setForceUpdate(prev => prev + 1);
                    }}
                    className="flex-1 px-2 py-1 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors cursor-pointer"
                  >
                    Show All
                  </button>
                  <button
                    onClick={() => {
                      console.log('Hide All clicked');
                      setShowObjectDetection(false);
                      setShowGestureDetection(false);
                      setShowHUDOverlays(false);
                      setForceUpdate(prev => prev + 1);
                    }}
                    className="flex-1 px-2 py-1 text-xs bg-gray-500 hover:bg-gray-600 text-white rounded transition-colors cursor-pointer"
                  >
                    Hide All
                  </button>
                </div>
              </div>
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
              {detectedGestures.map((gesture, index) => (
                <div key={`gesture-${index}`} className="bg-white/10 p-2 rounded-lg text-xs">
                  <div className="font-semibold text-white">{gesture.gesture} ({gesture.meaning})</div>
                  <div className="text-gray-300">Confidence: {Math.round(gesture.confidence * 100)}%</div>
                  <div className="text-gray-300">Priority: {gesture.priority}</div>
                </div>
              ))}
              {detectedObjects.length === 0 && detectedGestures.length === 0 && (
                <div className="text-gray-400 text-xs text-center py-4">
                  {isDetecting ? 'No detections yet...' : 'Start detection to see results'}
                </div>
              )}
            </div>
          </div>

          {/* Gesture Guide */}
          <div className="bg-white/5 p-4 rounded-lg border border-white/10">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-white">🤚 Gesture Commands</h3>
              <button
                onClick={() => setShowGestureGuide(!showGestureGuide)}
                className="text-xs px-2 py-1 bg-purple-500 hover:bg-purple-600 text-white rounded transition-colors"
              >
                {showGestureGuide ? 'Hide' : 'Show'}
              </button>
            </div>
            
            {showGestureGuide && (
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {/* Peace (V) */}
                <div className="bg-white/10 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">✌️</span>
                    <span className="text-sm font-semibold text-white">Peace (V)</span>
                  </div>
                  <div className="text-xs text-emerald-400 mb-1">→ Room clear</div>
                  <div className="text-xs text-gray-400">Index and middle finger extended in V shape</div>
                </div>

                {/* OK (Circle) */}
                <div className="bg-white/10 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">👌</span>
                    <span className="text-sm font-semibold text-white">OK (Circle)</span>
                  </div>
                  <div className="text-xs text-blue-400 mb-1">→ Detected person</div>
                  <div className="text-xs text-gray-400">Thumb and index finger form circle</div>
                </div>

                {/* Phone */}
                <div className="bg-white/10 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">🤙</span>
                    <span className="text-sm font-semibold text-white">Phone</span>
                  </div>
                  <div className="text-xs text-red-400 mb-1">→ Need help</div>
                  <div className="text-xs text-gray-400">Thumb and pinky extended, spread apart</div>
                </div>

                {/* Thumbs Up */}
                <div className="bg-white/10 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">👍</span>
                    <span className="text-sm font-semibold text-white">Thumbs Up</span>
                  </div>
                  <div className="text-xs text-emerald-400 mb-1">→ Affirmative</div>
                  <div className="text-xs text-gray-400">Thumb pointing up from wrist</div>
                </div>

                {/* Thumbs Down */}
                <div className="bg-white/10 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">👎</span>
                    <span className="text-sm font-semibold text-white">Thumbs Down</span>
                  </div>
                  <div className="text-xs text-red-400 mb-1">→ No/failure</div>
                  <div className="text-xs text-gray-400">Thumb pointing down from wrist</div>
                </div>

                {/* Point Up */}
                <div className="bg-white/10 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">☝️</span>
                    <span className="text-sm font-semibold text-white">Point Up</span>
                  </div>
                  <div className="text-xs text-red-500 mb-1">→ Emergency</div>
                  <div className="text-xs text-gray-400">Index finger pointing up</div>
                </div>

                {/* Flat Hand (Sideways) */}
                <div className="bg-white/10 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">🫱</span>
                    <span className="text-sm font-semibold text-white">Flat Hand (Sideways)</span>
                  </div>
                  <div className="text-xs text-cyan-400 mb-1">→ Let's move</div>
                  <div className="text-xs text-gray-400">Hand flat, fingers spread horizontally</div>
                </div>

                <div className="mt-3 p-2 bg-purple-500/20 rounded border border-purple-500/30">
                  <div className="text-xs text-purple-300 font-semibold mb-1">💡 Pro Tips:</div>
                  <div className="text-xs text-gray-300 space-y-1">
                    <div>• Hold gestures for 1-2 seconds for detection</div>
                    <div>• Keep hand visible in camera frame</div>
                    <div>• Use clear, deliberate movements</div>
                    <div>• Emergency gestures have highest priority</div>
                  </div>
                </div>
              </div>
            )}
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
