

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
                # self.active_scenario = ScenarioOnePersons(self._my_mirrors, self._my_afps)
                self.active_scenario = Scenario_1_PersonsDynamic(self._my_mirrors, self._my_afps)
            elif len(self._my_afps.get_active_ids()) == 2 :
                self.active_scenario = Scenario_2_PersonsDynamic(self._my_mirrors, self._my_afps)
            else:
                self.active_scenario = Scenario_3_PersonsDynamic(self._my_mirrors, self._my_afps)

        if self.active_scenario:
            self.active_scenario.update()
            self._my_mirrors.move_mirors(self._my_afps)


#  //////////////////
#    BASE Scenarios
#  //////////////////

class ScenarioBase:
    def __init__(self, my_mirrors:MyMirrors, afps:MyActiveFacepoints) -> None:
        self.start_time = perf_counter()
        self.my_mirrors = my_mirrors
        self.afps = afps
        self.max_age_s = 10

    def get_active_time_s(self):
        return perf_counter() - self.start_time

    def set_tracking(self, mirror, face_id_1, face_id_2):
        self.my_mirrors.set_tracking(mirror, face_id_1, face_id_2)
    def reset_tracking(self, mirror):
        self.my_mirrors.reset_tracking(mirror)
    
    # return aged
    def update(self):
        return  self.get_active_time_s() > self.max_age_s


class ScenarioZeroPersons(ScenarioBase):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)
        print("ScenarioZeroPersons active")
        for m in range(self.my_mirrors.nbr_mirrors):
            self.my_mirrors.reset_tracking(m)


class ScenarioOnePersons(ScenarioBase):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)
        print("ScenarioOnePersons active")
        for m in range(self.my_mirrors.nbr_mirrors):
            self.my_mirrors.set_tracking(m, self.afps[0].id, self.afps[0].id)



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
        

#  //////////////////
#    TABLE Scenarios
#  //////////////////

class ScenarioTable(ScenarioBase):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)

        self._active_line  = 0
        self._time_table   = []
        self._mirror_table = []
        self._return_line_after_end = 0


    def append(self, duration, mirror_sp, return_line = False):
        self._time_table.append(duration)
        self._mirror_table.append(mirror_sp)
        if (return_line) :
            self._return_line_after_end = len(self._time_table) - 1

    def start(self):
        self.activate_line()


    def update(self):
        aged = False
        if (perf_counter() - self._line_start_time_s) > self._time_table[self._active_line]:
            self._active_line += 1
            if self._active_line == len(self._time_table):
                self._active_line = self._return_line_after_end
                aged = True
                return aged
            self.activate_line()
        return aged

    def activate_line(self):
        for mirror in range(0,8):
            if self._mirror_table[self._active_line][mirror][0] > -1:
                face_nr_1 = self._mirror_table[self._active_line][mirror][0]
                face_nr_2 = self._mirror_table[self._active_line][mirror][1]
                self.my_mirrors.set_tracking(mirror, self.afps[face_nr_1].id , self.afps[face_nr_2].id)
            elif self._mirror_table[self._active_line][mirror][0] == -2:
                self.my_mirrors.reset_tracking(mirror)
        self._line_start_time_s = perf_counter()



class Scenario_1_PersonsDynamic(ScenarioTable):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)
        print("ScenarioOnePersonsDynamic active")

        self.append(2.0, [[ 0, 0], [-1,-1], [-1,-1], [-1,-1], [-1,-1], [-1,-1], [-1,-1], [-1,-1 ]] )
        self.append(0.6, [[ 0, 0], [-1,-1], [-1,-1], [ 0, 0], [-1,-1], [-1,-1], [-1,-1], [-1,-1 ]] )
        self.append(0.4, [[ 0, 0], [-1,-1], [-1,-1], [ 0, 0], [-1,-1], [ 0, 0], [-1,-1], [-1,-1 ]] )
        self.append(0.2, [[ 0, 0], [-1,-1], [ 0, 0], [ 0, 0], [-1,-1], [ 0, 0], [-1,-1], [-1,-1 ]] )
        self.append(0.1, [[ 0, 0], [-1,-1], [ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0], [-1,-1], [-1,-1 ]] )
        self.append(0.1, [[ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0], [-1,-1], [-1,-1 ]] )
        self.append(0.1, [[ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0], [-1,-1 ]] )
        self.append(1.0, [[ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0], [ 0, 0 ]], True )

        self.start()

