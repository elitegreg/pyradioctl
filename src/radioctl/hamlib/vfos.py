from enum import auto, IntFlag


class VFO(IntFlag):
    VFOA = auto()
    VFOB = auto()
    VFOC = auto()
    SUB  = (1<<25)
    MAIN = (1<<26)
    VFO  = (1<<27)
    MEM  = (1<<28)

    def __str__(self):
        return self.name


class VFOMode(IntFlag):
    SIMPLEX = auto()
    DUPLEX = auto()

    def __str__(self):
        return self.name
