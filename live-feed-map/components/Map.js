// components/Map.js
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const Map = () => {
  return (
    <div className="w-full h-64 bg-gray-700 rounded-lg relative overflow-hidden">
      {/* Placeholder for map - you can integrate react-leaflet here */}
      <div className="w-full h-full flex items-center justify-center text-gray-300">
        <div className="text-center">
          <div className="text-4xl mb-2">🗺️</div>
          <p className="text-sm">Building Map</p>
          <p className="text-xs text-gray-400 mt-1">LiDAR-generated 3D map</p>
        </div>
      </div>
      
      {/* Map Overlay Elements */}
      <div className="absolute top-2 left-2 bg-blue-600 text-white px-2 py-1 rounded text-xs">
        Floor 1
      </div>
      <div className="absolute top-2 right-2 bg-yellow-600 text-black px-2 py-1 rounded text-xs font-bold">
        Firefighter
      </div>
      <div className="absolute bottom-2 left-2 bg-red-600 text-white px-2 py-1 rounded text-xs">
        Heat Zone
      </div>
      <div className="absolute bottom-2 right-2 bg-green-600 text-white px-2 py-1 rounded text-xs">
        Safe Path
      </div>
      
      {/* Simulated building layout */}
      <div className="absolute inset-4 border-2 border-white border-opacity-30 rounded">
        <div className="absolute top-2 left-2 w-8 h-8 bg-red-500 rounded-full animate-pulse"></div>
        <div className="absolute bottom-2 right-2 w-6 h-6 bg-green-500 rounded-full"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-blue-500 rounded-full"></div>
      </div>
    </div>
  );
};

export default Map;
