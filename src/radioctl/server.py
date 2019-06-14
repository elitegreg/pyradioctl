from radioctl.utils import logging
from radioctl.rigcap import VFO

import asyncio


_cmd_map = {
    b'F' : 'set_freq',
    b'f' : 'get_freq',
    b'M' : 'set_mode',
    b'm' : 'get_mode',
    b'V' : 'set_vfo',
    b'v' : 'get_vfo',
    b'J' : 'set_rit',
    b'j' : 'get_rit',
    b'Z' : 'set_xit',
    b'z' : 'get_xit',
    b'T' : 'set_ptt',
    b't' : 'get_ptt',
    b'\x8b' : 'get_dcd',
    b'R' : 'set_rptr_shift',
    b'r' : 'get_rptr_shift',
    b'O' : 'set_rptr_offs',
    b'o' : 'get_rptr_offs',
    b'C' : 'set_ctcss_tone',
    b'c' : 'get_ctcss_tone',
    b'D' : 'set_dcs_code',
    b'd' : 'get_dcs_code',
    b'\x90' : 'set_ctcss_sql',
    b'\x91' : 'get_ctcss_sql',
    b'\x92' : 'set_dcs_sql',
    b'\x93' : 'get_dcs_sql',
    b'I' : 'set_split_freq',
    b'i' : 'get_split_freq',
    b'X' : 'set_split_mode',
    b'x' : 'get_split_mode',
    b'S' : 'set_split_vfo',
    b's' : 'get_split_vfo',
    b'N' : 'set_ts',
    b'n' : 'get_ts',
    b'U' : 'set_func',
    b'u' : 'get_func',
    b'L' : 'set_level',
    b'l' : 'get_level',
    b'P' : 'set_parm',
    b'p' : 'get_parm',
    b'B' : 'set_bank',
    b'E' : 'set_mem',
    b'e' : 'get_mem',
    b'G' : 'vfo_op',
    b'g' : 'scan',
    b'H' : 'set_channel',
    b'h' : 'get_channel',
    b'A' : 'set_trn',
    b'a' : 'get_trn',
    b'Y' : 'set_ant',
    b'y' : 'get_ant',
    b'*' : 'reset',
    b'b' : 'send_morse',
    b'\x87' : 'set_powerstat',
    b'\x88' : 'get_powerstat',
    b'\x89' : 'send_dtmf',
    b'\x8a' : 'recv_dtmf',
    b'_' : 'get_info',
    b'1' : 'dump_caps',
    b'2' : 'power2mW',
    b'4' : 'mW2power',
    b'w' : 'send_cmd',
}


class Session:
    def __init__(self, rig, stream_reader, stream_writer):
        self._rig = rig
        self._stream_reader = stream_reader
        self._stream_writer = stream_writer

    async def run(self):
        logging.debug('New session')
        while True:
            cmdline = await self._stream_reader.readline()
            if not cmdline:
                break
            cmd = cmdline.strip().split()
            logging.debug('Command received: {}', cmd)
            if len(cmd[0]) == 1:
                cmd[0] = _cmd_map.get(cmd[0], 'unknown')
                logging.debug('...interpretted as: {}', cmd[0])
            else:
                cmd[0] = cmd[0].decode().lstrip('\\')

            try:
                cmd_func = getattr(self, 'cmd_{}'.format(cmd[0]), None)
                if cmd_func:
                    await cmd_func(*cmd)
                else:
                    raise NotImplementedError

                if cmd[0].startswith('set'):
                    self._stream_writer.write(b'RPRT 0\n')
            except Exception:
                logging.exception('Command Error:')
                self._stream_writer.write(b'RPRT -1\n')

        logging.debug('Disconnect')

    async def cmd_dump_state(self, cmd):
        self._stream_writer.write(self._rig.capabilities().format_for_rigctl().encode())

    async def cmd_get_freq(self, cmd):
        freq = await self._rig.get_active_vfo_freq()
        self._stream_writer.write('{:d}\n'.format(freq).encode())

    async def cmd_set_freq(self, cmd, freq):
        freq = int(float(freq))
        await self._rig.set_active_vfo_freq(freq)

    async def cmd_get_split_freq(self, cmd):
        freq = await self._rig.get_tx_vfo_freq()
        self._stream_writer.write('{:d}\n'.format(freq).encode())

    async def cmd_set_split_freq(self, cmd, freq):
        freq = int(float(freq))
        await self._rig.set_tx_vfo_freq(freq)

    async def cmd_set_split_vfo(self, cmd, onoff, vfo):
        vfoflag = getattr(VFO, vfo.decode().upper())
        await self._rig.set_tx_vfo(onoff == b'1', vfoflag)

    async def cmd_set_vfo(self, cmd, vfo):
        vfoflag = getattr(VFO, vfo.decode().upper())
        await self._rig.set_active_vfo(vfoflag)


class Server:
    def __init__(self, rig):
        self._rig = rig

    async def start(self, host='127.0.0.1', port=4532, loop=None):
        logging.info('TCP server started on {}:{}', host, port)
        await asyncio.start_server(
            self.handle_new_connection,
            host,
            port,
            loop=loop)

    def handle_new_connection(self, stream_reader, stream_writer):
        session = Session(self._rig, stream_reader, stream_writer)
        asyncio.Task(session.run())
