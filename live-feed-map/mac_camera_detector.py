#!/usr/bin/env python3
"""
Enhanced Mac Camera Detector for Live Feed Map
Combines object detection, pose detection, and gesture recognition
Acts as one of the firefighter helmets in the live feed system
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
import mediapipe as mp

class MacCameraDetector:
    def __init__(self, server_url="http://localhost:3000", camera_id="FF-001"):
        self.server_url = server_url
        self.camera_id = camera_id
        self.model = None
        self.cap = None
        self.running = False
        self.coco_classes = self.load_coco_classes()
        
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Threading components
        self.frame_queue = Queue(maxsize=5)
        self.result_queue = Queue(maxsize=10)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        self.lock = threading.Lock()
        
        # Detection state
        self.last_detections = []
        self.last_poses = []
        
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
    
    def initialize_system(self):
        """Initialize camera and YOLO model"""
        # Initialize camera
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return False
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"Camera initialized: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
        
        # Initialize YOLO model
        try:
            print("Loading YOLO model...")
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
    
    def detect_poses(self, frame):
        """Detect human poses using MediaPipe"""
        poses = []
        
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                # Get frame dimensions
                h, w, _ = frame.shape
                
                # Extract key points
                landmarks = results.pose_landmarks.landmark
                
                # Define important key points for firefighters
                key_points = {
                    'nose': landmarks[0],
                    'left_shoulder': landmarks[11],
                    'right_shoulder': landmarks[12],
                    'left_elbow': landmarks[13],
                    'right_elbow': landmarks[14],
                    'left_wrist': landmarks[15],
                    'right_wrist': landmarks[16],
                    'left_hip': landmarks[23],
                    'right_hip': landmarks[24],
                    'left_knee': landmarks[25],
                    'right_knee': landmarks[26],
                    'left_ankle': landmarks[27],
                    'right_ankle': landmarks[28]
                }
                
                # Calculate bounding box for person
                x_coords = [lm.x * w for lm in landmarks if lm.visibility > 0.5]
                y_coords = [lm.y * h for lm in landmarks if lm.visibility > 0.5]
                
                if x_coords and y_coords:
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    
                    # Analyze pose for firefighter actions
                    pose_analysis = self.analyze_firefighter_pose(key_points, w, h)
                    
                    pose_detection = {
                        "type": "pose",
                        "pose_id": 0,
                        "confidence": pose_analysis['confidence'],
                        "bbox": [int(x_min), int(y_min), int(x_max), int(y_max)],
                        "center": [int((x_min + x_max) / 2), int((y_min + y_max) / 2)],
                        "action": pose_analysis['action'],
                        "priority": pose_analysis['priority'],
                        "key_points": {k: [int(v.x * w), int(v.y * h)] for k, v in key_points.items() if v.visibility > 0.5},
                        "method": "mediapipe"
                    }
                    poses.append(pose_detection)
                    
        except Exception as e:
            print(f"Error in pose detection: {e}")
        
        return poses
    
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
    
    def process_frame_comprehensive(self, frame):
        """Process frame with both object detection and pose detection"""
        detections = self.detect_objects(frame)
        poses = self.detect_poses(frame)
        
        return detections, poses
    
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
                    detections, poses = self.process_frame_comprehensive(frame)
                    
                    if not self.result_queue.full():
                        self.result_queue.put((frame, detections, poses))
                    else:
                        try:
                            self.result_queue.get_nowait()
                            self.result_queue.put((frame, detections, poses))
                        except:
                            pass
                else:
                    time.sleep(0.01)
            except Exception as e:
                print(f"Detection worker error: {e}")
                break
    
    def draw_detections_comprehensive(self, frame, detections, poses):
        """Draw both object detections and poses on frame"""
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
        
        # Draw poses
        for pose in poses:
            if pose["type"] == "pose":
                x1, y1, x2, y2 = pose["bbox"]
                action = pose["action"]
                confidence = pose["confidence"]
                priority = pose["priority"]
                
                # Color coding for poses
                if priority >= 9:
                    color = (0, 0, 255)  # Red - Emergency
                elif priority >= 7:
                    color = (255, 0, 255)  # Magenta - High priority
                else:
                    color = (255, 255, 0)  # Cyan - Normal
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"{action}: {confidence:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Draw key points
                for point_name, (px, py) in pose["key_points"].items():
                    cv2.circle(frame, (px, py), 3, color, -1)
        
        return frame
    
    def send_comprehensive_results_async(self, detections, poses, timestamp):
        """Send comprehensive detection results to web server"""
        try:
            # Combine all detections
            all_detections = detections + poses
            
            # Calculate statistics
            object_detections = [d for d in detections if d["type"] == "object"]
            pose_detections = [d for d in poses if d["type"] == "pose"]
            
            room_objects = [d for d in object_detections if d.get("priority", 0) > 0]
            high_priority_objects = [d for d in object_detections if d.get("priority", 0) >= 7]
            emergency_poses = [d for d in pose_detections if d.get("priority", 0) >= 9]
            
            payload = {
                "camera_id": self.camera_id,
                "timestamp": timestamp,
                "detections": all_detections,
                "object_detections": object_detections,
                "pose_detections": pose_detections,
                "detection_count": len(all_detections),
                "object_count": len(object_detections),
                "pose_count": len(pose_detections),
                "room_objects": room_objects,
                "room_object_count": len(room_objects),
                "high_priority_objects": high_priority_objects,
                "high_priority_count": len(high_priority_objects),
                "emergency_poses": emergency_poses,
                "emergency_pose_count": len(emergency_poses),
                "source": "mac-camera-detector"
            }
            
            response = requests.post(
                f"{self.server_url}/api/object-detection",
                json=payload,
                timeout=2
            )
            
            if response.status_code == 200:
                print(f"Results sent: {len(object_detections)} objects, {len(pose_detections)} poses")
                if emergency_poses:
                    print(f"EMERGENCY POSES DETECTED: {[p['action'] for p in emergency_poses]}")
                return True
            else:
                print(f"Error sending results: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending comprehensive results: {e}")
            return False
    
    def run_detection_loop(self, duration=60):
        """Run comprehensive detection loop"""
        if not self.initialize_system():
            return
        
        self.running = True
        start_time = time.time()
        frame_count = 0
        
        print(f"Starting Mac Camera Detector for {duration} seconds...")
        print("Detecting objects and poses for firefighter helmet simulation")
        print("Press 'q' to quit early")
        
        # Start worker threads
        capture_thread = threading.Thread(target=self.frame_capture_worker, daemon=True)
        detection_thread = threading.Thread(target=self.detection_worker, daemon=True)
        
        capture_thread.start()
        detection_thread.start()
        
        try:
            while self.running and (time.time() - start_time) < duration:
                if not self.result_queue.empty():
                    frame, detections, poses = self.result_queue.get()
                    
                    # Draw detections and poses
                    frame_enhanced = self.draw_detections_comprehensive(frame.copy(), detections, poses)
                    
                    # Send results to server
                    timestamp = datetime.now().isoformat()
                    self.executor.submit(self.send_comprehensive_results_async, detections, poses, timestamp)
                    
                    # Display frame
                    cv2.imshow(f'Mac Camera Detector - {self.camera_id}', frame_enhanced)
                    
                    frame_count += 1
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        except KeyboardInterrupt:
            print("\nStopping Mac Camera Detector...")
        finally:
            self.cleanup()
            print(f"Detection complete. Processed {frame_count} frames.")
    
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
        
        if self.pose:
            self.pose.close()
        
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description='Mac Camera Detector for Live Feed Map')
    parser.add_argument('--server', default='http://localhost:3000', help='Server URL')
    parser.add_argument('--camera-id', default='FF-001', help='Camera ID (firefighter helmet)')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')
    
    args = parser.parse_args()
    
    detector = MacCameraDetector(args.server, args.camera_id)
    detector.run_detection_loop(args.duration)

if __name__ == "__main__":
    main()
