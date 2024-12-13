import os
# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

import cv2
import mediapipe as mp
import numpy as np
from collections import Counter
from scipy.spatial import KDTree
from ultralytics import YOLO

# Initialize Mediapipe Hand and YOLO
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)

# Load YOLO model
model = YOLO("yolo11n.pt")
PIC_WIDTH, PIC_HEIGHT = 640, 480  # Dimensions for YOLO model input

# Color mapping
basic_colors = {
    "Red": (255, 0, 0),
    "Green": (0, 255, 0),
    "Blue": (0, 0, 255),
    "Yellow": (255, 255, 0),
    "Black": (0, 0, 0),
    "White": (255, 255, 255),
    "Gray": (128, 128, 128),
    "Orange": (255, 165, 0),
    "Pink": (255, 192, 203),
    "Purple": (128, 0, 128),
    "Brown": (165, 42, 42)
}
color_values = np.array(list(basic_colors.values()))
tree = KDTree(color_values)

# Object names from COCO dataset
coco_object_names = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light",
    "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
    "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
    "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote", "keyboard", "cell phone",
    "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear",
    "hair drier", "toothbrush"
]

def adjust_contrast(image, alpha=1.5, beta=0):
    """
    Adjust the contrast and brightness of an image.

    Parameters:
        image (numpy.ndarray): Input image.
        alpha (float): Contrast control. >1 increases contrast.
        beta (int): Brightness control.

    Returns:
        numpy.ndarray: Adjusted image.
    """
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def color_mapper_bulk(rgb_pixels):
    """
    Query the KDTree in bulk to get the nearest color for each pixel.
    """
    _, indices = tree.query(rgb_pixels)
    return np.array([list(basic_colors.keys())[idx] for idx in indices])

def get_dominant_color(cropped_image, threshold=0.1):
    """
    Get the dominant color within the detection box or determine if the color is too complex.
    """
    pixels = cropped_image.reshape(-1, 3)
    color_names = color_mapper_bulk(pixels)
    counter = Counter(color_names)

    # Adjust weights for black and gray
    counter["Black"] *= 0.5  # Reduce weight by 50%
    counter["Gray"] *= 0.7  # Reduce weight by 30%

    dominant_color, count = counter.most_common(1)[0]
    total_pixels = len(pixels)
    if count / total_pixels < threshold:
        return "too complex"
    return dominant_color

def letterbox_image(image, size):
    """
    Resize the input image to fit the desired size, adding padding as necessary.
    """
    h, w = image.shape[:2]
    scale = min(size[1] / h, size[0] / w)
    nh, nw = int(h * scale), int(w * scale)
    padded_image = cv2.resize(image, (nw, nh))
    top = (size[1] - nh) // 2
    bottom = size[1] - nh - top
    left = (size[0] - nw) // 2
    right = size[0] - nw - left
    return cv2.copyMakeBorder(padded_image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(128, 128, 128)), scale, top, left

def detect_gesture(frame):
    """
    Detect hand gestures and return the filtered hand landmarks and pointing line.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            h, w, _ = frame.shape
            landmarks = [(int(l.x * w), int(l.y * h)) for l in hand_landmarks.landmark]

            # Gesture recognition: Four fingers folded, one extended
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
            tip_x, tip_y = int(index_tip.x * w), int(index_tip.y * h)
            mcp_x, mcp_y = int(index_mcp.x * w), int(index_mcp.y * h)

            # Calculate pointing line
            pointing_line = ((tip_x, tip_y), (tip_x + (tip_x - mcp_x) * 30, tip_y + (tip_y - mcp_y) * 30))

            return landmarks, pointing_line
    return None, None

def identify_color(frame, pointing_line, object_type):
    """
    Identify the color of a specific object type based on pointing line.

    Parameters:
        frame (numpy.ndarray): The input video frame.
        pointing_line (tuple): The hand's pointing line.
        object_type (str): The type of object to detect (from COCO dataset).

    Returns:
        str: The dominant color of the detected object or "Object not found".
    """
    padded_frame, scale, top, left = letterbox_image(frame, (PIC_WIDTH, PIC_HEIGHT))
    results = model(padded_frame)
    boxes = results[0].boxes

    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        x1 = int((x1 - left) / scale)
        y1 = int((y1 - top) / scale)
        x2 = int((x2 - left) / scale)
        y2 = int((y2 - top) / scale)

        object_name = coco_object_names[int(box.cls[0])]

        # Check if the detected object matches the specified object type
        if object_name == object_type:
            cropped_image = frame[y1:y2, x1:x2]
            return get_dominant_color(cropped_image)

    return "Object not found"

def process_video(input_stream, object_type):
    """
    Process a single video frame to detect the color of a specified object type.

    Parameters:
        input_stream (cv2.VideoCapture): Input video stream object.
        object_type (str): The type of object to detect (from COCO dataset).

    Returns:
        str: Detected color or an error message.
    """
    ret, frame = input_stream.read()
    if not ret:
        return "No frame available"

    frame = cv2.resize(frame, (PIC_WIDTH, PIC_HEIGHT))  # Resize frame
    frame = adjust_contrast(frame, alpha=1.5)  # Adjust contrast

    landmarks, pointing_line = detect_gesture(frame)
    if not pointing_line:
        return "No gesture detected"

    return identify_color(frame, pointing_line, object_type)

# Example usage:
#cap = cv2.VideoCapture(0)
#result = process_video(cap, "person")  # Detect the color of a bottle
#cap.release()
#print(f"Result: {result}")
