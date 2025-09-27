'use client';

import { useState } from 'react';
import Link from 'next/link';
import Map from '../../components/Map';
import LiveFeed from '../../components/LiveFeed';
import Status from '../../components/Status';
import Transcriptions from '../../components/Transcriptions';
import VoiceCommander from '../../components/VoiceCommander';
import SafetyAlert from '../../components/SafetyAlert';

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
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Status Banner */}
      <div className="bg-emerald-500/10 border-b border-emerald-500/20 text-emerald-400 py-3 px-6 text-center">
        <div className="flex items-center justify-center gap-3">
          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium">Operations Active</span>
          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 p-8 h-[calc(100vh-120px)]">
        
        {/* Left Column - Live Feed */}
        <div className="lg:col-span-1 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <h2 className="text-lg font-semibold text-white">Live Feed</h2>
          </div>
          <LiveFeed />
        </div>

        {/* Center Column - Map */}
        <div className="lg:col-span-1 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
            <h2 className="text-lg font-semibold text-white">Tactical Map</h2>
          </div>
          <Map />
        </div>

        {/* Right Column - Communications & Status */}
        <div className="lg:col-span-1 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 shadow-xl flex flex-col">
          {/* Status Section */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
              <h2 className="text-lg font-semibold text-white">System Status</h2>
            </div>
            <Status />
          </div>

          {/* Communications Section */}
          <div className="flex-1 flex flex-col">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
              <h2 className="text-lg font-semibold text-white">Command Center</h2>
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
            
            {/* Messages Display */}
            <div className="flex-1 bg-white/5 rounded-xl p-4 mb-4 overflow-y-auto max-h-32 border border-white/10">
              <div className="text-sm text-gray-400 font-medium mb-3">Communications Log</div>
              {messages.map((message) => (
                <div key={message.id} className="mb-3 p-3 bg-white/5 rounded-lg border-l-4 border-blue-500">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-blue-400 font-medium">{message.sender}</span>
                    <span className="text-xs text-gray-400 font-mono">{message.timestamp}</span>
                  </div>
                  <div className="text-sm text-white">{message.text}</div>
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
                className="flex-1 bg-white/10 text-white p-3 rounded-lg border border-white/20 focus:border-blue-500 focus:outline-none text-sm font-medium"
              />
              <button
                onClick={sendMessage}
                className="bg-blue-500 hover:bg-blue-600 px-4 py-3 rounded-lg font-medium text-sm shadow-lg transition-all duration-200 transform hover:scale-[1.02]"
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
