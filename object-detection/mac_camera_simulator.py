#!/usr/bin/env python3
"""
Mac Camera Simulator for Object Detection Testing
Simulates Arduino camera data capture and sends to Jetson processing
"""

import cv2
import time
import json
import base64
import requests
import numpy as np
from datetime import datetime
import argparse

class MacCameraSimulator:
    def __init__(self, server_url="http://localhost:3000", camera_id="FF-001"):
        self.server_url = server_url
        self.camera_id = camera_id
        self.cap = None
        self.running = False
        
    def initialize_camera(self):
        """Initialize Mac camera"""
        try:
            self.cap = cv2.VideoCapture(0)  # Use default camera
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 5)  # 5 FPS for processing
            
            print(f"Camera initialized: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def capture_frame(self):
        """Capture a single frame from camera"""
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
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
    
    def send_frame_to_jetson(self, frame_data):
        """Send frame data to Jetson processing (simulated)"""
        try:
            # Simulate sending to Jetson via serial/HTTP
            payload = {
                "camera_id": self.camera_id,
                "frame_data": frame_data,
                "timestamp": datetime.now().isoformat(),
                "source": "mac-camera-sim"
            }
            
            # For now, we'll process directly since we don't have Jetson
            # In real implementation, this would send to Jetson via serial
            print(f"Frame sent to Jetson simulation: {len(frame_data)} bytes")
            return True
            
        except Exception as e:
            print(f"Error sending frame to Jetson: {e}")
            return False
    
    def run_detection_loop(self, duration=60):
        """Run object detection loop for specified duration"""
        if not self.initialize_camera():
            return
        
        self.running = True
        start_time = time.time()
        frame_count = 0
        
        print(f"Starting object detection simulation for {duration} seconds...")
        print("Press 'q' to quit early")
        
        try:
            while self.running and (time.time() - start_time) < duration:
                # Capture frame
                frame = self.capture_frame()
                if frame is None:
                    print("Failed to capture frame")
                    continue
                
                # Encode frame
                frame_data = self.encode_frame(frame)
                if frame_data is None:
                    continue
                
                # Send to Jetson (simulated)
                self.send_frame_to_jetson(frame_data)
                
                # Display frame (optional)
                cv2.imshow('Mac Camera Simulator', frame)
                
                frame_count += 1
                
                # Check for quit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # Control frame rate
                time.sleep(0.2)  # 5 FPS
                
        except KeyboardInterrupt:
            print("\nStopping camera simulation...")
        finally:
            self.cleanup()
            print(f"Simulation complete. Processed {frame_count} frames.")
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description='Mac Camera Simulator for Object Detection')
    parser.add_argument('--server', default='http://localhost:3000', help='Server URL')
    parser.add_argument('--camera-id', default='FF-001', help='Camera ID')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')
    
    args = parser.parse_args()
    
    simulator = MacCameraSimulator(args.server, args.camera_id)
    simulator.run_detection_loop(args.duration)

if __name__ == "__main__":
    main()
