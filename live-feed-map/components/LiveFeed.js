// components/LiveFeed.js
const LiveFeed = () => {
    return (
      <div className="w-full">
        {/* Camera Feed Display */}
        <div className="w-full h-64 bg-gray-700 rounded-lg flex items-center justify-center relative overflow-hidden">
          <div className="text-center text-gray-300">
            <div className="text-4xl mb-2">📹</div>
            <p className="text-sm">Camera Feed</p>
            <p className="text-xs text-gray-400 mt-1">Live video from helmet</p>
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
        </div>
        
        {/* Status Indicators */}
        <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
          <div className="bg-green-600 text-white p-2 rounded text-center">
            <div className="font-bold">Camera</div>
            <div>Online</div>
          </div>
          <div className="bg-green-600 text-white p-2 rounded text-center">
            <div className="font-bold">Audio</div>
            <div>Recording</div>
          </div>
        </div>
      </div>
    );
  };
  
  export default LiveFeed;
  