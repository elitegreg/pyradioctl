from enum import IntEnum, auto


class PTT(IntEnum):
    RX = 0
    TX = 1
    TX_MIC = 2
    TX_DATA = 3
    TUNE = 4

    def __str__(self):
        return self.name
