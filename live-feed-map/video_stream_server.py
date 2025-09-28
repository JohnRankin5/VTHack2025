#!/usr/bin/env python3
"""
Video Stream Server for Live Feed Map
Streams Mac camera video to web interface with detection overlays
"""

import cv2
import base64
import json
import asyncio
import websockets
import threading
import time
from datetime import datetime
import numpy as np
from ultralytics import YOLO
import mediapipe as mp  # Import MediaPipe
from radar_avoidance_system import RadarDataManager

class VideoStreamServer:
    def __init__(self, host="localhost", port=8765, websocket_data_store=None):
        self.host = host
        self.port = port
        self.cap = None
        self.running = False
        self.clients = set()
        self.model = None
        self.mp_hands = mp.solutions.hands  # Initialize MediaPipe Hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils  # For drawing landmarks
        self.coco_classes = self.load_coco_classes()
        
        # Room classification system
        self.objects_in_room = set()  # Set to store unique objects
        self.object_confidence_threshold = 0.5  # Higher threshold for room classification
        self.room_classification = "Unknown"
        self.room_confidence = 0.0
        self.classification_update_counter = 0
        self.classification_update_interval = 30  # Classify room every 30 frames (~1 second)
        
        # Radar avoidance system
        self.radar_manager = None
        if websocket_data_store:
            self.radar_manager = RadarDataManager(websocket_data_store)
            print("🔧 Radar avoidance system integrated with video stream")

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

    def add_to_room(self, object_name, attributes=None):
        """Add an object to the room's set with optional attributes"""
        if attributes:
            # Add specific attributes for more detailed classification
            enhanced_object = f"{attributes}_{object_name}"
            self.objects_in_room.add(enhanced_object)
        else:
            self.objects_in_room.add(object_name)
    
    def get_object_attributes(self, class_name, bbox, frame):
        """Extract enhanced attributes from detected objects (color, size, position, material)"""
        attributes = []
        
        # Extract region of interest
        x1, y1, x2, y2 = bbox
        roi = frame[y1:y2, x1:x2]
        frame_h, frame_w = frame.shape[:2]
        
        if roi.size > 0:
            # Enhanced color detection with multiple methods
            color = self.detect_enhanced_color(roi)
            if color:
                attributes.append(color)
            
            # Enhanced size classification with object-specific thresholds
            size = self.classify_object_size(class_name, bbox, frame_w, frame_h)
            if size:
                attributes.append(size)
            
            # Position within room (tactical positioning)
            position = self.get_room_position(bbox, frame_w, frame_h)
            if position:
                attributes.append(position)
            
            # Material detection for fire safety
            material = self.detect_material_type(class_name, roi)
            if material:
                attributes.append(material)
        
        return "_".join(attributes) if attributes else None

    def detect_enhanced_color(self, roi):
        """Enhanced color detection using multiple methods"""
        try:
            # Method 1: Dominant color using K-means
            roi_reshaped = roi.reshape(-1, 3)
            
            # Method 2: HSV analysis for better color detection
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            avg_hsv = np.mean(hsv_roi, axis=(0, 1))
            h, s, v = avg_hsv
            
            # Method 3: RGB analysis with improved thresholds
            avg_color = np.mean(roi, axis=(0, 1))
            b, g, r = avg_color
            
            # Enhanced color classification using HSV + RGB
            if s < 30 or v < 50:  # Low saturation or brightness
                if v > 200:
                    return "white"
                elif v < 80:
                    return "black"
                else:
                    return "gray"
            
            # Color detection using HSV hue values
            if 0 <= h <= 10 or 160 <= h <= 180:  # Red range
                return "red"
            elif 35 <= h <= 85:  # Green range
                return "green"
            elif 100 <= h <= 130:  # Blue range
                return "blue"
            elif 15 <= h <= 35:  # Yellow/Orange range
                if 15 <= h <= 25:
                    return "yellow"
                else:
                    return "orange"
            elif 130 <= h <= 160:  # Purple/Pink range
                return "purple"
            elif 85 <= h <= 100:  # Cyan range
                return "cyan"
            
            # Fallback to RGB for edge cases
            if r > g and r > b:
                return "red"
            elif g > r and g > b:
                return "green"
            elif b > r and b > g:
                return "blue"
            
            return "neutral"
            
        except Exception as e:
            print(f"Error in color detection: {e}")
            return "unknown"

    def classify_object_size(self, class_name, bbox, frame_w, frame_h):
        """Object-specific size classification for tactical assessment"""
        x1, y1, x2, y2 = bbox
        area = (x2 - x1) * (y2 - y1)
        width = x2 - x1
        height = y2 - y1
        
        # Percentage of frame occupied
        frame_area = frame_w * frame_h
        area_percentage = (area / frame_area) * 100
        
        # Object-specific size thresholds for firefighter relevance
        size_thresholds = {
            'person': {'small': 5, 'medium': 15, 'large': 30},
            'chair': {'small': 2, 'medium': 8, 'large': 20},
            'couch': {'small': 8, 'medium': 20, 'large': 40},
            'table': {'small': 3, 'medium': 12, 'large': 25},
            'bed': {'small': 10, 'medium': 25, 'large': 45},
            'tv': {'small': 2, 'medium': 8, 'large': 18},
            'refrigerator': {'small': 8, 'medium': 18, 'large': 35},
            'door': {'small': 5, 'medium': 15, 'large': 30},
            'window': {'small': 2, 'medium': 10, 'large': 25}
        }
        
        thresholds = size_thresholds.get(class_name, {'small': 3, 'medium': 10, 'large': 25})
        
        if area_percentage >= thresholds['large']:
            return "large"
        elif area_percentage >= thresholds['medium']:
            return "medium"
        elif area_percentage >= thresholds['small']:
            return "small"
        else:
            return "tiny"

    def get_room_position(self, bbox, frame_w, frame_h):
        """Determine tactical position of object within room"""
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Normalize coordinates (0-1)
        norm_x = center_x / frame_w
        norm_y = center_y / frame_h
        
        # Tactical positioning for firefighters
        position_parts = []
        
        # Vertical position (important for evacuation routes)
        if norm_y < 0.3:
            position_parts.append("upper")
        elif norm_y > 0.7:
            position_parts.append("lower")
        else:
            position_parts.append("mid")
        
        # Horizontal position (left/right tactical approach)
        if norm_x < 0.25:
            position_parts.append("left")
        elif norm_x > 0.75:
            position_parts.append("right")
        elif 0.4 <= norm_x <= 0.6:
            position_parts.append("center")
        
        # Corner detection (important for search patterns)
        if (norm_x < 0.2 and norm_y < 0.2) or (norm_x > 0.8 and norm_y < 0.2) or \
           (norm_x < 0.2 and norm_y > 0.8) or (norm_x > 0.8 and norm_y > 0.8):
            position_parts.append("corner")
        
        return "_".join(position_parts) if position_parts else "center"

    def detect_material_type(self, class_name, roi):
        """Detect material type for fire safety assessment"""
        try:
            # Material classification based on object type and visual cues
            material_mapping = {
                'chair': ['wood', 'metal', 'plastic', 'fabric'],
                'table': ['wood', 'metal', 'glass'],
                'couch': ['fabric', 'leather'],
                'bed': ['fabric', 'wood'],
                'door': ['wood', 'metal'],
                'window': ['glass', 'metal'],
                'refrigerator': ['metal'],
                'tv': ['plastic', 'metal'],
                'bottle': ['plastic', 'glass'],
                'cup': ['ceramic', 'plastic', 'glass']
            }
            
            possible_materials = material_mapping.get(class_name, ['unknown'])
            
            # Simple heuristics based on color and texture
            avg_color = np.mean(roi, axis=(0, 1))
            b, g, r = avg_color
            
            # Texture analysis using standard deviation
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            texture_std = np.std(gray_roi)
            
            # Material detection heuristics
            if class_name in ['chair', 'table', 'bed']:
                if texture_std > 30 and (r > 100 and g > 80 and b < 100):  # Wood-like
                    return "wood"
                elif texture_std < 15 and (r > 150 or g > 150 or b > 150):  # Metal-like
                    return "metal"
                elif texture_std > 25:  # Fabric-like
                    return "fabric"
            elif class_name in ['bottle', 'window']:
                if texture_std < 20:  # Smooth surface
                    return "glass"
                else:
                    return "plastic"
            elif class_name in ['refrigerator', 'tv']:
                return "metal"
            
            # Default to first possible material
            return possible_materials[0] if possible_materials else "unknown"
            
        except Exception as e:
            print(f"Error in material detection: {e}")
            return "unknown"

    def llm_classify_room(self, objects_list):
        """Lightweight rule-based room classification (can be replaced with actual LLM)"""
        objects_str = " ".join(objects_list).lower()
        
        # Room classification rules based on object combinations
        room_indicators = {
            "kitchen": {
                "primary": ["refrigerator", "microwave", "oven", "sink", "toaster"],
                "secondary": ["dining_table", "chair", "bowl", "cup", "knife", "spoon"],
                "weight": 0.0
            },
            "living_room": {
                "primary": ["couch", "tv", "remote"],
                "secondary": ["chair", "book", "vase", "clock"],
                "weight": 0.0
            },
            "bedroom": {
                "primary": ["bed", "pillow"],
                "secondary": ["chair", "book", "clock", "teddy_bear"],
                "weight": 0.0
            },
            "dining_room": {
                "primary": ["dining_table", "chair"],
                "secondary": ["bowl", "cup", "wine_glass", "vase"],
                "weight": 0.0
            },
            "bathroom": {
                "primary": ["toilet", "sink", "toothbrush"],
                "secondary": ["hair_drier", "scissors"],
                "weight": 0.0
            },
            "office": {
                "primary": ["laptop", "keyboard", "mouse", "book"],
                "secondary": ["chair", "cup", "clock"],
                "weight": 0.0
            }
        }
        
        # Calculate weights for each room type
        for room_type, indicators in room_indicators.items():
            # Primary indicators (high weight)
            for primary_obj in indicators["primary"]:
                if primary_obj in objects_str:
                    indicators["weight"] += 3.0
            
            # Secondary indicators (lower weight)
            for secondary_obj in indicators["secondary"]:
                if secondary_obj in objects_str:
                    indicators["weight"] += 1.0
        
        # Find the room with highest weight
        best_room = max(room_indicators.items(), key=lambda x: x[1]["weight"])
        room_name, room_data = best_room
        
        if room_data["weight"] > 2.0:  # Minimum confidence threshold
            confidence = min(room_data["weight"] / 10.0, 1.0)  # Normalize to 0-1
            return room_name.replace("_", " ").title(), confidence
        else:
            return "Unknown Room", 0.0

    def classify_room(self):
        """Classify the current room based on detected objects with enhanced attributes"""
        if len(self.objects_in_room) < 2:  # Need at least 2 objects for classification
            return
        
        objects_list = list(self.objects_in_room)
        room_type, confidence = self.llm_classify_room(objects_list)
        
        # Update room classification if confidence is higher
        if confidence > self.room_confidence:
            self.room_classification = room_type
            self.room_confidence = confidence
            
            # Enhanced logging with attribute breakdown
            print(f"🏠 Room Classification: {room_type} (confidence: {confidence:.2f})")
            print(f"📦 Enhanced Objects detected ({len(objects_list)}):")
            
            # Group objects by type for better readability
            object_groups = {}
            for obj in sorted(objects_list):
                if '_' in obj:
                    parts = obj.split('_')
                    base_object = parts[-1]  # Last part is the object type
                    attributes = '_'.join(parts[:-1])  # Everything else is attributes
                else:
                    base_object = obj
                    attributes = "basic"
                
                if base_object not in object_groups:
                    object_groups[base_object] = []
                object_groups[base_object].append(attributes)
            
            for obj_type, attr_list in object_groups.items():
                print(f"   • {obj_type}: {', '.join(attr_list)}")
            
            # Tactical assessment
            self.print_tactical_assessment(objects_list, room_type)

    def print_tactical_assessment(self, objects_list, room_type):
        """Print tactical assessment for firefighters"""
        print(f"\n🚨 TACTICAL ASSESSMENT - {room_type.upper()}:")
        
        # Analyze object attributes for tactical info
        hazard_objects = []
        large_obstacles = []
        corner_items = []
        flammable_materials = []
        
        for obj in objects_list:
            if 'large' in obj:
                large_obstacles.append(obj)
            if 'corner' in obj:
                corner_items.append(obj)
            if any(material in obj for material in ['wood', 'fabric', 'plastic']):
                flammable_materials.append(obj)
            if any(hazard in obj for hazard in ['red', 'metal', 'glass']):
                hazard_objects.append(obj)
        
        if large_obstacles:
            print(f"   ⚠️  Large obstacles: {len(large_obstacles)} items")
        if corner_items:
            print(f"   🔍 Corner items: {len(corner_items)} (check blind spots)")
        if flammable_materials:
            print(f"   🔥 Flammable materials: {len(flammable_materials)} items")
        if hazard_objects:
            print(f"   ⚡ Potential hazards: {len(hazard_objects)} items")
        
        print("=" * 50)

    def get_room_context(self):
        """Get contextual information about the current room for firefighters"""
        room_contexts = {
            "Kitchen": {
                "hazards": ["Gas lines", "Electrical appliances", "Hot surfaces"],
                "priorities": ["Check stove/oven", "Gas shut-off", "Electrical panel"],
                "evacuation": "Multiple exit routes typically available"
            },
            "Living Room": {
                "hazards": ["Furniture obstacles", "Electronics", "Fabric materials"],
                "priorities": ["Check for occupants", "Clear pathways", "Electrical hazards"],
                "evacuation": "Usually connects to main exits"
            },
            "Bedroom": {
                "hazards": ["Limited exits", "Clothing/fabric", "Personal items"],
                "priorities": ["Check under beds", "Closets", "Windows as exits"],
                "evacuation": "Often single exit - check windows"
            },
            "Bathroom": {
                "hazards": ["Water/electrical", "Confined space", "Slippery surfaces"],
                "priorities": ["Water shut-off", "Ventilation", "Check behind door"],
                "evacuation": "Limited space - quick sweep needed"
            },
            "Office": {
                "hazards": ["Paper/documents", "Electronics", "Cables"],
                "priorities": ["Data/equipment", "Electrical panel", "Check desks"],
                "evacuation": "Multiple workstations to check"
            }
        }
        
        return room_contexts.get(self.room_classification, {
            "hazards": ["Unknown hazards"],
            "priorities": ["Standard sweep"],
            "evacuation": "Assess available exits"
        })

    def initialize_camera(self):
        """Initialize camera and detection models"""
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return False

            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

            print(f"Camera initialized: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

            # Initialize YOLO model
            try:
                print("Loading YOLO model...")
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

            print("Object detection only - hand gestures enabled")

            return True

        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False

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
                                
                                # Add to room classification system if confidence is high enough
                                if confidence > self.object_confidence_threshold:
                                    bbox = [int(x1), int(y1), int(x2), int(y2)]
                                    attributes = self.get_object_attributes(class_name, bbox, frame)
                                    self.add_to_room(class_name, attributes)

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

    def detect_gestures(self, frame):
        """Detect hand gestures using MediaPipe"""
        gestures = []

        # Convert the frame to RGB for MediaPipe processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                # Draw the hand landmarks
                self.mp_drawing.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)

                # Analyze the landmarks to classify gestures
                gesture = self.classify_gesture(landmarks, frame.shape)
                if gesture:
                    gestures.append(gesture)

        return gestures

    def classify_gesture(self, landmarks, frame_shape):
        """Classify hand gestures based on landmarks and return proper gesture object"""
        gesture = None
        bbox = None
        confidence = 0.85  # Default confidence for recognized gestures

        # Extract key points (landmarks) from the hand
        thumb_tip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        index_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]
        wrist = landmarks.landmark[self.mp_hands.HandLandmark.WRIST]

        # Get frame dimensions for coordinate conversion
        h, w = frame_shape[:2]
        
        # Calculate bounding box from ALL hand landmarks (more accurate)
        x_coords = [lm.x * w for lm in landmarks.landmark]
        y_coords = [lm.y * h for lm in landmarks.landmark]
        
        x1, x2 = int(min(x_coords)), int(max(x_coords))
        y1, y2 = int(min(y_coords)), int(max(y_coords))
        
        # Add padding to bounding box
        padding = 20
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(w, x2 + padding)
        y2 = min(h, y2 + padding)

        gesture_name = None
        gesture_meaning = None
        
        # Gesture Classification based on hand landmarks
        try:
            # 1. Peace (V) - Room clear (Thumb down, Index and middle finger forming a V)
            if (thumb_tip.y < index_tip.y and abs(thumb_tip.x - index_tip.x) > 0.1 and abs(thumb_tip.x - index_tip.x) < 0.2):
                gesture_name = "peace"
                gesture_meaning = "room clear"

            # 2. Circle with fingers out (OK) - Detected person
            elif (abs(thumb_tip.x - index_tip.x) < 0.05 and abs(thumb_tip.y - index_tip.y) < 0.05):
                gesture_name = "ok"
                gesture_meaning = "detected person"

            # 3. Phone symbol - Need help
            elif (abs(thumb_tip.x - pinky_tip.x) > 0.15 and abs(thumb_tip.y - pinky_tip.y) > 0.1):
                gesture_name = "phone"
                gesture_meaning = "need help"

            # 4. Thumb up - Affirmative (Thumb pointing up)
            elif (thumb_tip.y < wrist.y and abs(thumb_tip.x - wrist.x) > 0.1):
                gesture_name = "thumbs_up"
                gesture_meaning = "affirmative"

            # 5. Thumb down - No/failure
            elif (thumb_tip.y > wrist.y and abs(thumb_tip.x - wrist.x) > 0.1):
                gesture_name = "thumbs_down"
                gesture_meaning = "no/failure"

            # 6. Pointer finger up - Emergency
            elif (index_tip.y < thumb_tip.y and abs(index_tip.x - thumb_tip.x) < 0.05):
                gesture_name = "point_up"
                gesture_meaning = "emergency"

            # 7. Flat Hand (Sideways) - Let's move
            elif (abs(index_tip.x - pinky_tip.x) > 0.15 and abs(index_tip.y - pinky_tip.y) < 0.1):
                gesture_name = "flat_hand"
                gesture_meaning = "let's move"

        except Exception as e:
            print(f"Error classifying gesture: {e}")
            return None

        if gesture_name:
            return {
                "type": "gesture",
                "bbox": [x1, y1, x2, y2],
                "gesture": gesture_name,
                "meaning": gesture_meaning,
                "confidence": confidence,
                "priority": 8  # High priority for gestures
            }
        
        return None




    def draw_detections(self, frame, detections, gestures):
        """Draw both object detections and gestures on frame"""
        # Draw object detections
        for detection in detections:
            if detection["type"] == "object":
                x1, y1, x2, y2 = detection["bbox"]
                confidence = detection["confidence"]
                class_name = detection["class_name"]
                priority = detection["priority"]

                # Color coding for objects
                if priority >= 8:
                    color = (68, 68, 239)  # Red - High priority (BGR format)
                elif priority >= 5:
                    color = (8, 179, 234)  # Yellow - Medium priority (BGR format)
                else:
                    color = (246, 130, 59)  # Blue - Low priority (BGR format)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"{class_name}: {confidence:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Draw gesture detections
        for gesture in gestures:
            if gesture and gesture.get("type") == "gesture":
                x1, y1, x2, y2 = gesture["bbox"]
                confidence = gesture["confidence"]
                gesture_name = gesture["gesture"]
                gesture_meaning = gesture.get("meaning", "")
                
                # Use cyan color for gestures (different from objects)
                color = (255, 255, 0)  # Cyan in BGR format

                # Draw bounding box for gestures
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                label = f"{gesture_name}: {gesture_meaning}"
                
                # Draw label background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                            (x1 + label_size[0], y1), color, -1)
                cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        return frame

    def draw_radar_hud(self, frame, radar_data):
        """Draw radar-based HUD overlay on frame"""
        if not radar_data:
            return frame
        
        try:
            h, w = frame.shape[:2]
            
            # Get radar information
            hud_data = radar_data.get('hud_data', {})
            collision_warning = radar_data.get('collision_warning')
            distance_viz = radar_data.get('distance_visualization')
            
            # Draw distance display (top-right corner)
            distance = hud_data.get('distance_m')
            if distance is not None:
                distance_text = f"Distance: {distance:.1f}m"
                status = hud_data.get('status', 'UNKNOWN')
                
                # Color based on status
                if status == "EMERGENCY":
                    color = (0, 0, 255)  # Red
                elif status == "CRITICAL":
                    color = (0, 165, 255)  # Orange
                elif status == "WARNING":
                    color = (0, 255, 255)  # Yellow
                else:
                    color = (0, 255, 0)  # Green
                
                # Draw distance box
                text_size = cv2.getTextSize(distance_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                box_x = w - text_size[0] - 20
                box_y = 10
                
                # Background rectangle
                cv2.rectangle(frame, (box_x - 10, box_y), (box_x + text_size[0] + 10, box_y + text_size[1] + 20), (0, 0, 0), -1)
                cv2.rectangle(frame, (box_x - 10, box_y), (box_x + text_size[0] + 10, box_y + text_size[1] + 20), color, 2)
                
                # Distance text
                cv2.putText(frame, distance_text, (box_x, box_y + text_size[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Status indicator
                status_text = f"Status: {status}"
                cv2.putText(frame, status_text, (box_x, box_y + text_size[1] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Draw collision warning (center of screen)
            if collision_warning:
                warning_text = collision_warning.get('message', 'WARNING')
                action_text = collision_warning.get('action', '')
                level = collision_warning.get('level', 'WARNING')
                
                if level == "EMERGENCY":
                    warning_color = (0, 0, 255)  # Red
                elif level == "CRITICAL":
                    warning_color = (0, 165, 255)  # Orange
                else:
                    warning_color = (0, 255, 255)  # Yellow
                
                # Draw warning box in center
                warning_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 3)[0]
                action_size = cv2.getTextSize(action_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                
                box_width = max(warning_size[0], action_size[0]) + 40
                box_height = warning_size[1] + action_size[1] + 40
                
                center_x = w // 2
                center_y = h // 2
                
                # Warning background
                cv2.rectangle(frame, 
                            (center_x - box_width//2, center_y - box_height//2),
                            (center_x + box_width//2, center_y + box_height//2),
                            (0, 0, 0), -1)
                cv2.rectangle(frame, 
                            (center_x - box_width//2, center_y - box_height//2),
                            (center_x + box_width//2, center_y + box_height//2),
                            warning_color, 3)
                
                # Warning text
                cv2.putText(frame, warning_text, 
                          (center_x - warning_size[0]//2, center_y - 10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1.0, warning_color, 3)
                
                # Action text
                if action_text:
                    cv2.putText(frame, action_text, 
                              (center_x - action_size[0]//2, center_y + 20), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, warning_color, 2)
            
            # Draw radar visualization (bottom-left corner)
            if distance_viz:
                self.draw_radar_visualization(frame, distance_viz)
                
        except Exception as e:
            print(f"Error drawing radar HUD: {e}")
        
        return frame

    def draw_radar_visualization(self, frame, distance_viz):
        """Draw a simple radar-like visualization"""
        try:
            h, w = frame.shape[:2]
            
            # Radar display parameters
            radar_center_x = 80
            radar_center_y = h - 80
            radar_radius = 60
            
            current_distance = distance_viz.get('current_distance', 0)
            max_range = distance_viz.get('max_range', 5.0)
            zones = distance_viz.get('zones', [])
            
            # Draw radar background circle
            cv2.circle(frame, (radar_center_x, radar_center_y), radar_radius, (50, 50, 50), -1)
            cv2.circle(frame, (radar_center_x, radar_center_y), radar_radius, (255, 255, 255), 2)
            
            # Draw zone circles
            for zone in zones:
                zone_range = zone.get('range', 1.0)
                zone_radius = int((zone_range / max_range) * radar_radius)
                if zone_radius <= radar_radius:
                    # Convert hex color to BGR
                    color_hex = zone.get('color', '#FFFFFF')
                    if color_hex.startswith('#'):
                        color_hex = color_hex[1:]
                    
                    # Simple color mapping
                    if 'FF0000' in color_hex:  # Red
                        zone_color = (0, 0, 255)
                    elif 'FF6600' in color_hex:  # Orange
                        zone_color = (0, 165, 255)
                    elif 'FFAA00' in color_hex:  # Yellow
                        zone_color = (0, 255, 255)
                    else:  # Green
                        zone_color = (0, 255, 0)
                    
                    cv2.circle(frame, (radar_center_x, radar_center_y), zone_radius, zone_color, 1)
            
            # Draw current distance indicator (as a line pointing up)
            if current_distance <= max_range:
                distance_radius = int((current_distance / max_range) * radar_radius)
                end_x = radar_center_x
                end_y = radar_center_y - distance_radius
                
                # Color based on distance
                if current_distance <= 0.5:
                    line_color = (0, 0, 255)  # Red
                elif current_distance <= 1.0:
                    line_color = (0, 165, 255)  # Orange
                elif current_distance <= 2.0:
                    line_color = (0, 255, 255)  # Yellow
                else:
                    line_color = (0, 255, 0)  # Green
                
                cv2.line(frame, (radar_center_x, radar_center_y), (end_x, end_y), line_color, 3)
                cv2.circle(frame, (end_x, end_y), 3, line_color, -1)
            
            # Draw radar label
            cv2.putText(frame, "RADAR", (radar_center_x - 25, radar_center_y + radar_radius + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
        except Exception as e:
            print(f"Error drawing radar visualization: {e}")

    def encode_frame(self, frame):
        """Encode frame as base64 JPEG"""
        try:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            return jpg_as_text
        except Exception as e:
            print(f"Error encoding frame: {e}")
            return None

    async def handle_client(self, websocket):
        """Handle WebSocket client connection"""
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")

        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
            print(f"Client disconnected. Total clients: {len(self.clients)}")

    async def broadcast_frame(self, frame_data, detections, gestures, radar_data=None):
        """Broadcast frame and detection data to all connected clients"""
        if self.clients:
            message = {
                "type": "frame",
                "data": frame_data,
                "detections": detections,
                "gestures": gestures,
                "room_classification": {
                    "type": self.room_classification,
                    "confidence": self.room_confidence,
                    "objects_count": len(self.objects_in_room),
                    "context": self.get_room_context()
                },
                "radar_data": radar_data,
                "timestamp": datetime.now().isoformat()
            }

            disconnected = set()
            for client in self.clients:
                try:
                    await client.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)

            self.clients -= disconnected

    def camera_loop(self, loop):
        """Main camera capture and processing loop"""
        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to capture frame")
                    continue

                # Process frame for detections
                detections = self.detect_objects(frame)
                gestures = self.detect_gestures(frame)
                
                # Process radar data if available
                radar_data = None
                if self.radar_manager:
                    try:
                        processed_count = self.radar_manager.process_new_radar_data()
                        radar_data = self.radar_manager.get_avoidance_data()
                        
                        # Log radar processing occasionally
                        if processed_count > 0:
                            print(f"📡 Processed {processed_count} new radar readings")
                    except Exception as e:
                        print(f"⚠️ Radar processing error: {e}")
                
                # Room classification (every 30 frames ~1 second)
                self.classification_update_counter += 1
                if self.classification_update_counter >= self.classification_update_interval:
                    self.classify_room()
                    self.classification_update_counter = 0

                # Create frame with all overlays
                frame_with_detections = frame.copy()
                
                # Draw object and gesture detections
                frame_with_detections = self.draw_detections(frame_with_detections, detections, gestures)
                
                # Draw radar HUD if available
                if radar_data:
                    frame_with_detections = self.draw_radar_hud(frame_with_detections, radar_data)

                # Encode frame
                frame_data = self.encode_frame(frame_with_detections)
                if frame_data:
                    # Broadcast to WebSocket clients
                    asyncio.run_coroutine_threadsafe(
                        self.broadcast_frame(frame_data, detections, gestures, radar_data),
                        loop
                    )

                time.sleep(0.033)  # ~30 FPS

            except Exception as e:
                print(f"Error in camera loop: {e}")
                break

    async def start_server(self):
        """Start the WebSocket server"""
        print(f"Starting video stream server on {self.host}:{self.port}")

        if not self.initialize_camera():
            print("Failed to initialize camera")
            return

        self.running = True

        loop = asyncio.get_event_loop()

        camera_thread = threading.Thread(target=self.camera_loop, args=(loop,), daemon=True)
        camera_thread.start()

        async with websockets.serve(self.handle_client, self.host, self.port):
            print("Video stream server started. Waiting for connections...")
            await asyncio.Future()  # Run forever

    def stop(self):
        """Stop the server"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    # Import the data store from websocket bridge if available
    try:
        from websocket_data_bridge import data_store
        server = VideoStreamServer(websocket_data_store=data_store)
        print("🔗 Connected to websocket data bridge for radar integration")
    except ImportError:
        print("⚠️ Websocket data bridge not available - running without radar integration")
        server = VideoStreamServer()

    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("\nStopping video stream server...")
    finally:
        server.stop()

if __name__ == "__main__":
    main()
