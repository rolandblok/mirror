import statistics
import numpy as np
import math
import unittest

# CONSTANTS
X = 0   # array indices for cartesian dimensions
Y = 1
Z = 2
A = 0   # array indices for mirror angles
B = 1

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
        pass
    def add_measurement(self, x, y):
        self.y.append(y[X])
        self.y.append(y[Y])
        self.A.append([1, 0, x[X], x[Y], 0,    0])
        self.A.append([0, 1, 0,    0,    x[X], x[Y]])

    def solve(self):
        if len(self.y) > 3:
            self.p = np.linalg.lstsq(self.A, self.y, rcond=None)[0]
            self.C = (self.p[0], self.p[1])
            self.M = [[self.p[2], self.p[3]], [self.p[4], self.p[5]]]
            self.Minv = np.linalg.inv(self.M)
            return True
        else:
            return False

    def evalX2Y(self, x, int_cast = False):
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
