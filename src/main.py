import cv2
import time
from detection import *
from tweet import send_tweet
from coding import coding_interpreter, welcome_message




def main():
    print("Hello Programmer!")

    engine = GestureEngine()


    while True:

        print("What would you like to do today?")
        print("1. Send a tweet: (Point upwards)") 
        print("2. Write some Code: (Fist)") 
        print("3. Go to sleep: (ILY)") 

        nav = engine.detect("navigation")

        match nav:
            case "TWEET":
                print("Hold up any combination of hand signals to pick a meme:")
                image = engine.detect("tweet_select")
                confirmed = engine.detect("confirm")
                if confirmed:
                    #call tweet function with argument image
                    send_tweet("somewhere")
                else:
                    continue
            case "CODE":
                #run coding function
                print(welcome_message)
                code = engine.detect("code")
            
            case "SLEEP":
                print("Going to Sleep, Goodbye!")
                for i in range(3):
                    print(f'Going to sleep in {3-i}')
                    time.sleep(1)
                break







if __name__ == "__main__":
    main()
