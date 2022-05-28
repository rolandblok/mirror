

from time import perf_counter
from my_active_facepoints import MyActiveFacepoints
from my_mirrors import MyMirrors


class MyScenarioPlayer:
    def __init__(self, mirror_mover, camera_to_mirror):
        self.active_scenario = None
        self.previous_fp = set()
        self._my_mirrors = MyMirrors(mirror_mover, camera_to_mirror)

    def update(self, afps:MyActiveFacepoints) -> None: 
        if afps.get_active_ids() != self.previous_fp:
            self.previous_fp = afps.get_active_ids()
            # switch scenario
            self._switch_scenario(afps)
        if self.active_scenario:
            self.active_scenario.update()
            self._my_mirrors.move_mirors(afps)

    def _switch_scenario(self, afps):
        print(f"switching scenarios {len(afps.get_active_ids())}")
        if len(afps.get_active_ids()) == 0 :
            self.active_scenario = ScenarioZeroPersons(self._my_mirrors, afps)
        elif len(afps.get_active_ids()) == 1 :
            self.active_scenario = ScenarioOnePersons(self._my_mirrors, afps)
        elif len(afps.get_active_ids()) == 2 :
            self.active_scenario = ScenarioTwoPersons(self._my_mirrors, afps)
        else:
            self.active_scenario = ScenarioZeroPersons(self._my_mirrors, afps)
    
class ScenarioBase:
    def __init__(self, my_mirrors:MyMirrors, afps:MyActiveFacepoints) -> None:
        self.start_time = perf_counter()
        self.my_mirrors = my_mirrors
        self.afps = afps

    def get_active_time_s(self):
        return perf_counter() - self.start_time
    

class ScenarioZeroPersons(ScenarioBase):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)

    def update(self):
        print("ZEro active")
        for n in range(self.my_mirrors.nbr_mirrors):
            self.my_mirrors.reset_tracking(n)

class ScenarioOnePersons(ScenarioBase):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)

    def update(self):
        for n in range(self.my_mirrors.nbr_mirrors):
            self.my_mirrors.set_tracking(n, self.afps[0].id, self.afps[0].id)
        
class ScenarioTwoPersons(ScenarioBase):
    def __init__(self, my_mirrors, afps) -> None:
        super().__init__(my_mirrors, afps)

    def update(self):
        for n in range(0,4):
            self.my_mirrors.set_tracking(n, self.afps[0].id, self.afps[1].id)
        for n in range(4,6):
            self.my_mirrors.set_tracking(n, self.afps[1].id, self.afps[1].id)
        for n in range(6,8):
            self.my_mirrors.set_tracking(n, self.afps[0].id, self.afps[0].id)
        




