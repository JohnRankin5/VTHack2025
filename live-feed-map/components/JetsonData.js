'use client';

import { useState, useEffect } from 'react';

const JetsonData = () => {
  const [sensorData, setSensorData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  const fetchSensorData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch('/api/jetson-data?count=20');
      const data = await response.json();
      
      if (data.success) {
        setSensorData(data.data);
      } else {
        setError(data.error || 'Failed to fetch sensor data');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/sensor-stats');
      const data = await response.json();
      
      if (data.success) {
        setStats(data.stats);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  useEffect(() => {
    if (isRunning) {
      fetchSensorData();
      fetchStats();
      
      const interval = setInterval(() => {
        fetchSensorData();
        fetchStats();
      }, 2000); // Poll every 2 seconds
      
      return () => clearInterval(interval);
    }
  }, [isRunning]);

  const toggleDataCollection = () => {
    setIsRunning(!isRunning);
    if (!isRunning) {
      fetchSensorData();
      fetchStats();
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getDataValue = (entry) => {
    if (typeof entry.processed_data === 'object') {
      return JSON.stringify(entry.processed_data, null, 2);
    }
    return entry.processed_data || entry.raw_data;
  };

  return (
    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 shadow-xl">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-emerald-500 animate-pulse' : 'bg-gray-500'}`}></div>
          <h3 className="text-lg font-semibold text-white">Jetson Sensor Data</h3>
        </div>
        <div className="flex items-center gap-3">
          {stats && (
            <div className="text-sm text-gray-400">
              Total: {stats.total_entries} entries
            </div>
          )}
          <button
            onClick={toggleDataCollection}
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

      {/* Stats Display */}
      {stats && (
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white/5 p-4 rounded-lg border border-white/10">
            <div className="text-sm text-gray-400 mb-1">Total Entries</div>
            <div className="text-2xl font-bold text-white">{stats.total_entries}</div>
          </div>
          <div className="bg-white/5 p-4 rounded-lg border border-white/10">
            <div className="text-sm text-gray-400 mb-1">Latest Update</div>
            <div className="text-sm font-medium text-white">
              {stats.latest_timestamp ? formatTimestamp(stats.latest_timestamp) : 'No data'}
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-4 rounded-lg mb-6">
          <div className="font-semibold">Error:</div>
          <div className="text-sm">{error}</div>
        </div>
      )}

      {/* Data Display */}
      <div className="mb-6">
        <div className="text-sm text-gray-400 font-medium mb-3">Recent Sensor Data</div>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {isLoading && sensorData.length === 0 ? (
            <div className="text-center text-gray-500 py-4">
              <div className="text-2xl mb-2">📡</div>
              <div className="text-sm">Loading sensor data...</div>
            </div>
          ) : sensorData.length === 0 ? (
            <div className="text-center text-gray-500 py-4">
              <div className="text-2xl mb-2">📡</div>
              <div className="text-sm">No sensor data received</div>
              <div className="text-xs text-gray-400 mt-1">Start data collection to begin receiving data</div>
            </div>
          ) : (
            sensorData.map((entry) => (
              <div key={entry.id} className="bg-white/5 p-3 rounded-lg border border-white/10">
                <div className="flex justify-between items-center mb-2">
                  <div className="text-xs text-gray-400">
                    ID: {entry.id} | {formatTimestamp(entry.timestamp)}
                  </div>
                  <div className="text-xs text-emerald-400 font-medium">
                    {entry.source}
                  </div>
                </div>
                
                <div className="space-y-1">
                  <div className="text-xs text-gray-400">Raw Data:</div>
                  <div className="text-sm text-white font-mono bg-gray-800/50 p-2 rounded">
                    {entry.raw_data}
                  </div>
                  
                  {entry.processed_data && (
                    <>
                      <div className="text-xs text-gray-400">Processed Data:</div>
                      <div className="text-sm text-white font-mono bg-gray-800/50 p-2 rounded max-h-20 overflow-y-auto">
                        {getDataValue(entry)}
                      </div>
                    </>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Status Display */}
      <div className="flex justify-center">
        <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
          isRunning 
            ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400' 
            : 'bg-gray-500/10 border border-gray-500/30 text-gray-400'
        }`}>
          <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-emerald-500' : 'bg-gray-500'}`}></div>
          <span className="text-sm font-medium">
            {isRunning ? 'Receiving Data' : 'Data Collection Stopped'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default JetsonData;
