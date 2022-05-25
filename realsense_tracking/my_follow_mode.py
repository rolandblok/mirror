
from my_utils import *
import time

FACE_RANGE_M = 0.1  # same face distance
FACE_RANGE2_M2 = FACE_RANGE_M*FACE_RANGE_M  # same face distance quadratic
FACE_MAX_AGE_S = 2  # maximum age for a face: after 2 seconds no detect : remove

def fp_2str(fp):
    return("{:.2f},{:.2f},{:.2f}".format(fp[0],fp[1],fp[2]))


class MyFollowMode:
    def __init__(self):
        self.active_face_points = MyActiveFacepoints()

    def updateFacePoints(self, new_face_points):
        self.active_face_points.update_fps(new_face_points)

        
class MyActiveFacepoints:
    def __init__(self):
        self.afps = []

    def update_fps(self, new_fps):
        # print(f" new_fps {len(new_fps)}")
        for fp in new_fps:
            closest_afp_i, dist2_m2 = self.closest(fp)
            if (closest_afp_i > -1) and (dist2_m2 < FACE_RANGE2_M2) :
                self.afps[closest_afp_i].update_fp(fp)
            else :
                print("new fp with dist2_m2 {:.2f} {}".format(dist2_m2, fp_2str(fp)))
                self.afps.append( MyActiveFacepoint(fp) )
        for afp in self.afps:
            if afp.age_s() > FACE_MAX_AGE_S:
                self.afps.remove(afp)

    def closest(self, fp):
        min_dist2_m2 = 100000
        min_index = -1
        for index, cur_afp in enumerate(self.afps):
            dist2_m2 = cur_afp.distance2(fp)
            # print(f"{dist2_m2} {fp} {cur_afp.fp}")
            if (dist2_m2 < min_dist2_m2):
                min_dist2_m2 = dist2_m2
                min_index = index
        return min_index, min_dist2_m2

    
class MyActiveFacepoint:
    def __init__(self, fp):
        self.id = unique_id()
        self.fp = fp
        self.last_seen_time_s = time.perf_counter()
    
    def update_fp(self, fp):
        self.fp = fp
        self.last_seen_time_s = time.perf_counter()

    def age_s(self):
        return time.perf_counter() - self.last_seen_time_s

    def distance2(self, fp):
        return  distance_sqr(fp, self.fp)

    def toString(self):
        return(f"{self.id} {self.last_seen_time_s}")
