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

class VideoStreamServer:
    def __init__(self, host="localhost", port=8765):
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
        confidence = 0.85  # Realistic confidence score
        
        # Gesture Classification based on hand landmarks
        try:
            # 1. Peace (V) - Room clear
            if (thumb_tip.y < index_tip.y and abs(thumb_tip.x - index_tip.x) > 0.1):
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

            # 4. Thumb up - Affirmative
            elif (thumb_tip.y < wrist.y and abs(thumb_tip.x - wrist.x) > 0.1):
                gesture_name = "thumbs_up"
                gesture_meaning = "affirmative"

            # 5. Thumb down - No/failure
            elif (thumb_tip.y > wrist.y and abs(thumb_tip.x - wrist.x) > 0.1):
                gesture_name = "thumbs_down"
                gesture_meaning = "no/failure"

            # 6. Open hand - Stop/freeze
            elif (abs(index_tip.y - middle_tip.y) < 0.05 and abs(middle_tip.y - ring_tip.y) < 0.05 and abs(ring_tip.y - pinky_tip.y) < 0.05):
                gesture_name = "open_hand"
                gesture_meaning = "stop/freeze"

            # 7. Pointer finger up - Emergency
            elif (index_tip.y < thumb_tip.y and abs(index_tip.x - thumb_tip.x) < 0.05):
                gesture_name = "point_up"
                gesture_meaning = "emergency"

            # 8. Flat hand sideways - Let's move
            elif (abs(index_tip.x - pinky_tip.x) > 0.15 and abs(index_tip.y - pinky_tip.y) < 0.1):
                gesture_name = "move"
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
                    color = '#ef4444';  # Red - High priority
                elif priority >= 5:
                    color = '#eab308';  # Yellow - Medium priority
                else:
                    color = '#3b82f6';  # Blue - Low priority

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
                color = (0, 255, 255)  # Cyan in BGR format

                # Draw bounding box for gestures
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                label = f"{gesture_name}: {gesture_meaning}"
                
                # Draw label background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                            (x1 + label_size[0], y1), color, -1)
                cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        return frame

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

    async def broadcast_frame(self, frame_data, detections, gestures):
        """Broadcast frame and detection data to all connected clients"""
        if self.clients:
            message = {
                "type": "frame",
                "data": frame_data,
                "detections": detections,
                "gestures": gestures,
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

                frame_with_detections = frame.copy()

                # Encode frame
                frame_data = self.encode_frame(frame_with_detections)
                if frame_data:
                    # Broadcast to WebSocket clients
                    asyncio.run_coroutine_threadsafe(
                        self.broadcast_frame(frame_data, detections, gestures),
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
    server = VideoStreamServer()

    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("\nStopping video stream server...")
    finally:
        server.stop()

if __name__ == "__main__":
    main()
