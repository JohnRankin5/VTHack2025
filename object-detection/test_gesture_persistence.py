#!/usr/bin/env python3
"""
Test script to verify gesture persistence is working
"""

import cv2
import time
from hand_gesture_detector import HandGestureDetector

def test_gesture_persistence():
    """Test that gestures persist for the specified time"""
    detector = HandGestureDetector()
    cap = cv2.VideoCapture(0)
    
    print("Testing Gesture Persistence")
    print("Make a gesture and hold it - it should persist for 3 seconds")
    print("Press 'q' to quit")
    
    last_gesture_time = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect gestures
        gestures = detector.detect_gestures(frame)
        
        # Draw gestures
        frame = detector.draw_gestures(frame, gestures)
        
        # Print gesture info
        if gestures:
            current_time = time.time()
            if last_gesture_time is None or current_time - last_gesture_time > 1:
                print(f"Active gestures: {[g['gesture'] for g in gestures]}")
                last_gesture_time = current_time
        
        # Display frame
        cv2.imshow('Gesture Persistence Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    detector.cleanup()

if __name__ == "__main__":
    test_gesture_persistence()
