import cv2
import numpy as np
import time
import mss
import asyncio
import websockets
import json
import threading

# ===================== WebSocket Config =====================
HOST = "10.42.0.117"   # <-- set your server IP
PORT = 65431           # <-- set your server port

# ===================== Runtime Options ======================
CAPTURE_INTERVAL_SEC = 0.05   # faster sampling
ENABLE_PLOT = False           # keep False for max speed
SHOW_PREVIEW = True           # set False for even more speed
PRINT_EVERY_N = 10            # throttle console prints

# ⚠️ IMPORTANT: Update ONLY the width and height to match your radar window size.
CAPTURE_WIDTH = 10
CAPTURE_HEIGHT = 500

# ROI within the captured region (0..1)
ROI_X_START_NORM = 0.25
ROI_X_END_NORM   = 0.90
ROI_Y_START_NORM = 0.05
ROI_Y_END_NORM   = 0.95

MAX_RANGE_M = 50.0

# --- Calibration ---
CALIBRATION_SCALE = 0.3
CALIBRATION_OFFSET_M = 0.0

# --- Color filtering (HSV) ---
LOWER_RED_YELLOW_1 = np.array([  0, 100, 100])
UPPER_RED_YELLOW_1 = np.array([ 30, 255, 255])
LOWER_RED_YELLOW_2 = np.array([160, 100, 100])
UPPER_RED_YELLOW_2 = np.array([179, 255, 255])

# Binary mask threshold: inRange already gives 0/255, so we only need “>0”
SIGNAL_THRESHOLD = 1

# If no signal found
DEFAULT_CLOSED_DISTANCE_M = 0.0

# ===================== Async WS sender (persistent) =====================
class WSSender:
    def __init__(self, host, port):
        self.uri = f"ws://{host}:{port}"
        self.queue = asyncio.Queue()
        self.stop_evt = asyncio.Event()

    async def run(self):
        while not self.stop_evt.is_set():
            try:
                async with websockets.connect(self.uri) as ws:
                    # drain queue while connected
                    while not self.stop_evt.is_set():
                        msg = await self.queue.get()
                        await ws.send(msg)
            except Exception as e:
                # brief backoff, then retry
                # print("WS reconnecting:", e)
                await asyncio.sleep(0.5)

    async def send(self, payload: dict):
        await self.queue.put(json.dumps(payload))

    async def stop(self):
        self.stop_evt.set()

def start_ws_sender(host, port):
    loop = asyncio.new_event_loop()
    sender = WSSender(host, port)

    def run_loop():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(sender.run())

    t = threading.Thread(target=run_loop, daemon=True)
    t.start()
    return sender, loop, t

# ===================== Radar logic =====================
def analyze_radar_roi(roi_bgr: np.ndarray, roi_y_start: int):
    """
    Detect deepest row containing red/yellow signal using binary masks only.
    Returns (estimated_distance_m, peak_y_pixel).
    """
    # Convert ROI to HSV
    roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)

    # Two red/yellow masks (0/255)
    m1 = cv2.inRange(roi_hsv, LOWER_RED_YELLOW_1, UPPER_RED_YELLOW_1)
    m2 = cv2.inRange(roi_hsv, LOWER_RED_YELLOW_2, UPPER_RED_YELLOW_2)

    # Combine binary masks
    mask = cv2.bitwise_or(m1, m2)

    # For speed, check which rows have any nonzero pixel
    rows_any = np.any(mask > 0, axis=1)
    idx = np.flatnonzero(rows_any)

    if idx.size == 0:
        return DEFAULT_CLOSED_DISTANCE_M, roi_y_start  # none found

    deepest_signal_index = int(idx[-1])  # last row that has signal

    # Normalize and convert to meters
    normalized_distance = deepest_signal_index / mask.shape[0]
    raw_distance_m = normalized_distance * MAX_RANGE_M

    # Apply calibration and clamp
    est_m = (raw_distance_m * CALIBRATION_SCALE) + CALIBRATION_OFFSET_M
    est_m = float(np.clip(est_m, 0.0, MAX_RANGE_M))

    peak_y_pixel = deepest_signal_index + roi_y_start
    return est_m, peak_y_pixel

