#!/usr/bin/env python3
"""
Compare old vs new gesture detection systems
"""

import cv2
import time
from conflict_free_gestures import ConflictFreeGestureDetector
from hand_gesture_detector import HandGestureDetector

def main():
    # Initialize both detectors
    old_detector = HandGestureDetector()
    new_detector = ConflictFreeGestureDetector()
    
    cap = cv2.VideoCapture(0)
    
    print("🔄 Gesture Detection Comparison")
    print("=" * 50)
    print("Left side: OLD system (conflicts)")
    print("Right side: NEW system (conflict-free)")
    print("\nTry these gestures to see the difference:")
    print("  • Thumbs up (should only detect thumbs_up, not open_hand)")
    print("  • Open hand (should only detect stop, not thumbs_up)")
    print("  • Peace sign (should be clear peace, not point_up)")
    print("\nPress 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Split frame for side-by-side comparison
        height, width = frame.shape[:2]
        left_frame = frame[:, :width//2].copy()
        right_frame = frame[:, width//2:].copy()
        
        # Detect with old system (left side)
        try:
            old_gestures = old_detector.detect_gestures(left_frame)
            left_frame = old_detector.draw_gestures(left_frame, old_gestures)
            
            # Add label
            cv2.putText(left_frame, "OLD SYSTEM", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Print old detections
            if old_gestures:
                for gesture in old_gestures:
                    print(f"OLD: {gesture['gesture']} - {gesture['meaning']}")
        except Exception as e:
            cv2.putText(left_frame, "OLD SYSTEM ERROR", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Detect with new system (right side)
        try:
            new_gestures = new_detector.detect_gestures(right_frame)
            right_frame = new_detector.draw_gestures(right_frame, new_gestures)
            
            # Add label
            cv2.putText(right_frame, "NEW SYSTEM", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Print new detections
            if new_gestures:
                for gesture in new_gestures:
                    print(f"NEW: {gesture['gesture']} - {gesture['meaning']}")
        except Exception as e:
            cv2.putText(right_frame, "NEW SYSTEM ERROR", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Combine frames
        combined_frame = cv2.hconcat([left_frame, right_frame])
        
        # Add divider line
        cv2.line(combined_frame, (width//2, 0), (width//2, height), (255, 255, 255), 2)
        
        # Display combined frame
        cv2.imshow('Gesture Detection Comparison', combined_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    old_detector.cleanup()
    new_detector.cleanup()
    print("✅ Comparison complete!")

if __name__ == "__main__":
    main()
