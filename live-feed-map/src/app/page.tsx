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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black text-white">
      {/* Emergency Status Banner */}
      <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white py-2 px-4 text-center">
        <div className="flex items-center justify-center gap-2">
          <div className="w-2 h-2 bg-yellow-300 rounded-full animate-pulse"></div>
          <span className="text-sm font-bold tracking-wide">TACTICAL OPERATIONS ACTIVE</span>
          <div className="w-2 h-2 bg-yellow-300 rounded-full animate-pulse"></div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6 h-[calc(100vh-140px)]">
        
        {/* Left Column - Live Feed */}
        <div className="lg:col-span-1 bg-gradient-to-b from-slate-800 to-slate-900 rounded-xl p-6 shadow-2xl border border-orange-500/20">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <h2 className="text-xl font-bold text-orange-400 tracking-wide">LIVE FEED</h2>
          </div>
          <LiveFeed />
        </div>

        {/* Center Column - Map */}
        <div className="lg:col-span-1 bg-gradient-to-b from-slate-800 to-slate-900 rounded-xl p-6 shadow-2xl border border-orange-500/20">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
            <h2 className="text-xl font-bold text-blue-400 tracking-wide">TACTICAL MAP</h2>
          </div>
          <Map />
        </div>

        {/* Right Column - Communications & Status */}
        <div className="lg:col-span-1 bg-gradient-to-b from-slate-800 to-slate-900 rounded-xl p-6 shadow-2xl border border-orange-500/20 flex flex-col">
          {/* Status Section */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <h2 className="text-xl font-bold text-green-400 tracking-wide">SYSTEM STATUS</h2>
            </div>
            <Status />
          </div>

          {/* Communications Section */}
          <div className="flex-1 flex flex-col">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse"></div>
              <h2 className="text-xl font-bold text-purple-400 tracking-wide">COMMAND CENTER</h2>
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
            <div className="flex-1 bg-slate-700/50 rounded-lg p-4 mb-4 overflow-y-auto max-h-32 border border-slate-600/50">
              <div className="text-xs text-slate-400 font-semibold mb-2 tracking-wide">COMMUNICATIONS LOG</div>
              {messages.map((message) => (
                <div key={message.id} className="mb-3 p-3 bg-slate-600/50 rounded-lg border-l-4 border-orange-500">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-orange-300 font-bold">{message.sender}</span>
                    <span className="text-xs text-slate-400 font-mono">{message.timestamp}</span>
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
                placeholder="Enter tactical command..."
                className="flex-1 bg-slate-700 text-white p-3 rounded-lg border border-slate-600 focus:border-orange-500 focus:outline-none text-sm font-medium"
              />
              <button
                onClick={sendMessage}
                className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 px-4 py-3 rounded-lg font-bold text-sm shadow-lg transition-all duration-200 transform hover:scale-105"
              >
                SEND
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
