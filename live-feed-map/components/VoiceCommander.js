'use client';

import { useState, useRef, useEffect } from 'react';

const VoiceCommander = ({ onNewCommand }) => {
  const [isJoined, setIsJoined] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const recognitionRef = useRef(null);
  const isSpeakingRef = useRef(isSpeaking); // Use a ref to keep track of the latest value of isSpeaking

  // Update the ref when the isSpeaking state changes
  useEffect(() => {
    isSpeakingRef.current = isSpeaking;
  }, [isSpeaking]);

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      recognitionRef.current = new window.webkitSpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        console.log('Speech recognition result - isSpeaking:', isSpeakingRef.current);
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
            console.log('Final transcript detected:', finalTranscript.trim(), 'isSpeaking:', isSpeakingRef.current);
            // Auto-send final transcript as command only when speaking
            if (finalTranscript.trim() && isSpeakingRef.current) {
              console.log('Sending voice command:', finalTranscript.trim());
              sendVoiceCommand(finalTranscript.trim());
            }
          } else {
            interimTranscript += transcript;
          }
        }

        // Only update transcript when speaking
        if (isSpeakingRef.current) {
          console.log('Updating transcript:', finalTranscript + interimTranscript);
          setTranscript(finalTranscript + interimTranscript);
        } else {
          console.log('Not speaking - ignoring transcript update');
        }
      };

      recognitionRef.current.onend = () => {
        // Restart recognition if joined
        if (isJoined) {
          setTimeout(() => {
            if (recognitionRef.current) {
              recognitionRef.current.start();
            }
          }, 100);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        if (isJoined) {
          // Restart recognition after error
          setTimeout(() => {
            if (recognitionRef.current) {
              recognitionRef.current.start();
            }
          }, 1000);
        }
      };
    }
  }, [isJoined]);

  const joinCall = () => {
    if (recognitionRef.current && !isJoined) {
      setTranscript('');
      setIsJoined(true);
      recognitionRef.current.start();
    }
  };

  const leaveCall = () => {
    if (recognitionRef.current && isJoined) {
      recognitionRef.current.stop();
      setIsJoined(false);
      setIsSpeaking(false);
      setTranscript('');
    }
  };

  const startSpeaking = () => {
    console.log('startSpeaking called - isJoined:', isJoined, 'isSpeaking:', isSpeaking);
    if (isJoined && !isSpeaking) {
      console.log('Starting to speak');
      setIsSpeaking(true);
      setTranscript('');
    }
  };

  const stopSpeaking = () => {
    console.log('stopSpeaking called - isJoined:', isJoined, 'isSpeaking:', isSpeaking);
    if (isJoined && isSpeaking) {
      console.log('Stopping speaking');
      setIsSpeaking(false);
      setTranscript('');
    }
  };


  const sendVoiceCommand = async (commandText) => {
    console.log('Sending voice command:', commandText);
    setIsProcessing(true);
    
    try {
      // Send to voice command API
      const response = await fetch('/api/voice-command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transcript: commandText,
          source: 'command-center',
          timestamp: new Date().toISOString()
        }),
      });

      if (response.ok) {
        console.log('Voice command sent successfully');
        // Also send to transcription API for chat
        const transcribeResponse = await fetch('/api/transcribe', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            transcription: commandText,
            source: 'command-center',
            timestamp: new Date().toISOString()
          }),
        });
        
        if (transcribeResponse.ok) {
          console.log('Transcription sent successfully');
        } else {
          console.error('Failed to send transcription:', transcribeResponse.status);
        }
        
                // Send to main chat via callback
                if (onNewCommand) {
                  const newMessage = {
                    id: Date.now(),
                    sender: 'Command Center',
                    text: commandText,
                    timestamp: new Date().toLocaleTimeString()
                  };
                  onNewCommand(newMessage);
                }
      }
    } catch (error) {
      console.error('Error sending voice command:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-gray-700 p-3 rounded">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-semibold">Command Center Voice</h3>
      </div>

      {/* Voice Controls */}
      <div className="space-y-2 mb-3">
        <div className="space-y-2">
          <button
            onClick={isJoined ? leaveCall : joinCall}
            disabled={isProcessing}
            className={`w-full py-2 px-3 rounded text-xs font-semibold ${
              isJoined 
                ? 'bg-red-600 hover:bg-red-700 text-white' 
                : 'bg-green-600 hover:bg-green-700 text-white'
            } disabled:opacity-50`}
          >
            {isJoined ? '📞 Leave Call' : '📞 Join Call'}
          </button>
          
          {isJoined && (
            <button
              onClick={isSpeaking ? stopSpeaking : startSpeaking}
              disabled={isProcessing}
              className={`w-full py-2 px-3 rounded text-xs font-semibold ${
                isSpeaking 
                  ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                  : 'bg-gray-600 hover:bg-gray-700 text-white'
              } disabled:opacity-50`}
            >
              {isSpeaking ? '🎤 Stop Speaking' : '🎤 Start Speaking'}
            </button>
          )}
        </div>

        {/* Transcript Display */}
        <div className="bg-gray-600 p-2 rounded min-h-[60px]">
          <div className="text-xs text-gray-300 mb-1">Live Transcript:</div>
          <div className="text-sm text-white">
            {!isJoined ? 'Join call to start voice commands' :
             !isSpeaking ? 'Click "Start Speaking" to begin talking' :
             transcript || 'Listening...'}
          </div>
        </div>
        
        {/* Status indicator */}
        {isJoined && (
          <div className="text-xs text-green-400 text-center mb-2">
            {isSpeaking ? '✓ Speaking - Commands auto-send' : '✓ Ready to speak'}
          </div>
        )}

      </div>

      {/* Status Indicators */}
      <div className="flex justify-center text-xs mb-3">
        <div className={`flex items-center gap-1 ${isJoined ? 'text-green-400' : 'text-gray-400'}`}>
          <div className={`w-2 h-2 rounded-full ${isJoined ? 'bg-green-400' : 'bg-gray-400'}`}></div>
          {isJoined ? (isSpeaking ? 'Speaking' : 'In Call - Ready') : 'Disconnected'}
        </div>
      </div>

    </div>
  );
};

export default VoiceCommander;
