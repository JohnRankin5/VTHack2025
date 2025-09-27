// components/Status.js
const Status = () => {
    return (
      <div className="space-y-2">
        {/* Connection Status */}
        <div className="bg-gray-700 p-3 rounded">
          <div className="text-sm font-semibold mb-2">System Status</div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span>Helmet Connection:</span>
              <span className="text-green-400">Active</span>
            </div>
            <div className="flex justify-between">
              <span>LiDAR:</span>
              <span className="text-green-400">Online</span>
            </div>
            <div className="flex justify-between">
              <span>Radar:</span>
              <span className="text-green-400">Online</span>
            </div>
            <div className="flex justify-between">
              <span>IMU:</span>
              <span className="text-green-400">Connected</span>
            </div>
            <div className="flex justify-between">
              <span>Camera:</span>
              <span className="text-green-400">Recording</span>
            </div>
          </div>
        </div>

        {/* Environmental Data */}
        <div className="bg-gray-700 p-3 rounded">
          <div className="text-sm font-semibold mb-2">Environmental</div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span>Temperature:</span>
              <span className="text-yellow-400">85°F</span>
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
              <span>Battery:</span>
              <span className="text-green-400">87%</span>
            </div>
          </div>
        </div>

        {/* Object Detection */}
        <div className="bg-gray-700 p-3 rounded">
          <div className="text-sm font-semibold mb-2">Object Detection</div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span>Objects Detected:</span>
              <span className="text-yellow-400">3</span>
            </div>
            <div className="flex justify-between">
              <span>Nearest Object:</span>
              <span className="text-red-400">2.3m</span>
            </div>
            <div className="flex justify-between">
              <span>Safe Distance:</span>
              <span className="text-green-400">Maintained</span>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  export default Status;
  