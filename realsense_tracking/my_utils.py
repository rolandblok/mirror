import statistics

class MyMovingAverage:
    def __init__(self, depth):
        self.data = []
        self.depth = depth
        
    def add_point(self, p):
        self.data.append(p)
        if len(self.data) > self.depth:
            self.data = self.data[-self.depth:]

    def get_current(self):
        return statistics.mean(self.data)
