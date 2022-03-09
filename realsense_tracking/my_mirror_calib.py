import numpy as np
import math
from scipy.optimize import curve_fit
import statistics
from my_utils import *




#                         0    1    2   3     4    5    6    7    8   9   10  11  
def myProjection(x_coor, p12, p13, p21, p23, p31, p32, p33,  tx,  ty,  tz):
    y_coors = []

    for x,y,z in x_coor:
        xx = (tx + 1*x   + p12 * y + p13 * z)
        yy = (ty + p21*x + 1 * y   + p23 * z)
        zz = (tz + p31*x + p32 * y + p33 * z)
        alpha = math.atan(xx/zz)
        beta  = math.atan(yy/zz)
        y_coors.append(alpha)
        y_coors.append(beta)
    return y_coors


# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
# ydata = f(xdata, *params) + eps.
class MyMirrorCalib:
    def __init__(self):
        self.x_data = []
        self.y_data = []
        self._P = []  # p11, p12, p13, p21, p22, p23, p31, p32, p33
        self._P0 = [        -0.010, -0.025, 
                     0.038,          0.037 ,
                    -0.225, -0.081,  0.363 ,
                     0.282, -0.154, -0.064    ]
        self._T = []  # tx, ty, tz
        self.solved = False
    
    def add_data(self, Fc, angles):
        # add a data point : 
        #    Fc     : Face point in cartesian camera coordinates
        #    angles : angles of the mirror so it perpendicular to the face position : eg : you can see yourself.
        # ydata = f(xdata, *params) + eps.
        if (angles[0] < math.pi/2) and (angles[0] > -math.pi/2) and (angles[1] < math.pi/2) and (angles[1] > -math.pi/2):
            self.x_data.append(Fc)
            self.y_data.append(angles[0])
            self.y_data.append(angles[1])
        else:
            print("illigal input : {}".format(angles) )

    def solve(self):
        if(len(self.x_data) > 3) :
            self._P = curve_fit(myProjection, self.x_data, self.y_data, self._P0)[0]
            self.solved = True
            return True
        else:
            return False

    def eval(self, x) :
        p = self._P
        x = [x]
        return myProjection(x, p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9])

    def printCalibMatrix(self):
        print("M [ {:6.3f} {:6.3f} {:6.3f}  ".format(1,          self._P[0], self._P[1]))
        print("    {:6.3f} {:6.3f} {:6.3f}  ".format(self._P[2], 1,          self._P[3]))
        print("    {:6.3f} {:6.3f} {:6.3f} ]".format(self._P[4], self._P[5], self._P[6]))
        print("T [ {:6.3f} {:6.3f} {:6.3f} ]".format(self._P[7], self._P[8], self._P[9]))

    def printResiduals(self, in_degrees=True):
        degrees = 1
        if in_degrees:
            degrees = 180 / math.pi
        print("    x,      y,      z  :      a      b   :     am      bm  :     da     db")
        for i in range(len(self.x_data)):
            x = self.x_data[i][X]
            y = self.x_data[i][Y]
            z = self.x_data[i][Z]
            ym = self.eval(self.x_data[i])
            ym = np.multiply(ym, degrees)
            ya = degrees*self.y_data[2*i+0]
            yb = degrees*self.y_data[2*i+1]
            dya = ( ya - ym[0] )
            dyb = ( yb - ym[1] )
            print(" {:7.3f} {:7.3f} {:7.3f} : {:7.3f} {:7.3f} : {:7.3f} {:7.3f} : {:7.3f} {:7.3f} ".format(x,y,z, ya,yb ,ym[0],ym[1], dya, dyb ))


    def printResidualsStatistics(self, in_degrees=True):
        degrees = 1
        if in_degrees:
            degrees = 180 / math.pi
        dya = []
        dyb = []
        for i in range(len(self.x_data)):
            ym = self.eval(self.x_data[i])
            dya.append( self.y_data[2*i+0] - ym[0] )
            dyb.append( self.y_data[2*i+1] - ym[1] )
        stda = degrees * statistics.stdev(dya)
        stdb = degrees * statistics.stdev(dyb)
        dya2 = np.multiply(np.abs(dya), degrees)
        dyb2 = np.multiply(np.abs(dyb), degrees)
        maxa = max(dya2)
        maxb = max(dyb2)
        mina = min(dya2)
        minb = min(dyb2)

        print("std = {:6.3f}  {:6.3f} ".format(stda, stdb))
        print("min = {:6.3f}  {:6.3f} ".format(mina, minb))
        print("max = {:6.3f}  {:6.3f} ".format(maxa, maxb))





