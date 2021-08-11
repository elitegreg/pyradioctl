class RigCapabilities:
    def __init__(self, model, aliases=None):
        self._model = model
        self._aliases = aliases if aliases else []
        self._rx_bands = []
        self._tx_bands = []
        self._tuning_steps = []
        self._filters = []
        self._max_rit = 0
        self._max_xit = 0
        self._max_ifshift = 0
        self._announces = 0
        self._preamps = []
        self._attenuators = []
        self._get_funcs = set()
        self._set_funcs = set()
        self._get_levels = set()
        self._set_levels = set()
        self._get_parms = set()
        self._set_parms = set()
        self._vfos = []

    def add_rx_band(self, band):
        self._rx_bands.append(band)

    def add_tx_band(self, band):
        self._tx_bands.append(band)

    def add_tuning_step(self, modes, step):
        self._tuning_steps.append((modes, step))

    def add_filter(self, modes, filter_width):
        self._filters.append((modes, filter_width))

    def add_preamp(self, preamp):
        self._preamps.append(preamp)

    def add_attenuator(self, att):
        self._attenuators.append(att)

    def add_func(self, func, getit=True, setit=True):
        if getit:
            self._get_funcs.add(func)
        if setit:
            self._set_funcs.add(func)

    def add_level(self, level, getit=True, setit=True):
        if getit:
            self._get_levels.add(level)
        if setit:
            self._set_levels.add(level)

    def add_parm(self, parm, getit=True, setit=True):
        if getit:
            self._get_parms.add(parm)
        if setit:
            self._set_parms.add(parm)

    def set_max_rit(self, maxrit):
        self._max_rit = maxrit

    def set_max_xit(self, maxxit):
        self._max_xit = maxxit

    def set_max_ifshift(self, maxifshift):
        self._max_ifshift = maxifshift

    def set_announces(self, announces):
        self._announces = announces

    def add_vfos(self, *vfos):
        self._vfos.extend(vfos)

    @property
    def vfos(self):
        return self._vfos

    #TODO getters
