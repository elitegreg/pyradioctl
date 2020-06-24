from .modes import Mode
from .ptt import PTT
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

    PTT_MAP_FROM = {
        '0' : PTT.TX_MIC,
        '1' : PTT.TX_DATA,
        '2' : PTT.TUNE,
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
        self._send('RX;')
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
            self._state.activemode = self.MODE_MAP_FROM[(mode, data)]
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
        self._state.activevfo = self._decode_vfo(msg[2])

    def rcv_cmd_FT(self, msg):
        if self._state.splitvfo == self._state.activevfo:
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

    def rcv_cmd_RX(self, msg):
        self._state.txstate = PTT.RX;

    def rcv_cmd_TX(self, msg):
        self._state.txstate = self.PTT_MAP_FROM[msg[2]]

    def set_activefreq(self, freq):
        vfo = str(self._state.activevfo)[-1]
        cmd = f'F{vfo}{freq:011d};'
        self._send(cmd)

    def set_activemode(self, mode, passband):
        mode = getattr(Mode, mode)
        (modeval, dataval) = self.MODE_MAP_TO[mode]
        self._send(f'MD{modeval};')
        self._send(f'DA{int(dataval)};')

    def set_activevfo(self, vfo):
        self._send(f'FR{self._encode_vfo(vfo)};')

    def set_splitfreq(self, freq):
        vfo = str(self._state.splitvfo)[-1]
        cmd = f'F{vfo}{freq:011d};'
        self._send(cmd)

    def set_splitmode(self, mode, passband):
        state = self._state
        mode = getattr(Mode, mode)
        (modeval, dataval) = self.MODE_MAP_TO[mode]
        activevfo = self._state.activevfo
        splitvfo = self._state.splitvfo
        self.set_activevfo(splitvfo)
        self._send(f'MD{modeval};')
        self._send(f'DA{int(dataval)};')
        self.set_activevfo(activevfo)

    def set_splitvfo(self, vfo):
        self._send(f'FT{self._encode_vfo(vfo)};')

    def set_split(self, onoff, txvfo):
        if onoff:
            self.set_splitvfo(txvfo)
        else:
            self.set_splitvfo(self.state.activevfo)

    def set_powerstate(self, val):
        if val >= 2: # standby
            self._send('PS0;')
        elif val == 1:
            # TODO low current power up
            self._send('PS1;')
        elif val == 0:
            self._send('PS9;')
        #else TODO

    def set_ptt(self, ptt):
        # TODO only responds when using AI
        # so need to update state when in poll/query mode
        if ptt == PTT.RX:
            self._send('RX;')
        elif ptt in (PTT.TX, PTT.TX_MIC):
            self._send('TX0;')
        elif ptt == PTT.TX_DATA:
            self._send('TX1;')
        elif ptt == PTT.TUNE:
            self._send('TX2;')
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
        self._send('KY0;')

    def morse_speed(self, speed):
        speed = int(speed)
        if speed > 60: # TODO rig specific
            speed = 60
        elif speed < 4:
            speed = 4
        self._send(f'KS{speed:03d};')
