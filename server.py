from flask import Flask, render_template, Response
from camera import VideoCamera

from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
from datetime import datetime

#from signal import signal, SIGPIPE, SIG_DFL
#signal(SIGPIPE,SIG_DFL)

app = Flask(__name__)

curr_time = datetime.now()
formatted_time = curr_time.strftime('%H:%M:%S')
filepath = 'times' + formatted_time + '.txt'

def eye_aspect_ratio(eye):
	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])
 
	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])
 
	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)
 
	# return the eye aspect ratio
	return ear

global camera 
camera = VideoCamera()


@app.route('/')
def index():
	return render_template('index.html')

def gen(camera):

	EYE_AR_THRESH = 0.21

	EYE_AR_CONSEC_FRAMES = 3

	# initialize the frame counters and the total number of blinks
	COUNTER = 0
	TOTAL = 0

	# initialize dlib's face detector (HOG-based) and then create
	# the facial landmark predictor
	print("[INFO] loading facial landmark predictor...")
	detector = dlib.get_frontal_face_detector()
	#predictor = dlib.shape_predictor(args["shape_predictor"])
	predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

	# grab the indexes of the facial landmarks for the left and
	# right eye, respectively
	(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
	(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

	# start the video stream thread
	print("[INFO] starting video stream thread...")

	while True:
		frame = camera.get_frame()
		if frame is not None:
			##code added
			frame = imutils.resize(frame, width=500)
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

			# detect faces in the grayscale frame
			rects = detector(gray, 0)

			# loop over the face detections
			for rect in rects:
				# determine the facial landmarks for the face region, then
				# convert the facial landmark (x, y)-coordinates to a NumPy
				# array
				shape = predictor(gray, rect)
				shape = face_utils.shape_to_np(shape)
		 
				# extract the left and right eye coordinates, then use the
				# coordinates to compute the eye aspect ratio for both eyes
				leftEye = shape[lStart:lEnd]
				rightEye = shape[rStart:rEnd]
				leftEAR = eye_aspect_ratio(leftEye)
				rightEAR = eye_aspect_ratio(rightEye)
		 
				# average the eye aspect ratio together for both eyes
				ear = (leftEAR + rightEAR) / 2.0

				# compute the convex hull for the left and right eye, then
				# visualize each of the eyes
				leftEyeHull = cv2.convexHull(leftEye)
				rightEyeHull = cv2.convexHull(rightEye)
				cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
				cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

				# check to see if the eye aspect ratio is below the blink
				# threshold, and if so, increment the blink frame counter
				if ear < EYE_AR_THRESH:
					COUNTER += 1
		 
				# otherwise, the eye aspect ratio is not below the blink
				# threshold
				else:
					# if the eyes were closed for a sufficient number of
					# then increment the total number of blinks
					if COUNTER >= EYE_AR_CONSEC_FRAMES:
						#note down times in a txt file
					
						with open(filepath, 'a') as fh:
							curr_time = datetime.now()
							formatted_time = curr_time.strftime('%H:%M:%S.%f')
							fh.write(formatted_time+ '\n')

						TOTAL += 1
		 
					# reset the eye frame counter
					COUNTER = 0

					# draw the total number of blinks on the frame along with
				# the computed eye aspect ratio for the frame
				cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
					cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
				cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
					cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
		 

			ret, jpeg = cv2.imencode('.jpg', frame)
			frame = jpeg.tobytes()
			# show the frame
			#cv2.imshow("Frame", frame)
			yield (b'--frame\r\n'
				   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
			#yield(frame)		   
			#key = cv2.waitKey(1) & 0xFF
			#print (type(frame))l
			# if the `q` key was pressed, break from the loop
			'''if key == ord("q"):
				break'''
	 
	# do a bit of cleanup
	cv2.destroyAllWindows()
	camera.__del__()
	

def stop(camera):
	camera.__del__()

		
@app.route('/video_feed')
def video_feed():
	return Response(gen(camera),
					mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/vstop')
def vstop():
	stop(camera)
	return 'finish'

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
