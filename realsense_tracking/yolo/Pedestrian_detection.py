import numpy as np
import cv2
import os
import imutils

# https://data-flair.training/blogs/pedestrian-detection-python-opencv/


NMS_THRESHOLD=0.3
MIN_CONFIDENCE=0.2

def emptyfunc(p):
    pass

def pedestrian_detection(image, model, layer_name, personidz=0):
	(H, W) = image.shape[:2]
	results = []


	blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
		swapRB=True, crop=False)
	model.setInput(blob)
	layerOutputs = model.forward(layer_name)

	boxes = []
	centroids = []
	confidences = []

	for output in layerOutputs:
		for detection in output:

			scores = detection[5:]
			classID = np.argmax(scores)
			confidence = scores[classID]

			if classID == personidz and confidence > MIN_CONFIDENCE:

				box = detection[0:4] * np.array([W, H, W, H])
				(centerX, centerY, width, height) = box.astype("int")

				x = int(centerX - (width / 2))
				y = int(centerY - (height / 2))

				boxes.append([x, y, int(width), int(height)])
				centroids.append((centerX, centerY))
				confidences.append(float(confidence))
	# apply non-maxima suppression to suppress weak, overlapping
	# bounding boxes
	idzs = cv2.dnn.NMSBoxes(boxes, confidences, MIN_CONFIDENCE, NMS_THRESHOLD)
	# ensure at least one detection exists
	if len(idzs) > 0:
		# loop over the indexes we are keeping
		for i in idzs.flatten():
			# extract the bounding box coordinates
			(x, y) = (boxes[i][0], boxes[i][1])
			(w, h) = (boxes[i][2], boxes[i][3])
			# update our results list to consist of the person
			# prediction probability, bounding box coordinates,
			# and the centroid
			res = (confidences[i], (x, y, x + w, y + h), centroids[i])
			results.append(res)
	# return the list of results
	return results



labelsPath = "coco.names"
LABELS = open(labelsPath).read().strip().split("\n")

weights_path = "yolov4-tiny.weights"
config_path = "yolov4-tiny.cfg"

model = cv2.dnn.readNetFromDarknet(config_path, weights_path)
'''
model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
'''

layer_name = model.getLayerNames()
layer_name = [layer_name[i - 1] for i in model.getUnconnectedOutLayers()]
# cap = cv2.VideoCapture("streetup.mp4")
cap = cv2.VideoCapture("../videos/video_1440_1440_zoomed.mp4")
# cap = cv2.VideoCapture("../videos/video_1440_1440.mp4")
# cap = cv2.VideoCapture("../videos/video.640.480.avi")

cv2.namedWindow('Parameters', cv2.WINDOW_AUTOSIZE)
cv2.resizeWindow('Parameters', 1000, 200)
cv2.createTrackbar('frame_nr', 'Parameters', 1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), emptyfunc)

while True:

	frame_nr_params = cv2.getTrackbarPos('frame_nr', 'Parameters')
	frame_nr = cap.get(cv2.CAP_PROP_POS_FRAMES)
	if (frame_nr != frame_nr_params ):
		cap.set(1,frame_nr_params)

	(grabbed, image) = cap.read()

	if not grabbed:
		break
	image = imutils.resize(image, width=700)
	results = pedestrian_detection(image, model, layer_name,
		personidz=LABELS.index("person"))

	for res in results:
		cv2.rectangle(image, (res[1][0],res[1][1]), (res[1][2],res[1][3]), (0, 255, 0), 2)

	cv2.imshow("Detection",image)
	frame_nr = cap.get(cv2.CAP_PROP_POS_FRAMES)
	cv2.setTrackbarPos('frame_nr', 'Parameters', int(frame_nr))

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()


