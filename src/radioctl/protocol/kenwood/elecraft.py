from .dialects import register_dialect


class ElecraftDialect:
    MODE_MAP_FROM = {
        '1': "LSB",
        '2': "USB",
        '3': "CW",
        '4': "FM",
        '5': "AM",
        '6': "PKTUSB",
        '7': "CWR",
        '9': "PKTLSB",
    }

    MODE_MAP_TO = {
        "LSB": 1,
        "USB": 2,
        "CW": 3,
        "FM": 4,
        "AM": 5,
        "PKTUSB": 6,
        "CWR": 7,
        "PKTLSB": 9,
    }

    def __init__(self, cfg):
        pass

    def mode_from_rig(self, rigmode):
        return self.MODE_MAP_FROM[rigmode]

    def mode_to_rig(self, mode):
        return self.MODE_MAP_TO[mode]

    @property
    def startup_commands(self):
        return "DT0;"


register_dialect("Elecraft", ElecraftDialect)
