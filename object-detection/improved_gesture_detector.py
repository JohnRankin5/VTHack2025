#!/usr/bin/env python3
"""
Improved Hand Gesture Recognition System
More accurate gesture detection with better algorithms
"""

import cv2
import mediapipe as mp
import numpy as np
import math
from typing import List, Dict, Tuple, Optional
import time

class ImprovedGestureDetector:
    def __init__(self):
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
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
            'open_hand': 'Stop/Freeze',
            'point_up': 'Emergency',
            'stop': 'Stop/Freeze',
            'move': "Let's move"
        }
    
    def is_finger_up(self, landmarks, tip_id, pip_id):
        """Check if a finger is pointing up"""
        return landmarks[tip_id].y < landmarks[pip_id].y
    
    def is_finger_down(self, landmarks, tip_id, pip_id):
        """Check if a finger is pointing down"""
        return landmarks[tip_id].y > landmarks[pip_id].y
    
    def detect_peace_gesture(self, landmarks):
        """Detect peace gesture (V sign) - index and middle finger up"""
        if len(landmarks) < 21:
            return False
        
        # Index and middle fingers up
        index_up = self.is_finger_up(landmarks, 8, 6)
        middle_up = self.is_finger_up(landmarks, 12, 10)
        
        # Ring and pinky down
        ring_down = self.is_finger_down(landmarks, 16, 14)
        pinky_down = self.is_finger_down(landmarks, 20, 18)
        
        return index_up and middle_up and ring_down and pinky_down
    
    def detect_ok_gesture(self, landmarks):
        """Detect OK gesture - thumb and index finger form circle"""
        if len(landmarks) < 21:
            return False
        
        # Calculate distance between thumb tip and index finger tip
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
        
        # Check if other fingers are up
        middle_up = self.is_finger_up(landmarks, 12, 10)
        ring_up = self.is_finger_up(landmarks, 16, 14)
        pinky_up = self.is_finger_up(landmarks, 20, 18)
        
        # OK: thumb and index close, others up
        return distance < 0.05 and middle_up and ring_up and pinky_up
    
    def detect_phone_gesture(self, landmarks):
        """Detect phone gesture - thumb and pinky up"""
        if len(landmarks) < 21:
            return False
        
        # Thumb and pinky up
        thumb_up = landmarks[4].x > landmarks[3].x  # Thumb pointing sideways
        pinky_up = self.is_finger_up(landmarks, 20, 18)
        
        # Other fingers down
        index_down = self.is_finger_down(landmarks, 8, 6)
        middle_down = self.is_finger_down(landmarks, 12, 10)
        ring_down = self.is_finger_down(landmarks, 16, 14)
        
        return thumb_up and pinky_up and index_down and middle_down and ring_down
    
    def detect_thumbs_up(self, landmarks):
        """Detect thumbs up gesture"""
        if len(landmarks) < 21:
            return False
        
        # Thumb up and sideways
        thumb_up = landmarks[4].x > landmarks[3].x and landmarks[4].y < landmarks[3].y
        
        # All other fingers down
        index_down = self.is_finger_down(landmarks, 8, 6)
        middle_down = self.is_finger_down(landmarks, 12, 10)
        ring_down = self.is_finger_down(landmarks, 16, 14)
        pinky_down = self.is_finger_down(landmarks, 20, 18)
        
        return thumb_up and index_down and middle_down and ring_down and pinky_down
    
    def detect_thumbs_down(self, landmarks):
        """Detect thumbs down gesture"""
        if len(landmarks) < 21:
            return False
        
        # Thumb down
        thumb_down = landmarks[4].y > landmarks[3].y
        
        # All other fingers down
        index_down = self.is_finger_down(landmarks, 8, 6)
        middle_down = self.is_finger_down(landmarks, 12, 10)
        ring_down = self.is_finger_down(landmarks, 16, 14)
        pinky_down = self.is_finger_down(landmarks, 20, 18)
        
        return thumb_down and index_down and middle_down and ring_down and pinky_down
    
    def detect_open_hand(self, landmarks):
        """Detect open hand - all fingers up"""
        if len(landmarks) < 21:
            return False
        
        # All fingers up
        thumb_up = landmarks[4].x > landmarks[3].x
        index_up = self.is_finger_up(landmarks, 8, 6)
        middle_up = self.is_finger_up(landmarks, 12, 10)
        ring_up = self.is_finger_up(landmarks, 16, 14)
        pinky_up = self.is_finger_up(landmarks, 20, 18)
        
        return thumb_up and index_up and middle_up and ring_up and pinky_up
    
    def detect_point_up(self, landmarks):
        """Detect pointing up gesture - only index finger up"""
        if len(landmarks) < 21:
            return False
        
        # Only index finger up
        index_up = self.is_finger_up(landmarks, 8, 6)
        
        # Other fingers down
        middle_down = self.is_finger_down(landmarks, 12, 10)
        ring_down = self.is_finger_down(landmarks, 16, 14)
        pinky_down = self.is_finger_down(landmarks, 20, 18)
        thumb_down = landmarks[4].y > landmarks[3].y
        
        return index_up and middle_down and ring_down and pinky_down and thumb_down
    
    def detect_stop_gesture(self, landmarks):
        """Detect stop gesture - open palm"""
        return self.detect_open_hand(landmarks)
    
    def detect_move_gesture(self, landmarks):
        """Detect move gesture - flat hand sideways"""
        if len(landmarks) < 21:
            return False
        
        # Check if hand is oriented sideways
        wrist = landmarks[0]
        middle_base = landmarks[9]
        
        dx = middle_base.x - wrist.x
        dy = middle_base.y - wrist.y
        
        # Horizontal orientation
        is_horizontal = abs(dy) < abs(dx) * 0.5
        
        # All fingers extended
        all_extended = self.detect_open_hand(landmarks)
        
        return is_horizontal and all_extended
    
    def detect_gestures(self, frame):
        """Detect all gestures in the frame"""
        results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        detected_gestures = []
        current_time = time.time()
        
        # Clean up old gestures
        self.cleanup_old_gestures(current_time)
        
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                landmarks = hand_landmarks.landmark
                
                # Test each gesture
                gesture_detectors = [
                    ('peace', self.detect_peace_gesture),
                    ('ok', self.detect_ok_gesture),
                    ('phone', self.detect_phone_gesture),
                    ('thumbs_up', self.detect_thumbs_up),
                    ('thumbs_down', self.detect_thumbs_down),
                    ('open_hand', self.detect_open_hand),
                    ('point_up', self.detect_point_up),
                    ('stop', self.detect_stop_gesture),
                    ('move', self.detect_move_gesture)
                ]
                
                for gesture_name, detector_func in gesture_detectors:
                    try:
                        if detector_func(landmarks):
                            # Calculate bounding box
                            x_coords = [lm.x for lm in landmarks]
                            y_coords = [lm.y for lm in landmarks]
                            
                            h, w, _ = frame.shape
                            x_min, x_max = int(min(x_coords) * w), int(max(x_coords) * w)
                            y_min, y_max = int(min(y_coords) * h), int(max(y_coords) * h)
                            
                            gesture_key = f"{gesture_name}_{hand_idx}"
                            
                            # Update active gestures
                            self.active_gestures[gesture_key] = {
                                'gesture': gesture_name,
                                'meaning': self.gesture_meanings[gesture_name],
                                'confidence': 0.8,
                                'bbox': [x_min, y_min, x_max, y_max],
                                'center': [int((x_min + x_max) / 2), int((y_min + y_max) / 2)],
                                'hand_id': hand_idx,
                                'priority': self.get_gesture_priority(gesture_name),
                                'timestamp': current_time
                            }
                            break  # Only detect one gesture per hand
                    except Exception as e:
                        print(f"Error detecting {gesture_name}: {e}")
                        continue
        
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
    
    def get_gesture_priority(self, gesture_name):
        """Get priority for gesture"""
        priority_map = {
            'point_up': 10,    # Emergency
            'phone': 9,        # Need help
            'thumbs_down': 8,  # No/Failure
            'stop': 7,         # Stop/Freeze
            'ok': 6,           # Detected person
            'peace': 5,        # Room clear
            'thumbs_up': 4,    # Affirmative
            'move': 3,         # Let's move
            'open_hand': 2     # Stop/Freeze
        }
        return priority_map.get(gesture_name, 1)
    
    def draw_gestures(self, frame, gestures):
        """Draw gesture detections on frame"""
        for gesture in gestures:
            x1, y1, x2, y2 = gesture['bbox']
            gesture_name = gesture['gesture']
            meaning = gesture['meaning']
            priority = gesture['priority']
            
            # Color coding
            if priority >= 9:
                color = (0, 0, 255)  # Red - Emergency
            elif priority >= 7:
                color = (0, 255, 255)  # Yellow - Warning
            else:
                color = (0, 255, 0)  # Green - Normal
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            
            # Draw label
            label = f"{gesture_name}: {meaning}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def cleanup(self):
        """Clean up resources"""
        if self.hands:
            self.hands.close()

def main():
    """Test the improved gesture detector"""
    detector = ImprovedGestureDetector()
    cap = cv2.VideoCapture(0)
    
    print("Improved Gesture Detection Test")
    print("Gestures to test:")
    for gesture, meaning in detector.gesture_meanings.items():
        print(f"  {gesture}: {meaning}")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect gestures
        gestures = detector.detect_gestures(frame)
        
        # Draw gestures
        frame = detector.draw_gestures(frame, gestures)
        
        # Display frame
        cv2.imshow('Improved Gesture Detection', frame)
        
        # Print detected gestures
        if gestures:
            for gesture in gestures:
                print(f"Detected: {gesture['gesture']} - {gesture['meaning']}")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    detector.cleanup()

if __name__ == "__main__":
    main()
