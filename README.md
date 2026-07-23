# Hand Gesture-Controlled Robotic Arm

> **Real-time hand landmark detection using MediaPipe for gesture-based robotic arm control via Arduino serial communication**

---

## 📋 Project Overview

This project implements a **gesture-controlled robotic arm system** that uses computer vision to detect hand landmarks in real-time and translates hand gestures into motion commands for a robotic arm. The system detects the distance between the thumb and index finger, maps it to a PWM signal, and sends it to an Arduino microcontroller that drives servo motors.

### Key Features

- **Real-time hand tracking** using MediaPipe Hand Landmarker
- **Gesture-to-PWM mapping** based on thumb-index finger distance
- **Serial communication** with Arduino for servo/actuator control
- **Visual feedback** with landmark overlay and PWM display

---

## 🎯 How It Works

```
┌─────────────┐
│   Webcam    │
│  (OpenCV)   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  MediaPipe      │
│  Hand Landmarker│
│  (21 landmarks) │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Calculate      │
│  thumb-index    │
│  distance       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Map distance   │
│  to PWM (0-255) │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Serial (UART)  │
│  /dev/ttyACM0   │
│  9600 baud      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│    Arduino      │
│  (Servo Control)│
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Robotic Arm    │
│  (Motion)       │
└─────────────────┘
```

### Gesture Mapping

The system tracks two key landmarks:
- **Landmark 4:** Thumb tip
- **Landmark 8:** Index finger tip

The Euclidean distance between these points is calculated and linearly mapped:

```
Distance Range: 20px → 200px
PWM Output:     0   → 255
```

This allows intuitive control:
- **Pinch (close):** Low PWM → arm retracts/stops
- **Open hand:** High PWM → arm extends/moves at full speed
- **Intermediate:** Proportional speed control

---

## 🗂 Code Structure

```
hand_landmarkers_detection/
├── control.py              # Main control script (MediaPipe Tasks API)
├── control2.py             # Alternative implementation / iteration
├── control3.py             # Alternative implementation / iteration
├── hand_landmarker.task    # MediaPipe Hand Landmarker model file
├── requirements.txt        # Python dependencies
└── .gitignore
```

### Main Components

**`control.py`**
- Initializes MediaPipe Hand Landmarker with the `.task` model
- Captures webcam frames via OpenCV
- Detects hand landmarks and extracts thumb (4) and index tip (8)
- Computes distance using `math.hypot(x2-x1, y2-y1)`
- Maps distance to PWM range [0, 255]
- Sends PWM value to Arduino via serial (`/dev/ttyACM0`, 9600 baud)
- Displays real-time visualization with landmark overlay

---

## 🛠 Installation &amp; Dependencies

### Prerequisites

- Python 3.7+
- Webcam
- Arduino (Uno/Mega) connected via USB
- Servo motor(s) connected to Arduino

### Setup

```bash
# Clone the repository
git clone https://github.com/heba266/hand_landmarkers_detection.git
cd hand_landmarkers_detection

# Install Python dependencies
pip install -r requirements.txt
```

### Arduino Setup

Upload a sketch to your Arduino that reads serial data and controls servos. Example:

```cpp
#include <Servo.h>

Servo armServo;
int pwmValue = 0;

void setup() {
  Serial.begin(9600);
  armServo.attach(9);  // Servo on pin 9
}

void loop() {
  if (Serial.available() > 0) {
    pwmValue = Serial.parseInt();
    pwmValue = constrain(pwmValue, 0, 255);
    int angle = map(pwmValue, 0, 255, 0, 180);
    armServo.write(angle);
  }
}
```

---

## 🚀 Usage

```bash
python control.py
```

### Controls

- **Open hand:** Increase arm speed/extension
- **Pinch (thumb + index close):** Decrease speed/retract
- **Press `q`:** Quit the application

### Troubleshooting

- **Serial port not found:** Check `/dev/ttyACM0` matches your Arduino port (use `ls /dev/tty*` on Linux or check Device Manager on Windows)
- **No hand detected:** Ensure good lighting and hand is fully visible in frame
- **Lag:** Reduce camera resolution or frame rate

---

## 📊 Technical Details

| Component | Specification |
|-----------|---------------|
| **Hand Tracking** | MediaPipe Hand Landmarker (21 landmarks per hand) |
| **Model** | `hand_landmarker.task` (TensorFlow Lite) |
| **Camera** | OpenCV `VideoCapture(0)` |
| **Serial Protocol** | UART, 9600 baud, ASCII-encoded integer + newline |
| **PWM Range** | 0–255 (8-bit) |
| **Distance Mapping** | Linear: 20px–200px → 0–255 |
| **Frame Processing** | BGR → RGB conversion for MediaPipe |

---

## 🔮 Future Improvements

- [ ] Multi-gesture recognition (open palm, fist, pointing, peace sign)
- [ ] Multi-DOF arm control (base rotation, elbow, wrist)
- [ ] Gesture smoothing with low-pass filter
- [ ] ROS integration for robotic arm control
- [ ] GUI for gesture-to-action mapping configuration

---

## 🔗 Related Projects

| Repository | Description |
|------------|-------------|
| [behavior_tree](https://github.com/heba266/behavior_tree) | BehaviorTree.CPP-based mission control for autonomous navigation |
| [bev_cnn](https://github.com/heba266/bev_cnn) | CNN-based multi-camera Bird's-Eye-View generation |
| [costmap_custom_plugin](https://github.com/heba266/costmap_custom_plugin) | Custom ROS costmap plugins for obstacle layer integration |

---

## 📚 References

1. MediaPipe Hand Landmarker: [https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)
2. MediaPipe Tasks Python API: [https://ai.google.dev/edge/mediapipe/solutions/tasks](https://ai.google.dev/edge/mediapipe/solutions/tasks)
3. OpenCV Documentation: [https://docs.opencv.org](https://docs.opencv.org)

---

## 👥 Authors

**Heba El-Afifi** — Computer &amp; Communication Engineering, Alexandria University  
📧 iheba3930@gmail.com | 🐙 [github.com/heba266](https://github.com/heba266)

*Developed in collaboration with a teammate as part of a robotics control project.*

---

## 📄 License

This project is released under the MIT License.
