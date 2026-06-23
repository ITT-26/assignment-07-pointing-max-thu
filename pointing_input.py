# here goes your mediapipe-to-pointer implementation
import cv2
import time
import math
import pyautogui
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pynput.mouse import Controller, Button
from mediapipe_sample_code.hand_landmark_drawer import draw_landmarks_on_image


MODEL_PATH = "./mediapipe_sample_code/hand_landmarker.task"

mouse = Controller()

# Get screen resolution automatically
screen_width, screen_height = pyautogui.size()

# Smoothing factor for cursor movement
alpha = 0.15

# Start cursor in the center of the screen
smooth_x = screen_width // 2
smooth_y = screen_height // 2

pinch_candidate_start = 0
pinch_confirm_time = 0.12
click_threshold = 0.05
pinch_active = False
drag_started = False
pinch_start_time = 0
last_click_time = 0
double_click_window = 0.4
drag_threshold_time = 0.5
drag_started = False



options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=MODEL_PATH),
    num_hands=1,
    running_mode=vision.RunningMode.VIDEO,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6,
)

detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

cv2.namedWindow("Pose Pointing")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue
    frame = cv2.flip(frame, 1) # Mirror image to make interaction feel more natural
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    timestamp_ms = int(time.time() * 1000)
    result = detector.detect_for_video(mp_image, timestamp_ms)

    if len(result.hand_landmarks) > 0:
        # Use the first detected hand
        hand = result.hand_landmarks[0]
        # Landmark 8 = index fingertip
        # Landmark 4 = thumb tip
        index_tip = hand[8]
        thumb_tip = hand[4]
        
        # Map fingertip position to screen coordinates
        x = int(index_tip.x * screen_width)
        y = int(index_tip.y * screen_height)

        # Ignore very small movements to reduce cursor jitter
        if abs(x - smooth_x) < 15:
            x = smooth_x
        if abs(y - smooth_y) < 15:
            y = smooth_y

        # Apply exponential smoothing for more stable cursor movement
        smooth_x = int(alpha * x + (1 - alpha) * smooth_x)
        smooth_y = int(alpha * y + (1 - alpha) * smooth_y)
        mouse.position = (smooth_x, smooth_y)
        # Calculate thumb-index distance for pinch detection
        distance = math.sqrt((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2)
        
        current_time = time.time()

        # start pinch
        # if distance < click_threshold and not pinch_active:
        #     pinch_active = True
        #     pinch_start_time = current_time

        # Start pinch only if the pinch is stable for a short time.
        # This avoids accidental clicks caused by one-frame detection jitter.
        if distance < click_threshold and not pinch_active:
            if pinch_candidate_start == 0:
                pinch_candidate_start = current_time

            elif current_time - pinch_candidate_start > pinch_confirm_time:
                pinch_active = True
                pinch_start_time = current_time
                pinch_candidate_start = 0

        elif distance >= click_threshold and not pinch_active:
            pinch_candidate_start = 0
            
        # continue pinch
        elif distance < click_threshold and pinch_active:
            pinch_duration = current_time - pinch_start_time
            # pinch for long enough => start drag
            if pinch_duration > drag_threshold_time and not drag_started:
                mouse.press(Button.left)
                drag_started = True

        # end pinch
        elif distance >= click_threshold and pinch_active:

            pinch_duration = current_time - pinch_start_time

            # end drag
            if drag_started:
                mouse.release(Button.left)
                drag_started = False

            # short pinch => click
            elif pinch_duration < drag_threshold_time:
                if current_time - last_click_time < double_click_window:
                    mouse.click(Button.left, 2)
                    last_click_time = 0
                else:
                    mouse.click(Button.left, 1)
                    last_click_time = current_time
            pinch_active = False
        # Display pinch distance for debugging
        cv2.putText(frame, f"Pinch: {distance:.3f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX,1,(0, 255, 0),2)
    
    # Draw landmarks and status text on the image
    annotated = draw_landmarks_on_image(rgb,result)
    annotated = cv2.cvtColor(annotated,cv2.COLOR_RGB2BGR)
    status = "MOVE"
    if drag_started:
        status = "DRAG"
    elif pinch_active:
        status = "PINCH"
    cv2.putText(annotated,status,(20, 80),cv2.FONT_HERSHEY_SIMPLEX,1,(0, 255, 0),2)
    # Display webcam window
    cv2.imshow("Pose Pointing", annotated) 

    # Press 'q' to exit
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()