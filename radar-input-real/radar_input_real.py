import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import mss # Screen capture library

# --- Configuration (UPDATE width/height/ROI only) ---
CAPTURE_INTERVAL_SEC = 0.5 

# ⚠️ IMPORTANT: Update ONLY the width and height to match your radar window size.
CAPTURE_WIDTH = 10     # Desired width of the radar plot to capture
CAPTURE_HEIGHT = 500    # Desired height of the radar plot to capture

# Define the Region of Interest (ROI) for the radar data within the CAPTURED REGION (Normalized to 0-1)
ROI_X_START_NORM = 0.25
ROI_X_END_NORM = 0.90
ROI_Y_START_NORM = 0.05
ROI_Y_END_NORM = 0.95
MAX_RANGE_M = 50.0

# --- COLOR FILTERING SETTINGS (FINAL: ONLY RED/YELLOW) ---
# Define HSV ranges for Red/Yellow (High Intensity Signal)
# Range 1 (Red/Orange/Yellow: 0 to ~30 Hue)
LOWER_RED_YELLOW_1 = np.array([0, 100, 100]) # High Saturation and Value to target strong signals
UPPER_RED_YELLOW_1 = np.array([30, 255, 255])
# Range 2 (True Red wrap-around)
LOWER_RED_YELLOW_2 = np.array([160, 100, 100])
UPPER_RED_YELLOW_2 = np.array([179, 255, 255])

# Threshold for signal tracking (brightness in the masked image). 
SIGNAL_THRESHOLD = 50 
# Default distance to report if NO red signal is detected.
DEFAULT_CLOSED_DISTANCE_M = 0.0

