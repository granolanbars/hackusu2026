

import os
os.environ["GLOG_minloglevel"] = "3"        # hide INFO, WARNING, ERROR
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"    # hide TensorFlow Lite logs
os.environ["MEDIAPIPE_DISABLE_GPU"] = "1"   # optional, stops GPU delegate spam

import ctypes
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
import cv2
import time
from detection import *
from coding import code_edit
from tweet import send_tweet
from colors import c, RED, GREEN, YELLOW, CYAN, MAGENTA


def main():
    print(c("Hello Programmer!", CYAN))

    engine = GestureEngine()

    while True:

        print(c("What would you like to do today?", CYAN))
        #print(c("1. Send a tweet: (Point upwards)", YELLOW))
        print(c("1. Write some Code: (Fist)", YELLOW))
        print(c("2. Go to sleep: (ILY)", YELLOW))

        nav = engine.detect("navigation")

        match nav:

            # case "TWEET":
            #     print(c("Hold up any combination of hand signals to pick a meme:", MAGENTA))
            #     image = engine.detect("tweet_select")
            #     confirmed = engine.detect("confirm")
            #     if confirmed:
            #         send_tweet("somewhere")
            #     else:
            #         continue

            case "CODE":
                print(c("Entering Hand++ coding mode...", CYAN))
                code_edit(engine)
                continue

            case "SLEEP":
                print(c("Going to Sleep, Goodbye!", RED))
                for i in range(3):
                    print(c(f"Going to sleep in {3-i}", RED))
                    time.sleep(1)
                break


if __name__ == "__main__":
    main()