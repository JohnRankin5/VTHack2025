'use client';

import { useState } from 'react';
import Map from '../../components/Map';
import LiveFeed from '../../components/LiveFeed';
import Status from '../../components/Status';

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

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-red-600 p-4 shadow-lg">
        <h1 className="text-2xl font-bold text-center">Firefighter Helmet HUD</h1>
      </header>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 p-4 h-[calc(100vh-80px)]">
        
        {/* Left Column - Live Feed */}
        <div className="lg:col-span-1 bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4 text-center">Live Camera Feed</h2>
          <LiveFeed />
        </div>

        {/* Center Column - Map */}
        <div className="lg:col-span-1 bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4 text-center">Building Map</h2>
          <Map />
        </div>

        {/* Right Column - Communications & Status */}
        <div className="lg:col-span-1 bg-gray-800 rounded-lg p-4 flex flex-col">
          {/* Status Section */}
          <div className="mb-4">
            <h2 className="text-lg font-semibold mb-2">System Status</h2>
            <Status />
          </div>

          {/* Communications Section */}
          <div className="flex-1 flex flex-col">
            <h2 className="text-lg font-semibold mb-2">Communications</h2>
            
            {/* Messages Display */}
            <div className="flex-1 bg-gray-700 rounded p-3 mb-3 overflow-y-auto max-h-48">
              {messages.map((message) => (
                <div key={message.id} className="mb-2 p-2 bg-gray-600 rounded">
                  <div className="text-xs text-gray-300">{message.sender} - {message.timestamp}</div>
                  <div className="text-sm">{message.text}</div>
                </div>
              ))}
            </div>

            {/* Message Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type message..."
                className="flex-1 bg-gray-700 text-white p-2 rounded border border-gray-600 focus:border-red-500 focus:outline-none"
              />
              <button
                onClick={sendMessage}
                className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded font-semibold"
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
