import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import Image
from mediapipe import ImageFormat

import math
import serial
import time

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(2)  

base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)

# mp_hands = mp.solutions.hands
# hands = mp_hands.Hands(
#     static_image_mode=False,
#     max_num_hands=1,
#     min_detection_confidence=0.7,
#     min_tracking_confidence=0.6
# )

# mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

def map_value(x, in_min, in_max, out_min, out_max):

    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1) 
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)

    result = detector.detect(mp_image)

    if result.hand_landmarks:
        for hand_landmarks in result.hand_landmarks:
            gesture = ''

            # mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers = []
            #thump, compare tip and joint it it's extended
            fingers.append(hand_landmarks[4].x < hand_landmarks[3].x) # true if extended
            #index finger
            fingers.append(hand_landmarks[8].y < hand_landmarks[6].y)
            #middle finger
            fingers.append(hand_landmarks[12].y < hand_landmarks[10].y)
            #ring finger
            fingers.append(hand_landmarks[16].y < hand_landmarks[14].y)
            #pinky
            fingers.append(hand_landmarks[20].y < hand_landmarks[18].y)

            fingers_sum = sum(fingers)

            if fingers[0] and fingers[1] and not any(fingers[2:]):
                h, w, _ = frame.shape
                x1 = int(hand_landmarks[4].x * w)  #thumb coordinates
                y1 = int(hand_landmarks[4].y * h)

                x2 = int(hand_landmarks[8].x * w)  #tip coordinates
                y2 = int(hand_landmarks[8].y * h)

                cv2.circle(frame, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(frame, (x2, y2), 10, (255, 0, 0), cv2.FILLED)

                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                distance = math.hypot(x2 - x1, y2 - y1)

                pwm_control = map_value(distance, 20, 200, 0, 255)
                pwm_control = max(0, min(255, pwm_control))

                data = str(pwm_control) + '\n'
                arduino.write(f"M2:{pwm_control}\n".encode('utf-8'))
                cv2.putText(frame, f'pwm_control: {pwm_control}', (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            else :


                if fingers_sum == 0:  #FIST
                    gesture = 'STOP'
                elif fingers_sum == 5:  #PALM
                    gesture = 'FORWARD_MED'
                elif fingers[1] and not any(fingers[2:]):  #POINTING
                    gesture = 'FORWARD_HIGH'
                elif fingers[1] and fingers[2] and not any(fingers[3:]):  #2 POINTING
                    gesture = 'DOWNWARD_MED'
                elif fingers[0] and not any(fingers[1:]):   #THUMPS UP
                    gesture = 'FORWARD_RAMP'
                elif fingers[0] and any(fingers[1:]):  #THUMPS DOWN
                    gesture = 'DOWNWARD_RAMP'
                else:
                    gesture = 'UNDEFINED'

            
                for idx in [4, 8, 12, 16, 20]:  # fingers tips
                    cx, cy = int(hand_landmarks[idx].x * frame.shape[1]), int(hand_landmarks[idx].y * frame.shape[0])
                    cv2.circle(frame, (cx, cy), 6, (0, 255, 0), -1)


            
                arduino.write(f"M1:{gesture}\n".encode('utf-8'))


                cv2.putText(frame, f'gesture: {gesture}', (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()