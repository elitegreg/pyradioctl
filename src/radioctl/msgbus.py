from .utils.signal_slots import *

from enum import auto, IntEnum

import collections


class MsgType(IntEnum):
    MODEL_UPDATED = auto()
    VFO_FREQUENCY_SET = auto()
    VFO_FREQUENCY_QUERY = auto()
    VFO_FREQUENCY_RESULT = auto()
    VFO_MODE_SET= auto()
    VFO_MODE_QUERY= auto()
    VFO_MODE_RESULT= auto()
    RX_VFO_SET= auto()
    RX_VFO_QUERY= auto()
    RX_VFO_RESULT= auto()
    TX_VFO_SET= auto()
    TX_VFO_QUERY= auto()
    TX_VFO_RESULT= auto()
    RECEIVE_SET = auto()
    RECEIVE_QUERY = auto()
    RECEIVE_RESULT = auto()
    TRANSMIT_SET = auto()
    TRANSMIT_QUERY = auto()
    TRANSMIT_RESULT = auto()


class MsgBus:
    def __init__(self):
        self._signals = collections.defaultdict(SignalSlots)

    def __index__(self, key):
        return self._signals[key]
