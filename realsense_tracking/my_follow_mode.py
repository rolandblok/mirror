
from my_utils import *

FACE_RANGE_M = 0.05  # same face distance

class MyCameraToMirror:
    def __init__(self):
        self.active_face_points = []
        pass

    def get_mirror_face(self, face_1, face_2):

    

    def updateFacePoints(self, face_points):
        ddists2 = []
        for fp in face_points:
            dists2 = []
            for afp in self.active_face_points:
                dists2.append(distance_sqr(fp,afp))
            ddists2.append(dists2)

        if len(face_points) > len(self.active_face_points):
            pass
        elif len(face_points) < len(self.active_face_points):
            pass
        else:
            pass
        
    
