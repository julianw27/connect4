#!/usr/bin/env python3
import time
import cv2
import json
import bottle

# Detect color based on BGR values
def detect_color(b, g, r):
    b, g, r = int(b), int(g), int(r)
    total_brightness = r + g + b # Total brightness
    if total_brightness < 30:  # Very dark pixels are empty
        return 0
    
    # Calculate differences between color channels
    red_vs_blue = r - b
    blue_vs_red = b - r
    red_vs_green = r - g
    blue_vs_green = b - g
    
    # Determine orange or blue based on channel differences
    if red_vs_blue > 5 and red_vs_green > 3 and r > 25: # orange detection
        return 1
    
    if blue_vs_red > 5 and blue_vs_green > 3 and b > 25: # blue detection
        return 2 
    
    # If no color dominance, assume empty
    return 0 

# Classify a pixel and return the corresponding value
def classify_pixel(b, g, r):
    return detect_color(b, g, r)


# Get the current state of the board using field centers and color classification
def get_board_state(img):

    field_centers = [
        [(391, 1009), (608, 1008), (823, 1009), (1039, 1007), (1258, 1005), (1482, 1004), (1701, 993)],
        [(375, 847), (604, 849), (822, 838), (1043, 845), (1258, 849), (1484, 845), (1703, 844)],
        [(360, 676), (599, 681), (827, 672), (1055, 673), (1274, 666), (1498, 676), (1711, 678)],
        [(357, 507), (596, 501), (822, 505), (1051, 503), (1274, 505), (1498, 499), (1724, 500)],
        [(350, 321), (590, 323), (822, 326), (1042, 328), (1283, 320), (1515, 324), (1733, 321)],
        [(332, 141), (582, 138), (819, 150), (1045, 143), (1278, 138), (1524, 148), (1744, 146)]
    ]

    board = []
    
    # Classify each field on the board and build the board state
    for user_row in [5, 4, 3, 2, 1, 0]:
        row_data = []
        for col in range(7):
            cx, cy = field_centers[user_row][col]
            b, g, r = img[cy, cx]
            result = classify_pixel(b, g, r)
            row_data.append(result)
        board.append(row_data)
    return board


# Capture an image from the camera
def capture_from_camera():
    test_devices = ['/dev/video5', 5, '/dev/video3', 3, '/dev/video1', 1]
    
    # Try each camera device until one works
    for camera_id in test_devices:
        print(f"Trying camera device: {camera_id}")
        try:
            cap = cv2.VideoCapture(camera_id)
            if cap.isOpened():
                print(f"Successfully opened camera: {camera_id}")
                
                # Camera settings
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Disable auto exposure
                cap.set(cv2.CAP_PROP_EXPOSURE, -8)  # Lower exposure for bright conditions
                cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.3)  # Lower brightness
                cap.set(cv2.CAP_PROP_CONTRAST, 0.8)    # Higher contrast to distinguish colors
                
                time.sleep(1)  # Wait a moment for settings to take effect
                
                # Capture a single frame and return it
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"Successfully captured frame with shape: {frame.shape}")
                    cap.release()
                    return frame
                else:
                    print(f"Failed to capture frame from camera {camera_id}")
                    cap.release()
                    return None 
        except Exception as e:
            print(f"Exception trying camera {camera_id}: {e}")
    
    print("ERROR: No camera device worked!")
    return None

# _______ Bottle web server setup _______
# POST request handler
@bottle.route('/capture_board', method='POST')
def capture_board():
    bottle.response.content_type = 'application/json' # Set response content type to JSON
    
    # Capture board image, get state, and return it
    print("Capturing image from camera...")
    img = capture_from_camera()
    board_state = get_board_state(img)
    print(f"Detected board state: {board_state}")
    
    return json.dumps(board_state)

# __________MAIN PROGRAM ENTRY POINT_____________
if __name__ == '__main__':
    bottle.run(host='::', port=9547)
