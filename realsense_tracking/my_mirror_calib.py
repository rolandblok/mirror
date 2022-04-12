import numpy as np
import math
from scipy.optimize import curve_fit
import statistics
from my_utils import *
import matplotlib.pyplot as plt


def add_defaults(**kwargs):
    defaults = {'p11':1, 'p12':0, 'p13':0,
                'p21':0, 'p22':1, 'p23':0,
                'p31':0, 'p32':0, 'p33':1,
                'tx':0, 'ty':0, 'tz':0,
                's_alpha':1, 's_beta':1,
                'alpha_0':0, 'beta_0':0}
    defaults.update(kwargs)
    return defaults


def myProjection(x_coor, p11=1, p12=0, p13=0, p21=0, p22=1, p23=0, p31=0, p32=0, p33=1,  tx=0,  ty=0,  tz=0, s_alpha=1, s_beta=1, alpha_0=0, beta_0=0):
# def myProjection(x_coor, tx,  ty,  tz):
    y_coors = []

    for x,y,z in x_coor:
        # xx = (tx + 1*x + 1 * y + 1 * z)
        # yy = (ty + 1*x + 1 * y + 1 * z)
        # zz = (tz + 1*x + 1 * y + 1 * z)
        xx = (tx + p11*x   + p12 * y + p13 * z)
        yy = (ty + p21*x + p22 * y   + p23 * z)
        zz = (tz + p31*x + p32 * y + p33 * z)        
        alpha = alpha_0 + s_alpha * math.atan(xx/zz)
        beta  = beta_0 + s_beta * math.atan(yy/zz)
        y_coors.append(alpha)
        y_coors.append(beta)
    return y_coors

def printCalibMatrix(parameters):

    print("M [ {:6.3f} {:6.3f} {:6.3f}  ".format(parameters['p11'], parameters['p12'], parameters['p13']))
    print("    {:6.3f} {:6.3f} {:6.3f}  ".format(parameters['p21'], parameters['p22'], parameters['p23']))
    print("    {:6.3f} {:6.3f} {:6.3f} ]".format(parameters['p31'], parameters['p32'], parameters['p33']))
    print("T [ {:6.3f} {:6.3f} {:6.3f} ]".format(parameters['tx'], parameters['ty'], parameters['tz']))
    print("S [ {:6.3f} {:6.3f} ]".format(parameters['s_alpha'], parameters['s_beta']))
    print("0 [ {:6.3f} {:6.3f} ]".format(parameters['alpha_0'], parameters['beta_0']))




# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
# ydata = f(xdata, *params) + eps.
class MyMirrorCalib:
    def __init__(self):
        self.x_data = []
        self.y_data = []
        self._P = add_defaults()
        self.solved = False

    def printCalibMatrix(self):
        printCalibMatrix(self._P)
   
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
        start_values = {'tx':0, 'ty':0, 'tz':0, 's_alpha':1, 's_beta':1, 'alpha_0':0, 'beta_0':0}
        params, initial = zip(*start_values.items())
        f = lambda x,*args:myProjection(x, **dict(zip(params, args)))
        p = curve_fit(f, self.x_data, self.y_data, initial)[0]
        self._P = add_defaults(**dict(zip(params, p)))

        self.solved = True
        self._calcFitStats()

    @staticmethod
    def eval_for_curve_fit(x, tx, ty, tz, s_alpha, s_beta):
        return myProjection(x, tx=tx, ty=ty, tz=tz, s_alpha=s_alpha, s_beta=s_beta)

    def eval(self, x) :
        p = self._P
        x = [x]
        return myProjection(x, **p)

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





