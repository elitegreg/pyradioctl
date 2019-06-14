import asyncio
import functools
import serial

from struct import Struct

from .utils import asyncio_serial
from .utils import logging

from .bcd import bcd_to_integer, integer_to_bcd
from .rigcap import VFO


CIV_Header_Fmt = Struct('HBBB')
CIV_Footer = b'\xFD'
Byte_Encode = Struct('B')


class CIV_Header:
    @staticmethod
    def size():
        return CIV_Header_Fmt.size

    @staticmethod
    def parse(buf):
        (preamble, dest, src, cmd) = CIV_Header_Fmt.unpack_from(buf)
        assert(preamble == 0xFEFE)
        return dict(dest=dest, src=src, cmd=cmd)

    @staticmethod
    def fmt(dest, src, cmd, subcmd=None):
        hdr = CIV_Header_Fmt.pack(0xFEFE, dest, src, cmd)
        if subcmd is not None:
            hdr += Byte_Encode.pack(subcmd)
        return hdr


class IcomXcvr:
    DefaultXcvrAddr = 0x60
    DefautlControllerAddr = 0xE0

    def __init__(self, port_name, baudrate, xcvr_addr = DefaultXcvrAddr, controller_addr = DefautlControllerAddr, **kwargs):
        self._port_name = port_name
        self._baudrate = baudrate
        self._xcvr_addr = xcvr_addr
        self._controller_addr = controller_addr
        self._reader = None
        self._writer = None
        self._rx_vfo = VFO.VFOA
        self._tx_vfo = VFO.VFOA
        self._satmode = False
        self._split = False

    async def open(self, **kwargs):
        self._reader, self._writer = await asyncio_serial.open_serial_connection(
            url = self._port_name,
            baudrate = self._baudrate,
            **kwargs)
        # TODO not generic icom
        await self.set_satmode(False)
        await self.set_active_vfo(VFO.VFOA)

    async def writecmd(self, cmd, subcmd=None, data=b''):
        buf = CIV_Header.fmt(self._xcvr_addr, self._controller_addr, cmd, subcmd) + data + CIV_Footer
        logging.debug('IcomXcvr: wrote: {}', buf)
        self._writer.write(buf)
        while True:
            pkt = await self._reader.readuntil(CIV_Footer)
            hdr = CIV_Header.parse(pkt)
            if hdr['dest'] == self._controller_addr:
                logging.debug('IcomProtocol: Data Received: dest={dest:x} src={src:x} cmd={cmd:x}', **hdr)
                data = pkt[CIV_Header.size():-1]
                if len(data) > 0:
                    dataval = bcd_to_integer(data)
                    logging.debug('... data={}', dataval)
                    return dataval
                return

    async def get_active_vfo_freq(self):
        return await self.writecmd(0x03)

    async def set_active_vfo_freq(self, freq):
        return await self.writecmd(0x05, None, integer_to_bcd(freq))

    async def get_tx_vfo_freq(self):
        if not self._split:
            return await self.get_active_vfo_freq()
        rxvfo = self._rx_vfo
        await self.set_active_vfo(self._tx_vfo)
        result = await self.get_active_vfo_freq()
        await self.set_active_vfo(rxvfo)
        return result

    async def set_tx_vfo_freq(self, freq):
        if not self._split:
            return await self.set_active_vfo_freq(freq)
        rxvfo = self._rx_vfo
        await self.set_active_vfo(self._tx_vfo)
        await self.set_active_vfo_freq(freq)
        await self.set_active_vfo(rxvfo)

    async def set_tx_vfo(self, onoff, vfo):
        if not onoff:
            if self._satmode:
                await self.set_satmode(False)
            self._split = False
            self._tx_vfo = self._rx_vfo
        else:
            self._split = True
            self._tx_vfo = vfo
            await self.set_satmode((vfo & (VFO.MAIN | VFO.SUB)) != 0)

    async def set_active_vfo(self, vfo):
        if vfo == VFO.MEM:
            return await self.writecmd(0x08)
        elif vfo == VFO.VFOA:
            subcmd = 0x0
        elif vfo == VFO.VFOB:
            subcmd = 0x1
        elif vfo == VFO.MAIN:
            subcmd = 0xD0
        elif vfo == VFO.SUB:
            subcmd = 0xD1
        else:
            raise RuntimeError('Invalid VFO')
        self._rx_vfo = vfo
        return await self.writecmd(0x07, subcmd)

    async def set_satmode(self, onoff):
        if onoff:
            data = 1
            if self._tx_vfo == VFO.MAIN:
                self._rx_vfo = VFO.SUB
            else:
                self._rx_vfo = VFO.MAIN
        else:
            data = 0
            self._rx_vfo = VFO.VFOA
        await self.writecmd(0x1A, 0x07, data.to_bytes(1, byteorder='little'))
        self._satmode = bool(data)

