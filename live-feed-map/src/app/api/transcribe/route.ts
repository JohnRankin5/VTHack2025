import { NextRequest, NextResponse } from 'next/server';

// In-memory storage for transcriptions (in production, use a database)
let transcriptions: Array<{
  id: string;
  text: string;
  timestamp: string;
  source: string;
}> = [];

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { transcription, source = 'jetson-tx2' } = body;

    if (!transcription || typeof transcription !== 'string') {
      return NextResponse.json(
        { error: 'Transcription text is required' },
        { status: 400 }
      );
    }

    // Create new transcription entry
    const newTranscription = {
      id: Date.now().toString(),
      text: transcription.trim(),
      timestamp: new Date().toISOString(),
      source: source
    };

    // Add to storage
    transcriptions.push(newTranscription);

    // Keep only last 100 transcriptions to prevent memory issues
    if (transcriptions.length > 100) {
      transcriptions = transcriptions.slice(-100);
    }

    console.log('Received transcription:', newTranscription);

    return NextResponse.json({
      success: true,
      message: 'Transcription received successfully',
      transcription: newTranscription
    });

  } catch (error) {
    console.error('Error processing transcription:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    // Return all transcriptions
    return NextResponse.json({
      success: true,
      transcriptions: transcriptions.reverse() // Most recent first
    });
  } catch (error) {
    console.error('Error fetching transcriptions:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