# --- Core Processing Function ---
def analyze_radar_frame(frame):
    """
    Analyzes a single frame, filtering ONLY for the red/yellow signal (target), 
    and finds the deepest (furthest) point of that red/yellow signal.
    """
    # Convert BGRA (from mss) to a standard OpenCV BGR format
    frame = cv2.cvtColor(np.array(frame), cv2.COLOR_BGRA2BGR)
    
    h, w, _ = frame.shape
    
    # 1. Define and Crop the ROI within the captured screen region
    roi_x_start = int(w * ROI_X_START_NORM)
    roi_x_end = int(w * ROI_X_END_NORM)
    roi_y_start = int(h * ROI_Y_START_NORM)
    roi_y_end = int(h * ROI_Y_END_NORM)
    
    if roi_x_start >= roi_x_end or roi_y_start >= roi_y_end:
        return DEFAULT_CLOSED_DISTANCE_M, None
        
    roi = frame[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
    
    # 2. Convert to HSV and apply color masks for Red/Yellow
    roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Create masks for the two red/yellow ranges
    mask_red_1 = cv2.inRange(roi_hsv, LOWER_RED_YELLOW_1, UPPER_RED_YELLOW_1)
    mask_red_2 = cv2.inRange(roi_hsv, LOWER_RED_YELLOW_2, UPPER_RED_YELLOW_2)
    
    # Combine the two masks (logical OR)
    combined_mask = cv2.bitwise_or(mask_red_1, mask_red_2)
    
    # Apply the mask: only red/yellow colors remain, others become black (0 intensity)
    masked_roi = cv2.bitwise_and(roi, roi, mask=combined_mask)
    
    # Convert the resulting image to grayscale/Value channel for intensity analysis
    masked_gray = cv2.cvtColor(masked_roi, cv2.COLOR_BGR2GRAY)
    
    # 3. Find vertical positions (rows) that maintain a signal intensity
    max_intensity_per_row = np.max(masked_gray, axis=1)
    
    # Get the indices (row numbers) where the signal is above the threshold (i.e., strong red/yellow)
    strong_signal_indices = np.where(max_intensity_per_row > SIGNAL_THRESHOLD)[0]

    # 4. Find the FURTHEST (deepest/highest index) red/yellow signal
    if strong_signal_indices.size == 0:
        # No red/yellow signal detected. Object is "very closed."
        estimated_distance_m = DEFAULT_CLOSED_DISTANCE_M
        peak_y_pixel = roi_y_start 
    else:
        # Find the highest index (furthest down the plot)
        deepest_signal_index = strong_signal_indices[-1]
        
        # 5. Convert the pixel index to the estimated distance in meters
        normalized_distance = deepest_signal_index / len(max_intensity_per_row)
        estimated_distance_m = normalized_distance * MAX_RANGE_M
        
        # Determine the vertical pixel index in the CAPTURED frame for visualization
        peak_y_pixel = deepest_signal_index + roi_y_start
    
    return estimated_distance_m, peak_y_pixel

# --- Real-Time Processing Loop ---
def process_real_time_screen_radar():
    """
    Calculates the centered monitor region, captures the region, and processes it.
    """
    sct = mss.mss()
    
    # Get primary monitor dimensions
    monitor_info = sct.monitors[0]
    screen_width = monitor_info["width"]
    screen_height = monitor_info["height"]

    # Calculate centered coordinates
    monitor_region = {
        "left": int(screen_width / 2 - CAPTURE_WIDTH / 2),
        "top": int(screen_height / 2 - CAPTURE_HEIGHT / 2),
        "width": CAPTURE_WIDTH,
        "height": CAPTURE_HEIGHT,
        "mon": 1 # Use the first monitor by default
    }
    
    print(f"Screen Resolution: {screen_width}x{screen_height}")
    print(f"Calculated Capture Region (Centered): {monitor_region}")

    # Initialize plot for real-time distance tracking
    plt.ion() 
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_title('Real-Time Relative Distance to Object (Screen Capture)')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Estimated Relative Distance (m)')
    ax.grid(True)
    
    # Data storage
    start_time = time.time()
    last_capture_time = 0
    time_series = []
    distance_series = []
    
    print("\n--- Starting Real-Time Screen Capture Radar Extraction ---")
    print(f"Processing Interval: {CAPTURE_INTERVAL_SEC} seconds.")
    print("Press 'q' in the live window to quit.")

    while True:
        current_time = time.time()
        
        # Check if the capture interval has passed (The "screenshot" logic)
        if current_time - last_capture_time >= CAPTURE_INTERVAL_SEC:
            last_capture_time = current_time
            
            # 1. Capture the screen region
            try:
                sct_img = sct.grab(monitor_region)
            except Exception as e:
                print(f"Error during screen grab: {e}. Check if the monitor is active.")
                break

            # 2. Analyze the captured image
            distance_m, peak_y_pixel = analyze_radar_frame(sct_img)
            
            if distance_m is not None:
                elapsed_time = current_time - start_time
                time_series.append(elapsed_time)
                distance_series.append(distance_m)
                
                print(f"Time: {elapsed_time:.2f} s | Distance: {distance_m:.2f} m")

                # 3. Update the plot
                ax.clear()
                ax.plot(time_series, distance_series, marker='.', linestyle='-', color='red')
                ax.set_title(f'Distance: {distance_m:.2f} m')
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Estimated Relative Distance (m)')
                ax.grid(True)
                fig.canvas.draw()
                fig.canvas.flush_events()
            
            # 4. Draw the results on the live frame for visual feedback
            frame = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
            if distance_m is not None and peak_y_pixel is not None:
                # Draw the detected reflection line on the captured image
                cv2.line(frame, (0, peak_y_pixel), (frame.shape[1], peak_y_pixel), (0, 255, 255), 2)
                # Display the estimated distance
                cv2.putText(frame, 
                            f"Distance: {distance_m:.2f} m", 
                            (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            1, 
                            (0, 255, 255), 
                            2, 
                            cv2.LINE_AA)
            
            cv2.imshow('Live Screen Capture Radar Analysis (Press Q to quit)', frame)
        
        # Exit loop on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cv2.destroyAllWindows()
    plt.ioff()
    plt.show() # Keep the final plot open

if __name__ == "__main__":
    process_real_time_screen_radar()