from enum import auto, IntFlag


class Antenna(IntFlag):
    ANT_1 = auto()
    ANT_2 = auto()
    ANT_3 = auto()
    ANT_4 = auto()
    ANT_5 = auto()
    RXANT_1 = auto()
    RXANT_2 = auto()
    RXANT_3 = auto()

    def __str__(self):
        return self.name
