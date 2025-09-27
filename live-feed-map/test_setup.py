#!/usr/bin/env python3
"""
Test script to verify the video streaming setup
"""

def test_imports():
    """Test if all required packages can be imported"""
    print("🔧 Testing package imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import ultralytics
        print("✅ Ultralytics imported successfully")
    except ImportError as e:
        print(f"❌ Ultralytics import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    try:
        import websockets
        print("✅ WebSockets imported successfully")
    except ImportError as e:
        print(f"❌ WebSockets import failed: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    return True

def test_camera():
    """Test if camera can be accessed"""
    print("\n📹 Testing camera access...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Camera could not be opened")
            return False
        
        ret, frame = cap.read()
        if not ret:
            print("❌ Could not read from camera")
            cap.release()
            return False
        
        print(f"✅ Camera working - frame shape: {frame.shape}")
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_yolo():
    """Test if YOLO model can be loaded"""
    print("\n🤖 Testing YOLO model loading...")
    
    try:
        from ultralytics import YOLO
        
        # Try to load a model
        model_files = ['yolov8n.pt', 'yolov5n.pt', 'yolov5s.pt']
        
        for model_file in model_files:
            try:
                print(f"   Trying {model_file}...")
                model = YOLO(model_file, verbose=False)
                print(f"✅ {model_file} loaded successfully")
                return True
            except Exception as model_error:
                print(f"   Failed to load {model_file}: {model_error}")
                continue
        
        print("❌ Could not load any YOLO model")
        return False
        
    except Exception as e:
        print(f"❌ YOLO test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚒 Mac Camera Video Stream Setup Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Package import test failed")
        return False
    
    # Test camera
    if not test_camera():
        print("\n❌ Camera test failed")
        return False
    
    # Test YOLO
    if not test_yolo():
        print("\n❌ YOLO test failed")
        return False
    
    print("\n✅ All tests passed! Setup is ready.")
    print("\nTo start the video stream:")
    print("1. Run: ./start_mac_detector.sh")
    print("2. Open: http://localhost:3000/live-feed")
    print("3. Select 'Firefighter Alpha (Mac Camera)'")
    print("4. Click 'Start Detection'")
    
    return True

if __name__ == "__main__":
    main()
