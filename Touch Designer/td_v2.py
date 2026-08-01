import cv2
import mediapipe as mp
import time

# MediaPipe 1.0+ Tasks API Imports
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Initialize Hand Landmarker
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2
)

landmarker = HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB and wrap into MediaPipe Image object
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Get current timestamp in milliseconds required by VIDEO mode
    frame_timestamp_ms = int(time.time() * 1000)

    # Run hand detection
    result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

    # Check for detected hand landmarks
    if result.hand_landmarks:
        for hand in result.hand_landmarks:
            h, w, _ = frame.shape

            # Landmark 4: Thumb Tip, Landmark 8: Index Tip
            thumb_tip = hand[4]
            index_tip = hand[8]

            # Convert to pixel coordinates
            thumb_px = (int(thumb_tip.x * w), int(thumb_tip.y * h))
            index_px = (int(index_tip.x * w), int(index_tip.y * h))

            # Draw circles on keypoints
            cv2.circle(frame, thumb_px, 8, (0, 255, 0), -1)
            cv2.circle(frame, index_px, 8, (0, 255, 0), -1)

            # Calculate pinch distance (normalized space)
            distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
            label = 'Pinch' if distance < 0.05 else 'Open Hand'

            # Display label
            cv2.putText(frame, f"State: {label}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('TouchDesigner Hand Tracking (MP 1.0)', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

landmarker.close()
cap.release()
cv2.destroyAllWindows()