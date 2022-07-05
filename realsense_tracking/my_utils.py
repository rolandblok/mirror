import statistics
import numpy as np
import math
import unittest
import time


STREAM_WIDTH=640
STREAM_HEIGHT=480
RS_REFRESH = 30
# STREAM_WIDTH=1280
# STREAM_HEIGHT=720
# RS_REFRESH = 6


# CONSTANTS
X = 0   # array indices for cartesian dimensions
Y = 1
Z = 2
A = 0   # array indices for mirror angles
B = 1
NO_ANGLES_PER_MIRROR = 2
NO_MIRRORS = 8

REL_MIR_POS={}
# REL_MIR_POS[0] = (11/16,  4/6)
# REL_MIR_POS[1] = (11/16,  2/6)
# REL_MIR_POS[2] = ( 8/16,  1/6)
# REL_MIR_POS[3] = ( 5/16,  2/6)
# REL_MIR_POS[4] = ( 5/16,  4/6)
# REL_MIR_POS[5] = ( 8/16,  5/6)
# REL_MIR_POS[6] = (14/16,  3/6)
# REL_MIR_POS[7] = ( 2/16,  3/6)

REL_MIR_POS[4] = (11/16,  4/6)
REL_MIR_POS[3] = (11/16,  2/6)
REL_MIR_POS[2] = ( 8/16,  1/6)
REL_MIR_POS[1] = ( 5/16,  2/6)
REL_MIR_POS[0] = ( 5/16,  4/6)
REL_MIR_POS[5] = ( 8/16,  5/6)
REL_MIR_POS[7] = (14/16,  3/6)
REL_MIR_POS[6] = ( 2/16,  3/6)

def PIX_MIR_POS(W,H, m):
    return tuple2int((REL_MIR_POS[m][X]*W , REL_MIR_POS[m][Y]*H))

def closest_mirror_pix(W, H, pix_pos): # W,H : screen width, height; pix_pos : pixel pos (x,y)
    distances = [distance_sqr(PIX_MIR_POS(W,H,m), pix_pos) for m in range(NO_MIRRORS)]
    return min(enumerate(distances), key=lambda t:t[1])

def cv_draw_hex(cv2, image, center, radius_x, radius_y, color, thickness):
    cv2.line(image, tuple2int((center[X] + radius_x,   center[Y]            )), tuple2int((center[X] + radius_x/2, center[Y] - radius_y)) , color, thickness )
    cv2.line(image, tuple2int((center[X] + radius_x/2, center[Y] - radius_y )), tuple2int((center[X] - radius_x/2, center[Y] - radius_y)) , color, thickness )
    cv2.line(image, tuple2int((center[X] - radius_x/2, center[Y] - radius_y )), tuple2int((center[X] - radius_x,   center[Y]           )) , color, thickness )
    cv2.line(image, tuple2int((center[X] - radius_x,   center[Y]            )), tuple2int((center[X] - radius_x/2, center[Y] + radius_y)) , color, thickness )
    cv2.line(image, tuple2int((center[X] - radius_x/2, center[Y] + radius_y )), tuple2int((center[X] + radius_x/2, center[Y] + radius_y)) , color, thickness )
    cv2.line(image, tuple2int((center[X] + radius_x/2, center[Y] + radius_y )), tuple2int((center[X] + radius_x,   center[Y]           )) , color, thickness )

def cv_draw_mirrors(cv2, image, W, H):
    color      = (255, 255, 255)
    thickness  = 1
    radius_x     = W *2/16
    radius_y     = H *1/8
    for m in range(0, NO_MIRRORS):
        pmp = PIX_MIR_POS(W,H,m)
        cv_draw_hex(cv2, image, pmp, radius_x, radius_y, color, thickness)
        cv2.putText(image, f"{m}", pmp, cv2.FONT_HERSHEY_SIMPLEX , 0.5, (255,255,55), thickness=1 )


def empty_fun(x):
    pass

def tuple2int(t) :
    return tuple(map(int, t))


class MyMovingAverage:
    def __init__(self, depth):
        self.data = []
        self.depth = depth
        
    def add_point(self, p):
        self.data.append(p)
        if len(self.data) > self.depth:
            self.data = self.data[-self.depth:]

    def get_current(self):
        return statistics.mean(self.data)


# ..>w_top
# ---
# |  \
# |   \
# |    \
# |     -------
# ......>w_bot

class MyMovingAverageLowPass(MyMovingAverage):
    def __init__(self, depth, w_top, w_bot):
        super().__init__(depth)
        self.w_top = w_top
        self.w_bot = w_bot
        
    def add_point(self, p):
        super().add_point(p)

    def get_current(self):
        sum = 0
        sum_w = 0
        last = self.data[-1]
        for d in self.data:
            w = self.weight(d, last)
            sum   += w*d
            sum_w += w
        return sum / sum_w

    def weight(self, d_old, d_new):
        delta = abs(d_new - d_old)
        if delta < self.w_top :
            return 1
        elif delta > self.w_bot:
            return 0
        else :
            return (delta - self.w_top) / (self.w_bot - self.w_top)

