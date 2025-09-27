#!/usr/bin/env python3
"""
Enhanced Integrated Detection System
Combines YOLOv5 object detection with hand gesture recognition
"""

import cv2
import json
import requests
import numpy as np
from datetime import datetime
import argparse
from ultralytics import YOLO
import time
import threading
from queue import Queue
import concurrent.futures
from hand_gesture_detector import HandGestureDetector

class EnhancedDetectionSystem:
    def __init__(self, server_url="http://localhost:3004", camera_id="FF-001"):
        self.server_url = server_url
        self.camera_id = camera_id
        self.model = None
        self.cap = None
        self.running = False
        self.coco_classes = self.load_coco_classes()
        
        # Initialize gesture detector
        self.gesture_detector = HandGestureDetector()
        
        # Threading components
        self.frame_queue = Queue(maxsize=5)
        self.result_queue = Queue(maxsize=10)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        self.lock = threading.Lock()
        
        # Gesture tracking
        self.last_gestures = []
        self.gesture_cooldown = {}  # Prevent spam
        self.gesture_cooldown_time = 2.0  # 2 seconds between same gesture
        
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
    
    def get_room_object_priority(self, class_name):
        """Get priority for room objects"""
        room_objects = {
            'door': 10, 'couch': 9, 'bed': 9, 'chair': 8, 'dining table': 8,
            'toilet': 7, 'sink': 7, 'refrigerator': 6, 'tv': 6, 'laptop': 5,
            'microwave': 5, 'oven': 5, 'toaster': 4, 'book': 3, 'clock': 3,
            'vase': 2, 'scissors': 2, 'teddy bear': 1, 'hair drier': 1, 'toothbrush': 1
        }
        return room_objects.get(class_name, 0)
    
    def initialize_system(self):
        """Initialize camera and YOLOv5 model"""
        # Initialize camera
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"Camera initialized: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
        
        # Initialize YOLOv5 model
        try:
            print("Loading YOLOv5 model...")
            # Try different model files in order of preference
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
        
        return True
    
    def process_frame_enhanced(self, frame):
        """Process frame with both object detection and gesture recognition"""
        detections = []
        gestures = []
        
        # Object detection with YOLOv5
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
                                priority = self.get_room_object_priority(class_name)
                                
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
        
        # Hand gesture detection
        try:
            gestures = self.gesture_detector.detect_gestures(frame)
            
            # Filter gestures based on cooldown
            current_time = time.time()
            filtered_gestures = []
            
            for gesture in gestures:
                gesture_name = gesture['gesture']
                
                # Check cooldown
                if gesture_name in self.gesture_cooldown:
                    if current_time - self.gesture_cooldown[gesture_name] < self.gesture_cooldown_time:
                        continue
                
                # Add to cooldown
                self.gesture_cooldown[gesture_name] = current_time
                
                # Convert gesture to detection format
                gesture_detection = {
                    "type": "gesture",
                    "gesture": gesture['gesture'],
                    "meaning": gesture['meaning'],
                    "confidence": gesture['confidence'],
                    "bbox": gesture['bbox'],
                    "center": gesture['center'],
                    "priority": gesture['priority'],
                    "hand_id": gesture['hand_id'],
                    "method": "mediapipe"
                }
                filtered_gestures.append(gesture_detection)
            
            gestures = filtered_gestures
            
        except Exception as e:
            print(f"Error in gesture detection: {e}")
        
        return detections, gestures
    
    def frame_capture_worker(self):
        """Worker thread for capturing frames"""
        while self.running:
            try:
                ret, frame = self.cap.read()
                if ret:
                    if not self.frame_queue.full():
                        self.frame_queue.put(frame)
                    else:
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put(frame)
                        except:
                            pass
                time.sleep(0.01)
            except Exception as e:
                print(f"Frame capture error: {e}")
                break
    
    def detection_worker(self):
        """Worker thread for processing frames"""
        while self.running:
            try:
                if not self.frame_queue.empty():
                    frame = self.frame_queue.get()
                    detections, gestures = self.process_frame_enhanced(frame)
                    
                    if not self.result_queue.full():
                        self.result_queue.put((frame, detections, gestures))
                    else:
                        try:
                            self.result_queue.get_nowait()
                            self.result_queue.put((frame, detections, gestures))
                        except:
                            pass
                else:
                    time.sleep(0.01)
            except Exception as e:
                print(f"Detection worker error: {e}")
                break
    
    def draw_detections_enhanced(self, frame, detections, gestures):
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
        
        # Draw gestures
        frame = self.gesture_detector.draw_gestures(frame, gestures)
        
        return frame
    
    def send_enhanced_results_async(self, detections, gestures, timestamp):
        """Send enhanced detection results to web server"""
        try:
            # Separate object and gesture data
            object_detections = [d for d in detections if d["type"] == "object"]
            gesture_detections = [d for d in detections if d["type"] == "gesture"]
            
            # Add gestures to detections list
            all_detections = object_detections + gesture_detections
            
            # Calculate statistics
            room_objects = [d for d in object_detections if d.get("priority", 0) > 0]
            high_priority_objects = [d for d in object_detections if d.get("priority", 0) >= 7]
            emergency_gestures = [d for d in gesture_detections if d.get("priority", 0) >= 9]
            
            payload = {
                "camera_id": self.camera_id,
                "timestamp": timestamp,
                "detections": all_detections,
                "object_detections": object_detections,
                "gesture_detections": gesture_detections,
                "detection_count": len(all_detections),
                "object_count": len(object_detections),
                "gesture_count": len(gesture_detections),
                "room_objects": room_objects,
                "room_object_count": len(room_objects),
                "high_priority_objects": high_priority_objects,
                "high_priority_count": len(high_priority_objects),
                "emergency_gestures": emergency_gestures,
                "emergency_gesture_count": len(emergency_gestures),
                "source": "enhanced-system"
            }
            
            response = requests.post(
                f"{self.server_url}/api/object-detection",
                json=payload,
                timeout=2
            )
            
            if response.status_code == 200:
                print(f"Enhanced results sent: {len(object_detections)} objects, {len(gesture_detections)} gestures")
                if emergency_gestures:
                    print(f"EMERGENCY GESTURES DETECTED: {[g['gesture'] for g in emergency_gestures]}")
                return True
            else:
                print(f"Error sending results: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending enhanced results: {e}")
            return False
    
    def run_enhanced_detection_loop(self, duration=60):
        """Run enhanced detection loop with gesture recognition"""
        if not self.initialize_system():
            return
        
        self.running = True
        start_time = time.time()
        frame_count = 0
        
        print(f"Starting enhanced detection with gestures for {duration} seconds...")
        print("Detecting gestures:")
        for gesture, meaning in self.gesture_detector.gesture_meanings.items():
            print(f"  {gesture}: {meaning}")
        print("Press 'q' to quit early")
        
        # Start worker threads
        capture_thread = threading.Thread(target=self.frame_capture_worker, daemon=True)
        detection_thread = threading.Thread(target=self.detection_worker, daemon=True)
        
        capture_thread.start()
        detection_thread.start()
        
        try:
            while self.running and (time.time() - start_time) < duration:
                if not self.result_queue.empty():
                    frame, detections, gestures = self.result_queue.get()
                    
                    # Draw detections and gestures
                    frame_enhanced = self.draw_detections_enhanced(frame.copy(), detections, gestures)
                    
                    # Send results to server
                    timestamp = datetime.now().isoformat()
                    self.executor.submit(self.send_enhanced_results_async, detections, gestures, timestamp)
                    
                    # Display frame
                    cv2.imshow('Enhanced Detection with Gestures', frame_enhanced)
                    
                    frame_count += 1
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        except KeyboardInterrupt:
            print("\nStopping enhanced detection system...")
        finally:
            self.cleanup()
            print(f"Enhanced detection complete. Processed {frame_count} frames.")
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        self.executor.shutdown(wait=True)
        
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except:
                break
        
        while not self.result_queue.empty():
            try:
                self.result_queue.get_nowait()
            except:
                break
        
        if self.cap:
            self.cap.release()
        
        if self.gesture_detector:
            self.gesture_detector.cleanup()
        
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description='Enhanced Detection System with Gestures')
    parser.add_argument('--server', default='http://localhost:3004', help='Server URL')
    parser.add_argument('--camera-id', default='FF-001', help='Camera ID')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')
    
    args = parser.parse_args()
    
    system = EnhancedDetectionSystem(args.server, args.camera_id)
    system.run_enhanced_detection_loop(args.duration)

if __name__ == "__main__":
    main()
