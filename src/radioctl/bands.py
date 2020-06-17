class Band:
    AllModes = 'AllModes'

    def __init__(self):
        self._freq_range = (None, None)
        self._modes = 0
        self._vfos = 0
        self._antennas = 0
        self._power_levels = { self.AllModes: (0, 0) }

    def add_modes(self, mode):
        self._modes |= mode

    def add_vfos(self, vfo):
        self._vfos |= vfo

    def add_antennas(self, antenna):
        self._antennas |= antenna

    def set_freq(self, start, end):
        assert(start < end)
        self._freq_range = (start, end)

    def set_power(self, mode, low_power, high_power):
        self._power_levels[mode] = (low_power, high_power)

    @property
    def freq_lower_bound(self):
        return self._freq_range[0]

    @property
    def freq_upper_bound(self):
        return self._freq_range[1]

    @property
    def modes(self):
        return self._modes

    @property
    def vfos(self):
        return self._vfos

    @property
    def antennas(self):
        return self._antennas

    @property
    def low_power(self):
        return self._power_levels[self.AllModes][0]

    @property
    def high_power(self):
        return self._power_levels[self.AllModes][1]
