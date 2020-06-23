from .ptt import PTT
from .vfos import VFO

import logging


class RigState:
    def __init__(self):
        self._vfos = {}
        self._activevfo = None
        self._vfomode = None
        self._activemode = None
        self._splitmode = None
        self._txstate = PTT.RX

    @property
    def capabilities(self):
        return self._rigcap

    def getvfo(self, vfo):
        return self._vfos[vfo]

    def setvfo(self, vfo, freq):
        logging.debug('Setting %s frequency to %s', vfo, freq)
        self._vfos[vfo] = freq

    @property
    def activefreq(self):
        return self.getvfo(self.activevfo)

    @activefreq.setter
    def activefreq(self, freq):
        return self.setvfo(self.activevfo)

    @property
    def activevfo(self):
        return self._activevfo

    @activevfo.setter
    def activevfo(self, vfo):
        logging.debug('Setting activevfo to %s', vfo)
        self._activevfo = vfo

    @property
    def vfomode(self):
        return self._vfomode

    @vfomode.setter
    def vfomode(self, mode):
        logging.debug('Setting vfomode to %s', mode)
        self._vfomode = mode

    @property
    def splitfreq(self):
        return self.getvfo(self.splitvfo)

    @splitfreq.setter
    def splitfreq(self, freq):
        return self.setvfo(self.splitvfo)

    @property
    def splitvfo(self):
        return VFO.VFOB if self._activevfo == VFO.VFOA else VFO.VFOA

    @property
    def activemode(self):
        return self._activemode

    @activemode.setter
    def activemode(self, mode):
        logging.debug('Setting activemode to %s', mode)
        self._activemode = mode

    @property
    def splitmode(self):
        return self._splitmode

    @splitmode.setter
    def splitmode(self, mode):
        logging.debug('Setting splitmode to %s', mode)
        self._splitmode = mode

    @property
    def txstate(self):
        return self._txstate

    @txstate.setter
    def txstate(self, state):
        logging.debug('Setting txstate to %s', state)
        self._txstate = state
