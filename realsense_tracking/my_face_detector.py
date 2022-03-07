from enum import Enum
import dlib
import mediapipe as mp
import cv2
from my_utils import *



class DetectorType(Enum):
    FACE_DETECTION_DISABLE = 0
    FACE_DETECTION_MEDIAPIPE = 1
    FACE_DETECTION_HAAR = 2
    FACE_DETECTION_DLIB = 3


class MyFaceDetector:
    def __init__(self,detector_type):
        self.detector_type = detector_type

        if (self.detector_type == DetectorType.FACE_DETECTION_MEDIAPIPE):
            self.mp_face_detection = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.7)
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_face_keypoints = mp.solutions.face_detection.FaceKeyPoint

        elif (self.detector_type == DetectorType.FACE_DETECTION_DLIB):
            self.dlib_detector = dlib.get_frontal_face_detector()    

        elif (self.detector_type == DetectorType.FACE_DETECTION_HAAR):
            self.haar_cascade = cv2.CascadeClassifier('xml/haarcascade_frontalface_default.xml')


    def close(self):
        if self.detector_type == DetectorType.FACE_DETECTION_MEDIAPIPE:
            self.mp_face_detection.close()


    def detect(self, color_image, color_image_draw):
        face_eyes = []
        if (self.detector_type == DetectorType.FACE_DETECTION_DISABLE):
            return face_eyes

        elif (self.detector_type == DetectorType.FACE_DETECTION_HAAR):
            gray_image = cv2.cvtColor( color_image, cv2.COLOR_BGR2GRAY )
            faces_rect = self.haar_cascade.detectMultiScale( gray_image, scaleFactor=1.1, minNeighbors=9)
            for (x, y, w, h) in faces_rect:
                xm = math.floor(x + w/2)
                ym = math.floor(y + h/2)
                face_eyes.append((xm,ym))
                cv2.rectangle(color_image_draw, (x, y), (x+w, y+h), (0, 255, 0), thickness=2)
                
        elif (self.detector_type == DetectorType.FACE_DETECTION_DLIB):
            rgb_image = cv2.cvtColor( color_image, cv2.COLOR_BGR2RGB )
            dets = self.dlib_detector(rgb_image, 1)
            for i, d in enumerate(dets):
                xm = math.floor((d.left() + d.right())/2)
                ym = math.floor((d.top() + d.bottom())/2)
                face_eyes.append((xm,ym))
                cv2.rectangle(color_image_draw, (d.left(), d.top() ), (d.right(), d.bottom()), (0, 255, 0), thickness=2)

        elif (self.detector_type == DetectorType.FACE_DETECTION_MEDIAPIPE):
            color_colormap_dim = color_image.shape
            image_RGB = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            faces = self.mp_face_detection.process(image_RGB)
            if faces.detections:
                for face in faces.detections:
                    self.mp_drawing.draw_detection(color_image_draw, face)
                    r_eye = (mp.solutions.face_detection.get_key_point(face, self.mp_face_keypoints.RIGHT_EYE))
                    r_eye = (r_eye.x*color_colormap_dim[1], r_eye.y*color_colormap_dim[0])
                    l_eye = (mp.solutions.face_detection.get_key_point(face, self.mp_face_keypoints.LEFT_EYE))
                    l_eye = (l_eye.x*color_colormap_dim[1], l_eye.y*color_colormap_dim[0])
                    xm = math.floor((r_eye[X] + l_eye[X])/2)
                    ym = math.floor((r_eye[Y] + l_eye[Y])/2)
                    face_eyes.append((xm,ym))

                    cv2.circle(color_image_draw, tuple2int(r_eye), 5, (255,255,0), 2)
                    cv2.circle(color_image_draw, tuple2int(l_eye), 5, (255,255,0), 2)
                    
                    
        return face_eyes

