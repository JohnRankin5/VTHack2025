import { NextRequest, NextResponse } from 'next/server';

// In-memory storage for voice commands (in production, use a database)
let voiceCommands: Array<{
  id: string;
  text: string;
  audio?: string;
  source: string;
  timestamp: string;
  status: 'sent' | 'delivered' | 'acknowledged';
}> = [];

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { transcript, audio, source = 'command-center' } = body;

    if (!transcript && !audio) {
      return NextResponse.json(
        { error: 'Transcript or audio is required' },
        { status: 400 }
      );
    }

    // Create new voice command entry
    const newCommand = {
      id: Date.now().toString(),
      text: transcript || 'Voice command',
      audio: audio,
      source: source,
      timestamp: new Date().toISOString(),
      status: 'sent' as const
    };

    // Add to storage
    voiceCommands.push(newCommand);

    // Keep only last 50 commands to prevent memory issues
    if (voiceCommands.length > 50) {
      voiceCommands = voiceCommands.slice(-50);
    }

    console.log('Received voice command:', newCommand);

    // Simulate sending to firefighters (in real implementation, this would send to helmet devices)
    setTimeout(() => {
      // Update status to delivered
      const commandIndex = voiceCommands.findIndex(cmd => cmd.id === newCommand.id);
      if (commandIndex !== -1) {
        voiceCommands[commandIndex].status = 'delivered';
      }
    }, 1000);

    return NextResponse.json({
      success: true,
      message: 'Voice command sent successfully',
      command: newCommand
    });

  } catch (error) {
    console.error('Error processing voice command:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    // Return all voice commands
    return NextResponse.json({
      success: true,
      commands: voiceCommands.reverse() // Most recent first
    });
  } catch (error) {
    console.error('Error fetching voice commands:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
