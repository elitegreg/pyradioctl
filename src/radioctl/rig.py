from .capabilities import Capabilities
from .model import Model
from .utils import asyncio_serial


class Rig:
    def __init__(self, capabilities, protocol):
        self._rigcap = capabilities
        self._model = Model()
        self._protocol = protocol
        self._msgbus = protocol.msgbus

        for vfo in capabilities.vfos:
            self._model.add_vfo(vfo)

        self._model.register_signals(self.msgbus)

    @property
    def capabilities(self):
        return self._rigcap

    @property
    def model(self):
        return self._model

    @property
    def msgbus(self):
        return self._msgbus

    @property
    def protocol(self):
        return self._protocol

    def open_serial(self, loop, serial_port, baudrate):
        (reader, writer) = loop.run_until_complete(
            asyncio_serial.open_serial_connection(
                url = serial_port,
                baudrate = baudrate))
        self.protocol.open(loop, reader, writer)
