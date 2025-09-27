'use client';

import { useState, useEffect } from 'react';

const Transcriptions = () => {
  const [transcriptions, setTranscriptions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchTranscriptions = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/transcribe');
      const data = await response.json();
      
      if (data.success) {
        setTranscriptions(data.transcriptions);
      }
    } catch (error) {
      console.error('Error fetching transcriptions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Fetch transcriptions on component mount
    fetchTranscriptions();
    
    // Set up polling to fetch new transcriptions every 5 seconds
    const interval = setInterval(fetchTranscriptions, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-gray-700 p-3 rounded">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-sm font-semibold">Voice Transcriptions</h3>
        <button
          onClick={fetchTranscriptions}
          disabled={isLoading}
          className="text-xs bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded disabled:opacity-50"
        >
          {isLoading ? 'Loading...' : 'Refresh'}
        </button>
      </div>
      
      <div className="max-h-48 overflow-y-auto space-y-2">
        {transcriptions.length === 0 ? (
          <div className="text-xs text-gray-400 text-center py-4">
            No transcriptions yet
          </div>
        ) : (
          transcriptions.map((transcription) => (
            <div key={transcription.id} className="bg-gray-600 p-2 rounded text-xs">
              <div className="flex justify-between items-start mb-1">
                <span className="text-blue-400 font-semibold">
                  {transcription.source}
                </span>
                <span className="text-gray-400 text-xs">
                  {new Date(transcription.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="text-white">
                {transcription.text}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Transcriptions;
