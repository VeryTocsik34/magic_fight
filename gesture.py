import cv2
import mediapipe as mp


class Gesture:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Webcam is not available")

    def __del__(self):
        if hasattr(self, "cap") and self.cap is not None:
            self.cap.release()

    def _finger_states(self, hand_landmarks, hand_label):
        lm = hand_landmarks.landmark
        fingers = {
            "index": lm[8].y < lm[6].y,
            "middle": lm[12].y < lm[10].y,
            "ring": lm[16].y < lm[14].y,
            "pinky": lm[20].y < lm[18].y,
        }

        # Thumb direction depends on handedness.
        if hand_label == "Right":
            fingers["thumb"] = lm[4].x < lm[3].x
        else:
            fingers["thumb"] = lm[4].x > lm[3].x

        return fingers

    def _classify(self, fingers):
        thumb = fingers["thumb"]
        index = fingers["index"]
        middle = fingers["middle"]
        ring = fingers["ring"]
        pinky = fingers["pinky"]

        if all([thumb, index, middle, ring, pinky]):
            return "stop"
        if index and middle and not ring and not pinky and thumb:
            return "live long"
        if index and middle and not ring and not pinky:
            return "peace"
        if index and pinky and not middle and not ring:
            return "rock"
        if thumb and not any([index, middle, ring, pinky]):
            return "thumbs up"
        if thumb and pinky and not any([index, middle, ring]):
            return "call me"
        if not any([thumb, index, middle, ring, pinky]):
            return "fist"
        return None

    def get_gesture(self):
        ok, frame = self.cap.read()
        if not ok or frame is None:
            return None

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(frame_rgb)

        if not result.multi_hand_landmarks:
            return None

        hand_landmarks = result.multi_hand_landmarks[0]
        hand_label = "Right"
        if result.multi_handedness:
            hand_label = result.multi_handedness[0].classification[0].label

        fingers = self._finger_states(hand_landmarks, hand_label)
        return self._classify(fingers)

