#!/usr/bin/env python3
"""
Integrated Object Detection System
Combines Mac camera simulation with Jetson processing for testing
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
import threading
from queue import Queue
import concurrent.futures

class IntegratedDetectionSystem:
    def __init__(self, server_url="http://localhost:3004", camera_id="FF-001"):
        self.server_url = server_url
        self.camera_id = camera_id
        self.model = None
        self.cap = None
        self.running = False
        self.coco_classes = self.load_coco_classes()
        
        # Threading components
        self.frame_queue = Queue(maxsize=5)  # Buffer for frames
        self.result_queue = Queue(maxsize=10)  # Buffer for results
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        self.lock = threading.Lock()
        
    def load_coco_classes(self):
        """Load COCO class names with room-specific objects highlighted"""
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
        """Get priority for room objects (higher = more important for firefighter navigation)"""
        room_objects = {
            'door': 10, 'couch': 9, 'bed': 9, 'chair': 8, 'dining table': 8,
            'toilet': 7, 'sink': 7, 'refrigerator': 6, 'tv': 6, 'laptop': 5,
            'microwave': 5, 'oven': 5, 'toaster': 4, 'book': 3, 'clock': 3,
            'vase': 2, 'scissors': 2, 'teddy bear': 1, 'hair drier': 1, 'toothbrush': 1
        }
        return room_objects.get(class_name, 0)
    
    def detect_doors_custom(self, frame):
        """Custom door detection using edge detection and geometric analysis"""
        door_detections = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                
                # Door characteristics:
                # - Tall and narrow (height > width)
                # - Reasonable size (not too small, not too large)
                # - Aspect ratio typical of doors (2:1 to 4:1)
                aspect_ratio = h / w if w > 0 else 0
                
                if (area > 5000 and  # Minimum area
                    aspect_ratio > 1.5 and aspect_ratio < 4.0 and  # Door-like aspect ratio
                    h > 100 and w > 30 and  # Minimum dimensions
                    y < frame.shape[0] * 0.8):  # Not at bottom of frame (doors are usually higher)
                    
                    # Calculate confidence based on how well it matches door characteristics
                    confidence = min(0.8, (aspect_ratio - 1.5) / 2.5 * 0.3 + 0.5)
                    
                    door_detection = {
                        "class_id": -1,  # Custom class
                        "class_name": "door",
                        "confidence": confidence,
                        "bbox": [x, y, x + w, y + h],
                        "center": [x + w//2, y + h//2],
                        "priority": 10,
                        "size": (w, h),
                        "method": "custom_edge_detection"
                    }
                    door_detections.append(door_detection)
                    
        except Exception as e:
            print(f"Error in custom door detection: {e}")
        
        return door_detections
    
    def initialize_system(self):
        """Initialize camera and YOLOv5 model"""
        # Initialize camera
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return False
            
            # Set camera properties for faster processing
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Smaller resolution for speed
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.cap.set(cv2.CAP_PROP_FPS, 30)  # Higher FPS
            
            print(f"Camera initialized: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
        
        # Initialize YOLOv5 model (use model with door detection)
        try:
            print("Loading YOLOv5 model...")
            # Try to use a model that includes door detection
            try:
                self.model = YOLO('yolov8n.pt')  # YOLOv8 has better object coverage
                print("YOLOv8 model loaded successfully!")
            except:
                self.model = YOLO('yolov5n.pt')  # Fallback to YOLOv5
                print("YOLOv5 model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
        
        return True
    
    def process_frame_async(self, frame):
        """Process frame with YOLOv5 in separate thread"""
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
                        
                        # Filter low confidence detections (lower threshold for room objects)
                        if confidence > 0.2:
                            class_name = self.coco_classes[class_id] if class_id < len(self.coco_classes) else "unknown"
                            priority = self.get_room_object_priority(class_name)
                            
                            detection = {
                                "class_id": class_id,
                                "class_name": class_name,
                                "confidence": float(confidence),
                                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                                "center": [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                                "priority": priority,
                                "size": (int(x2 - x1), int(y2 - y1)),  # Width, Height
                                "method": "yolo"
                            }
                            detections.append(detection)
            
            # Add custom door detection
            door_detections = self.detect_doors_custom(frame)
            detections.extend(door_detections)
            
            return detections
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return []
    
    def frame_capture_worker(self):
        """Worker thread for capturing frames"""
        while self.running:
            try:
                ret, frame = self.cap.read()
                if ret:
                    # Skip frames if queue is full (drop old frames)
                    if not self.frame_queue.full():
                        self.frame_queue.put(frame)
                    else:
                        # Remove oldest frame and add new one
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put(frame)
                        except:
                            pass
                time.sleep(0.01)  # Small delay to prevent overwhelming
            except Exception as e:
                print(f"Frame capture error: {e}")
                break
    
    def detection_worker(self):
        """Worker thread for processing frames"""
        while self.running:
            try:
                if not self.frame_queue.empty():
                    frame = self.frame_queue.get()
                    detections = self.process_frame_async(frame)
                    
                    # Add to result queue
                    if not self.result_queue.full():
                        self.result_queue.put((frame, detections))
                    else:
                        # Remove oldest result and add new one
                        try:
                            self.result_queue.get_nowait()
                            self.result_queue.put((frame, detections))
                        except:
                            pass
                else:
                    time.sleep(0.01)  # Small delay when no frames
            except Exception as e:
                print(f"Detection worker error: {e}")
                break
    
    def draw_detections(self, frame, detections):
        """Draw bounding boxes and labels on frame with room object prioritization"""
        # Sort detections by priority (highest first)
        detections_sorted = sorted(detections, key=lambda x: x.get("priority", 0), reverse=True)
        
        for detection in detections_sorted:
            x1, y1, x2, y2 = detection["bbox"]
            confidence = detection["confidence"]
            class_name = detection["class_name"]
            priority = detection.get("priority", 0)
            size = detection.get("size", (0, 0))
            
            # Color coding based on priority and method
            method = detection.get("method", "yolo")
            if class_name == "door" and method == "custom_edge_detection":
                color = (0, 0, 255)  # Red for custom door detection
                thickness = 4
            elif priority >= 8:  # High priority room objects
                color = (0, 255, 0)  # Green
                thickness = 3
            elif priority >= 5:  # Medium priority
                color = (0, 255, 255)  # Yellow
                thickness = 2
            else:  # Low priority
                color = (255, 0, 0)  # Blue
                thickness = 1
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            
            # Draw label with size info
            label = f"{class_name}: {confidence:.2f} ({size[0]}x{size[1]})"
            if priority > 0:
                label += f" [P{priority}]"
            if method == "custom_edge_detection":
                label += " [CUSTOM]"
            
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 8), (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        return frame
    
    def send_detection_results_async(self, detections, timestamp):
        """Send detection results to web server in separate thread"""
        try:
            # Filter and prioritize room objects
            room_objects = [d for d in detections if d.get("priority", 0) > 0]
            high_priority_objects = [d for d in detections if d.get("priority", 0) >= 7]
            
            payload = {
                "camera_id": self.camera_id,
                "timestamp": timestamp,
                "detections": detections,
                "detection_count": len(detections),
                "room_objects": room_objects,
                "room_object_count": len(room_objects),
                "high_priority_objects": high_priority_objects,
                "high_priority_count": len(high_priority_objects),
                "source": "integrated-system"
            }
            
            response = requests.post(
                f"{self.server_url}/api/object-detection",
                json=payload,
                timeout=2  # Shorter timeout for faster processing
            )
            
            if response.status_code == 200:
                print(f"Detection results sent: {len(detections)} objects, {len(room_objects)} room objects, {len(high_priority_objects)} high priority")
                return True
            else:
                print(f"Error sending results: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending detection results: {e}")
            return False
    
    def run_detection_loop(self, duration=60):
        """Run integrated object detection loop with multithreading"""
        if not self.initialize_system():
            return
        
        self.running = True
        start_time = time.time()
        frame_count = 0
        
        print(f"Starting multithreaded object detection for {duration} seconds...")
        print("Press 'q' to quit early")
        
        # Start worker threads
        capture_thread = threading.Thread(target=self.frame_capture_worker, daemon=True)
        detection_thread = threading.Thread(target=self.detection_worker, daemon=True)
        
        capture_thread.start()
        detection_thread.start()
        
        try:
            while self.running and (time.time() - start_time) < duration:
                # Get processed results
                if not self.result_queue.empty():
                    frame, detections = self.result_queue.get()
                    
                    # Draw detections on frame
                    frame_with_detections = self.draw_detections(frame.copy(), detections)
                    
                    # Send results to server asynchronously
                    timestamp = datetime.now().isoformat()
                    self.executor.submit(self.send_detection_results_async, detections, timestamp)
                    
                    # Display frame
                    cv2.imshow('Multithreaded Object Detection', frame_with_detections)
                    
                    frame_count += 1
                
                # Check for quit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # No sleep needed - threading handles the timing
                
        except KeyboardInterrupt:
            print("\nStopping detection system...")
        finally:
            self.cleanup()
            print(f"Detection complete. Processed {frame_count} frames.")
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        # Clear queues
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
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description='Integrated Object Detection System')
    parser.add_argument('--server', default='http://localhost:3004', help='Server URL')
    parser.add_argument('--camera-id', default='FF-001', help='Camera ID')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')
    
    args = parser.parse_args()
    
    system = IntegratedDetectionSystem(args.server, args.camera_id)
    system.run_detection_loop(args.duration)

if __name__ == "__main__":
    main()
