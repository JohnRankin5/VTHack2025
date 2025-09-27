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
    <div className="bg-gradient-to-b from-slate-700 to-slate-800 p-4 rounded-lg border border-orange-500/30 shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
          <h3 className="text-sm font-bold text-orange-400 tracking-wide">VOICE COMMAND</h3>
        </div>
      </div>

      {/* Voice Controls */}
      <div className="space-y-2 mb-3">
        <div className="space-y-2">
          <button
            onClick={isJoined ? leaveCall : joinCall}
            disabled={isProcessing}
            className={`w-full py-3 px-4 rounded-lg text-sm font-bold transition-all duration-200 ${
              isJoined 
                ? 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white shadow-lg' 
                : 'bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white shadow-lg'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isJoined ? '📞 DISCONNECT' : '📞 CONNECT'}
          </button>
          
          {isJoined && (
            <button
              onClick={isSpeaking ? stopSpeaking : startSpeaking}
              disabled={isProcessing}
              className={`w-full py-3 px-4 rounded-lg text-sm font-bold transition-all duration-200 ${
                isSpeaking 
                  ? 'bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white shadow-lg animate-pulse' 
                  : 'bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-700 hover:to-slate-800 text-white shadow-lg'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isSpeaking ? '🎤 TRANSMITTING' : '🎤 TRANSMIT'}
            </button>
          )}
        </div>

        {/* Transcript Display */}
        <div className="bg-slate-600/50 p-3 rounded-lg min-h-[60px] border border-slate-500/50">
          <div className="text-xs text-slate-300 mb-2 font-semibold tracking-wide">LIVE TRANSCRIPT</div>
          <div className="text-sm text-white font-mono">
            {!isJoined ? 'Connect to establish voice link' :
             !isSpeaking ? 'Click TRANSMIT to begin speaking' :
             transcript || 'Listening for voice input...'}
          </div>
        </div>
        
        {/* Status indicator */}
        {isJoined && (
          <div className="text-xs text-center mb-2 p-2 bg-slate-700/50 rounded-lg border border-slate-600/50">
            <div className={`font-bold ${isSpeaking ? 'text-orange-400' : 'text-green-400'}`}>
              {isSpeaking ? '🔴 TRANSMITTING - Auto-send active' : '🟢 READY - Voice link established'}
            </div>
          </div>
        )}

      </div>

      {/* Status Indicators */}
      <div className="flex justify-center text-xs mb-3">
        <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${
          isJoined 
            ? isSpeaking 
              ? 'bg-orange-500/20 border-orange-500/50 text-orange-400' 
              : 'bg-green-500/20 border-green-500/50 text-green-400'
            : 'bg-slate-500/20 border-slate-500/50 text-slate-400'
        }`}>
          <div className={`w-2 h-2 rounded-full ${
            isJoined 
              ? isSpeaking 
                ? 'bg-orange-400 animate-pulse' 
                : 'bg-green-400 animate-pulse'
              : 'bg-slate-400'
          }`}></div>
          <span className="font-bold tracking-wide">
            {isJoined ? (isSpeaking ? 'TRANSMITTING' : 'CONNECTED') : 'OFFLINE'}
          </span>
        </div>
      </div>

    </div>
  );
};

export default VoiceCommander;
