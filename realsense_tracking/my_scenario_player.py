

from time import perf_counter
from my_active_facepoints import MyActiveFacepoints
from my_mirrors import MyMirrors


class MyScenarioPlayer:
    def __init__(self, mirror_mover, camera_to_mirror, afps:MyActiveFacepoints):
        self.active_scenario = None
        self.previous_fp = set()
        self._my_mirrors = MyMirrors(mirror_mover, camera_to_mirror)
        self._my_afps = afps
        self._manual = False
        
    def set_manual(self, mode):
        self._manual = mode
        if self._manual:
            self.active_scenario = ScenarioBase(self._my_mirrors, self._my_afps)
        else :
            self.active_scenario = None

    def set_manual_target(self, mirror, face_id_1, face_id_2):
        self.active_scenario.set_tracking(mirror, face_id_1, face_id_2)
    def set_manual_reset(self, mirror):
        self.active_scenario.reset_tracking(mirror )


    def update(self) -> None: 
        if (not self._manual) and (self._my_afps.get_active_ids() != self.previous_fp):
            self.previous_fp = self._my_afps.get_active_ids()
            # switch scenario
            print(f"switching scenarios {len(self._my_afps.get_active_ids())}")
            if len(self._my_afps.get_active_ids()) == 0 :
                self.active_scenario = ScenarioZeroPersons(self._my_mirrors, self._my_afps)
            elif len(self._my_afps.get_active_ids()) == 1 :
                self.active_scenario = ScenarioOnePersons(self._my_mirrors, self._my_afps)
            elif len(self._my_afps.get_active_ids()) == 2 :
                self.active_scenario = ScenarioTwoPersons2(self._my_mirrors, self._my_afps)
            elif len(self._my_afps.get_active_ids()) == 3 :
                self.active_scenario = ScenarioThreePersons(self._my_mirrors, self._my_afps)
            else:
                self.active_scenario = ScenarioZeroPersons(self._my_mirrors, self._my_afps)

        if self.active_scenario:
            self.active_scenario.update()
            self._my_mirrors.move_mirors(self._my_afps)


class ScenarioBase:
    def __init__(self, my_mirrors:MyMirrors, afps:MyActiveFacepoints) -> None:
        self.start_time = perf_counter()
        self.my_mirrors = my_mirrors
        self.afps = afps

    def get_active_time_s(self):
        return perf_counter() - self.start_time

    def set_tracking(self, mirror, face_id_1, face_id_2):
        self.my_mirrors.set_tracking(mirror, face_id_1, face_id_2)
    def reset_tracking(self, mirror):
        self.my_mirrors.reset_tracking(mirror)
    
    def update(self):
        pass

class ScenarioTable(ScenarioBase):
    def __init__(self, my_mirrors, afps, time_table = [], return_line_after_end = 0) -> None:
        super().__init__(my_mirrors, afps)

        self._active_line = 0

        if len(time_table) == 0:
            self.time_table = [] #    d(s)   m0     m1     m2     m3     m4     m5     m6     m7 
            self.time_table.append( [ 0,   -1,-1, -1,-1, -1,-1, -1,-1, -1,-1, -1,-1, -1,-1, -1,-1 ] )
            self.return_line_after_end = 0
        else:
            self.time_table = time_table
            self.return_line_after_end = return_line_after_end

        self.activate_line()


    def update(self):
        if (perf_counter() - self._line_start_time_s) > self.time_table[self._active_line]:
            self._active_line += 1
            if self._active_line == len(self.time_table):
                self._active_line = self.return_line_after_end
            self.activate_line()

    def activate_line(self):
        for mirror in range(0,8):
            index = 1 + 2*mirror
            if self.time_table[self.active_line][index] > -1:
                self.my_mirrors.set_tracking(mirror, self.time_table[self.active_line][index], [self.active_line][index+1])
            elif self.time_table[self.active_line][index] == -2:
                self.my_mirrors.reset_tracking(mirror)
        self._line_start_time_s = perf_counter()
        

class ScenarioZeroPersons(ScenarioBase):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)
        print("ScenarioZeroPersons active")
        for m in range(self.my_mirrors.nbr_mirrors):
            self.my_mirrors.reset_tracking(m)

    def update(self):
        pass

class ScenarioOnePersons(ScenarioBase):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)
        print("ScenarioOnePersons active")
        for m in range(self.my_mirrors.nbr_mirrors):
            self.my_mirrors.set_tracking(m, self.afps[0].id, self.afps[0].id)

    def update(self):
        pass        


