from .hamlib.modes import Mode
from .hamlib.ptt import PTT
from .msgbus import MsgBus, MsgType

import logging

class VFO:
    def __init__(self, index, name):
        self._index = index
        self._name = name
        self._frequency = 0
        self._mode = Mode.CW
        self._queries = []
        self._freq_set = None
        self._mode_set = None

    def __str__(self):
        return f'VFO-{self._name} {self._frequency} {self._mode}'

    def register_signals(self, msgbus):
        msgbus[MsgType.VFO_FREQUENCY_RESULT].connect(self.__update_frequency)
        msgbus[MsgType.VFO_MODE_RESULT].connect(self.__update_mode)
        self._queries.append(msgbus[MsgType.VFO_FREQUENCY_QUERY])
        self._queries.append(msgbus[MsgType.VFO_MODE_QUERY])
        self._freq_set = msgbus[MsgType.VFO_FREQUENCY_SET]
        self._mode_set = msgbus[MsgType.VFO_MODE_SET]

    def query_all(self):
        for query in self._queries:
            query(index=self._index)

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
    def frequency(self, freq):
        self._freq_set(self._index, freq)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode_set(self._index, mode)

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
        self._primary_rx_vfo = 0
        self._primary_tx_vfo = 0

    def register_signals(self, msgbus):
        msgbus[MsgType.TRANSMIT_RESULT].connect(self.__update_tx)
        msgbus[MsgType.RX_VFO_RESULT].connect(self.__update_rx_vfo)
        msgbus[MsgType.TX_VFO_RESULT].connect(self.__update_tx_vfo)
        self._tx_signal = msgbus[MsgType.TRANSMIT_SET]
        self._rx_vfo_signal = msgbus[MsgType.RX_VFO_SET]
        self._tx_vfo_signal = msgbus[MsgType.TX_VFO_SET]
        self._queries.append(msgbus[MsgType.TRANSMIT_QUERY])
        self._queries.append(msgbus[MsgType.RX_VFO_QUERY])
        self._queries.append(msgbus[MsgType.TX_VFO_QUERY])
        for vfo in self._vfos:
            vfo.register_signals(msgbus)

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
        assert(value is not None)
        assert(self._rx_signal)
        assert(self._tx_signal)
        if value:
            self._tx_signal(value)
            self._tx = value
        else:
            self._rx_signal(value)
            self._tx = value

    @property
    def primary_rx_vfo(self):
        return self._vfos[self._primary_rx_vfo]

    @primary_rx_vfo.setter
    def primary_rx_vfo(self, value):
        if type(value) is not int:
            value = self._vfos_by_name[value].index
        self._rx_vfo_signal(index=value)

    @property
    def primary_tx_vfo(self):
        return self._vfos[self._primary_tx_vfo]

    @primary_tx_vfo.setter
    def primary_tx_vfo(self, value):
        if type(value) is not int:
            value = self._vfos_by_name[value].index
        self._tx_vfo_signal(index=value)

    def __update_tx(self, value):
        self._tx = value

    def __update_rx_vfo(self, value):
        self._primary_rx_vfo = value

    def __update_tx_vfo(self, value):
        logging.debug("__update_tx_vfo")
        self._primary_tx_vfo = value

