from enum import auto, IntFlag


class Function(IntFlag):
    FAGC = auto()
    NB = auto()
    COMP = auto()
    VOX = auto()
    TONE = auto()
    TSQL = auto()
    SBKIN = auto()
    FBKIN = auto()
    ANF = auto()
    NR = auto()
    AIP = auto()
    APF = auto()
    MON = auto()
    MN = auto()
    RF = auto()
    ARO = auto()
    LOCK = auto()
    MUTE = auto()
    VSC = auto()
    REV = auto()
    SQL = auto()
    ABM = auto()
    BC = auto()
    MBC = auto()
    RIT = auto()
    AFC = auto()
    SATMODE = auto()
    SCOPE = auto()
    RESUME = auto()
    TBURST = auto()
    TUNER = auto()
    XIT = auto()
    NB2 = auto()
    DSQL = auto()
    AFLT = auto()
    ANL = auto()
    BC2 = auto()
    DUAL_WATCH = auto()
    DIVERSITY = auto()

    def __str__(self):
        return self.name
