import numpy
import Math
import scipy.optimize


# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
# ydata = f(xdata, *params) + eps.
class MyMirrorCalib:
    def __init__(self):
        self.x_data = []
        self.y_data = []
        self._P = []  # p11, p12, p13, p21, p22, p23, p31, p32, p33
        self._T = []  # tx, ty, tz

    # mxx, myx, mzx, mxy, myy, mzy, mxz, myz, mzz, tx, ty, tz
    def ensure_matrix(self, *args):
        if (len(args) == 1) and isinstance(args[0], numpy.matrix):
            return args[0]
        else:
            M = numpy.matrix([[args[0], args[1], args[2], 0], \
                              [args[3], args[4], args[5], 0], \
                              [args[6], args[7], args[8], 0], \
                              [args[9], args[10], args[11], 0]])
        return M

    
    def add_data(self,Fc, angles):
        # add a data point : 
        #    Fc          : Face point in cartesian camera coordinates
        #    tan(angles) : tangents of angles of the mirror so it perpendicular to the face position : eg : you can see yourself.
        # ydata = f(xdata, *params) + eps.
        self.x_data.push(Fc)
        self.y_data.push([Math.tan(angles[0]), Math.tan(angles[1])])

    def solve(self):
        pass

    def project_to_screen_with_perspective_multi(self, coordinates, *args):
        M = self.ensure_matrix(*args)
        result = [self._project(x,y,z, M, True) for x,y,z in coordinates]
        return  numpy.vstack(result)
    
    def _project(x, y, z, M):
        mir_cor =  numpy.matrix([x, y, z, 1]) @ M
        angles = []
        angles.push( Math.arctan(mir_cor[0] / mir_cor[2]) )
        angles.push( Math.arctan(mir_cor[1] / mir_cor[2]) )
        return angles.tolist()




