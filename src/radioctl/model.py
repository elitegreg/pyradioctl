from .hamlib.modes import Mode
from .hamlib.ptt import PTT
from .msgbus import MsgBus, MsgType

class VFO:
    def __init__(self, index, name):
        self._index = index
        self._name = name
        self._frequency = 0
        self._mode = Mode.CW
        self._queries = []

    def __str__(self):
        return f'VFO-{self._name} {self._frequency} {self._mode}'

    def register_signals(self, msgbus):
        msgbus[MsgType.VFO_FREQUENCY_RESULT].connect(self.__update_frequency)
        msgbus[MsgType.VFO_MODE_RESULT].connect(self.__update_mode)
        self._queries.append(msgbus[MsgType.VFO_FREQUENCY_QUERY])
        self._queries.append(msgbus[MsgType.VFO_MODE_QUERY])
        self._queries.append(msgbus[MsgType.VFO_DATAMODE_QUERY])

    def query_all(self):
        for query in self._queries:
            query()

    @property
    def index(self):
        return self._index

    @property
    def name(self):
        return self._name

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self):
        self.

    @property
    def mode(self):
        return self._mode

    def __update_frequency(self, index, frequency):
        if index == self._index:
            self._frequency = frequency

    def __update_mode(self, index, mode):
        if index == self._index:
            self._mode = mode


class Model:
    def __init__(self):
        self._vfos = []
        self._vfos_by_name = {}
        self._tx = PTT.RX
        self._tx_signal = None
        self._queries = []

    def register_signals(self, msgbus):
        msgbus[MsgType.TRANSMIT_RESULT].connect(self.__update_tx)
        self._tx_signal = msgbus[MsgType.TRANSMIT_SET]
        self._queries.append(msgbus[MsgType.TRANSMIT_QUERY])

    def query_all(self):
        for query in self._queries:
            query()
        for vfo in self._vfos:
            vfo.query_all()

    def add_vfo(self, name):
        index = len(self._vfos)
        vfo = VFO(index, name)
        self._vfos.append(vfo)
        self._vfos_by_name[name] = vfo
        return vfo

    def get_vfo(self, index):
        return self._vfos[index]

    def get_vfo_by_name(self, name):
        return self._vfos_by_name[name]
    
    @property
    def tx(self):
        return self._tx

    @tx.setter
    def tx(self, value):
        assert(self._tx_signal)
        self._tx_signal(value)

    def __update_tx(self, value):
        self._tx = value
