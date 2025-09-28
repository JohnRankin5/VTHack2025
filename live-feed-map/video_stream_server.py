#!/usr/bin/env python3
"""
Video Stream Server for Live Feed Map
Streams Mac camera video to web interface with detection overlays
"""

import cv2
import base64
import json
import asyncio
import websockets
import threading
import time
from datetime import datetime
import numpy as np
from ultralytics import YOLO
# import mediapipe as mp  # Temporarily disabled due to installation issues
# Hand gesture detection removed - was unreliable

class VideoStreamServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.cap = None
        self.running = False
        self.clients = set()
        self.model = None
        self.pose = None
        self.mp_drawing = None
        self.coco_classes = self.load_coco_classes()
        
    def load_coco_classes(self):
        """Load COCO class names"""
        return [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
            'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
            'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
            'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
            'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
    
    def get_firefighter_object_priority(self, class_name):
        """Get priority for firefighter-relevant objects"""
        firefighter_objects = {
            'person': 10, 'door': 9, 'window': 9, 'fire hydrant': 10, 'stairs': 8,
            'chair': 6, 'bed': 7, 'couch': 6, 'dining table': 5, 'toilet': 4,
            'sink': 5, 'tv': 3, 'laptop': 4, 'book': 2, 'clock': 3,
            'bottle': 4, 'cup': 3, 'knife': 6, 'scissors': 5
        }
        return firefighter_objects.get(class_name, 0)
    
    def initialize_camera(self):
        """Initialize camera and detection models"""
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"Camera initialized: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
            
            # Initialize YOLO model
            try:
                print("Loading YOLO model...")
                model_files = ['yolov8n.pt', 'yolov5n.pt', 'yolov5s.pt']
                
                for model_file in model_files:
                    try:
                        print(f"Trying to load {model_file}...")
                        self.model = YOLO(model_file, verbose=False)
                        print(f"{model_file} loaded successfully!")
                        break
                    except Exception as model_error:
                        print(f"Failed to load {model_file}: {model_error}")
                        continue
                
                if self.model is None:
                    print("Failed to load any YOLO model")
                    return False
                    
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
            
            # Hand gesture detection removed - was unreliable
            print("Object detection only - hand gestures disabled")
            
            return True
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def detect_objects(self, frame):
        """Detect objects using YOLO"""
        detections = []
        
        if self.model is not None:
            try:
                results = self.model(frame)
                
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            confidence = box.conf[0].cpu().numpy()
                            class_id = int(box.cls[0].cpu().numpy())
                            
                            if confidence > 0.3:
                                class_name = self.coco_classes[class_id] if class_id < len(self.coco_classes) else "unknown"
                                priority = self.get_firefighter_object_priority(class_name)
                                
                                detection = {
                                    "type": "object",
                                    "class_id": class_id,
                                    "class_name": class_name,
                                    "confidence": float(confidence),
                                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                                    "center": [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                                    "priority": priority,
                                    "size": (int(x2 - x1), int(y2 - y1)),
                                    "method": "yolo"
                                }
                                detections.append(detection)
            except Exception as e:
                print(f"Error in object detection: {e}")
        
        return detections
    
    def detect_gestures(self, frame):
        """Hand gesture detection disabled - was unreliable"""
        return []
    
    def analyze_firefighter_pose(self, key_points, w, h):
        """Analyze pose for firefighter-specific actions"""
        try:
            # Calculate angles and positions
            nose = key_points['nose']
            left_shoulder = key_points['left_shoulder']
            right_shoulder = key_points['right_shoulder']
            left_wrist = key_points['left_wrist']
            right_wrist = key_points['right_wrist']
            left_knee = key_points['left_knee']
            right_knee = key_points['right_knee']
            
            # Determine action based on pose
            action = "standing"
            priority = 5
            confidence = 0.8
            
            # Check for crawling (low to ground)
            if left_knee.visibility > 0.5 and right_knee.visibility > 0.5:
                avg_knee_y = (left_knee.y + right_knee.y) / 2
                avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
                
                if avg_knee_y > 0.7 and avg_shoulder_y > 0.6:  # Low to ground
                    action = "crawling"
                    priority = 8
                    confidence = 0.9
            
            # Check for pointing gesture
            elif left_wrist.visibility > 0.5 and right_wrist.visibility > 0.5:
                # Check if one arm is extended more than the other
                left_arm_extended = abs(left_wrist.y - left_shoulder.y) > 0.3
                right_arm_extended = abs(right_wrist.y - right_shoulder.y) > 0.3
                
                if left_arm_extended or right_arm_extended:
                    action = "pointing"
                    priority = 7
                    confidence = 0.85
            
            # Check for walking/running
            elif left_knee.visibility > 0.5 and right_knee.visibility > 0.5:
                # Check if knees are at different heights (walking motion)
                knee_diff = abs(left_knee.y - right_knee.y)
                if knee_diff > 0.05:
                    action = "walking"
                    priority = 6
                    confidence = 0.8
            
            # Check for emergency signal (arms raised)
            if left_wrist.visibility > 0.5 and right_wrist.visibility > 0.5:
                if left_wrist.y < left_shoulder.y and right_wrist.y < right_shoulder.y:
                    action = "emergency_signal"
                    priority = 10
                    confidence = 0.95
            
            return {
                'action': action,
                'priority': priority,
                'confidence': confidence
            }
            
        except Exception as e:
            print(f"Error analyzing pose: {e}")
            return {
                'action': "unknown",
                'priority': 3,
                'confidence': 0.5
            }
    
    def draw_detections(self, frame, detections, gestures):
        """Draw both object detections and gestures on frame"""
        # Draw object detections
        for detection in detections:
            if detection["type"] == "object":
                x1, y1, x2, y2 = detection["bbox"]
                confidence = detection["confidence"]
                class_name = detection["class_name"]
                priority = detection["priority"]
                
                # Color coding for objects
                if priority >= 8:
                    color = (0, 255, 0)  # Green - High priority
                elif priority >= 5:
                    color = (0, 255, 255)  # Yellow - Medium priority
                else:
                    color = (255, 0, 0)  # Blue - Low priority
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"{class_name}: {confidence:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Gesture drawing disabled - no gesture detection
        
        return frame
    
    def encode_frame(self, frame):
        """Encode frame as base64 JPEG"""
        try:
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            return jpg_as_text
        except Exception as e:
            print(f"Error encoding frame: {e}")
            return None
    
    async def handle_client(self, websocket):
        """Handle WebSocket client connection"""
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")
        
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
            print(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast_frame(self, frame_data, detections, gestures):
        """Broadcast frame and detection data to all connected clients"""
        if self.clients:
            message = {
                "type": "frame",
                "data": frame_data,
                "detections": detections,
                "gestures": gestures,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to all connected clients
            disconnected = set()
            for client in self.clients:
                try:
                    await client.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.clients -= disconnected
    
    def camera_loop(self, loop):
        """Main camera capture and processing loop"""
        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to capture frame")
                    continue
                
                # Process frame for detections
                detections = self.detect_objects(frame)
                gestures = self.detect_gestures(frame)
                
                # IMPORTANT: send raw frame and draw overlays on the frontend to avoid double-drawing
                frame_with_detections = frame.copy()
                
                # Encode frame
                frame_data = self.encode_frame(frame_with_detections)
                if frame_data:
                    # Broadcast to WebSocket clients
                    asyncio.run_coroutine_threadsafe(
                        self.broadcast_frame(frame_data, detections, gestures),
                        loop
                    )
                
                # Control frame rate
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                print(f"Error in camera loop: {e}")
                break
    
    async def start_server(self):
        """Start the WebSocket server"""
        print(f"Starting video stream server on {self.host}:{self.port}")
        
        # Initialize camera and models
        if not self.initialize_camera():
            print("Failed to initialize camera")
            return
        
        self.running = True
        
        # Get the current event loop
        loop = asyncio.get_event_loop()
        
        # Start camera loop in separate thread
        camera_thread = threading.Thread(target=self.camera_loop, args=(loop,), daemon=True)
        camera_thread.start()
        
        # Start WebSocket server
        async with websockets.serve(self.handle_client, self.host, self.port):
            print("Video stream server started. Waiting for connections...")
            await asyncio.Future()  # Run forever
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.cap:
            self.cap.release()
        # No gesture detector to cleanup
        cv2.destroyAllWindows()

def main():
    server = VideoStreamServer()
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("\nStopping video stream server...")
    finally:
        server.stop()

if __name__ == "__main__":
    main()
