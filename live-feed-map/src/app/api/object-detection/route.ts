import { NextResponse } from 'next/server';

interface Detection {
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: [number, number, number, number]; // [x1, y1, x2, y2]
  center: [number, number];
}

interface DetectionResult {
  id: string;
  camera_id: string;
  timestamp: string;
  detections: Detection[];
  detection_count: number;
  source: string;
}

// In-memory storage for detection results
let detectionResults: DetectionResult[] = [];
const MAX_RESULTS = 100;

export async function POST(request: Request) {
  try {
    const data = await request.json();

    if (!data.camera_id || !data.timestamp || !Array.isArray(data.detections)) {
      return NextResponse.json({ 
        success: false, 
        message: 'Missing required fields: camera_id, timestamp, detections' 
      }, { status: 400 });
    }

    const newResult: DetectionResult = {
      id: Date.now().toString(),
      camera_id: data.camera_id,
      timestamp: data.timestamp,
      detections: data.detections,
      detection_count: data.detection_count || data.detections.length,
      source: data.source || 'unknown'
    };

    // Add to storage
    detectionResults.unshift(newResult);
    
    // Keep only recent results
    if (detectionResults.length > MAX_RESULTS) {
      detectionResults = detectionResults.slice(0, MAX_RESULTS);
    }

    console.log(`Received detection results from ${newResult.camera_id}: ${newResult.detection_count} objects detected`);
    
    // Log detected objects
    if (newResult.detections.length > 0) {
      const objectTypes = newResult.detections.map(d => d.class_name).join(', ');
      console.log(`Detected objects: ${objectTypes}`);
    }

    return NextResponse.json({ 
      success: true, 
      message: 'Detection results received', 
      result: newResult 
    }, { status: 200 });

  } catch (error) {
    console.error('Error processing detection results:', error);
    return NextResponse.json({ 
      success: false, 
      message: 'Internal server error' 
    }, { status: 500 });
  }
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const cameraId = searchParams.get('camera_id');
    const limit = parseInt(searchParams.get('limit') || '50');

    let results = detectionResults;

    // Filter by camera ID if specified
    if (cameraId) {
      results = results.filter(result => result.camera_id === cameraId);
    }

    // Limit results
    results = results.slice(0, limit);

    return NextResponse.json({ 
      success: true, 
      results: results,
      total: detectionResults.length
    }, { status: 200 });

  } catch (error) {
    console.error('Error fetching detection results:', error);
    return NextResponse.json({ 
      success: false, 
      message: 'Internal server error' 
    }, { status: 500 });
  }
}
