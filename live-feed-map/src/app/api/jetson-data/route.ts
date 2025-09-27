import { NextRequest, NextResponse } from 'next/server';

const JETSON_API_BASE = 'http://localhost:5001';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const count = searchParams.get('count') || '10';
    
    // Fetch data from Python socket server
    const response = await fetch(`${JETSON_API_BASE}/api/sensor-data?count=${count}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Jetson API responded with status: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      data: data.data,
      count: data.count,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching Jetson data:', error);
    
    return NextResponse.json({
      success: false,
      error: 'Failed to fetch Jetson data',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Forward POST requests to Python server if needed
    const response = await fetch(`${JETSON_API_BASE}/api/sensor-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Jetson API responded with status: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      data: data,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error posting to Jetson API:', error);
    
    return NextResponse.json({
      success: false,
      error: 'Failed to post to Jetson API',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
