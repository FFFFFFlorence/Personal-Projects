#Libraries OpenCV and mediapipe (google's framework)
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands               #Initializes the hand-tracking solution.
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)       #video capture
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    #Mediapipe processing & gesture detection
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            #A helper module to draw skeletal lines and key points onto video frames.
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Hand Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            for id, lm in enumerate(hand_landmarks.landmark):
                print(f"Landmark {id}: (x: {lm.x}, y: {lm.y}, z: {lm.z})")
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
    #pinch gesture logic
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
    if distance < 0.05:
        print("Pinch gesture detected")
    else:
        print("No pinch gesture detected")
        
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
            label = 'Pinch' if distance < 0.05 else 'Open Hand'
            cv2.putText(frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
cap.release()
cv2.destroyAllWindows()
