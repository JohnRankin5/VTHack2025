#!/usr/bin/env python3
"""
Hand Gesture Recognition System for Firefighter Communication
Integrates with YOLOv5 object detection system
"""

import cv2
import mediapipe as mp
import numpy as np
import math
from typing import List, Dict, Tuple, Optional
import time

class HandGestureDetector:
    def __init__(self):
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,  # Lower for better detection
            min_tracking_confidence=0.5   # Lower for better tracking
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Gesture persistence tracking
        self.active_gestures = {}  # Track active gestures with timestamps
        self.gesture_persistence_time = 3.0  # Keep gesture visible for 3 seconds
        
        # Gesture definitions
        self.gesture_definitions = {
            'peace': self.detect_peace_gesture,
            'ok': self.detect_ok_gesture,
            'phone': self.detect_phone_gesture,
            'thumbs_up': self.detect_thumbs_up,
            'thumbs_down': self.detect_thumbs_down,
            'open_hand': self.detect_open_hand,
            'point_up': self.detect_point_up,
            'stop': self.detect_stop_gesture,
            'move': self.detect_move_gesture
        }
        
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
        
        # Cooldown setup to avoid rapid firing of gestures
        self.gesture_cooldown = {}
        self.gesture_cooldown_time = 1.5  # Cooldown time for gesture detection
    
    def calculate_distance(self, point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def is_finger_extended(self, landmarks: List, finger_tips: List[int], finger_pips: List[int]) -> bool:
        """Check if a finger is extended based on landmark positions"""
        if len(finger_tips) != len(finger_pips):
            return False
        
        extended_count = 0
        for tip, pip in zip(finger_tips, finger_pips):
            if tip >= len(landmarks) or pip >= len(landmarks):
                return False
            
            tip_y = landmarks[tip].y
            pip_y = landmarks[pip].y
            
            # Finger is extended if tip is above pip (more lenient threshold)
            if tip_y < pip_y:  # Changed from > to < for proper extension
                extended_count += 1
        
        # Return true if at least half the fingers are extended
        return extended_count >= len(finger_tips) / 2
    
    def detect_peace_gesture(self, landmarks: List) -> bool:
        """Detect peace gesture (V sign) - index and middle finger extended"""
        if len(landmarks) < 21:
            return False
        
        # Index and middle finger extended, others down
        index_extended = self.is_finger_extended(landmarks, [8], [6])
        middle_extended = self.is_finger_extended(landmarks, [12], [10])
        ring_down = not self.is_finger_extended(landmarks, [16], [14])
        pinky_down = not self.is_finger_extended(landmarks, [20], [18])
        thumb_down = landmarks[4].y > landmarks[3].y
        
        return index_extended and middle_extended and ring_down and pinky_down and thumb_down
    
    def detect_ok_gesture(self, landmarks: List) -> bool:
        """Detect OK gesture - thumb and index finger forming circle"""
        if len(landmarks) < 21:
            return False
        
        # Calculate distance between thumb tip and index finger tip
        thumb_tip = (landmarks[4].x, landmarks[4].y)
        index_tip = (landmarks[8].x, landmarks[8].y)
        distance = self.calculate_distance(thumb_tip, index_tip)
        
        # Check if other fingers are extended
        middle_extended = self.is_finger_extended(landmarks, [12], [10])
        ring_extended = self.is_finger_extended(landmarks, [16], [14])
        pinky_extended = self.is_finger_extended(landmarks, [20], [18])
        
        # OK gesture: thumb and index close, other fingers extended
        return (distance < 0.05 and  # Thumb and index close
                middle_extended and ring_extended and pinky_extended)
    
    def detect_phone_gesture(self, landmarks: List) -> bool:
        """Detect phone gesture - thumb and pinky extended"""
        if len(landmarks) < 21:
            return False
        
        # Thumb extended
        thumb_extended = landmarks[4].y < landmarks[3].y
        # Pinky extended
        pinky_extended = self.is_finger_extended(landmarks, [20], [18])
        # Other fingers down
        index_down = not self.is_finger_extended(landmarks, [8], [6])
        middle_down = not self.is_finger_extended(landmarks, [12], [10])
        ring_down = not self.is_finger_extended(landmarks, [16], [14])
        
        return thumb_extended and pinky_extended and index_down and middle_down and ring_down
    
    def detect_thumbs_up(self, landmarks: List) -> bool:
        """Detect thumbs up gesture"""
        if len(landmarks) < 21:
            return False
        
        # Thumb extended upward
        thumb_extended = landmarks[4].y < landmarks[3].y and landmarks[4].x > landmarks[3].x
        # Other fingers closed
        index_down = not self.is_finger_extended(landmarks, [8], [6])
        middle_down = not self.is_finger_extended(landmarks, [12], [10])
        ring_down = not self.is_finger_extended(landmarks, [16], [14])
        pinky_down = not self.is_finger_extended(landmarks, [20], [18])
        
        return thumb_extended and index_down and middle_down and ring_down and pinky_down
    
    def detect_thumbs_down(self, landmarks: List) -> bool:
        """Detect thumbs down gesture"""
        if len(landmarks) < 21:
            return False
        
        # Thumb extended downward
        thumb_extended = landmarks[4].y > landmarks[3].y
        # Other fingers closed
        index_down = not self.is_finger_extended(landmarks, [8], [6])
        middle_down = not self.is_finger_extended(landmarks, [12], [10])
        ring_down = not self.is_finger_extended(landmarks, [16], [14])
        pinky_down = not self.is_finger_extended(landmarks, [20], [18])
        
        return thumb_extended and index_down and middle_down and ring_down and pinky_down
    
    def detect_open_hand(self, landmarks: List) -> bool:
        """Detect open hand gesture - all fingers extended"""
        if len(landmarks) < 21:
            return False
        
        # All fingers extended
        thumb_extended = landmarks[4].x > landmarks[3].x
        index_extended = self.is_finger_extended(landmarks, [8], [6])
        middle_extended = self.is_finger_extended(landmarks, [12], [10])
        ring_extended = self.is_finger_extended(landmarks, [16], [14])
        pinky_extended = self.is_finger_extended(landmarks, [20], [18])
        
        return thumb_extended and index_extended and middle_extended and ring_extended and pinky_extended
    
    def detect_point_up(self, landmarks: List) -> bool:
        """Detect pointing up gesture - only index finger extended"""
        if len(landmarks) < 21:
            return False
        
        # Only index finger extended
        index_extended = self.is_finger_extended(landmarks, [8], [6])
        # Other fingers down
        middle_down = not self.is_finger_extended(landmarks, [12], [10])
        ring_down = not self.is_finger_extended(landmarks, [16], [14])
        pinky_down = not self.is_finger_extended(landmarks, [20], [18])
        # Thumb down or sideways
        thumb_down = landmarks[4].y > landmarks[3].y
        
        return index_extended and middle_down and ring_down and pinky_down and thumb_down
    
    def detect_stop_gesture(self, landmarks: List) -> bool:
        """Detect stop gesture - open palm facing forward"""
        # Same as open hand for now
        return self.detect_open_hand(landmarks)
    
    def detect_move_gesture(self, landmarks: List) -> bool:
        """Detect move gesture - flat hand sideways"""
        if len(landmarks) < 21:
            return False
        
        # Check if hand is oriented sideways (flat)
        wrist = landmarks[0]
        middle_base = landmarks[9]
        
        # Calculate orientation
        dx = middle_base.x - wrist.x
        dy = middle_base.y - wrist.y
        
        # Flat hand sideways: horizontal orientation
        is_horizontal = abs(dy) < abs(dx) * 0.5
        
        # All fingers extended (like open hand)
        all_extended = self.detect_open_hand(landmarks)
        
        return is_horizontal and all_extended
    
    
    def detect_gestures(self, frame: np.ndarray) -> List[Dict]:
        """Detect gestures with persistence tracking"""
        results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        detected_gestures = []
        current_time = time.time()
        
        # Clean up old gestures
        self.cleanup_old_gestures(current_time)
        
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                landmarks = hand_landmarks.landmark
                
                # Convert normalized coordinates to pixel coordinates
                h, w, _ = frame.shape
                pixel_landmarks = []
                for landmark in landmarks:
                    pixel_landmarks.append({
                        'x': int(landmark.x * w),
                        'y': int(landmark.y * h),
                        'z': landmark.z
                    })
                
                # Test each gesture
                for gesture_name, gesture_func in self.gesture_definitions.items():
                    try:
                        if gesture_func(landmarks):
                            # Calculate hand bounding box
                            x_coords = [lm.x for lm in landmarks]
                            y_coords = [lm.y for lm in landmarks]
                            
                            x_min, x_max = int(min(x_coords) * w), int(max(x_coords) * w)
                            y_min, y_max = int(min(y_coords) * h), int(max(y_coords) * h)
                            
                            gesture_key = f"{gesture_name}_{hand_idx}"
                            
                            # Update or add gesture to active gestures
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
                    except Exception as e:
                        print(f"Error detecting {gesture_name}: {e}")
                        continue
        
        # Return all active gestures (both current and persistent)
        for gesture_key, gesture_data in self.active_gestures.items():
            detected_gestures.append(gesture_data)
        
        return detected_gestures
    
    def cleanup_old_gestures(self, current_time):
        """Remove gestures that are older than persistence time"""
        keys_to_remove = []
        for gesture_key, gesture_data in self.active_gestures.items():
            if current_time - gesture_data['timestamp'] > self.gesture_persistence_time:
                keys_to_remove.append(gesture_key)
        
        for key in keys_to_remove:
            del self.active_gestures[key]


    
    def get_gesture_priority(self, gesture_name: str) -> int:
        """Get priority for gesture (higher = more important)"""
        priority_map = {
            'point_up': 10,    # Emergency - highest priority
            'phone': 9,        # Need help
            'thumbs_down': 8,  # No/Failure
            'stop': 7,         # Stop/Freeze
            'ok': 6,           # Detected person
            'peace': 5,        # Room clear
            'thumbs_up': 4,    # Affirmative
            'move': 3,         # Let's move
            'open_hand': 2     # Stop/Freeze (alternative)
        }
        return priority_map.get(gesture_name, 1)
    
    def draw_gestures(self, frame: np.ndarray, gestures: List[Dict]) -> np.ndarray:
        """Draw gesture detections on frame"""
        for gesture in gestures:
            x1, y1, x2, y2 = gesture['bbox']
            gesture_name = gesture['gesture']
            meaning = gesture['meaning']
            priority = gesture['priority']

            # Color coding based on priority
            if priority >= 9:
                color = (0, 0, 255)  # Red - Emergency/Help
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
