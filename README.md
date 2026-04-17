# Hand++

Hand++ is a gesture controlled implementation of the esoteric programming language: "brainf*ck".
It uses googles hand recognition model, OpenCV, and MediaPipe to run gesture recognition.
The commands are similar to its parent language, with the added functionality of setting memory values by the distance between thumbs in pixels instead of using hundreds of + signs 

The commands are as follows:

| Instruction            | Left Hand | Right Hand  |
|------------------------|-----------|-------------|
| Increment Memory Value | Fist      | Thumbs Up   |
| Decrement Memory Value | Fist      | Thumbs Down |
| Increment Pointer      | Fist      | Palm        |
| Decrement Pointer      | Fist      | Fist        |
| Get Input              | Fist      | Victory     |
| Output Character       | Fist      | Point Up    |
| Start Loop             | Palm      | Palm        |
| End Loop               | Palm      | Fist        |
| Set Memory Value       | ILY       | ILY         |
| Get Memory Value       | ILY       | Point Up    |
| Run Program            | Thumb Up  | Thumb Up    |


Tips and Tricks:  
-the victory and point up work more often when your thumb is in line with your middle or ring finger instead of in front  
-the set memory value command is easier to use if you measure the value out using sideways thumbs up and then lift your index and pointer fingers into ILY to confirm it at the value you want.   
-If your camera is not working, you can change which camera OpenCV uses in the detection.py file by changing the argument from 0 to 1, 2 etc. in self.cap = cv2.VideoCapture(0) on line 37  

  
Coming Soon:  

Tweet functionality For Fun!!!  



