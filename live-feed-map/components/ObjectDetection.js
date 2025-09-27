'use client';

import { useState, useEffect } from 'react';

const ObjectDetection = ({ cameraId = 'FF-001' }) => {
  const [detections, setDetections] = useState([]);
  const [isActive, setIsActive] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [detectionStats, setDetectionStats] = useState({
    totalDetections: 0,
    uniqueObjects: 0,
    lastDetectionTime: null
  });

  // Fetch detection results from API
  const fetchDetections = async () => {
    try {
      const response = await fetch(`/api/object-detection?camera_id=${cameraId}&limit=10`);
      const data = await response.json();
      
      if (data.success && data.results.length > 0) {
        setDetections(data.results);
        setLastUpdate(new Date().toLocaleTimeString());
        
        // Calculate stats
        const allObjects = data.results.flatMap(result => result.detections);
        const uniqueObjects = [...new Set(allObjects.map(obj => obj.class_name))];
        
        setDetectionStats({
          totalDetections: allObjects.length,
          uniqueObjects: uniqueObjects.length,
          lastDetectionTime: data.results[0]?.timestamp
        });
        
        setIsActive(true);
      } else {
        setIsActive(false);
      }
    } catch (error) {
      console.error('Error fetching detections:', error);
      setIsActive(false);
    }
  };

  // Fetch detections every 2 seconds only when running
  useEffect(() => {
    if (!isRunning) return;
    
    const interval = setInterval(fetchDetections, 2000);
    fetchDetections(); // Initial fetch
    
    return () => clearInterval(interval);
  }, [cameraId, isRunning]);

  const toggleDetection = () => {
    setIsRunning(!isRunning);
    if (!isRunning) {
      fetchDetections(); // Initial fetch when starting
    }
  };

  const getObjectColor = (className) => {
    const colors = {
      'person': 'bg-red-500',
      'chair': 'bg-blue-500',
      'table': 'bg-green-500',
      'door': 'bg-yellow-500',
      'window': 'bg-purple-500',
      'laptop': 'bg-indigo-500',
      'book': 'bg-pink-500',
      'bottle': 'bg-cyan-500',
      'default': 'bg-gray-500'
    };
    return colors[className] || colors.default;
  };

  const formatConfidence = (confidence) => {
    return (confidence * 100).toFixed(1);
  };

  return (
    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 shadow-xl">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${isActive ? 'bg-emerald-500 animate-pulse' : 'bg-gray-500'}`}></div>
          <h3 className="text-lg font-semibold text-white">Object Detection</h3>
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

      {/* Detection Stats */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white/5 p-4 rounded-lg border border-white/10">
          <div className="text-sm text-gray-400 mb-1">Total Detections</div>
          <div className="text-2xl font-bold text-white">{detectionStats.totalDetections}</div>
        </div>
        <div className="bg-white/5 p-4 rounded-lg border border-white/10">
          <div className="text-sm text-gray-400 mb-1">Unique Objects</div>
          <div className="text-2xl font-bold text-white">{detectionStats.uniqueObjects}</div>
        </div>
      </div>

      {/* Recent Detections */}
      <div className="mb-6">
        <div className="text-sm text-gray-400 font-medium mb-3">Recent Detections</div>
        <div className="space-y-2 max-h-40 overflow-y-auto">
          {detections.length === 0 ? (
            <div className="text-center text-gray-500 py-4">
              <div className="text-2xl mb-2">🔍</div>
              <div className="text-sm">No objects detected</div>
            </div>
          ) : (
            detections.map((result, index) => (
              <div key={result.id} className="bg-white/5 p-3 rounded-lg border border-white/10">
                <div className="flex justify-between items-center mb-2">
                  <div className="text-xs text-gray-400">
                    {new Date(result.timestamp).toLocaleTimeString()}
                  </div>
                  <div className="text-xs text-emerald-400 font-medium">
                    {result.detection_count} objects
                  </div>
                </div>
                
                {result.detections.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {result.detections.map((detection, detIndex) => (
                      <div
                        key={detIndex}
                        className={`px-2 py-1 rounded text-xs font-medium text-white ${getObjectColor(detection.class_name)}`}
                      >
                        {detection.class_name} ({formatConfidence(detection.confidence)}%)
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
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
            {isRunning && isActive ? 'Detection Active' : 
             isRunning ? 'Starting Detection...' : 'Detection Stopped'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default ObjectDetection;
