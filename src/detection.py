import os
os.environ["GLOG_minloglevel"] = "2"   # hide INFO and WARNING logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["MEDIAPIPE_DISABLE_GPU"] = "1"
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
        self.timestamp = 0


        cv2.namedWindow("Resized_Window", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Resized_Window", 960, 540)

        self.cap = cv2.VideoCapture(0)
    
        
        self.smoothed_dist = 0.0
        self.alpha = 0.25

        hold_ms = 400
        none_reset_ms = 200

        self.debouncers = {
    "navigation": GestureDebouncer(hold_ms, none_reset_ms),
    "tweet_select": GestureDebouncer(hold_ms, none_reset_ms),
    "confirm": GestureDebouncer(hold_ms, none_reset_ms),
    "code": GestureDebouncer(hold_ms, none_reset_ms)
        }
        self.detector = vision.GestureRecognizer.create_from_options(options)

    def process_distance(self, raw_dist, frame_height):
        if raw_dist is None:
            return None
        normalized = raw_dist / frame_height
        scaled = normalized * 200
        self.smoothed_dist = self.alpha * scaled + (1 - self.alpha) * self.smoothed_dist
        literal = round(self.smoothed_dist / 10) * 10
        return int(literal)

   
    def detect_gestures(self, frame):
        h, w, _ = frame.shape

        # --- Dynamic drawing parameters ---
        th = max(2, int(h * 0.004))        # line thickness
        fs = h * 0.0015                    # font scale
        pad = int(h * 0.02)                # text padding

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = self.detector.recognize(mp_image)

        left = "None"
        right = "None"
        left_lm = None
        right_lm = None
        right_dist = None

        # --- PASS 1: detect hands, draw boxes, store landmarks ---
        if result.gestures:
            for i, gesture_list in enumerate(result.gestures):
                gesture = gesture_list[0].category_name
                hand_label = result.handedness[i][0].category_name
                landmarks = result.hand_landmarks[i]

                # Bounding box
                xs = [lm.x * w for lm in landmarks]
                ys = [lm.y * h for lm in landmarks]
                x_min, x_max = int(min(xs)), int(max(xs))
                y_min, y_max = int(min(ys)), int(max(ys))

                # Draw rectangle
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max),
                            (0, 255, 0), th)

                # Label
                label = f"{hand_label}: {gesture}"
                cv2.putText(frame, label,
                            (x_min, max(0, y_min - pad)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            fs, (0, 255, 0), th)

                # Assign left/right
                if hand_label == "Left":
                    left = gesture
                    left_lm = landmarks
                else:
                    right = gesture
                    right_lm = landmarks

        # --- PASS 2: draw thumb-to-thumb line if both hands exist ---
        if left_lm is not None and right_lm is not None:
            left_thumb = left_lm[4]   # thumb tip
            right_thumb = right_lm[4]

            x1, y1 = int(left_thumb.x * w), int(left_thumb.y * h)
            x2, y2 = int(right_thumb.x * w), int(right_thumb.y * h)

            # Draw the line between thumbs
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), th)

            # Optional: compute distance between thumbs
            raw_dist = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            right_dist = self.process_distance(raw_dist, h)

            # Distance label
            label_x = x1 if y1 > y2 else x2
            label_y = y1 if y1 > y2 else y2

            cv2.putText(frame,
                        f"value: {right_dist}",
                        (label_x, max(0, label_y - pad)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        fs, (255, 0, 0), th)

        return {
            "left": left,
            "right": right,
            "left_landmarks": left_lm,
            "right_landmarks": right_lm,
            "dist": right_dist,
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
    
    def ruleset_code(self, g):
        left, right, literal = g["left"], g["right"], g["dist"]

        if left == "None" or right == "None":
            #print("None")
            return None
        elif left == "Thumb_Down" and right == "Thumb_Down":
            #print("CANCEL")
            return ("CANCEL", left, right, None)
        elif left == "Thumb_Up" and right == "Thumb_Up":
            #print("RUN")
            return ("RUN", left, right, None)
        else:
            #print("LINE READ")
            return ("LINE", left, right, literal)


    def ruleset_confirm(self, g):
        left, right = g["left"], g["right"],
        
        #print("DEBUG Confirm ruleset:", left, right)

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
                print(">>>",end="")


        while True:
            ret, frame = self.cap.read()
            gestures = self.detect_gestures(frame)   # detect + draw on THIS frame
            cv2.imshow("Resized_Window", frame)       # show AFTER drawing
            cv2.waitKey(1)

           

            

            if not ret:
                continue


            if mode == "navigation":
                raw = self.ruleset_navigation(gestures)
            elif mode == "tweet_select":
                raw = self.ruleset_tweet_select(gestures)
            elif mode == "confirm":
                raw = self.ruleset_confirm(gestures)
            elif mode == "code":
                raw = self.ruleset_code(gestures)
                stable = debouncer.update(raw, gestures["left"], gestures["right"], gestures["dist"])
                if stable is not None:
                    return stable
                continue
            else:
                raise ValueError(f"Unknown mode: {mode}")
            
            #debug
            #print("Raw:", raw)

            stable = debouncer.update(raw, gestures["left"], gestures["right"], None)

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

    def update(self, value, left, right, literal=None):
        now = time.time()

        # -----------------------------------------------------
        # 1. None-reset logic (must hold None for 250 ms)
        # -----------------------------------------------------
        if value is None:
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