def process_real_time_screen_radar():
    sct = mss.mss()

    # Calculate centered coordinates (fixed-size capture)
    mon = sct.monitors[0]
    screen_w, screen_h = mon["width"], mon["height"]
    monitor_region = {
        "left":  int(screen_w / 2 - CAPTURE_WIDTH  / 2),
        "top":   int(screen_h / 2 - CAPTURE_HEIGHT / 2),
        "width": CAPTURE_WIDTH,
        "height": CAPTURE_HEIGHT,
        "mon": 1
    }

    # Precompute ROI pixel bounds (constant per frame because capture size is fixed)
    roi_x_start = int(CAPTURE_WIDTH  * ROI_X_START_NORM)
    roi_x_end   = int(CAPTURE_WIDTH  * ROI_X_END_NORM)
    roi_y_start = int(CAPTURE_HEIGHT * ROI_Y_START_NORM)
    roi_y_end   = int(CAPTURE_HEIGHT * ROI_Y_END_NORM)

    # Safety clamp
    roi_x_start = max(0, min(roi_x_start, CAPTURE_WIDTH-1))
    roi_x_end   = max(roi_x_start+1, min(roi_x_end, CAPTURE_WIDTH))
    roi_y_start = max(0, min(roi_y_start, CAPTURE_HEIGHT-1))
    roi_y_end   = max(roi_y_start+1, min(roi_y_end, CAPTURE_HEIGHT))

    print(f"Screen: {screen_w}x{screen_h}")
    print(f"Capture region: {monitor_region}")
    print(f"ROI pixels: x[{roi_x_start}:{roi_x_end}] y[{roi_y_start}:{roi_y_end}]")
    print(f"Calibration -> SCALE: {CALIBRATION_SCALE:.3f}, OFFSET_M: {CALIBRATION_OFFSET_M:.3f}")
    print("Press 'q' to quit.")

    # Start WS sender
    sender, ws_loop, ws_thread = start_ws_sender(HOST, PORT)

    # Optional plotting (disabled by default for speed)
    if ENABLE_PLOT:
        import matplotlib.pyplot as plt
        plt.ion()
        fig, ax = plt.subplots(figsize=(6, 3))
        line, = ax.plot([], [], marker='.', linestyle='-')
        ax.set_ylim(0, MAX_RANGE_M)
        ax.set_xlim(0, 10)  # will expand dynamically
        ax.grid(True)
        times, dists = [], []

    last_time = 0.0
    i = 0

    try:
        while True:
            now = time.time()
            if now - last_time < CAPTURE_INTERVAL_SEC:
                # tiny sleep prevents 100% CPU spin
                time.sleep(0.001)
                # check for key while idle
                if SHOW_PREVIEW and cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
            last_time = now

            # Grab frame (BGRA)
            sct_img = sct.grab(monitor_region)

            # Convert to BGR only once and crop ROI
            frame_bgr = cv2.cvtColor(np.asarray(sct_img), cv2.COLOR_BGRA2BGR)
            roi_bgr = frame_bgr[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

            # Analyze ROI
            distance_m, peak_y_pixel = analyze_radar_roi(roi_bgr, roi_y_start)

            # Send over WS (non-blocking via queue)
            payload = {
                "type": "radar_distance",
                "distance_m": float(distance_m),
                "t_sec": float(now),
            }
            try:
                asyncio.run_coroutine_threadsafe(sender.send(payload), ws_loop)
            except Exception as e:
                pass  # keep running

            # Throttled console print
            i += 1
            if i % PRINT_EVERY_N == 0:
                print(f"t={now:.2f}  dist={distance_m:.2f} m")

            # Optional live preview
            if SHOW_PREVIEW:
                # draw line in the *full* capture frame at peak row
                cv2.line(frame_bgr, (0, peak_y_pixel), (frame_bgr.shape[1]-1, peak_y_pixel), (0, 255, 255), 2)
                cv2.putText(frame_bgr, f"{distance_m:.2f} m", (8, 28),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
                cv2.imshow('Radar Screen Capture (q to quit)', frame_bgr)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Optional light plotting
            if ENABLE_PLOT:
                times.append(now)
                dists.append(distance_m)
                line.set_data(times, dists)
                ax.set_xlim(times[0], times[-1] if times else 10)
                fig.canvas.draw(); fig.canvas.flush_events()

    finally:
        cv2.destroyAllWindows()
        # stop ws loop
        try:
            ws_loop.call_soon_threadsafe(ws_loop.stop)
        except Exception:
            pass

if __name__ == "__main__":
    process_real_time_screen_radar()
