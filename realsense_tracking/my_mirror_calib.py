import numpy as np
import math
from scipy.optimize import curve_fit
import statistics
from my_utils import *
import matplotlib.pyplot as plt



#                         0    1    2    3     4    5    6    7    8   9   10  11  
def myProjection(x_coor, p12, p13, p21, p23, p31, p32, p33,  tx,  ty,  tz):
# def myProjection(x_coor, tx,  ty,  tz):
    y_coors = []

    for x,y,z in x_coor:
        # xx = (tx + 1*x + 1 * y + 1 * z)
        # yy = (ty + 1*x + 1 * y + 1 * z)
        # zz = (tz + 1*x + 1 * y + 1 * z)
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
        # self._P0 = [0.2, 0.2, 0]
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

    def solve(self, remove_outliers = True):
        if(len(self.x_data) > 3) :
            self._solve()
            if (remove_outliers):
                self.removeOutliers()
                self._solve()
            return True
        else:
            return False

    def _solve(self):
        self._P = curve_fit(myProjection, self.x_data, self.y_data, self._P0)[0]
        self.solved = True
        self._calcFitStats()

    def eval(self, x) :
        p = self._P
        x = [x]
        # return myProjection(x, p[0], p[1], p[2])
        return myProjection(x, p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9])

    def printCalibMatrix(self):

        print("M [ {:6.3f} {:6.3f} {:6.3f}  ".format(1,         1,         1))
        print("    {:6.3f} {:6.3f} {:6.3f}  ".format(1,         1,         1))
        print("    {:6.3f} {:6.3f} {:6.3f} ]".format(1,         1,         1))
        print("T [ {:6.3f} {:6.3f} {:6.3f} ]".format(self._P[0], self._P[1], self._P[2]))


    def plotResiduals(self, in_degrees=True):
        degrees = 1
        if in_degrees:
            degrees = 180 / math.pi

        x = []  
        y = []
        z = []
        dya = []
        dyb = []

        for i in range(len(self.x_data)):
            x.append( self.x_data[i][X] )
            y.append( self.x_data[i][Y] ) 
            z.append( self.x_data[i][Z] ) 
            ym = self.eval(self.x_data[i])
            ym = np.multiply(ym, degrees)
            dya.append( degrees*self.y_data[2*i+0] - ym[0] )
            dyb.append( degrees*self.y_data[2*i+1] - ym[1] ) 

        # fig, (axa,axb) = plt.subplots(nrows=2, projection='3d')
        fig = plt.figure(1, figsize=(20,10))
        axa = fig.add_subplot(121, projection='3d')
   
        sca = axa.scatter(x, y, z, c=dya, cmap='rainbow')
        axa.set_title("a")
        plt.colorbar(sca)

        axa.set_xlabel('X')
        axa.set_ylabel('Y')
        axa.set_zlabel('Z')

        # fig2 = plt.figure(2)
        axb = fig.add_subplot(122, projection='3d')
        scb = axb.scatter(x, y, z, c=dyb,cmap='rainbow')
        axb.set_title("b")
        plt.colorbar(scb)


        axb.set_xlabel('X')
        axb.set_ylabel('Y')
        axb.set_zlabel('Z')
        plt.show() 


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

    def _calcFitStats(self) :
        dya = []
        dyb = []
        for i in range(len(self.x_data)):
            ym = self.eval(self.x_data[i])
            dya.append( self.y_data[2*i+0] - ym[0] )
            dyb.append( self.y_data[2*i+1] - ym[1] )
        self.stda = statistics.stdev(dya)
        self.stdb = statistics.stdev(dyb)
        dya2 = np.abs(dya)
        dyb2 = np.abs(dyb)
        self.maxa = max(dya2)
        self.maxb = max(dyb2)
        self.mina = min(dya2)
        self.minb = min(dyb2)



    def printResidualsStatistics(self, in_degrees=True):
        degrees = 1
        if in_degrees:
            degrees = 180 / math.pi

        print("std = {:6.3f}  {:6.3f} ".format(self.stda*degrees, self.stdb*degrees))
        print("min = {:6.3f}  {:6.3f} ".format(self.mina*degrees, self.minb*degrees))
        print("max = {:6.3f}  {:6.3f} ".format(self.maxa*degrees, self.maxb*degrees))

    def removeOutliers(self) :
        new_x_data = []
        new_y_data = []
        no_items_removed = 0        
        for i in range(len(self.x_data)):
            ym = self.eval(self.x_data[i])
            dya = self.y_data[2*i+0] - ym[0] 
            dyb = self.y_data[2*i+1] - ym[1] 
            if (np.abs(dya) < 1.5*self.stda) and (np.abs(dyb) < 1.5*self.stdb) :
                new_x_data.append(self.x_data[i])
                new_y_data.append(self.y_data[2*i+0])
                new_y_data.append(self.y_data[2*i+1])
            else:
                no_items_removed += 1


        self.x_data = new_x_data
        self.y_data = new_y_data





