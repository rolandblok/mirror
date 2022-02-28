import numpy
import math
from scipy.optimize import curve_fit


#                         0    1    2   3     4    5    6    7    8   9   10  11  
def myProjection(x_coor, p11, p12, p13, p21, p22, p23, p31, p32, p33, tx, ty, tz):
    y_coors = []

    for x,y,z in x_coor:
        xx = (tx + p11*x + p12 * y + p13 * z)
        yy = (ty + p21*x + p22 * y + p23 * z)
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
        self._T = []  # tx, ty, tz
        self.solved = False
    
    def add_data(self,Fc, angles):
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
            self._P = curve_fit(myProjection, self.x_data, self.y_data)[0]
            self.solved = True
            return True
        else:
            return False

    def eval(self, x) :
        p = self._P
        x = [x]
        return myProjection(x, p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11])

        





