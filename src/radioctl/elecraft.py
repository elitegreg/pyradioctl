from .modes import Mode
from .ptt import PTT
from .vfos import VFO, VFOMode

import asyncio
import logging



class ElecraftProtocol:
    DATA_MODES = (6, 9)

    MODE_MAP_FROM = {
        # Elecraft Mode #, Data Submode
        (1, None): Mode.LSB,
        (2, None): Mode.USB,
        (3, None): Mode.CW,
        (4, None): Mode.FM,
        (5, None): Mode.AM,
        (7, None): Mode.CWR,
        (6, 0): Mode.PKTUSB, # DATA-A
        (9, 0): Mode.PKTLSB, # DATA-A
        (6, 1): Mode.RTTY,   # AFSK-A
        (9, 1): Mode.RTTYR,  # AFSK-A
        (6, 2): Mode.PKTUSB, # PSK-D
        (9, 2): Mode.PKTLSB, # PSK-D
        (6, 3): Mode.RTTY,   # FSK-D
        (9, 3): Mode.RTTYR,  # FSK-D
    }

    MODE_MAP_TO = {
        # Elecraft Mode #, Data Submode
        Mode.LSB    : (1, None),
        Mode.USB    : (2, None),
        Mode.CW     : (3, None),
        Mode.FM     : (4, None),
        Mode.AM     : (5, None),
        Mode.RTTY   : (6, 1), # AFSK-A TODO support map to -D version
        Mode.CWR    : (7, False),
        Mode.RTTYR  : (9, 1), # AFSK-A TODO support map to -D version
        Mode.PKTLSB : (9, 0),
        Mode.PKTUSB : (6, 0),
    }

    VFO_MAP_FROM = {
        '0' : VFO.VFOA,
        '1' : VFO.VFOB,
    }

    VFO_MAP_TO = {
        VFO.VFOA : '0',
        VFO.VFOB : '1',
    }

    def __init__(self, state):
        self._state = state
        self._internal_mode = [1, 1]
        self._data_submode = 0
        self._morse_sender_task = None
        self._morse_buf = []
        self._morse_radio_has_buf = None

        self._state.activevfo = VFO.VFOA

    def open(self, loop, reader, writer):
        self._reader = reader
        self._writer = writer
        self._send('K31;')
        self._send('AI2;')
        self._send('IF;')
        self._send('FA;')
        self._send('FB;')
        self._send('FT;')
        self._send('MD;')
        self._send('MD$;')
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

    def _set_mode(self, vfo):
        mode = self._internal_mode[vfo.value - 1]
        data = self._data_submode

        if mode not in self.DATA_MODES:
            data = None

        try:
            if vfo == VFO.VFOA:
                self._state.activemode = self.MODE_MAP_FROM[(mode, data)]
            elif self._state.splitvfo == vfo:
                self._state.splitmode = self.MODE_MAP_FROM[(mode, data)]
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
                self._send(f'KY {buf};')
                await self._writer.drain()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        logging.debug('Morse Sender Complete')

    def rcv_cmd_DT(self, msg):
        self._data_submode = int(msg[2])
        self._set_mode(VFO.VFOA)
        self._set_mode(VFO.VFOB)

    def rcv_cmd_FA(self, msg):
        self._state.setvfo(VFO.VFOA, self._decode_freq(msg[2:13]))

    def rcv_cmd_FB(self, msg):
        self._state.setvfo(VFO.VFOB, self._decode_freq(msg[2:13]))

    def rcv_cmd_FR(self, msg):
        logging.warning('FR command recieved. VFOA is always used for receive.')

    def rcv_cmd_FT(self, msg):
        if msg[2] == '0':
            self._state.vfomode = VFOMode.SIMPLEX
        else:
            self._state.vfomode = VFOMode.DUPLEX

    def rcv_cmd_IF(self, msg):
        assert(msg[30] == '0')
        is_tx = (msg[28] == '1')
        if is_tx:
            self.rcv_cmd_FB(msg)
            self._state.txstate = PTT.TX
            vfo = VFO.VFOB
        else:
            self.rcv_cmd_FA(msg)
            self._state.txstate = PTT.RX
            vfo = VFO.VFOA
        self._internal_mode[vfo - 1] = int(msg[29])
        self._data_submode = int(msg[34])
        self._set_mode(vfo)

        if msg[32] == '1':
            self._state.vfmode = VFOMode.DUPLEX
        else:
            self._state.vfmode = VFOMode.SIMPLEX

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
        if msg[2] == '$':
            vfo = VFO.VFOB
            self._internal_mode[vfo - 1] = int(msg[3])
        else:
            vfo = VFO.VFOA
            self._internal_mode[vfo - 1] = int(msg[2])
        self._set_mode(vfo)

    def set_activefreq(self, freq):
        cmd = f'FA{freq:011d};'
        self._send(cmd)

    def set_activemode(self, mode, passband):
        mode = getattr(Mode, mode)
        (modeval, dataval) = self.MODE_MAP_TO[mode]
        self._send(f'MD{modeval};')
        if dataval:
            self._send(f'DT{dataval};')

    def set_activevfo(self, vfo):
        logging.error('Elecraft KX-3 does not support setting the vfo')

    def set_splitfreq(self, freq):
        cmd = f'FB{freq:011d};'
        self._send(cmd)

    def set_splitmode(self, mode, passband):
        mode = getattr(Mode, mode)
        (modeval, dataval) = self.MODE_MAP_TO[mode]
        self._send(f'MD${modeval};')
        self._send(f'DT{dataval};')

    def set_split(self, onoff, splitvfo):
        if onoff:
            self._send('FT1;')
        else:
            self._send('FT0;')

    def set_powerstate(self, val):
        self._send(f'PS{val};')

    def set_ptt(self, ptt):
        # TODO only responds when using AI
        # so need to update state when in poll/query mode
        if ptt == PTT.RX:
            self._state.txstate = PTT.RX
            self._send('RX;')
        elif ptt in (PTT.TX, PTT.TX_MIC, PTT.TX_DATA):
            self._state.txstate = PTT.TX
            self._send('TX;')
        #else TODO

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
        self._send('RX;')
