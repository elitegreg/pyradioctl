from .rigcap import RigCapabilities
from .rigstate import RigState
from .utils import asyncio_serial


class Rig:
    def __init__(self, model, itu_region, rig_protocol_factory):
        self._rigcap = RigCapabilities(model, itu_region)
        self._rigstate = RigState()
        self._protocol = rig_protocol_factory(self._rigstate)

    @property
    def capabilities(self):
        return self._rigcap

    @property
    def state(self):
        return self._rigstate

    @property
    def protocol(self):
        return self._protocol

    def open_serial(self, loop, serial_port, baudrate):
        (reader, writer) = loop.run_until_complete(
            asyncio_serial.open_serial_connection(
                url = serial_port,
                baudrate = baudrate))
        self.protocol.open(loop, reader, writer)
