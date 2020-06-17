from .modes import Mode
from .vfos import VFO, VFOMode

import asyncio
import logging



class KenwoodProtocol:
    MODE_MAP_FROM = {
        # Kenwood Mode #, Data Flag
        (1, False): Mode.LSB,
        (2, False): Mode.USB,
        (3, False): Mode.CW,
        (4, False): Mode.FM,
        (5, False): Mode.AM,
        (6, False): Mode.RTTY,
        (7, False): Mode.CWR,
        (9, False): Mode.RTTYR,
        (1, True): Mode.PKTLSB,
        (2, True): Mode.PKTUSB,
        (4, True): Mode.PKTFM,
        (5, True): Mode.PKTAM,
    }

    MODE_MAP_TO = {
        # Kenwood Mode #, Data Flag
        Mode.LSB    : (1, False),
        Mode.USB    : (2, False),
        Mode.CW     : (3, False),
        Mode.FM     : (4, False),
        Mode.AM     : (5, False),
        Mode.RTTY   : (6, False),
        Mode.CWR    : (7, False),
        Mode.RTTYR  : (9, False),
        Mode.PKTLSB : (1, True),
        Mode.PKTUSB : (2, True),
        Mode.PKTFM  : (4, True),
        Mode.PKTAM  : (5, True),
    }

    VFO_MAP_FROM = {
        '0' : VFO.VFOA,
        '1' : VFO.VFOB,
        '2' : VFO.MEM,
    }

    VFO_MAP_TO = {
        VFO.VFOA : '0',
        VFO.VFOB : '1',
        VFO.MEM  : '2',
    }

    def __init__(self, state):
        self._state = state
        self._internal_mode = 1
        self._data_mode = False
        self._morse_sender_task = None
        self._morse_buf = []
        self._morse_radio_has_buf = None

    def open(self, loop, reader, writer):
        self._reader = reader
        self._writer = writer
        self._send('AI2;')
        self._send('DA;')
        self._send('FA;')
        self._send('FB;')
        self._send('FR;')
        self._send('FT;')
        self._send('MD;')
        loop.create_task(self.reader_task(), name='Reader Task')

    def stop(self):
        pass

    async def reader_task(self):
        while True:
            pkt = await self._reader.readuntil(b';')
            msg = pkt.decode()
            logging.debug('Received: %s', msg)
            cmd = msg[0:2]
            handler = getattr(self, f'rcv_cmd_{cmd}', None)
            if handler:
                handler(msg)

    def _send(self, data):
        logging.debug('Sending: %s', data)
        self._writer.write(data.encode())

    def _decode_freq(self, freq):
        return int(freq.lstrip('0'))

    def _decode_vfo(self, vfofield):
        return self.VFO_MAP_FROM[vfofield]

    def _encode_vfo(self, vfo):
        return self.VFO_MAP_TO[vfo]

    def _set_mode(self):
        mode = self._internal_mode
        data = self._data_mode
        try:
            self._state.rxmode = self.MODE_MAP_FROM[(mode, data)]
        except KeyError:
            logging.debug('Error: Unknown mode mapping (%s, %s), assuming '
                          'a near term update will fix this', mode, data)

    async def _morse_sender(self):
        try:
            logging.debug('Starting Morse Sender...')
            self._morse_radio_has_buf = None

            while len(self._morse_buf):
                logging.debug('Morse string remaining: %s', self._morse_buf)
                if self._morse_radio_has_buf:
                    logging.debug('Waiting for rig to report buffer available %s', id(self._morse_radio_has_buf))
                    await self._morse_radio_has_buf.wait()
                buf = self._morse_buf.pop(0)
                self._send(f'KY {buf:24s};')
                await self._writer.drain()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        logging.debug('Morse Sender Complete')

    def rcv_cmd_DA(self, msg):
        self._data_mode = (msg[2] == '1')
        self._set_mode()

    def rcv_cmd_FA(self, msg):
        self._state.setvfo(VFO.VFOA, self._decode_freq(msg[2:-1]))

    def rcv_cmd_FB(self, msg):
        self._state.setvfo(VFO.VFOB, self._decode_freq(msg[2:-1]))

    def rcv_cmd_FR(self, msg):
        self._state.rxvfo = self._decode_vfo(msg[2])

    def rcv_cmd_FT(self, msg):
        self._state.txvfo = self._decode_vfo(msg[2])
        if self._state.txvfo == self._state.rxvfo:
            self._state.vfomode = VFOMode.SIMPLEX
        else:
            self._state.vfomode = VFOMode.DUPLEX

    def rcv_cmd_KY(self, msg):
        if self._morse_radio_has_buf is None:
            self._morse_radio_has_buf = asyncio.Event()
        if msg[2] == '0':
            logging.debug('Rig morse buffer available')
            self._morse_radio_has_buf.set()
        elif msg[2] == '1':
            logging.debug('Rig morse buffer FULL')
            self._morse_radio_has_buf.clear()

    def rcv_cmd_MD(self, msg):
        self._internal_mode = int(msg[2])
        self._set_mode()

    def set_rxfreq(self, freq):
        vfo = str(self._state.rxvfo)[-1]
        cmd = f'F{vfo}{freq:011d};'
        self._send(cmd)

    def set_rxmode(self, mode, passband):
        mode = getattr(Mode, mode)
        (modeval, dataval) = self.MODE_MAP_TO[mode]
        self._send(f'MD{modeval};')
        self._send(f'DA{int(dataval)};')

    def set_rxvfo(self, vfo):
        self._send(f'FR{self._encode_vfo(vfo)};')

    def set_txfreq(self, freq):
        vfo = str(self._state.txvfo)[-1]
        cmd = f'F{vfo}{freq:011d};'
        self._send(cmd)

    def set_powerstate(self, val):
        if val >= 2: # standby
            self._send('PS0;')
        elif val == 1:
            # TODO low current power up
            self._send('PS1;')
        elif val == 0:
            self._send('PS9;')

    def send_morse(self, buf):
        while len(buf) > 0:
            self._morse_buf.append(buf[0:24])
            buf = buf[24:]
        if not self._morse_sender_task or self._morse_sender_task.done():
            self._morse_sender_task = \
                asyncio.create_task(self._morse_sender(), name='Morse Sender')

    def cancel_morse(self):
        if self._morse_sender_task:
            self._morse_sender_task.cancel()
        self._send('KY0;')
