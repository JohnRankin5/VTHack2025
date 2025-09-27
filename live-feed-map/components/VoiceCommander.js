'use client';

import { useState, useRef, useEffect } from 'react';

const VoiceCommander = () => {
  const [isJoined, setIsJoined] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      recognitionRef.current = new window.webkitSpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
            // Auto-send final transcript as command
            if (finalTranscript.trim()) {
              console.log('Final transcript detected:', finalTranscript.trim());
              sendVoiceCommand(finalTranscript.trim());
            }
          } else {
            interimTranscript += transcript;
          }
        }

        setTranscript(finalTranscript + interimTranscript);
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
  }, []);

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
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await sendAudioToFirefighters(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Microphone access denied. Please allow microphone access.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
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
        
        // Add to local messages
        const newMessage = {
          id: Date.now(),
          type: 'voice-command',
          text: commandText,
          timestamp: new Date().toLocaleTimeString(),
          status: 'sent'
        };
        
        setMessages(prev => [newMessage, ...prev]);
        
        // Show success feedback
        setTimeout(() => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === newMessage.id 
                ? { ...msg, status: 'delivered' }
                : msg
            )
          );
        }, 1000);
      }
    } catch (error) {
      console.error('Error sending voice command:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const sendAudioToFirefighters = async (audioBlob) => {
    setIsProcessing(true);
    
    try {
      // Convert audio to base64 for transmission
      const reader = new FileReader();
      reader.onload = async () => {
        const base64Audio = reader.result.split(',')[1];
        
        // Send to API
        const response = await fetch('/api/voice-command', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            audio: base64Audio,
            transcript: transcript,
            source: 'command-center',
            timestamp: new Date().toISOString()
          }),
        });

        if (response.ok) {
          // Also send transcript to chat
          if (transcript.trim()) {
            await fetch('/api/transcribe', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                transcription: transcript,
                source: 'command-center',
                timestamp: new Date().toISOString()
              }),
            });
          }
          
          // Add to messages
          const newMessage = {
            id: Date.now(),
            type: 'voice-command',
            text: transcript || 'Voice command sent',
            timestamp: new Date().toLocaleTimeString(),
            status: 'sent'
          };
          
          setMessages(prev => [newMessage, ...prev]);
          setTranscript('');
          
          // Show success feedback
          setTimeout(() => {
            setMessages(prev => 
              prev.map(msg => 
                msg.id === newMessage.id 
                  ? { ...msg, status: 'delivered' }
                  : msg
              )
            );
          }, 1000);
        }
      };
      
      reader.readAsDataURL(audioBlob);
    } catch (error) {
      console.error('Error sending voice command:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const sendTextMessage = async () => {
    if (!transcript.trim()) return;
    
    await sendVoiceCommand(transcript);
    setTranscript('');
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return (
    <div className="bg-gray-700 p-3 rounded">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-semibold">Command Center Voice</h3>
        <button
          onClick={clearMessages}
          className="text-xs bg-gray-600 hover:bg-gray-500 px-2 py-1 rounded"
        >
          Clear
        </button>
      </div>

      {/* Voice Controls */}
      <div className="space-y-2 mb-3">
        <div className="flex gap-2">
          <button
            onClick={isJoined ? leaveCall : joinCall}
            disabled={isProcessing}
            className={`flex-1 py-2 px-3 rounded text-xs font-semibold ${
              isJoined 
                ? 'bg-red-600 hover:bg-red-700 text-white' 
                : 'bg-green-600 hover:bg-green-700 text-white'
            } disabled:opacity-50`}
          >
            {isJoined ? '📞 Leave Call' : '📞 Join Call'}
          </button>
          
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing || !isJoined}
            className={`flex-1 py-2 px-3 rounded text-xs font-semibold ${
              isRecording 
                ? 'bg-red-600 hover:bg-red-700 text-white' 
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            } disabled:opacity-50`}
          >
            {isRecording ? '⏹️ Stop Recording' : '🔴 Record Audio'}
          </button>
        </div>

        {/* Transcript Display */}
        <div className="bg-gray-600 p-2 rounded min-h-[60px]">
          <div className="text-xs text-gray-300 mb-1">Live Transcript:</div>
          <div className="text-sm text-white">
            {isJoined ? (transcript || 'Listening for commands...') : 'Join call to start voice commands'}
          </div>
        </div>

        {/* Send Button */}
        <button
          onClick={sendTextMessage}
          disabled={!transcript.trim() || isProcessing || !isJoined}
          className="w-full py-2 px-3 bg-purple-600 hover:bg-purple-700 text-white rounded text-xs font-semibold disabled:opacity-50"
        >
          {isProcessing ? 'Sending...' : '📤 Send Command'}
        </button>
      </div>

      {/* Status Indicators */}
      <div className="flex justify-between text-xs mb-3">
        <div className={`flex items-center gap-1 ${isJoined ? 'text-green-400' : 'text-gray-400'}`}>
          <div className={`w-2 h-2 rounded-full ${isJoined ? 'bg-green-400' : 'bg-gray-400'}`}></div>
          {isJoined ? 'In Call' : 'Disconnected'}
        </div>
        <div className={`flex items-center gap-1 ${isRecording ? 'text-red-400' : 'text-gray-400'}`}>
          <div className={`w-2 h-2 rounded-full ${isRecording ? 'bg-red-400' : 'bg-gray-400'}`}></div>
          {isRecording ? 'Recording' : 'Ready'}
        </div>
      </div>

      {/* Command History */}
      <div className="max-h-32 overflow-y-auto">
        <div className="text-xs text-gray-300 mb-2">Recent Commands:</div>
        {messages.length === 0 ? (
          <div className="text-xs text-gray-400 text-center py-2">
            No commands sent yet
          </div>
        ) : (
          messages.slice(0, 5).map((message) => (
            <div key={message.id} className="bg-gray-600 p-2 rounded mb-1 text-xs">
              <div className="flex justify-between items-start">
                <span className="text-white">{message.text}</span>
                <span className={`text-xs ${
                  message.status === 'delivered' ? 'text-green-400' : 'text-yellow-400'
                }`}>
                  {message.status === 'delivered' ? '✓' : '⏳'}
                </span>
              </div>
              <div className="text-gray-400 text-xs mt-1">
                {message.timestamp} • {message.type}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default VoiceCommander;
