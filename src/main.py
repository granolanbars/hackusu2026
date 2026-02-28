import cv2
import time
from detection import *
from tweet import send_tweet
from coding import coding



def main():
    print("Hello Programmer!")

    engine = GestureEngine()
    cap = cv2.VideoCapture(0)
    while True:
        

        ret, frame = cap.read()
        print("What would you like to do today?")
        print("1. Send a tweet: (Point upwards)") # find a hand signal
        print("2. Write some Code: (Fist)") # find a hand signal
        print("3. Go to sleep: (ILY)") # find a hand signal

        nav = engine.detect(frame, "navigation")

        match nav:
            case "TWEET":
                print("Hold up any combination of hand signals to pick a meme:")
                image = engine.detect(frame, "tweet_select")
                confirmed = engine.detect(frame, "confirm")
                if confirmed:
                    #call tweet function with argument image
                    send_tweet()
                else:
                    continue
            case "CODE":
                #run coding function
                coding()
            
            case "SLEEP":
                print("Going to Sleep, Goodbye!")
                for i in range(3):
                    print(f'Going to sleep in {3-i}')
                    time.sleep(1)
                break





        







if __name__ == "__main__":
    main()
