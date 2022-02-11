
# https://chev.me/arucogen/

import cv2.aruco
import numpy as np


class MyAruco:
    def __init__(self):
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters_create()

    def detect_and_draw(self, detect_image):
        # https://automaticaddison.com/how-to-detect-aruco-markers-using-opencv-and-python/
        (cornerss, ids, rejected) = cv2.aruco.detectMarkers(detect_image, self.aruco_dict, parameters=self.aruco_params)
        if (len(cornerss) > 0):
            ids = ids.flatten()
            for (corners, id) in zip(cornerss, ids):
                if (id == 17):
                    corners = corners.reshape((4, 2))
                    (top_left, top_right, bottom_right, bottom_left) = corners
            
                    print("detect aruco {}".format(id))
                    print("detect aruco {}".format(corners))
                    # Convert the (x,y) coordinate pairs to integers
                    top_right = (int(top_right[0]), int(top_right[1]))
                    bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
                    bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
                    top_left = (int(top_left[0]), int(top_left[1]))

                    center_x = top_left[0] + (top_right[0] - top_left[0])/2
                    center_y = top_left[1] + (top_right[1] - top_left[1])/2
                        
                    # Draw the bounding box of the ArUco detection
                    cv2.line(detect_image, top_left, top_right, (255, 255, 0), 2)
                    cv2.line(detect_image, top_right, bottom_right, (255, 255, 0), 2)
                    cv2.line(detect_image, bottom_right, bottom_left, (255, 255, 0), 2)
                    cv2.line(detect_image, bottom_left, top_left, (255, 255, 0), 2)

            return (center_x, center_y)


def detect_hexagon(image):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)  #Convert to grayscale image
    # edged = cv2.Canny(gray, 170, 255)            #Determine edges of objects in an image
    ret,thresh = cv2.threshold(gray,240,255,cv2.THRESH_BINARY)  
    # (contours,_) = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE) #Find contours in an image
    contours,_ = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)


    for cnt in contours:
        approx_corners = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt,True),True) # Both true for closed figurs
        if len(approx_corners) == 6: 
            cv2.drawContours(image,[approx_corners],-1,(0,255,0),1)
        # cv2.putText(image,shape,(cx,cy),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),2)  #Putting name of polygon along with the shape 
