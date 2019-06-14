import asyncio
import functools
import serial

from struct import Struct

from .utils import asyncio_serial
from .utils import logging

from .bcd import bcd_to_integer


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

    def __init__(self, port_name, baudrate, xcvr_addr = DefaultXcvrAddr, controller_addr = DefautlControllerAddr):
        self._port_name = port_name
        self._baudrate = baudrate
        self._xcvr_addr = xcvr_addr
        self._controller_addr = controller_addr
        self._reader = None
        self._writer = None

    async def open(self, **kwargs):
        self._reader, self._writer = await asyncio_serial.open_serial_connection(
            url = self._port_name,
            baudrate = self._baudrate,
            **kwargs)

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
                #break

