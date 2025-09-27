#!/usr/bin/env python3
"""
Conflict-Free Hand Gesture Recognition System
Improved gesture detection with clear separation between similar poses
"""

import cv2
import mediapipe as mp
import numpy as np
import math
from typing import List, Dict, Tuple, Optional
import time

class ConflictFreeGestureDetector:
    def __init__(self):
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,  # Slightly higher for stability
            min_tracking_confidence=0.6
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Gesture persistence tracking
        self.active_gestures = {}
        self.gesture_persistence_time = 3.0
        
        # Gesture meanings for firefighter communication
        self.gesture_meanings = {
            'peace': 'Room clear',
            'ok': 'Detected person', 
            'phone': 'Need help',
            'thumbs_up': 'Affirmative',
            'thumbs_down': 'No/Failure',
            'stop': 'Stop/Freeze',
            'point_up': 'Emergency',
            'move': "Let's move"
        }
        
        # Gesture priority (higher = more important)
        self.gesture_priority = {
            'point_up': 10,    # Emergency
            'phone': 9,        # Need help  
            'thumbs_down': 8,  # No/Failure
            'stop': 7,         # Stop/Freeze
            'ok': 6,           # Detected person
            'peace': 5,        # Room clear
            'thumbs_up': 4,    # Affirmative
            'move': 3          # Let's move
        }
    
    def is_finger_up(self, landmarks, tip_id, pip_id):
        """Check if a finger is pointing up with stricter criteria"""
        tip_y = landmarks[tip_id].y
        pip_y = landmarks[pip_id].y
        # More strict: finger must be clearly above PIP
        return tip_y < pip_y - 0.02  # 2% margin
    
    def is_finger_down(self, landmarks, tip_id, pip_id):
        """Check if a finger is pointing down with stricter criteria"""
        tip_y = landmarks[tip_id].y
        pip_y = landmarks[pip_id].y
        # More strict: finger must be clearly below PIP
        return tip_y > pip_y + 0.02  # 2% margin
    
    def is_thumb_up(self, landmarks):
        """Check if thumb is clearly up and extended"""
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        
        # Thumb must be extended sideways AND upward
        is_extended = thumb_tip.x > thumb_ip.x  # Sideways
        is_upward = thumb_tip.y < thumb_ip.y    # Upward
        is_clear = thumb_tip.y < thumb_mcp.y - 0.01  # Clearly above base
        
        return is_extended and is_upward and is_clear
    
    def is_thumb_down(self, landmarks):
        """Check if thumb is clearly down"""
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        
        # Thumb must be down and extended
        is_down = thumb_tip.y > thumb_ip.y + 0.02
        is_extended = thumb_tip.x > thumb_ip.x  # Still extended sideways
        
        return is_down and is_extended
    
    def count_extended_fingers(self, landmarks):
        """Count how many fingers are extended"""
        extended_count = 0
        
        # Index finger
        if self.is_finger_up(landmarks, 8, 6):
            extended_count += 1
        
        # Middle finger  
        if self.is_finger_up(landmarks, 12, 10):
            extended_count += 1
            
        # Ring finger
        if self.is_finger_up(landmarks, 16, 14):
            extended_count += 1
            
        # Pinky
        if self.is_finger_up(landmarks, 20, 18):
            extended_count += 1
            
        return extended_count
    
    def detect_peace_gesture(self, landmarks):
        """Detect peace gesture (V sign) - ONLY index and middle up"""
        if len(landmarks) < 21:
            return False
        
        # Count extended fingers
        extended_count = self.count_extended_fingers(landmarks)
        
        # Peace: exactly 2 fingers up (index + middle)
        if extended_count != 2:
            return False
        
        # Check specific fingers
        index_up = self.is_finger_up(landmarks, 8, 6)
        middle_up = self.is_finger_up(landmarks, 12, 10)
        ring_down = self.is_finger_down(landmarks, 16, 14)
        pinky_down = self.is_finger_down(landmarks, 20, 18)
        
        return index_up and middle_up and ring_down and pinky_down
    
    def detect_ok_gesture(self, landmarks):
        """Detect OK gesture - thumb and index form circle, others up"""
        if len(landmarks) < 21:
            return False
        
        # Thumb and index finger tips close together
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
        
        # Circle formation
        if distance > 0.06:  # Stricter distance
            return False
        
        # Other fingers must be up
        middle_up = self.is_finger_up(landmarks, 12, 10)
        ring_up = self.is_finger_up(landmarks, 16, 14)
        pinky_up = self.is_finger_up(landmarks, 20, 18)
        
        return middle_up and ring_up and pinky_up
    
    def detect_phone_gesture(self, landmarks):
        """Detect phone gesture - thumb and pinky up, others down"""
        if len(landmarks) < 21:
            return False
        
        # Count extended fingers
        extended_count = self.count_extended_fingers(landmarks)
        
        # Phone: exactly 2 fingers up (thumb + pinky)
        if extended_count != 2:
            return False
        
        # Check specific fingers
        thumb_up = self.is_thumb_up(landmarks)
        pinky_up = self.is_finger_up(landmarks, 20, 18)
        index_down = self.is_finger_down(landmarks, 8, 6)
        middle_down = self.is_finger_down(landmarks, 12, 10)
        ring_down = self.is_finger_down(landmarks, 16, 14)
        
        return thumb_up and pinky_up and index_down and middle_down and ring_down
    
    def detect_thumbs_up(self, landmarks):
        """Detect thumbs up - ONLY thumb up, all fingers down"""
        if len(landmarks) < 21:
            return False
        
        # Count extended fingers (excluding thumb)
        extended_count = self.count_extended_fingers(landmarks)
        
        # Thumbs up: exactly 0 fingers up, thumb up
        if extended_count != 0:
            return False
        
        # Thumb must be clearly up
        thumb_up = self.is_thumb_up(landmarks)
        
        # All fingers must be down
        index_down = self.is_finger_down(landmarks, 8, 6)
        middle_down = self.is_finger_down(landmarks, 12, 10)
        ring_down = self.is_finger_down(landmarks, 16, 14)
        pinky_down = self.is_finger_down(landmarks, 20, 18)
        
        return thumb_up and index_down and middle_down and ring_down and pinky_down
    
    def detect_thumbs_down(self, landmarks):
        """Detect thumbs down - ONLY thumb down, all fingers down"""
        if len(landmarks) < 21:
            return False
        
        # Count extended fingers (excluding thumb)
        extended_count = self.count_extended_fingers(landmarks)
        
        # Thumbs down: exactly 0 fingers up, thumb down
        if extended_count != 0:
            return False
        
        # Thumb must be clearly down
        thumb_down = self.is_thumb_down(landmarks)
        
        # All fingers must be down
        index_down = self.is_finger_down(landmarks, 8, 6)
        middle_down = self.is_finger_down(landmarks, 12, 10)
        ring_down = self.is_finger_down(landmarks, 16, 14)
        pinky_down = self.is_finger_down(landmarks, 20, 18)
        
        return thumb_down and index_down and middle_down and ring_down and pinky_down
    
    def detect_stop_gesture(self, landmarks):
        """Detect stop gesture - ALL 5 digits up"""
        if len(landmarks) < 21:
            return False
        
        # Count extended fingers
        extended_count = self.count_extended_fingers(landmarks)
        
        # Stop: exactly 4 fingers up (all except thumb)
        if extended_count != 4:
            return False
        
        # Thumb must be extended sideways
        thumb_extended = landmarks[4].x > landmarks[3].x
        
        # All fingers must be up
        index_up = self.is_finger_up(landmarks, 8, 6)
        middle_up = self.is_finger_up(landmarks, 12, 10)
        ring_up = self.is_finger_up(landmarks, 16, 14)
        pinky_up = self.is_finger_up(landmarks, 20, 18)
        
        return thumb_extended and index_up and middle_up and ring_up and pinky_up
    
    def detect_point_up(self, landmarks):
        """Detect point up - ONLY index finger up"""
        if len(landmarks) < 21:
            return False
        
        # Count extended fingers
        extended_count = self.count_extended_fingers(landmarks)
        
        # Point up: exactly 1 finger up (index only)
        if extended_count != 1:
            return False
        
        # Check specific fingers
        index_up = self.is_finger_up(landmarks, 8, 6)
        middle_down = self.is_finger_down(landmarks, 12, 10)
        ring_down = self.is_finger_down(landmarks, 16, 14)
        pinky_down = self.is_finger_down(landmarks, 20, 18)
        thumb_down = landmarks[4].y > landmarks[3].y
        
        return index_up and middle_down and ring_down and pinky_down and thumb_down
    
    def detect_move_gesture(self, landmarks):
        """Detect move gesture - horizontal stop hand"""
        if len(landmarks) < 21:
            return False
        
        # First check if it's a stop gesture
        if not self.detect_stop_gesture(landmarks):
            return False
        
        # Check hand orientation
        wrist = landmarks[0]
        middle_base = landmarks[9]
        
        dx = middle_base.x - wrist.x
        dy = middle_base.y - wrist.y
        
        # Horizontal orientation: more horizontal than vertical
        is_horizontal = abs(dx) > abs(dy) * 1.5
        
        return is_horizontal
    
    def detect_gestures(self, frame):
        """Detect all gestures with conflict resolution"""
        results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        detected_gestures = []
        current_time = time.time()
        
        # Clean up old gestures
        self.cleanup_old_gestures(current_time)
        
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                landmarks = hand_landmarks.landmark
                
                # Test gestures in priority order (highest first)
                gesture_detectors = [
                    ('point_up', self.detect_point_up),
                    ('phone', self.detect_phone_gesture),
                    ('thumbs_down', self.detect_thumbs_down),
                    ('stop', self.detect_stop_gesture),
                    ('ok', self.detect_ok_gesture),
                    ('peace', self.detect_peace_gesture),
                    ('thumbs_up', self.detect_thumbs_up),
                    ('move', self.detect_move_gesture)
                ]
                
                # Find the highest priority gesture that matches
                detected_gesture = None
                for gesture_name, detector_func in gesture_detectors:
                    try:
                        if detector_func(landmarks):
                            detected_gesture = gesture_name
                            break  # Take the first (highest priority) match
                    except Exception as e:
                        print(f"Error detecting {gesture_name}: {e}")
                        continue
                
                # If a gesture was detected, add it to active gestures
                if detected_gesture:
                    # Calculate bounding box
                    x_coords = [lm.x for lm in landmarks]
                    y_coords = [lm.y for lm in landmarks]
                    
                    h, w, _ = frame.shape
                    x_min, x_max = int(min(x_coords) * w), int(max(x_coords) * w)
                    y_min, y_max = int(min(y_coords) * h), int(max(y_coords) * h)
                    
                    gesture_key = f"{detected_gesture}_{hand_idx}"
                    
                    self.active_gestures[gesture_key] = {
                        'gesture': detected_gesture,
                        'meaning': self.gesture_meanings[detected_gesture],
                        'confidence': 0.9,  # High confidence due to strict detection
                        'bbox': [x_min, y_min, x_max, y_max],
                        'center': [int((x_min + x_max) / 2), int((y_min + y_max) / 2)],
                        'hand_id': hand_idx,
                        'priority': self.gesture_priority[detected_gesture],
                        'timestamp': current_time
                    }
        
        # Return all active gestures
        for gesture_data in self.active_gestures.values():
            detected_gestures.append(gesture_data)
        
        return detected_gestures
    
    def cleanup_old_gestures(self, current_time):
        """Remove old gestures"""
        keys_to_remove = []
        for gesture_key, gesture_data in self.active_gestures.items():
            if current_time - gesture_data['timestamp'] > self.gesture_persistence_time:
                keys_to_remove.append(gesture_key)
        
        for key in keys_to_remove:
            del self.active_gestures[key]
    
    def draw_gestures(self, frame, gestures):
        """Draw gesture detections on frame with priority-based colors"""
        for gesture in gestures:
            x1, y1, x2, y2 = gesture['bbox']
            gesture_name = gesture['gesture']
            meaning = gesture['meaning']
            priority = gesture['priority']
            
            # Color coding based on priority
            if priority >= 9:
                color = (0, 0, 255)  # Red - Emergency
                thickness = 4
            elif priority >= 7:
                color = (0, 255, 255)  # Yellow - Warning
                thickness = 3
            else:
                color = (0, 255, 0)  # Green - Normal
                thickness = 2
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            
            # Draw label with priority indicator
            label = f"{gesture_name}: {meaning}"
            if priority >= 9:
                label = f"🚨 {label}"
            elif priority >= 7:
                label = f"⚠️ {label}"
            
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def cleanup(self):
        """Clean up resources"""
        if self.hands:
            self.hands.close()

