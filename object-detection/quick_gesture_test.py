#!/usr/bin/env python3
"""
Quick test to verify conflict-free gesture detection is working
"""

import cv2
from conflict_free_gestures import ConflictFreeGestureDetector

def main():
    detector = ConflictFreeGestureDetector()
    cap = cv2.VideoCapture(0)
    
    print("🎯 Quick Conflict-Free Gesture Test")
    print("=" * 40)
    print("Testing for 10 seconds...")
    print("Try these gestures:")
    print("  • Thumbs up (thumb only)")
    print("  • Open hand (all 5 fingers)")
    print("  • Peace sign (index + middle)")
    print("  • Point up (index only)")
    print("Press 'q' to quit early")
    
    import time
    start_time = time.time()
    
    while time.time() - start_time < 10:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect gestures
        gestures = detector.detect_gestures(frame)
        
        # Draw gestures
        frame = detector.draw_gestures(frame, gestures)
        
        # Display frame
        cv2.imshow('Quick Gesture Test', frame)
        
        # Print detected gestures
        if gestures:
            for gesture in gestures:
                print(f"✅ {gesture['gesture']} - {gesture['meaning']}")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    detector.cleanup()
    print("✅ Test complete!")

if __name__ == "__main__":
    main()
