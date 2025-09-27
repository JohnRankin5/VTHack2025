'use client';

import { useState, useEffect } from 'react';

const GestureDetection = () => {
  const [detections, setDetections] = useState([]);
  const [isActive, setIsActive] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [emergencyAlerts, setEmergencyAlerts] = useState([]);
  const [gestureStats, setGestureStats] = useState({
    totalGestures: 0,
    emergencyGestures: 0,
    lastGestureTime: null
  });

  // Fetch detection results from API
  const fetchDetections = async () => {
    try {
      const response = await fetch(`/api/object-detection?camera_id=FF-001&limit=10`);
      const data = await response.json();
      
      if (data.success && data.results.length > 0) {
        setDetections(data.results);
        setLastUpdate(new Date().toLocaleTimeString());
        
        // Extract gesture data from results
        const allGestures = data.results.flatMap(result => result.gesture_detections || []);
        const emergencyGestures = data.results.flatMap(result => result.emergency_gestures || []);
        
        setGestureStats({
          totalGestures: allGestures.length,
          emergencyGestures: emergencyGestures.length,
          lastGestureTime: allGestures.length > 0 ? allGestures[0].timestamp : null
        });
        
        // Handle emergency gestures
        if (emergencyGestures.length > 0) {
          const newAlerts = emergencyGestures.map(gesture => ({
            id: Date.now() + Math.random(),
            gesture: gesture.gesture,
            meaning: gesture.meaning,
            timestamp: new Date().toLocaleTimeString(),
            priority: gesture.priority
          }));
          setEmergencyAlerts(prev => [...newAlerts, ...prev].slice(0, 5)); // Keep last 5 alerts
        }
        
        setIsActive(true);
      } else {
        setIsActive(false);
      }
    } catch (error) {
      console.error('Error fetching gesture detections:', error);
      setIsActive(false);
    }
  };

  // Fetch detections every 2 seconds
  useEffect(() => {
    if (!isRunning) return;
    
    const interval = setInterval(fetchDetections, 2000);
    fetchDetections(); // Initial fetch
    
    return () => clearInterval(interval);
  }, [isRunning]);

  const toggleDetection = () => {
    setIsRunning(!isRunning);
    if (!isRunning) {
      fetchDetections(); // Initial fetch when starting
    }
  };

  const getGestureColor = (gesture) => {
    const colors = {
      'peace': 'bg-green-500',
      'ok': 'bg-blue-500',
      'phone': 'bg-red-500',
      'thumbs_up': 'bg-emerald-500',
      'thumbs_down': 'bg-orange-500',
      'open_hand': 'bg-yellow-500',
      'point_up': 'bg-red-600',
      'stop': 'bg-yellow-600',
      'move': 'bg-purple-500',
      'default': 'bg-gray-500'
    };
    return colors[gesture] || colors.default;
  };

  const getPriorityColor = (priority) => {
    if (priority >= 9) return 'text-red-400 border-red-400';
    if (priority >= 7) return 'text-yellow-400 border-yellow-400';
    return 'text-green-400 border-green-400';
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 shadow-xl">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${isActive ? 'bg-emerald-500 animate-pulse' : 'bg-gray-500'}`}></div>
          <h3 className="text-lg font-semibold text-white">Hand Gesture Detection</h3>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-sm text-gray-400">
            {lastUpdate && `Last update: ${lastUpdate}`}
          </div>
          <button
            onClick={toggleDetection}
            className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all duration-200 ${
              isRunning 
                ? 'bg-red-500 hover:bg-red-600 text-white' 
                : 'bg-emerald-500 hover:bg-emerald-600 text-white'
            }`}
          >
            {isRunning ? 'Stop' : 'Start'}
          </button>
        </div>
      </div>

      {/* Emergency Alerts */}
      {emergencyAlerts.length > 0 && (
        <div className="mb-6">
          <div className="text-sm text-red-400 font-medium mb-3">🚨 Emergency Alerts</div>
          <div className="space-y-2">
            {emergencyAlerts.map((alert) => (
              <div key={alert.id} className="bg-red-500/10 border border-red-500/30 p-3 rounded-lg">
                <div className="flex justify-between items-center">
                  <div className="text-red-400 font-semibold">{alert.gesture}</div>
                  <div className="text-xs text-red-300">{alert.timestamp}</div>
                </div>
                <div className="text-sm text-red-300">{alert.meaning}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Gesture Stats */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white/5 p-4 rounded-lg border border-white/10">
          <div className="text-sm text-gray-400 mb-1">Total Gestures</div>
          <div className="text-2xl font-bold text-white">{gestureStats.totalGestures}</div>
        </div>
        <div className="bg-white/5 p-4 rounded-lg border border-white/10">
          <div className="text-sm text-gray-400 mb-1">Emergency Gestures</div>
          <div className="text-2xl font-bold text-red-400">{gestureStats.emergencyGestures}</div>
        </div>
      </div>

      {/* Recent Gesture Detections */}
      <div className="mb-6">
        <div className="text-sm text-gray-400 font-medium mb-3">Recent Gestures</div>
        <div className="space-y-2 max-h-40 overflow-y-auto">
          {detections.length === 0 ? (
            <div className="text-center text-gray-500 py-4">
              <div className="text-2xl mb-2">👋</div>
              <div className="text-sm">No gestures detected</div>
              <div className="text-xs text-gray-400 mt-1">Start detection to begin monitoring</div>
            </div>
          ) : (
            detections.map((result, index) => (
              result.gesture_detections && result.gesture_detections.length > 0 ? (
                <div key={result.id} className="bg-white/5 p-3 rounded-lg border border-white/10">
                  <div className="flex justify-between items-center mb-2">
                    <div className="text-xs text-gray-400">
                      {formatTimestamp(result.timestamp)}
                    </div>
                    <div className="text-xs text-emerald-400 font-medium">
                      {result.gesture_count} gestures
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap gap-1">
                    {result.gesture_detections.map((gesture, gestureIndex) => (
                      <div
                        key={gestureIndex}
                        className={`px-2 py-1 rounded text-xs font-medium text-white ${getGestureColor(gesture.gesture)}`}
                      >
                        {gesture.gesture}: {gesture.meaning}
                      </div>
                    ))}
                  </div>
                </div>
              ) : null
            ))
          )}
        </div>
      </div>

      {/* Gesture Legend */}
      <div className="mb-6">
        <div className="text-sm text-gray-400 font-medium mb-3">Gesture Meanings</div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded"></div>
            <span className="text-white">Peace (V) - Room clear</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span className="text-white">OK - Detected person</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span className="text-white">Phone - Need help</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-emerald-500 rounded"></div>
            <span className="text-white">Thumbs up - Affirmative</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-orange-500 rounded"></div>
            <span className="text-white">Thumbs down - No/Failure</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded"></div>
            <span className="text-white">Open hand - Stop/Freeze</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-600 rounded"></div>
            <span className="text-white">Point up - Emergency</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-purple-500 rounded"></div>
            <span className="text-white">Move - Let's move</span>
          </div>
        </div>
      </div>

      {/* Detection Status */}
      <div className="flex justify-center">
        <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
          isRunning && isActive 
            ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400' 
            : isRunning
            ? 'bg-yellow-500/10 border border-yellow-500/30 text-yellow-400'
            : 'bg-gray-500/10 border border-gray-500/30 text-gray-400'
        }`}>
          <div className={`w-2 h-2 rounded-full ${
            isRunning && isActive ? 'bg-emerald-500' : 
            isRunning ? 'bg-yellow-500' : 'bg-gray-500'
          }`}></div>
          <span className="text-sm font-medium">
            {isRunning && isActive ? 'Gesture Detection Active' : 
             isRunning ? 'Starting Detection...' : 'Gesture Detection Stopped'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default GestureDetection;
