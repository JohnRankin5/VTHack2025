import { NextRequest, NextResponse } from 'next/server';

const RADAR_API_BASE = 'http://localhost:5003';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const count = searchParams.get('count') || '10';
    const deviceType = searchParams.get('device_type') || 'laptop';
    
    // Fetch radar data from websocket data bridge
    const response = await fetch(`${RADAR_API_BASE}/api/device-data?device_type=${deviceType}&count=${count}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Radar API responded with status: ${response.status}`);
    }

    const data = await response.json();
    
    // Filter for radar distance data only
    const radarData = data.data?.filter((entry: any) => 
      entry.processed_data?.type === 'radar_distance'
    ) || [];

    // Process radar data for frontend consumption
    const processedRadarData = radarData.map((entry: any) => ({
      id: entry.id,
      timestamp: entry.timestamp,
      distance_m: entry.processed_data?.distance_m,
      t_sec: entry.processed_data?.t_sec,
      client_ip: entry.processed_data?.client_ip,
      device_type: entry.device_type,
      source: entry.source
    }));

    return NextResponse.json({
      success: true,
      data: processedRadarData,
      count: processedRadarData.length,
      total_entries: data.count || 0,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching radar data:', error);
    
    return NextResponse.json({
      success: false,
      error: 'Failed to fetch radar data',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Forward radar data to websocket bridge if needed
    const response = await fetch(`${RADAR_API_BASE}/api/device-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Radar API responded with status: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      data: data,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error posting radar data:', error);
    
    return NextResponse.json({
      success: false,
      error: 'Failed to post radar data',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
