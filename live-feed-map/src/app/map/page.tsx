'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function MapPage() {
  const [selectedLayer, setSelectedLayer] = useState('all');
  const [zoomLevel, setZoomLevel] = useState(13);
  const [showHeatZones, setShowHeatZones] = useState(true);
  const [showSafePaths, setShowSafePaths] = useState(true);
  const [showObjects, setShowObjects] = useState(true);

  const mapLayers = [
    { id: 'all', name: 'All Layers', color: 'blue' },
    { id: 'lidar', name: 'LiDAR Data', color: 'green' },
    { id: 'radar', name: 'Radar Data', color: 'yellow' },
    { id: 'thermal', name: 'Thermal', color: 'red' },
    { id: 'structural', name: 'Structural', color: 'purple' }
  ];

  const firefighterPositions = [
    { id: 1, name: 'Firefighter 1', position: [51.505, -0.09], status: 'active' },
    { id: 2, name: 'Firefighter 2', position: [51.506, -0.08], status: 'active' },
    { id: 3, name: 'Firefighter 3', position: [51.504, -0.10], status: 'inactive' }
  ];

  const heatZones = [
    { id: 1, position: [51.5055, -0.089], intensity: 'high', radius: 50 },
    { id: 2, position: [51.5045, -0.091], intensity: 'medium', radius: 30 },
    { id: 3, position: [51.5065, -0.087], intensity: 'low', radius: 20 }
  ];

  const safePaths = [
    { id: 1, start: [51.505, -0.09], end: [51.506, -0.08], status: 'clear' },
    { id: 2, start: [51.506, -0.08], end: [51.504, -0.10], status: 'blocked' },
    { id: 3, start: [51.504, -0.10], end: [51.505, -0.09], status: 'clear' }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 p-4 h-[calc(100vh-80px)]">
        
        {/* Main Map - Takes up 3 columns */}
        <div className="lg:col-span-3 bg-gray-800 rounded-lg p-4 relative">
          <div className="w-full h-full bg-gray-700 rounded-lg flex items-center justify-center relative overflow-hidden">
            {/* Map Placeholder */}
            <div className="text-center text-gray-300">
              <div className="text-6xl mb-4">🗺️</div>
              <p className="text-lg">Interactive Building Map</p>
              <p className="text-sm text-gray-400 mt-2">LiDAR + Radar + Thermal data overlay</p>
            </div>
            
            {/* Map Controls Overlay */}
            <div className="absolute top-4 left-4 bg-black bg-opacity-70 text-white px-3 py-2 rounded">
              <div className="text-sm font-semibold">Zoom: {zoomLevel}</div>
              <div className="text-xs">Layer: {selectedLayer}</div>
            </div>
            
            {/* Firefighter Positions */}
            {firefighterPositions.map((firefighter) => (
              <div
                key={firefighter.id}
                className={`absolute w-4 h-4 rounded-full ${
                  firefighter.status === 'active' ? 'bg-green-500' : 'bg-gray-500'
                } animate-pulse`}
                style={{
                  top: `${20 + firefighter.id * 15}%`,
                  left: `${30 + firefighter.id * 10}%`
                }}
              >
                <div className="absolute -top-6 left-0 text-xs bg-black bg-opacity-70 text-white px-1 rounded whitespace-nowrap">
                  {firefighter.name}
                </div>
              </div>
            ))}
            
            {/* Heat Zones */}
            {showHeatZones && heatZones.map((zone) => (
              <div
                key={zone.id}
                className={`absolute rounded-full border-2 ${
                  zone.intensity === 'high' ? 'border-red-500 bg-red-500 bg-opacity-20' :
                  zone.intensity === 'medium' ? 'border-orange-500 bg-orange-500 bg-opacity-20' :
                  'border-yellow-500 bg-yellow-500 bg-opacity-20'
                }`}
                style={{
                  top: `${25 + zone.id * 20}%`,
                  left: `${40 + zone.id * 15}%`,
                  width: `${zone.radius}px`,
                  height: `${zone.radius}px`
                }}
              >
                <div className="absolute -top-6 left-0 text-xs bg-black bg-opacity-70 text-white px-1 rounded">
                  {zone.intensity} heat
                </div>
              </div>
            ))}
            
            {/* Safe Paths */}
            {showSafePaths && safePaths.map((path) => (
              <div
                key={path.id}
                className={`absolute w-1 h-16 ${
                  path.status === 'clear' ? 'bg-green-500' : 'bg-red-500'
                } transform rotate-45`}
                style={{
                  top: `${35 + path.id * 10}%`,
                  left: `${50 + path.id * 8}%`
                }}
              >
                <div className="absolute -top-6 left-0 text-xs bg-black bg-opacity-70 text-white px-1 rounded">
                  {path.status}
                </div>
              </div>
            ))}
            
            {/* Building Structure Overlay */}
            <div className="absolute inset-8 border-2 border-white border-opacity-30 rounded">
              {/* Simulated building layout */}
              <div className="absolute top-4 left-4 w-16 h-8 border border-white border-opacity-50 rounded"></div>
              <div className="absolute top-4 right-4 w-12 h-12 border border-white border-opacity-50 rounded"></div>
              <div className="absolute bottom-4 left-4 w-20 h-6 border border-white border-opacity-50 rounded"></div>
              <div className="absolute bottom-4 right-4 w-8 h-16 border border-white border-opacity-50 rounded"></div>
            </div>
          </div>
        </div>

        {/* Control Panel - Takes up 1 column */}
        <div className="lg:col-span-1 bg-gray-800 rounded-lg p-4 flex flex-col space-y-4">
          
          {/* Map Layers */}
          <div className="bg-gray-700 p-3 rounded">
            <h3 className="text-sm font-semibold mb-2">Map Layers</h3>
            <div className="space-y-2">
              {mapLayers.map((layer) => (
                <button
                  key={layer.id}
                  onClick={() => setSelectedLayer(layer.id)}
                  className={`w-full text-left p-2 rounded text-xs ${
                    selectedLayer === layer.id 
                      ? 'bg-red-600 text-white' 
                      : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full bg-${layer.color}-500`}></div>
                    {layer.name}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Display Options */}
          <div className="bg-gray-700 p-3 rounded">
            <h3 className="text-sm font-semibold mb-2">Display Options</h3>
            <div className="space-y-2 text-xs">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={showHeatZones}
                  onChange={(e) => setShowHeatZones(e.target.checked)}
                  className="rounded"
                />
                Heat Zones
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={showSafePaths}
                  onChange={(e) => setShowSafePaths(e.target.checked)}
                  className="rounded"
                />
                Safe Paths
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={showObjects}
                  onChange={(e) => setShowObjects(e.target.checked)}
                  className="rounded"
                />
                Objects
              </label>
            </div>
          </div>

          {/* Zoom Controls */}
          <div className="bg-gray-700 p-3 rounded">
            <h3 className="text-sm font-semibold mb-2">Zoom Controls</h3>
            <div className="space-y-2">
              <input
                type="range"
                min="1"
                max="20"
                value={zoomLevel}
                onChange={(e) => setZoomLevel(Number(e.target.value))}
                className="w-full"
              />
              <div className="text-xs text-gray-300 text-center">
                Level: {zoomLevel}
              </div>
            </div>
          </div>

          {/* Firefighter Status */}
          <div className="bg-gray-700 p-3 rounded">
            <h3 className="text-sm font-semibold mb-2">Firefighter Status</h3>
            <div className="space-y-2">
              {firefighterPositions.map((firefighter) => (
                <div key={firefighter.id} className="bg-gray-600 p-2 rounded text-xs">
                  <div className="font-semibold">{firefighter.name}</div>
                  <div className={`text-xs ${
                    firefighter.status === 'active' ? 'text-green-400' : 'text-gray-400'
                  }`}>
                    Status: {firefighter.status}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Environmental Data */}
          <div className="bg-gray-700 p-3 rounded">
            <h3 className="text-sm font-semibold mb-2">Environmental</h3>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span>Temperature:</span>
                <span className="text-red-400">185°F</span>
              </div>
              <div className="flex justify-between">
                <span>Air Quality:</span>
                <span className="text-red-400">Poor</span>
              </div>
              <div className="flex justify-between">
                <span>Visibility:</span>
                <span className="text-yellow-400">Low</span>
              </div>
              <div className="flex justify-between">
                <span>Structural:</span>
                <span className="text-yellow-400">Stable</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

