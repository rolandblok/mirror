import numpy as np

from my_camera_to_mirror import MyCameraToMirror
from my_mirror_move import MyMirrorMove
from my_utils import NO_MIRRORS


class Mirror:
    def __init__(self, mirror_nbr, mirror_mover, camera_to_mirror) -> None:
        self._source_id = None
        self._destination_id = None
        self._mirror_nbr = mirror_nbr
        self._mirror_mover = mirror_mover
        self._camera_to_mirror = camera_to_mirror
        self._has_been_reset = False
        self._last_source_position = 0
        self._last_target_position = 0

    @property
    def has_been_reset(self):
        return self._has_been_reset

    def set_src_dest_id(self, src_id, dest_id):
        self._source_id = src_id
        self._destination_id = dest_id
        self._has_been_reset = False

    def move_q(self, afps):
        angles = [0,0]
        if (self._source_id is None) or (self._destination_id is None):
            self._has_been_reset = True        
        else:
            if afps.has_id(self._source_id) and afps.has_id(self._destination_id):
                self._last_source_position = afps.get_3d_location_by_id(self._source_id)
                self._last_target_position = afps.get_3d_location_by_id(self._destination_id)
            angles_deg0 = self._camera_to_mirror.get_angle(self._mirror_nbr, self._last_source_position)
            angles_deg1 = self._camera_to_mirror.get_angle(self._mirror_nbr, self._last_target_position)
            angles = np.mean( np.array([ angles_deg0, angles_deg1 ]), axis=0 )
            self._has_been_reset = False
        self._mirror_mover.move_q(self._mirror_nbr, angles)



class MyMirrors:
    def __init__(self, mirror_mover, camera_to_mirror) -> None:
        self._mirrors = [Mirror(n, mirror_mover, camera_to_mirror) for n in range(NO_MIRRORS)]
        self._mirror_mover = mirror_mover

    @property
    def nbr_mirrors(self):
        return NO_MIRRORS

    def set_tracking(self, mirror_nbr, source_afp_id, destination_afp_id):
        print(f"connect mirror {mirror_nbr} for face {source_afp_id} to {destination_afp_id} ")
        self._mirrors[mirror_nbr].set_src_dest_id(source_afp_id, destination_afp_id)
    
    def reset_tracking(self, mirror_nbr):
        print(f"reset mirror {mirror_nbr}  ")
        self._mirrors[mirror_nbr].set_src_dest_id(None, None)

    def move_mirors(self, afps):
        if all(mirror.has_been_reset for mirror in self._mirrors):
            return
        for mirror in self._mirrors:
            mirror.move_q(afps)
        self._mirror_mover.move_e()
