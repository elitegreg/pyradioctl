from enum import auto, IntFlag



class Mode(IntFlag):
    AM = auto()
    CW = auto()
    USB = auto()
    LSB = auto()
    RTTY = auto()
    FM = auto()
    WFM = auto()
    CWR = auto()
    RTTYR = auto()
    AMS = auto()
    PKTLSB = auto()
    PKTUSB = auto()
    PKTFM = auto()
    ECSSUSB = auto()
    ECSSLSB = auto()
    FAX = auto()
    SAM = auto()
    SAL = auto()
    SAH = auto()
    DSB = auto()
    FMN = auto()
    PKTAM = auto()
    P25 = auto()
    DSTAR = auto()
    DPMR = auto()
    NXDNVN = auto()
    NXDN_N = auto()
    DXR = auto()
    AMN = auto()
    PSK = auto()
    PSKR = auto()
    DD = auto()

    def __str__(self):
        return self.name
