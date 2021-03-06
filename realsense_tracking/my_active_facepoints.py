
from collections import namedtuple
from my_utils import *
import time

FACE_RANGE_M = 40  # same face distance
FACE_RANGE2_M2 = FACE_RANGE_M*FACE_RANGE_M  # same face distance quadratic
FACE_MAX_UNSEEN_TIME_S = 1.5  # maximum unseen time for a face: after x seconds no detect : remove
FACE_MIN_AGE_S = 0.7 # minimum age for a face to become active

def fp_2str(fp):
    return ",".join(f"{e:.3f}" for e in fp)
#    return("{:.2f},{:.2f},{:.2f}".format(fp[0],fp[1],fp[2]))

PixAnd3D = namedtuple("PixAnd3D",["pixels", "ThreeD"])
        
class MyActiveFacepoints:
    def __init__(self):
        self.afps = []

    def __getitem__(self, index):
        return self.afps[index]

    def updateFacePoints(self, new_fps):
        # print(f" new_fps {len(new_fps)}")
        for fp in new_fps:
            closest_afp_i, dist2_m2 = self.closest(fp)
            if (closest_afp_i > -1) and (dist2_m2 < FACE_RANGE2_M2) :
                self.afps[closest_afp_i].update_fp(fp)
            else :
                # print("\n".join(f"{fp_2str(s.fp_pix)}" for s in self.afps))
                # print("new fp with dist2_m2 {:.2f} {}".format(dist2_m2, fp_2str(fp.pixels)))
                self.afps.append( MyActiveFacepoint(fp) )
        for afp in self.afps:
            if afp.died:
                self.afps.remove(afp)

    def closest(self, fp):
        if not self.afps:
            return -1, 0
        distances = [cur.distance2(fp) for cur in self.afps]
        return min(enumerate(distances), key=lambda t:t[1])

    def get_active_ids(self):
        return {s.id for s in self.afps if s.active}

    def get_active_afps(self):
        return {afp for afp in self.afps if afp.active}


    def get_3d_location_by_id(self, id):
        for afp in self.afps:
            if afp.id == id:
                return afp.fp_3d
        raise Exception(f"Could not find active facepoint for id {id}")

    def has_id(self, id):
        for afp in self.afps:
            if afp.id == id:
                return True
        return False
        

class MyActiveFacepoint:
    def __init__(self, fp:PixAnd3D):
        self.id = unique_id()
        self._ma_fp_pix = MyMovingAverageVector(2, lambda : MyMovingAverageLowPass(8,5,10))
        self._ma_fp_3d  = MyMovingAverageVector(3, lambda : MyMovingAverageLowPass(8,0.1,0.2))
        self.update_fp(fp)
        self.born_time_s = time.perf_counter()
    
    @property
    def fp_pix(self):
        return self._ma_fp_pix.get_current()

    @property
    def fp_3d(self):
        return self._ma_fp_3d.get_current()

    def update_fp(self, fp:PixAnd3D):
        self._fp = fp
        self._ma_fp_pix.add_point(fp.pixels)
        self._ma_fp_3d.add_point(fp.ThreeD)
        self.last_seen_time_s = time.perf_counter()

    @property
    def active(self):
        return (time.perf_counter() - self.born_time_s) > FACE_MIN_AGE_S

    @property
    def died(self):
        return (time.perf_counter() - self.last_seen_time_s) > FACE_MAX_UNSEEN_TIME_S

    def distance2(self, fp):
        return  distance_sqr(fp.pixels, self.fp_pix)

    def toString(self):
        return(f"{self.id} {fp_2str(self.fp_pix)}[p] {fp_2str(self.fp_3d)}[m] ")