def main():
    """Test the conflict-free gesture detector"""
    detector = ConflictFreeGestureDetector()
    cap = cv2.VideoCapture(0)
    
    print("🎯 Conflict-Free Gesture Detection Test")
    print("=" * 50)
    print("Gesture Priority (higher = detected first):")
    for gesture, priority in sorted(detector.gesture_priority.items(), key=lambda x: x[1], reverse=True):
        meaning = detector.gesture_meanings[gesture]
        print(f"  {priority}: {gesture} - {meaning}")
    
    print("\nKey Improvements:")
    print("  • Strict finger counting prevents conflicts")
    print("  • Priority-based detection (emergency gestures first)")
    print("  • Clear separation between similar poses")
    print("  • No more open hand vs thumbs up conflicts")
    print("\nPress 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect gestures
        gestures = detector.detect_gestures(frame)
        
        # Draw gestures
        frame = detector.draw_gestures(frame, gestures)
        
        # Display frame
        cv2.imshow('Conflict-Free Gesture Detection', frame)
        
        # Print detected gestures
        if gestures:
            for gesture in gestures:
                print(f"✅ Detected: {gesture['gesture']} - {gesture['meaning']} (Priority: {gesture['priority']})")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    detector.cleanup()

if __name__ == "__main__":
    main()
