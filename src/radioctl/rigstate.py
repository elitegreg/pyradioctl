import logging


class RigState:
    def __init__(self):
        self._vfos = {}
        self._rxvfo = None
        self._txvfo = None
        self._vfomode = None
        self._rxmode = None
        self._txmode = None

    @property
    def capabilities(self):
        return self._rigcap

    def getvfo(self, vfo):
        return self._vfos[vfo]

    def setvfo(self, vfo, freq):
        logging.debug('Setting %s frequency to %s', vfo, freq)
        self._vfos[vfo] = freq

    @property
    def rxfreq(self):
        return self.getVFO(self.rxvfo)

    @rxfreq.setter
    def rxfreq(self, freq):
        return self.setVFO(self.rxvfo)

    @property
    def rxvfo(self):
        return self._rxvfo

    @rxvfo.setter
    def rxvfo(self, vfo):
        logging.debug('Setting rxvfo to %s', vfo)
        self._rxvfo = vfo

    @property
    def vfomode(self):
        return self._vfomode

    @vfomode.setter
    def vfomode(self, mode):
        logging.debug('Setting vfomode to %s', mode)
        self._vfomode = mode

    @property
    def txfreq(self):
        return self.getVFO(self.txvfo)

    @txfreq.setter
    def txfreq(self, freq):
        return self.setVFO(self.txvfo)

    @property
    def txvfo(self):
        return self._txvfo

    @txvfo.setter
    def txvfo(self, vfo):
        logging.debug('Setting txvfo to %s', vfo)
        self._txvfo = vfo

    @property
    def rxmode(self):
        return self._rxmode

    @rxmode.setter
    def rxmode(self, mode):
        logging.debug('Setting rxmode to %s', mode)
        self._rxmode = mode

    @property
    def txmode(self):
        return self._rxmode

    @txmode.setter
    def txmode(self, mode):
        logging.debug('Setting txmode to %s', mode)
        self._txmode = mode
