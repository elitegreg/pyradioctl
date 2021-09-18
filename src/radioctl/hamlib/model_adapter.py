from .vfos import VFO

class HamlibModelAdapter:
    def __init__(self, model):
        self._model = model

    @property
    def primary_rx_vfo_frequency(self):
        return self._model.primary_rx_vfo.frequency

    @primary_rx_vfo_frequency.setter
    def primary_rx_vfo_frequency(self, frequency):
        self._model.primary_rx_vfo.frequency = frequency

    @property
    def primary_rx_vfo_mode(self):
        return self._model.primary_rx_vfo.mode

    @primary_rx_vfo_mode.setter
    def primary_rx_vfo_mode(self, mode):
        self._model.primary_rx_vfo.mode = mode

    @property
    def primary_rx_vfo_name(self):
        vfo_name = 'VFO{}'.format(self._model.primary_rx_vfo.name)
        if not hasattr(VFO, vfo_name):
            raise KeyError(f'No HamLib VFO named: {vfo_name}')
        return vfo_name

    @primary_rx_vfo_name.setter
    def primary_rx_vfo_name(self, value):
        value = value.upper()
        if len(value) > len('VFO') and value.startswith('VFO'):
            value = value[3:]
        self._model.primary_rx_vfo = value
