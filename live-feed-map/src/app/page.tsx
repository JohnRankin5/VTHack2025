'use client';

import { useState } from 'react';
import Link from 'next/link';
import Map from '../../components/Map';
import LiveFeed from '../../components/LiveFeed';
import Status from '../../components/Status';
import Transcriptions from '../../components/Transcriptions';
import VoiceCommander from '../../components/VoiceCommander';
import SafetyAlert from '../../components/SafetyAlert';
import ObjectDetection from '../../components/ObjectDetection';

export default function Home() {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'Command Center', text: 'Team Alpha, proceed to building 3', timestamp: new Date().toLocaleTimeString() },
    { id: 2, sender: 'Firefighter 1', text: 'Copy that, moving to building 3', timestamp: new Date().toLocaleTimeString() }
  ]);
  const [newMessage, setNewMessage] = useState('');

  const sendMessage = () => {
    if (newMessage.trim()) {
      const message = {
        id: messages.length + 1,
        sender: 'Command Center',
        text: newMessage,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages([...messages, message]);
      setNewMessage('');
    }
  };

  const handleVoiceCommand = (message: any) => {
    setMessages(prev => [message, ...prev]);
  };

  const handleSafetyAlert = (alertData: any) => {
    const alertMessage = {
      id: Date.now(),
      sender: 'Safety System',
      text: `ALERT: ${alertData.firefighterId} - No movement detected for ${Math.floor(alertData.inactivityTime / 1000)}s`,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [alertMessage, ...prev]);
  };

  const handleSafetyOverride = (overrideData: any) => {
    const overrideMessage = {
      id: Date.now(),
      sender: 'Safety System',
      text: `OVERRIDE: ${overrideData.firefighterId} - Manual check-in confirmed (Override #${overrideData.overrideCount})`,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [overrideMessage, ...prev]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
      {/* Status Banner */}
      <div className="bg-gradient-to-r from-emerald-500/20 via-emerald-400/10 to-emerald-500/20 border-b border-emerald-500/30 text-emerald-300 py-4 px-6 text-center backdrop-blur-sm">
        <div className="flex items-center justify-center gap-4">
          <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-400/50"></div>
          <span className="text-sm font-semibold tracking-wide">OPERATIONS ACTIVE - ALL SYSTEMS ONLINE</span>
          <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-400/50"></div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 p-8 h-[calc(100vh-120px)]">
        
        {/* Left Column - Live Feed */}
        <div className="lg:col-span-1 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-md border border-white/20 rounded-2xl p-6 shadow-2xl hover:shadow-red-500/20 transition-all duration-300">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-4 h-4 bg-gradient-to-r from-red-500 to-orange-500 rounded-full animate-pulse shadow-lg shadow-red-500/50"></div>
            <h2 className="text-lg font-bold text-white bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">Live Feed</h2>
          </div>
          <LiveFeed />
        </div>

        {/* Center Column - Map */}
        <div className="lg:col-span-1 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-md border border-white/20 rounded-2xl p-6 shadow-2xl hover:shadow-blue-500/20 transition-all duration-300">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-4 h-4 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full animate-pulse shadow-lg shadow-blue-500/50"></div>
            <h2 className="text-lg font-bold text-white bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">Tactical Map</h2>
          </div>
          <Map />
        </div>

        {/* Right Column - Communications & Status */}
        <div className="lg:col-span-1 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-md border border-white/20 rounded-2xl p-6 shadow-2xl hover:shadow-emerald-500/20 transition-all duration-300 flex flex-col">
          {/* Status Section */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-4 h-4 bg-gradient-to-r from-emerald-500 to-green-500 rounded-full animate-pulse shadow-lg shadow-emerald-500/50"></div>
              <h2 className="text-lg font-bold text-white bg-gradient-to-r from-emerald-400 to-green-400 bg-clip-text text-transparent">System Status</h2>
            </div>
            <Status />
          </div>

          {/* Communications Section */}
          <div className="flex-1 flex flex-col">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-4 h-4 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full animate-pulse shadow-lg shadow-blue-500/50"></div>
              <h2 className="text-lg font-bold text-white bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">Command Center</h2>
            </div>
            
            {/* Safety Alert System */}
            <div className="mb-4">
              <SafetyAlert 
                firefighterId="FF-001" 
                onAlert={handleSafetyAlert}
                onOverride={handleSafetyOverride}
              />
            </div>

            {/* Voice Commander */}
            <div className="mb-4">
              <VoiceCommander onNewCommand={handleVoiceCommand} />
            </div>
            
            {/* Voice Transcriptions from Firefighters */}
            <div className="mb-4">
              <Transcriptions />
            </div>
            
            {/* Object Detection */}
            <div className="mb-4">
              <ObjectDetection cameraId="FF-001" />
            </div>
            
            {/* Messages Display */}
            <div className="flex-1 bg-gradient-to-br from-white/10 to-white/5 rounded-xl p-4 mb-4 overflow-y-auto max-h-32 border border-white/20 backdrop-blur-sm">
              <div className="text-sm text-gray-300 font-semibold mb-3 bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">Communications Log</div>
              {messages.map((message) => (
                <div key={message.id} className="mb-3 p-3 bg-gradient-to-r from-white/10 to-white/5 rounded-lg border-l-4 border-blue-500 shadow-lg hover:shadow-blue-500/20 transition-all duration-200">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-blue-300 font-semibold">{message.sender}</span>
                    <span className="text-xs text-gray-400 font-mono">{message.timestamp}</span>
                  </div>
                  <div className="text-sm text-white font-medium">{message.text}</div>
                </div>
              ))}
            </div>

            {/* Quick Text Commands */}
            <div className="flex gap-3">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Enter command..."
                className="flex-1 bg-gradient-to-r from-white/15 to-white/10 text-white p-3 rounded-lg border border-white/30 focus:border-blue-500 focus:outline-none text-sm font-medium backdrop-blur-sm shadow-lg"
              />
              <button
                onClick={sendMessage}
                className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 px-4 py-3 rounded-lg font-semibold text-sm shadow-lg shadow-blue-500/25 transition-all duration-200 transform hover:scale-[1.02] hover:shadow-blue-500/40"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
