# EyeBlink

This is a computer vision application that is capable of detecting and counting blinks in video streams using facial landmarks. To find if the user is blinking, it uses a metric called the eye aspect ratio (EAR) that involves a very simple calculation based on the ratio of distances between facial landmarks of the eyes. Here the server plays a video from YouTube and notes down the times at which the users blink (through their webcam) while watching the video and for further analysis. 

## Installation:

### Clone this project:
```
git clone https://github.com/aditi15ashley/EyeBlink.git
```
### Install the dependencies:

```
pip install -r requirements.txt
```

### Run the demo:
```
python server.py
```
## How it works:
The EAR measures the ratio of the horizontal eye landmarks to the vertical eye landmarks. The eye aspect ratio is approximately constant while the eye is open, but will rapidly fall to zero when a blink is taking place. If the EAR falls below a certian threshold, it is counted as a blink. The threshold currently set is 0.21 which can be changed to whatever seems appropriate. Note that the face should be as parallel to the screen as possible for accurate detection to take place. 

The raw code for this application is in `eyeblink.py` which simply does the job of detecting the eyeblinks and can be used for applications other than keeping track of when a user blinks while watching a YouTube video. 

To keep track of the eyeblinks in a saved webcam video feed from the disk instead of doing it in real-time, in `eyeblink.py`, uncomment line 59 and comment line 61 and run it like this:

```
$ python eyeblink.py \
	--video blink_detection_demo.mp4
``` 
