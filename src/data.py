from src.scd41 import Measurement
from os import mkdir

class Results(list):
    def __init__(self):
        super().__init__()
        try:
            f = open("/data/results", "r")
            for l in f.readlines():
                entry = Measurement.deserialize(l)
                super().append(entry)
        except:
            try:
                mkdir("/data")
            except:
                pass
            self.clear()

    def save(self):
        with open("/data/results", "w") as f:
            for result in self:
                f.write(result.serialize() + "\n")

    def clear(self):
        while len(self) > 0:
            self.pop()
        self.save()