class Scenario_2_PersonsDynamic(ScenarioTable):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)
        print("ScenarioOnePersonsDynamic active")

        self.append(2.0, [[ 0, 1], [-1,-1], [-1,-1], [-1,-1], [-1,-1], [-1,-1], [-1,-1], [-1,-1 ]] )
        self.append(0.6, [[ 0, 1], [-1,-1], [-1,-1], [ 0, 1], [-1,-1], [-1,-1], [-1,-1], [-1,-1 ]] )
        self.append(0.4, [[ 0, 1], [-1,-1], [-1,-1], [ 0, 1], [-1,-1], [ 0, 1], [-1,-1], [-1,-1 ]] )
        self.append(0.2, [[ 0, 1], [-1,-1], [ 0, 1], [ 0, 1], [-1,-1], [ 0, 1], [-1,-1], [-1,-1 ]] )
        self.append(0.1, [[ 0, 1], [-1,-1], [ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [-1,-1], [-1,-1 ]] )
        self.append(0.1, [[ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [-1,-1], [-1,-1 ]] )
        self.append(0.1, [[ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [-1,-1 ]] )
        self.append(4.0, [[ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1 ]], True )
        self.append(4.0, [[ 0, 1], [ 0, 0], [ 0, 1], [ 0, 1], [ 0, 1], [ 1, 1], [ 0, 1], [ 0, 1 ]] )
        self.append(3.8, [[ 0, 1], [ 0, 0], [ 1, 1], [ 0, 1], [ 0, 1], [ 1, 1], [ 0, 1], [ 0, 0 ]] )
        self.append(2.4, [[ 0, 1], [ 0, 0], [ 1, 1], [ 0, 0], [ 0, 1], [ 1, 1], [ 0, 1], [ 0, 0 ]] )
        self.append(4.3, [[ 1, 1], [ 0, 0], [ 1, 1], [ 0, 0], [ 0, 1], [ 1, 1], [ 0, 1], [ 0, 1 ]] )
        self.append(4.2, [[ 1, 1], [ 0, 0], [ 1, 1], [ 0, 0], [ 0, 1], [ 1, 1], [ 1, 1], [ 0, 1 ]] )
        self.append(3.2, [[ 1, 1], [ 1, 1], [ 1, 1], [ 0, 0], [ 0, 0], [ 1, 1], [ 1, 1], [ 0, 1 ]] )
        self.append(3.2, [[ 0, 1], [ 1, 1], [ 1, 1], [ 0, 0], [ 0, 0], [ 1, 1], [ 1, 1], [ 0, 1 ]] )
        self.append(3.8, [[ 0, 1], [ 1, 1], [ 0, 1], [ 0, 0], [ 0, 0], [ 1, 1], [ 1, 1], [ 0, 1 ]] )
        self.append(3.3, [[ 0, 1], [ 1, 1], [ 0, 1], [ 0, 1], [ 0, 0], [ 1, 1], [ 1, 1], [ 0, 1 ]] )
        self.append(3.7, [[ 0, 1], [ 1, 1], [ 0, 1], [ 0, 1], [ 0, 0], [ 1, 1], [ 1, 1], [ 0, 0 ]] )
        self.append(3.1, [[ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [ 0, 0], [ 1, 1], [ 1, 1], [ 0, 0 ]] )
        self.append(4.1, [[ 0, 1], [ 0, 1], [ 0, 1], [ 0, 1], [ 0, 0], [ 1, 1], [ 0, 1], [ 0, 0 ]] )

        self.start()

class Scenario_3_PersonsDynamic(ScenarioTable):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)
        print("ScenarioOnePersonsDynamic active")

        self.append(0.6, [[ 0, 1], [-1,-1], [-1,-1], [-1,-1], [-1,-1], [-1,-1], [-1,-1], [-1,-1 ]] )
        self.append(0.6, [[ 0, 1], [-1,-1], [-1,-1], [ 0, 2], [-1,-1], [-1,-1], [-1,-1], [-1,-1 ]] )
        self.append(0.4, [[ 0, 1], [-1,-1], [-1,-1], [ 0, 2], [-1,-1], [ 1, 2], [-1,-1], [-1,-1 ]] )
        self.append(0.2, [[ 0, 1], [-1,-1], [ 0, 0], [ 0, 2], [-1,-1], [ 1, 2], [-1,-1], [-1,-1 ]] )
        self.append(0.1, [[ 0, 1], [-1,-1], [ 0, 0], [ 0, 2], [ 1, 1], [ 1, 2], [-1,-1], [-1,-1 ]] )
        self.append(0.1, [[ 0, 1], [ 2, 2], [ 0, 0], [ 0, 2], [ 1, 1], [ 1, 2], [-1,-1], [-1,-1 ]] )
        self.append(0.1, [[ 0, 1], [ 2, 2], [ 0, 0], [ 0, 2], [ 1, 1], [ 1, 2], [ 0, 1], [-1,-1 ]] )
        self.append(1.0, [[ 0, 1], [ 2, 2], [ 0, 0], [ 0, 2], [ 1, 1], [ 1, 2], [ 0, 1], [ 1, 2 ]], True )
        self.append(2.0, [[ 1, 2], [ 2, 2], [ 0, 0], [ 0, 2], [ 1, 1], [ 1, 2], [ 0, 1], [ 0, 1 ]] )
        self.append(2.5, [[ 1, 2], [ 2, 2], [ 0, 0], [ 0, 1], [ 1, 2], [ 1, 2], [ 0, 1], [ 0, 1 ]] )
        self.append(1.5, [[ 1, 2], [ 0, 0], [ 0, 2], [ 0, 1], [ 1, 2], [ 1, 2], [ 0, 1], [ 0, 1 ]] )
        self.append(1.0, [[ 1, 2], [ 0, 0], [ 0, 2], [ 0, 1], [ 1, 2], [ 1, 1], [ 2, 2], [ 0, 1 ]] )
        self.append(2.3, [[ 0, 1], [ 0, 0], [ 0, 2], [ 0, 2], [ 1, 2], [ 1, 1], [ 2, 2], [ 0, 1 ]] )
        self.append(1.7, [[ 0, 1], [ 2, 2], [ 0, 2], [ 0, 2], [ 1, 1], [ 1, 1], [ 2, 2], [ 0, 1 ]] )
        self.append(2.1, [[ 0, 1], [ 2, 2], [ 0, 0], [ 0, 2], [ 1, 1], [ 1, 1], [ 0, 1], [ 0, 1 ]] )
        self.append(1.8, [[ 0, 1], [ 2, 2], [ 0, 0], [ 0, 2], [ 1, 1], [ 1, 2], [ 0, 1], [ 1, 2 ]] )

        self.start()



