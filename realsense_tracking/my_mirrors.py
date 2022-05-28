import numpy as np

from my_camera_to_mirror import MyCameraToMirror
from my_mirror_move import MyMirrorMove
from my_utils import NO_MIRRORS


class Mirror:
    def __init__(self, mirror_nbr, mirror_mover, camera_to_mirror) -> None:
        self._source = None
        self._destination = None
        self._mirror_nbr = mirror_nbr
        self._mirror_mover = mirror_mover
        self._camera_to_mirror = camera_to_mirror
        self._has_been_reset = False
        self.target_position1 = 0
        self.target_position2 = 0

    @property
    def has_been_reset(self):
        return self._has_been_reset

    def set_source(self, value):
        self._source = value

    def set_destination(self, value):
        self._destination = value

    def update_mirror(self, afps):
        if (self._source is None) or (self._destination is None):
            self._reset()
        else:
            if afps.has_id(self._source) and afps.has_id(self._destination):
                self.target_position1 = afps.get_3d_location_by_id(self._source)
                self.target_position2 = afps.get_3d_location_by_id(self._destination)
            self._move()

    def _reset(self):
        self._mirror_mover.move_q(self._mirror_nbr, [0, 0])
        self._has_been_reset = False
    
    def _move(self):
        angles_deg0 = self._camera_to_mirror.get_angle(self._mirror_nbr, self.target_position1)
        angles_deg1 = self._camera_to_mirror.get_angle(self._mirror_nbr, self.target_position2)
        angles_av = np.mean( np.array([ angles_deg0, angles_deg1 ]), axis=0 )
        self._mirror_mover.move_q(self._mirror_nbr, angles_av)
        self._has_been_reset = False

class MyMirrors:
    def __init__(self, mirror_mover, camera_to_mirror) -> None:
        self._mirrors = [Mirror(n, mirror_mover, camera_to_mirror) for n in range(NO_MIRRORS)]
        self._mirror_mover = mirror_mover

    @property
    def nbr_mirrors(self):
        return NO_MIRRORS

    def set_tracking(self, mirror_nbr, source_afp_id, destination_afp_id):
        self._mirrors[mirror_nbr].set_source(source_afp_id)
        self._mirrors[mirror_nbr].set_destination(destination_afp_id)
    
    def reset_tracking(self, mirror_nbr):
        self._mirrors[mirror_nbr].set_source(None)
        self._mirrors[mirror_nbr].set_destination(None)

    def move_mirors(self, afps):
        if all(mirror.has_been_reset for mirror in self._mirrors):
            return
        for mirror in self._mirrors:
            mirror.update_mirror(afps)
        self._mirror_mover.move_e()