class MyMovingAverageVector:
    def __init__(self, ma_depth, vec_depth):
        self.data = []
        for i in range(vec_depth):
            self.data.append(MyMovingAverage(ma_depth))

    def add_point(self, p):
        for pp,dd in zip(p, self.data):
            dd.add_point(pp)

    def get_current(self):
        return [d.get_current() for d in self.data]



class MyFPS(MyMovingAverage):
    def __init__(self, depth):
        super().__init__(depth)
        self.last_time_s =  time.perf_counter()
        self.add_frame()
    def add_frame(self):
        d_time_s = time.perf_counter() - self.last_time_s
        self.add_point(d_time_s)
        self.last_time_s = time.perf_counter()
    def get_fps(self):
        return(1/self.get_current())


def distance_sqr(va, vb):
    d = 0
    for a,b in zip(va,vb):
        d += (a-b)*(a-b)
    return d

def average(va, vb):
    return [0.5*(a+b) for a,b in zip(va,vb)]
        
    

def unique_id():
    # https://tutorial.eyehunts.com/python/python-static-variable-in-a-function-example-code/
    if not hasattr(unique_id, "id"):
        unique_id.id = 0  # it doesn't exist yet, so initialize it
    unique_id.id += 1
    return unique_id.id

# fit y = C + M x
# y = a,b
# C = cx, cy
# M = m11,m12; m21, m22
# x = x,y
#  REWRITE
# y = A.p
# 
# | a | = | 1 0 x y 0 0 | | cx  |
# | b | = | 0 1 0 0 x y | | cy  |
#                         | m11 |
#                         | m12 |
#                         | m21 |
#                         | m22 |
# 
# https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html
# 
class MyFitProjection() :
    def __init__(self):
        self.y = []
        self.A = []
        self.solved = False
        pass
    def add_measurement(self, x, y):
        self.y.append(y[X])
        self.y.append(y[Y])
        self.A.append([1, 0, x[X], x[Y], 0,    0])
        self.A.append([0, 1, 0,    0,    x[X], x[Y]])

    def solve(self):
        if len(self.y) > 4:
            self.p = np.linalg.lstsq(self.A, self.y, rcond=None)[0]
            self.C = (self.p[0], self.p[1])
            self.M = [[self.p[2], self.p[3]], [self.p[4], self.p[5]]]
            self.Minv = np.linalg.inv(self.M)
            self.solved = True
            return True
        else:
            return False
    def is_solved(self):
        return self.solved

    def evalX2Y(self, x):
        a = self.C[X] + self.p[2]*x[X] + self.p[3]*x[Y]
        b = self.C[Y] + self.p[4]*x[X] + self.p[5]*x[Y]
        return (a, b)

    def evalY2X(self, y):
        ymc = (y[X] - self.C[X], y[Y] - self.C[Y])
        xx = self.Minv[0][0] * ymc[X] + self.Minv[0][1] * ymc[Y]
        xy = self.Minv[1][0] * ymc[X] + self.Minv[1][1] * ymc[Y]
        return (xx, xy)
    


# ===========================
#  TESTING
# ===========================
if __name__ == '__main__':
    print('test MyFitProjection')
    hex_axis = MyFitProjection()
    hex_axis.add_measurement((  0, 1), (100, 50))
    hex_axis.add_measurement((  1, 0), (150,100))
    hex_axis.add_measurement((  0,-1), (100,150))
    hex_axis.add_measurement(( -1, 0), ( 50,100))
    hex_axis.solve()
    mida=(0,0)
    xy = hex_axis.evalX2Y(mida)
    print('a:{} to x:{}'.format(mida, xy))
    mida = hex_axis.evalY2X(xy)
    print('x:{} to a:{}'.format(xy, mida))

    mida=(1,1)
    xy = hex_axis.evalX2Y(mida)
    print('a:{} to x:{}'.format(mida, xy))
    mida = hex_axis.evalY2X(xy)
    print('x:{} to a:{}'.format(xy, mida))

    print("test MyMovingAverageVector")
    a = MyMovingAverageVector(3,2)
    a.add_point((1.1, 2.2))
    assert a.get_current()[0] == 1.1
    print(a.get_current())
    a.add_point((1.2, 2.4))
    assert a.get_current()[0] == 1.15
    print(a.get_current())
    a.add_point((1.3, 2.6))
    assert a.get_current()[0] == 1.2
    print(a.get_current())
