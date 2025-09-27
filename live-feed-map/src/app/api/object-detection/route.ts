import { NextResponse } from 'next/server';

interface Detection {
  type?: string;
  class_id?: number;
  class_name?: string;
  confidence: number;
  bbox: [number, number, number, number]; // [x1, y1, x2, y2]
  center: [number, number];
  priority?: number;
  // Gesture-specific fields
  gesture?: string;
  meaning?: string;
  hand_id?: number;
  method?: string;
}

interface DetectionResult {
  id: string;
  camera_id: string;
  timestamp: string;
  detections: Detection[];
  object_detections?: Detection[];
  gesture_detections?: Detection[];
  detection_count: number;
  object_count?: number;
  gesture_count?: number;
  room_objects?: Detection[];
  room_object_count?: number;
  high_priority_objects?: Detection[];
  high_priority_count?: number;
  emergency_gestures?: Detection[];
  emergency_gesture_count?: number;
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
      object_detections: data.object_detections,
      gesture_detections: data.gesture_detections,
      detection_count: data.detection_count || data.detections.length,
      object_count: data.object_count,
      gesture_count: data.gesture_count,
      room_objects: data.room_objects,
      room_object_count: data.room_object_count,
      high_priority_objects: data.high_priority_objects,
      high_priority_count: data.high_priority_count,
      emergency_gestures: data.emergency_gestures,
      emergency_gesture_count: data.emergency_gesture_count,
      source: data.source || 'unknown'
    };

    // Add to storage
    detectionResults.unshift(newResult);
    
    // Keep only recent results
    if (detectionResults.length > MAX_RESULTS) {
      detectionResults = detectionResults.slice(0, MAX_RESULTS);
    }

    console.log(`Received detection results from ${newResult.camera_id}: ${newResult.detection_count} total detections`);
    
    // Log detected objects and gestures
    if (newResult.object_detections && newResult.object_detections.length > 0) {
      const objectTypes = newResult.object_detections.map(d => d.class_name).join(', ');
      console.log(`Detected objects: ${objectTypes}`);
    }
    
    if (newResult.gesture_detections && newResult.gesture_detections.length > 0) {
      const gestureTypes = newResult.gesture_detections.map(d => `${d.gesture} (${d.meaning})`).join(', ');
      console.log(`Detected gestures: ${gestureTypes}`);
    }
    
    // Alert for emergency gestures
    if (newResult.emergency_gestures && newResult.emergency_gestures.length > 0) {
      const emergencyTypes = newResult.emergency_gestures.map(d => `${d.gesture} (${d.meaning})`).join(', ');
      console.log(`🚨 EMERGENCY GESTURES DETECTED: ${emergencyTypes}`);
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
