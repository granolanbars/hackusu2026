import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

GESTURES = [
    "None",
    "Closed_Fist",
    "Open_Palm",
    "Pointing_Up",
    "Thumb_Down",
    "Thumb_Up",
    "Victory",
    "ILoveYou"
]

class GestureEngine:
    def __init__(self, model_path="src/gesture_recognizer.task"):
        base = python.BaseOptions(model_asset_path=model_path)
        options = vision.GestureRecognizerOptions(
            base_options=base,
            running_mode=vision.RunningMode.IMAGE,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_hand_tracking_confidence=0.6,
        )
        self.detector = vision.GestureRecognizer.create_from_options(options)

    # ---------------------------------------------------------
    # Raw detection (runs MediaPipe once per frame)
    # ---------------------------------------------------------
    def detect_gestures(self, frame):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = self.detector.recognize(mp_image)

        left = "None"
        right = "None"
        left_lm = None
        right_lm = None

        if result.gestures:
            for i, gesture_list in enumerate(result.gestures):
                gesture = gesture_list[0].category_name
                hand_label = result.handedness[i][0].category_name
                landmarks = result.hand_landmarks[i]

                if hand_label == "Left":
                    left = gesture
                    left_lm = landmarks
                else:
                    right = gesture
                    right_lm = landmarks

        return {
            "left": left,
            "right": right,
            "left_landmarks": left_lm,
            "right_landmarks": right_lm,
            "raw": result
        }

    # ---------------------------------------------------------
    # Rulesets
    # ---------------------------------------------------------

    def ruleset_navigation(self, g):
        left, right = g["left"], g["right"]

        if left == "Pointing_Up" or right == "Pointing_Up":
            return "TWEET"
        if left == "Closed_Fist" or right == "Closed_Fist":
            return "CODE"
        if left == "ILoveYou" or right == "ILoveYou":
            return "SLEEP"

        return None

    def ruleset_tweet_select(self, g):
        left, right = g["left"], g["right"]

        if left == "None" or right == "None":
            return None

        li = GESTURES.index(left) - 1
        ri = GESTURES.index(right) - 1

        return li * 7 + ri  # 0–48

    def ruleset_confirm(self, g):
        left, right = g["left"], g["right"]

        if left == "Thumb_Down" and right == "Thumb_Down":
            return False

        if left == "Thumb_Up" and right == "Thumb_Up":
            return True

        return None


    #called by main
    def detect(self, frame, mode):
        gestures = self.detect_gestures(frame)

        if mode == "navigation":
            return self.ruleset_navigation(gestures)

        if mode == "tweet_select":
            return self.ruleset_tweet_select(gestures)

        if mode == "confirm":
            return self.ruleset_confirm(gestures)

        raise ValueError(f"Unknown mode: {mode}")
    


class GestureDebouncer:
    def __init__(self, hold_ms=750, none_reset_ms=250):
        self.hold_ms = hold_ms / 1000.0
        self.none_reset_ms = none_reset_ms / 1000.0

        self.armed = False
        self.none_start = None

        self.start_time = None
        self.last_value = None

    def update(self, value, left, right):
        now = time.time()

        # -----------------------------------------------------
        # 1. None-reset logic (must hold None for 250 ms)
        # -----------------------------------------------------
        if left == "None" and right == "None":
            if self.none_start is None:
                self.none_start = now
            elif now - self.none_start >= self.none_reset_ms:
                # Fully reset and arm the debouncer
                self.armed = True
                self.start_time = None
                self.last_value = None
            return None
        else:
            # Hands not None → stop None timer
            self.none_start = None

        # -----------------------------------------------------
        # 2. If not armed, ignore gestures
        # -----------------------------------------------------
        if not self.armed:
            return None

        # -----------------------------------------------------
        # 3. Gesture stability logic (must hold gesture for 750 ms)
        # -----------------------------------------------------
        if value != self.last_value:
            self.last_value = value
            self.start_time = now
            return None

        if value is None:
            return None

        if now - self.start_time >= self.hold_ms:
            # Fire once, then disarm until next None-reset
            self.armed = False
            return value

        return None
