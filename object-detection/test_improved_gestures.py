#!/usr/bin/env python3
"""
Test script using the improved gesture detector
"""

import cv2
import json
import requests
import time
import threading
from queue import Queue
import concurrent.futures
from improved_gesture_detector import ImprovedGestureDetector

class ImprovedGestureTest:
    def __init__(self, server_url="http://localhost:3001", camera_id="FF-001"):
        self.server_url = server_url
        self.camera_id = camera_id
        self.cap = None
        self.running = False
        
        # Initialize improved gesture detector
        self.gesture_detector = ImprovedGestureDetector()
        
        # Threading components
        self.frame_queue = Queue(maxsize=5)
        self.result_queue = Queue(maxsize=10)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        
    def initialize_system(self):
        """Initialize camera"""
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
            return True
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def process_frame_gestures_only(self, frame):
        """Process frame with improved gesture recognition"""
        gestures = []
        
        try:
            detected_gestures = self.gesture_detector.detect_gestures(frame)
            
            # Convert gestures to detection format
            for gesture in detected_gestures:
                gesture_detection = {
                    "type": "gesture",
                    "gesture": gesture['gesture'],
                    "meaning": gesture['meaning'],
                    "confidence": gesture['confidence'],
                    "bbox": gesture['bbox'],
                    "center": gesture['center'],
                    "priority": gesture['priority'],
                    "hand_id": gesture['hand_id'],
                    "method": "improved_mediapipe"
                }
                gestures.append(gesture_detection)
            
        except Exception as e:
            print(f"Error in gesture detection: {e}")
        
        return gestures
    
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
                    gestures = self.process_frame_gestures_only(frame)
                    
                    if not self.result_queue.full():
                        self.result_queue.put((frame, gestures))
                    else:
                        try:
                            self.result_queue.get_nowait()
                            self.result_queue.put((frame, gestures))
                        except:
                            pass
                else:
                    time.sleep(0.01)
            except Exception as e:
                print(f"Detection worker error: {e}")
                break
    
    def draw_gestures_only(self, frame, gestures):
        """Draw gestures on frame"""
        return self.gesture_detector.draw_gestures(frame, gestures)
    
    def send_gesture_results_async(self, gestures, timestamp):
        """Send gesture results to web server"""
        try:
            # Calculate statistics
            emergency_gestures = [g for g in gestures if g.get("priority", 0) >= 9]
            
            payload = {
                "camera_id": self.camera_id,
                "timestamp": timestamp,
                "detections": gestures,
                "object_detections": [],
                "gesture_detections": gestures,
                "detection_count": len(gestures),
                "object_count": 0,
                "gesture_count": len(gestures),
                "room_objects": [],
                "room_object_count": 0,
                "high_priority_objects": [],
                "high_priority_count": 0,
                "emergency_gestures": emergency_gestures,
                "emergency_gesture_count": len(emergency_gestures),
                "source": "improved-gesture-test"
            }
            
            response = requests.post(
                f"{self.server_url}/api/object-detection",
                json=payload,
                timeout=2
            )
            
            if response.status_code == 200:
                print(f"Improved gesture results sent: {len(gestures)} gestures")
                if emergency_gestures:
                    print(f"🚨 EMERGENCY GESTURES DETECTED: {[g['gesture'] for g in emergency_gestures]}")
                return True
            else:
                print(f"Error sending results: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending gesture results: {e}")
            return False
    
    def run_improved_gesture_test(self, duration=60):
        """Run improved gesture detection test"""
        if not self.initialize_system():
            return
        
        self.running = True
        start_time = time.time()
        frame_count = 0
        
        print(f"Starting improved gesture detection for {duration} seconds...")
        print("Improved gesture detection with better algorithms:")
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
                    frame, gestures = self.result_queue.get()
                    
                    # Draw gestures
                    frame_with_gestures = self.draw_gestures_only(frame.copy(), gestures)
                    
                    # Send results to server
                    timestamp = time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                    self.executor.submit(self.send_gesture_results_async, gestures, timestamp)
                    
                    # Display frame
                    cv2.imshow('Improved Gesture Detection Test', frame_with_gestures)
                    
                    frame_count += 1
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        except KeyboardInterrupt:
            print("\nStopping improved gesture test system...")
        finally:
            self.cleanup()
            print(f"Improved gesture test complete. Processed {frame_count} frames.")
    
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Improved Gesture Detection Test')
    parser.add_argument('--server', default='http://localhost:3001', help='Server URL')
    parser.add_argument('--camera-id', default='FF-001', help='Camera ID')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')
    
    args = parser.parse_args()
    
    system = ImprovedGestureTest(args.server, args.camera_id)
    system.run_improved_gesture_test(args.duration)

if __name__ == "__main__":
    main()
