# import the necessary packages
import numpy as np
import cv2
from fone_cam import *

def emptyfunc(p):
    pass

# https://debuggercafe.com/opencv-hog-hyperparameter-tuning-for-accurate-and-fast-person-detection/

# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
# hog.setSVMDetector(cv2.HOGDescriptor_getDaimlerPeopleDetector())

cv2.startWindowThread()

# open webcam video stream
# cap = cv2.VideoCapture(0)
# cap = VideoCapture("http://192.168.94.22:4747/video")
# cap = VideoCapture("video/video.avi")
# cap = cv2.VideoCapture("video/video.640.480.avi")
cap = cv2.VideoCapture("video/video_1440_1440_zoomed.mp4")

cv2.namedWindow('Parameters', cv2.WINDOW_AUTOSIZE)
cv2.resizeWindow('Parameters', 1000, 200)
cv2.createTrackbar('frame_nr', 'Parameters', 0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), emptyfunc)
cv2.createTrackbar('padding', 'Parameters', 1,16, emptyfunc)
cv2.setTrackbarPos('padding', 'Parameters', int(8))
cv2.createTrackbar('winstride', 'Parameters', 1, 16, emptyfunc)
cv2.setTrackbarPos('winstride', 'Parameters', int(8))

cv2.setTrackbarPos('frame_nr', 'Parameters', int(2700))


# # the output will be written to output.avi
# out = cv2.VideoWriter(
#     'output.avi',
#     cv2.VideoWriter_fourcc(*'MJPG'),
#     15.,
#     (640,480))


while(True):
    # Capture frame-by-frame
    frame_nr_params = cv2.getTrackbarPos('frame_nr', 'Parameters')
    frame_nr = cap.get(cv2.CAP_PROP_POS_FRAMES)
    if (frame_nr != frame_nr_params ):
        cap.set(1,frame_nr_params)
    ret, frame = cap.read()

    # resizing for faster detection
    shape=frame.shape[:2]
    ratio = shape[0]/shape[1]
    frame = cv2.resize(frame, (640, int(ratio * 640)))
    # using a greyscale picture, also for faster detection
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # detect people in the image
    # returns the bounding boxes for the detected objects
    # https://docs.opencv.org/4.x/d5/d33/structcv_1_1HOGDescriptor.html#a91e56a2c317392e50fbaa2f5dc78d30b
    wins = cv2.getTrackbarPos('winstride', 'Parameters')
    pad  = cv2.getTrackbarPos('padding', 'Parameters')
    # boxes, weights = hog.detectMultiScale(frame, winStride=(wins,wins), padding=(pad, pad) )
    boxes, weights = hog.detectMultiScale(frame, padding=(pad, pad))

    # boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])
    # for (xA, yA, xB, yB) in boxes:
    #     # display the detected boxes in the colour picture
    #     cv2.rectangle(frame, (xA, yA), (xB, yB),
    #                       (0, 255, 0), 2)

    for i, (x, y, w, h) in enumerate(boxes):
        if weights[i] < 0.13:
            continue
        elif weights[i] < 0.3 and weights[i] > 0.13:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        if weights[i] < 0.7 and weights[i] > 0.3:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 122, 255), 2)
        if weights[i] > 0.7:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    


    cv2.putText(frame, "{:.0f} {:.0f} ".format(frame_nr,len(boxes)), (10,10), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (255,255,255), thickness=2 )


    # Write the output video 
    # out.write(frame.astype('uint8'))
    # Display the resulting frame
    cv2.imshow('frame',frame)
    frame_nr = cap.get(cv2.CAP_PROP_POS_FRAMES)
    cv2.setTrackbarPos('frame_nr', 'Parameters', int(frame_nr))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
# cap.release()
# and release the output
# finally, close the window
cv2.destroyAllWindows()
cv2.waitKey(1)