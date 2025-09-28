'use client';

import { useState, useEffect } from 'react';

const RadarHUD = ({ radarData, isVisible = true }) => {
  const [alertFlash, setAlertFlash] = useState(false);

  // Flash alert for critical situations
  useEffect(() => {
    if (radarData?.collision_warning?.level === 'EMERGENCY') {
      const interval = setInterval(() => {
        setAlertFlash(prev => !prev);
      }, 500);
      return () => clearInterval(interval);
    } else {
      setAlertFlash(false);
    }
  }, [radarData?.collision_warning?.level]);

  if (!isVisible) {
    return null;
  }

  const hudData = radarData?.hud_data || {};
  const collisionWarning = radarData?.collision_warning;
  const distanceViz = radarData?.distance_visualization;
  const systemStats = radarData?.system_stats || {};

  const distance = hudData.distance_m;
  const status = hudData.status || 'NO_DATA';
  const trend = hudData.distance_trend || 'STABLE';

  // Check if radar data is available
  const radarAvailable = radarData && (distance !== null && distance !== undefined);

  // Status color mapping
  const getStatusColor = (status) => {
    switch (status) {
      case 'EMERGENCY': return '#FF0000';
      case 'CRITICAL': return '#FF6600';
      case 'WARNING': return '#FFAA00';
      case 'SAFE': return '#00FF00';
      default: return '#888888';
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'INCREASING': return '↗️';
      case 'DECREASING': return '↘️';
      case 'STABLE': return '➡️';
      default: return '❓';
    }
  };

  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Distance Display - Top Right */}
      <div className="absolute top-4 right-4 pointer-events-auto">
        <div 
          className="bg-black bg-opacity-80 border-2 rounded-lg p-3 min-w-[200px]"
          style={{ borderColor: radarAvailable ? getStatusColor(status) : '#666666' }}
        >
          {radarAvailable ? (
            <>
              <div className="text-white text-lg font-bold mb-1">
                🎯 Distance: {distance.toFixed(1)}m
              </div>
              <div 
                className="text-sm font-medium mb-1"
                style={{ color: getStatusColor(status) }}
              >
                Status: {status} {getTrendIcon(trend)}
              </div>
              {hudData.movement_recommendation && (
                <div className="text-xs text-gray-300">
                  Recommend: {hudData.movement_recommendation.replace('_', ' ')}
                </div>
              )}
              {systemStats.system_health === 'STALE_DATA' && (
                <div className="text-xs text-red-400 mt-1">
                  ⚠️ Radar data stale
                </div>
              )}
            </>
          ) : (
            <>
              <div className="text-gray-400 text-lg font-bold mb-1">
                📡 Radar: OFF
              </div>
              <div className="text-sm text-gray-500 mb-1">
                Status: Not Available
              </div>
              <div className="text-xs text-gray-500">
                Connect radar for distance measurement
              </div>
            </>
          )}
        </div>
      </div>

      {/* Collision Warning - Center Screen */}
      {collisionWarning && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div 
            className={`bg-black bg-opacity-90 border-4 rounded-xl p-6 max-w-md text-center transform transition-all duration-200 ${
              alertFlash && collisionWarning.level === 'EMERGENCY' ? 'scale-110' : 'scale-100'
            }`}
            style={{ 
              borderColor: collisionWarning.color || '#FF0000',
              boxShadow: `0 0 20px ${collisionWarning.color || '#FF0000'}50`
            }}
          >
            <div 
              className="text-2xl font-bold mb-2"
              style={{ color: collisionWarning.color || '#FF0000' }}
            >
              {collisionWarning.level === 'EMERGENCY' && '🚨'} 
              {collisionWarning.level}
              {collisionWarning.level === 'EMERGENCY' && ' 🚨'}
            </div>
            <div className="text-white text-lg mb-2">
              {collisionWarning.message}
            </div>
            <div 
              className="text-xl font-semibold"
              style={{ color: collisionWarning.color || '#FF0000' }}
            >
              {collisionWarning.action}
            </div>
          </div>
        </div>
      )}

      {/* Radar Visualization - Bottom Left */}
      <div className="absolute bottom-4 left-4 pointer-events-auto">
        <div className="bg-black bg-opacity-80 border border-gray-600 rounded-lg p-3">
          <div className={`text-sm font-bold mb-2 text-center ${radarAvailable ? 'text-white' : 'text-gray-500'}`}>
            🔘 RADAR {!radarAvailable && '(OFF)'}
          </div>
          {radarAvailable && distanceViz ? (
            <>
              <RadarDisplay distanceViz={distanceViz} />
              <div className="text-xs text-gray-300 mt-2 text-center">
                Range: {distanceViz.max_range?.toFixed(1)}m
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center" style={{ width: 100, height: 100 }}>
              <div className="text-center">
                <div className="text-gray-500 text-2xl mb-1">📡</div>
                <div className="text-xs text-gray-500">Offline</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* System Status - Bottom Right */}
      <div className="absolute bottom-4 right-4 pointer-events-auto">
        <div className="bg-black bg-opacity-80 border border-gray-600 rounded-lg p-2">
          <div className="text-white text-xs">
            <div>📊 Readings: {systemStats.total_readings || 0}</div>
            <div>⚠️ Alerts: {systemStats.consecutive_alerts || 0}</div>
            <div className={`${systemStats.system_health === 'HEALTHY' ? 'text-green-400' : 'text-red-400'}`}>
              💓 {systemStats.system_health || 'UNKNOWN'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const RadarDisplay = ({ distanceViz }) => {
  const { current_distance, max_range, zones } = distanceViz;
  const size = 100;
  const centerX = size / 2;
  const centerY = size / 2;
  const maxRadius = size / 2 - 10;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="absolute inset-0">
        {/* Background circle */}
        <circle
          cx={centerX}
          cy={centerY}
          r={maxRadius}
          fill="rgba(50, 50, 50, 0.8)"
          stroke="white"
          strokeWidth="1"
        />
        
        {/* Zone circles */}
        {zones?.map((zone, index) => {
          const radius = Math.min((zone.range / max_range) * maxRadius, maxRadius);
          return (
            <circle
              key={index}
              cx={centerX}
              cy={centerY}
              r={radius}
              fill="none"
              stroke={zone.color}
              strokeWidth="1"
              opacity="0.6"
            />
          );
        })}
        
        {/* Current distance indicator */}
        {current_distance <= max_range && (
          <>
            <line
              x1={centerX}
              y1={centerY}
              x2={centerX}
              y2={centerY - (current_distance / max_range) * maxRadius}
              stroke={current_distance <= 0.5 ? '#FF0000' : 
                     current_distance <= 1.0 ? '#FF6600' : 
                     current_distance <= 2.0 ? '#FFAA00' : '#00FF00'}
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle
              cx={centerX}
              cy={centerY - (current_distance / max_range) * maxRadius}
              r="3"
              fill={current_distance <= 0.5 ? '#FF0000' : 
                    current_distance <= 1.0 ? '#FF6600' : 
                    current_distance <= 2.0 ? '#FFAA00' : '#00FF00'}
            />
          </>
        )}
        
        {/* Crosshairs */}
        <line x1={centerX - 5} y1={centerY} x2={centerX + 5} y2={centerY} stroke="white" strokeWidth="1" opacity="0.5" />
        <line x1={centerX} y1={centerY - 5} x2={centerX} y2={centerY + 5} stroke="white" strokeWidth="1" opacity="0.5" />
      </svg>
      
      {/* Distance text overlay */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-white text-xs font-bold bg-black bg-opacity-60 px-1 rounded">
          {current_distance?.toFixed(1)}m
        </div>
      </div>
    </div>
  );
};

export default RadarHUD;
