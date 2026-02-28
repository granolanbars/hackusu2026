import time
import cv2
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
    def __init__(self, model_path="src\\task_files\\gesture_recognizer.task"):
        base = python.BaseOptions(model_asset_path=model_path)
        options = vision.GestureRecognizerOptions(
            base_options=base,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=2,
        )

        
        self.cap = cv2.VideoCapture(0)

        self.debouncers = {
    "navigation": GestureDebouncer(hold_ms=750, none_reset_ms=250),
    "tweet_select": GestureDebouncer(hold_ms=750, none_reset_ms=250),
    "confirm": GestureDebouncer(hold_ms=750, none_reset_ms=250)
        }
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

        ###DEBUG###
        #print("DEBUG nav ruleset:", left, right)

        if left == "Pointing_Up" or right == "Pointing_Up":
            return "TWEET"
        if left == "Closed_Fist" or right == "Closed_Fist":
            return "CODE"
        if left == "ILoveYou" or right == "ILoveYou":
            return "SLEEP"

        return None

    def ruleset_tweet_select(self, g):
        left, right = g["left"], g["right"]
        #print("DEBUG nav ruleset:", left, right)

        if left == "None" or right == "None":
            return None

        li = GESTURES.index(left)
        ri = GESTURES.index(right)

        return li * 7 + ri  # 0–48
    
    def rulset_code(self, g):
        left, right, literal = g["left"], g["right"], g["dist"]

        if left is n

    def ruleset_confirm(self, g):
        left, right = g["left"], g["right"],
        
        print("DEBUG Confirm ruleset:", left, right)

        if left == "Thumb_Down" and right == "Thumb_Down":
            return False

        if left == "Thumb_Up" and right == "Thumb_Up":
            return True

        return None


    #called by main
    def detect(self, mode):
        debouncer = self.debouncers[mode]

        match mode:
            case "tweet_select":
                print("Hold up any combination of two signs" \
                "\nto choose a new tweet")
            case "confirm":
                print("Two thumbs UP to CONFIRM")
                print("Two thumbs DOWN to CANCEL")
            case "code":
                print("Welcome to Hand++")


        while True:
            ret, frame = self.cap.read()

            cv2.imshow("Camera", frame)
            cv2.waitKey(1)

            if not ret:
                continue

            gestures = self.detect_gestures(frame)

            if mode == "navigation":
                raw = self.ruleset_navigation(gestures)
            elif mode == "tweet_select":
                raw = self.ruleset_tweet_select(gestures)
            elif mode == "confirm":
                raw = self.ruleset_confirm(gestures)
            elif mode == "code":
                raw = self.ruleset_code(gestures)
            else:
                raise ValueError(f"Unknown mode: {mode}")
            
            #debug
            #print("Raw:", raw)

            stable = debouncer.update(raw, gestures["left"], gestures["right"])

            if stable is not None:
                return stable
    


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
