#!/usr/bin/env python3
"""
Jetson TX2 Object Detection Processor
Processes camera frames using YOLOv5 and sends results to web server
"""

import cv2
import json
import base64
import requests
import numpy as np
from datetime import datetime
import argparse
from ultralytics import YOLO
import time

class JetsonProcessor:
    def __init__(self, server_url="http://localhost:3000", model_path="yolov5s.pt"):
        self.server_url = server_url
        self.model = None
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
    
    def initialize_model(self):
        """Initialize YOLOv5 model"""
        try:
            print("Loading YOLOv5 model...")
            self.model = YOLO('yolov5s.pt')  # Load YOLOv5s model
            print("Model loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def decode_frame(self, frame_data):
        """Decode base64 frame data to OpenCV image"""
        try:
            # Decode base64
            img_data = base64.b64decode(frame_data)
            
            # Convert to numpy array
            nparr = np.frombuffer(img_data, np.uint8)
            
            # Decode image
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return frame
        except Exception as e:
            print(f"Error decoding frame: {e}")
            return None
    
    def process_frame(self, frame):
        """Process frame with YOLOv5"""
        if self.model is None:
            return []
        
        try:
            # Run inference
            results = self.model(frame)
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Filter low confidence detections
                        if confidence > 0.5:
                            detection = {
                                "class_id": class_id,
                                "class_name": self.coco_classes[class_id] if class_id < len(self.coco_classes) else "unknown",
                                "confidence": float(confidence),
                                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                                "center": [int((x1 + x2) / 2), int((y1 + y2) / 2)]
                            }
                            detections.append(detection)
            
            return detections
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return []
    
    def send_detection_results(self, camera_id, detections, timestamp):
        """Send detection results to web server"""
        try:
            payload = {
                "camera_id": camera_id,
                "timestamp": timestamp,
                "detections": detections,
                "detection_count": len(detections),
                "source": "jetson-tx2"
            }
            
            response = requests.post(
                f"{self.server_url}/api/object-detection",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"Detection results sent: {len(detections)} objects detected")
                return True
            else:
                print(f"Error sending results: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending detection results: {e}")
            return False
    
    def process_frame_data(self, frame_data, camera_id):
        """Process frame data and send results"""
        # Decode frame
        frame = self.decode_frame(frame_data)
        if frame is None:
            return False
        
        # Process with YOLOv5
        detections = self.process_frame(frame)
        
        # Send results to server
        timestamp = datetime.now().isoformat()
        success = self.send_detection_results(camera_id, detections, timestamp)
        
        return success
    
    def run_simulation(self, duration=60):
        """Run simulation processing (for testing without real camera data)"""
        if not self.initialize_model():
            return
        
        print(f"Running Jetson simulation for {duration} seconds...")
        print("This simulates processing frames from Arduino camera")
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while (time.time() - start_time) < duration:
                # Simulate receiving frame data (in real implementation, this would come from serial)
                # For testing, we'll create a dummy frame
                dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                dummy_frame[:] = (50, 50, 50)  # Gray background
                
                # Add some simulated objects
                cv2.rectangle(dummy_frame, (100, 100), (200, 300), (0, 255, 0), 2)
                cv2.putText(dummy_frame, "Simulated Person", (100, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                cv2.rectangle(dummy_frame, (300, 200), (400, 350), (255, 0, 0), 2)
                cv2.putText(dummy_frame, "Simulated Chair", (300, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                
                # Encode frame
                _, buffer = cv2.imencode('.jpg', dummy_frame)
                frame_data = base64.b64encode(buffer).decode('utf-8')
                
                # Process frame
                success = self.process_frame_data(frame_data, "FF-001")
                
                if success:
                    frame_count += 1
                
                # Wait before next frame
                time.sleep(2)  # Process every 2 seconds
                
        except KeyboardInterrupt:
            print("\nStopping Jetson simulation...")
        
        print(f"Simulation complete. Processed {frame_count} frames.")

def main():
    parser = argparse.ArgumentParser(description='Jetson TX2 Object Detection Processor')
    parser.add_argument('--server', default='http://localhost:3000', help='Server URL')
    parser.add_argument('--model', default='yolov5s.pt', help='YOLOv5 model path')
    parser.add_argument('--duration', type=int, default=60, help='Simulation duration in seconds')
    
    args = parser.parse_args()
    
    processor = JetsonProcessor(args.server, args.model)
    processor.run_simulation(args.duration)

if __name__ == "__main__":
    main()