class ScenarioTwoPersons1(ScenarioBase):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)
        print("ScenarioTwoPersons active")
        self.my_mirrors.set_tracking(0, self.afps[0].id, self.afps[0].id)
        self.my_mirrors.set_tracking(1, self.afps[1].id, self.afps[1].id)
        self.my_mirrors.set_tracking(2, self.afps[0].id, self.afps[0].id)
        self.my_mirrors.set_tracking(3, self.afps[1].id, self.afps[1].id)
        self.my_mirrors.set_tracking(4, self.afps[0].id, self.afps[0].id)
        self.my_mirrors.set_tracking(5, self.afps[1].id, self.afps[1].id)
        self.my_mirrors.set_tracking(6, self.afps[0].id, self.afps[1].id)
        self.my_mirrors.set_tracking(7, self.afps[0].id, self.afps[1].id)
    def update(self):
        pass

class ScenarioTwoPersons2(ScenarioBase):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)
        print("ScenarioTwoPersons active")
        self.my_mirrors.set_tracking(0, self.afps[0].id, self.afps[1].id)
        self.my_mirrors.set_tracking(1, self.afps[0].id, self.afps[1].id)
        self.my_mirrors.set_tracking(2, self.afps[0].id, self.afps[1].id)
        self.my_mirrors.set_tracking(3, self.afps[0].id, self.afps[1].id)
        self.my_mirrors.set_tracking(4, self.afps[0].id, self.afps[1].id)
        self.my_mirrors.set_tracking(5, self.afps[0].id, self.afps[1].id)
        self.my_mirrors.set_tracking(6, self.afps[0].id, self.afps[1].id)
        self.my_mirrors.set_tracking(7, self.afps[0].id, self.afps[1].id)
    def update(self):
        pass

class ScenarioThreePersons(ScenarioBase):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)
        print("ScenarioThreePersons active")
        self.my_mirrors.set_tracking(0, self.afps[0].id, self.afps[0].id)
        self.my_mirrors.set_tracking(1, self.afps[0].id, self.afps[1].id)
        self.my_mirrors.set_tracking(2, self.afps[1].id, self.afps[1].id)
        self.my_mirrors.set_tracking(3, self.afps[1].id, self.afps[2].id)
        self.my_mirrors.set_tracking(4, self.afps[2].id, self.afps[2].id)
        self.my_mirrors.set_tracking(5, self.afps[2].id, self.afps[0].id)
        self.my_mirrors.set_tracking(6, self.afps[0].id, self.afps[0].id)
        self.my_mirrors.set_tracking(7, self.afps[1].id, self.afps[1].id)
        
    def update(self):
        pass



class ScenarioOnePersonsDynamic(ScenarioTable):
    def __init__(self, my_mirrors, afps) -> None:
        print("ScenarioOnePersonsDynamic active")

        time_table = [] #    d(s)   m0     m1     m2     m3     m4     m5     m6     m7 
        time_table.append( [ 0,   -1,-1, -1,-1, -1,-1, -1,-1, -1,-1, -1,-1, -1,-1, -1,-1 ] )
        time_table.append( [ 1,    0, 0, -1,-1, -1,-1, -1,-1, -1,-1, -1,-1, -1,-1, -1,-1 ] )
        time_table.append( [ 1,    0, 0, -1,-1, -1,-1,  0, 0, -1,-1, -1,-1, -1,-1, -1,-1 ] )
        time_table.append( [ 1,    0, 0, -1,-1, -1,-1,  0, 0, -1,-1,  0, 0, -1,-1, -1,-1 ] )
        time_table.append( [ 1,    0, 0, -1,-1,  0, 0,  0, 0, -1,-1,  0, 0, -1,-1, -1,-1 ] )
        time_table.append( [ 1,    0, 0, -1,-1,  0, 0,  0, 0,  0, 0,  0, 0, -1,-1, -1,-1 ] )
        time_table.append( [ 1,    0, 0,  0, 0,  0, 0,  0, 0,  0, 0,  0, 0, -1,-1, -1,-1 ] )
        time_table.append( [ 1,    0, 0,  0, 0,  0, 0,  0, 0,  0, 0,  0, 0,  0, 0, -1,-1 ] )
        time_table.append( [ 10,   0, 0,  0, 0,  0, 0,  0, 0,  0, 0,  0, 0,  0, 0,  0, 0  ] )
        return_line_after_end = len(time_table) - 1

        super().__init__(my_mirrors, afps, time_table, return_line_after_end)


