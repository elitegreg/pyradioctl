class Band:
    def __init__(self):
        self._freq_range = (None, None)
        self._vfos = set()
        self._power_levels = (0, 0)

    def add_vfos(self, *vfos):
        self._vfos.update(set(vfos))

    def set_freq_range(self, start, end):
        assert(start < end)
        self._freq_range = (start, end)

    def set_power(self, low_power, high_power):
        self._power_levels = (low_power, high_power)

    def freeze(self):
        self._vfos = frozenset(self._vfos)

    @property
    def freq_range(self):
        return self._freq_range

    @property
    def vfos(self):
        return self._vfos

    @property
    def low_power(self):
        return self._power_levels[0]

    @property
    def high_power(self):
        return self._power_levels[1]
