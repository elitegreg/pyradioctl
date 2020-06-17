from .hamlib.formatters import CapabilitiesFormatter
from .vfos import VFO

import asyncio
import logging


_cmd_map = {
    'F' : 'set_freq',
    'f' : 'get_freq',
    'M' : 'set_mode',
    'm' : 'get_mode',
    'V' : 'set_vfo',
    'v' : 'get_vfo',
    'J' : 'set_rit',
    'j' : 'get_rit',
    'Z' : 'set_xit',
    'z' : 'get_xit',
    'T' : 'set_ptt',
    't' : 'get_ptt',
    '\x8b' : 'get_dcd',
    'R' : 'set_rptr_shift',
    'r' : 'get_rptr_shift',
    'O' : 'set_rptr_offs',
    'o' : 'get_rptr_offs',
    'C' : 'set_ctcss_tone',
    'c' : 'get_ctcss_tone',
    'D' : 'set_dcs_code',
    'd' : 'get_dcs_code',
    '\x90' : 'set_ctcss_sql',
    '\x91' : 'get_ctcss_sql',
    '\x92' : 'set_dcs_sql',
    '\x93' : 'get_dcs_sql',
    'I' : 'set_split_freq',
    'i' : 'get_split_freq',
    'X' : 'set_split_mode',
    'x' : 'get_split_mode',
    'S' : 'set_split_vfo',
    's' : 'get_split_vfo',
    'N' : 'set_ts',
    'n' : 'get_ts',
    'U' : 'set_func',
    'u' : 'get_func',
    'L' : 'set_level',
    'l' : 'get_level',
    'P' : 'set_parm',
    'p' : 'get_parm',
    'B' : 'set_bank',
    'E' : 'set_mem',
    'e' : 'get_mem',
    'G' : 'vfo_op',
    'g' : 'scan',
    'H' : 'set_channel',
    'h' : 'get_channel',
    'A' : 'set_trn',
    'a' : 'get_trn',
    'Y' : 'set_ant',
    'y' : 'get_ant',
    '*' : 'reset',
    'b' : 'send_morse',
    '\x87' : 'set_powerstat',
    '\x88' : 'get_powerstat',
    '\x89' : 'send_dtmf',
    '\x8a' : 'recv_dtmf',
    '_' : 'get_info',
    '1' : 'dump_caps',
    '2' : 'power2mW',
    '4' : 'mW2power',
    'w' : 'send_cmd',
}


_cmd_args = {
    'set_freq' : 1,
    'get_freq' : 0,
    'set_mode' : 2,
    'get_mode' : 0,
    'set_vfo' : 1,
    'get_vfo' : 0,
    'set_rit' : 0,
    'get_rit' : 0,
    'set_xit' : 0,
    'get_xit' : 0,
    'set_ptt' : 0,
    'get_ptt' : 0,
    'get_dcd' : 0,
    'set_rptr_shift' : 0,
    'get_rptr_shift' : 0,
    'set_rptr_offs' : 0,
    'get_rptr_offs' : 0,
    'set_ctcss_tone' : 0,
    'get_ctcss_tone' : 0,
    'set_dcs_code' : 0,
    'get_dcs_code' : 0,
    'set_ctcss_sql' : 0,
    'get_ctcss_sql' : 0,
    'set_dcs_sql' : 0,
    'get_dcs_sql' : 0,
    'set_split_freq' : 0,
    'get_split_freq' : 0,
    'set_split_mode' : 0,
    'get_split_mode' : 0,
    'set_split_vfo' : 0,
    'get_split_vfo' : 0,
    'set_ts' : 0,
    'get_ts' : 0,
    'set_func' : 0,
    'get_func' : 0,
    'set_level' : 0,
    'get_level' : 0,
    'set_parm' : 0,
    'get_parm' : 0,
    'set_bank' : 0,
    'set_mem' : 0,
    'get_mem' : 0,
    'vfo_op' : 0,
    'scan' : 0,
    'set_channel' : 0,
    'get_channel' : 0,
    'set_trn' : 0,
    'get_trn' : 0,
    'set_ant' : 0,
    'get_ant' : 0,
    'reset' : 0,
    'send_morse' : 1,
    'cancel_morse' : 0,
    'set_powerstat' : 1,
    'get_powerstat' : 0,
    'send_dtmf' : 0,
    'recv_dtmf' : 0,
    'get_info' : 0,
    'dump_caps' : 0,
    'power2mW' : 0,
    'mW2power' : 0,
    'send_cmd' : 0,
}


def parse_command(cmdline):
    if cmdline.startswith('b'): # special case for morse code
        yield ('send_morse', cmdline[1:].strip())
        return

    cmdfields = cmdline.split()

    while cmdfields:
        if cmdfields[0][0] == '\\':
            cmd = cmdfields.pop(0).lstrip('\\')
        else:
            cmds = []
            for c in cmdfields.pop(0): # each char
                # TODO allow "F 7074000 mv"
                cmds.append(_cmd_map.get(c, 'unknown'))
            while cmds:
                cmd = cmds.pop(0)
                if len(cmds) > 0:
                    yield (cmd,)

        argcount = _cmd_args.get(cmd, 0)
        args = cmdfields[0:argcount]
        yield (cmd, *args)
        cmdfields = cmdfields[argcount:]


class Session:
    def __init__(self, rig, stream_reader, stream_writer):
        self._rig = rig
        self._stream_reader = stream_reader
        self._stream_writer = stream_writer

    @property
    def rigcap(self):
        return self._rig.capabilities

    @property
    def rigproto(self):
        return self._rig.protocol

    @property
    def rigstate(self):
        return self._rig.state

    async def run(self):
        logging.debug('New session')
        while True:
            line = await self._stream_reader.readline()
            if not line:
                break

            try:
                line = line.decode('latin_1').strip()
            except:
                logging.exception('Failed decoding while reading from rigctld')
                continue


            logging.debug('Command(s) received: %s', line)

            for cmd in parse_command(line):
                try:
                    logging.info('Dispatch command: %s', cmd)
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
        caps = CapabilitiesFormatter(self._rig.capabilities)
        self._stream_writer.write(str(caps).encode())

    async def cmd_get_freq(self, cmd):
        state = self.rigstate
        freq = state.getvfo(state.rxvfo)
        self._stream_writer.write('{:d}\n'.format(freq).encode())

    async def cmd_set_freq(self, cmd, freq):
        freq = int(float(freq))
        self.rigproto.set_rxfreq(freq)

    async def cmd_get_mode(self, cmd):
        state = self.rigstate
        mode = str(state.rxmode)
        self._stream_writer.write(f'{mode}\n0\n'.encode())

    async def cmd_set_mode(self, cmd, mode, passband):
        if mode == '?':
            rxfreq = self.rigstate.rxfreq
            modes = self.rigcaps.modes_for(rxfreq)
            modes = ' '.join((str(mode) for mode in modes))
            self._stream_writer.write(f'{modes}\n'.encode())
        else:
            passband = int(passband)
            self.rigproto.set_rxmode(mode, passband)

    #async def cmd_get_split_freq(self, cmd):
        #freq = await self.rigproto.get_tx_vfo_freq()
        #self._stream_writer.write('{:d}\n'.format(freq).encode())

    #async def cmd_set_split_freq(self, cmd, freq):
        #freq = int(float(freq))
        #await self.rigproto.set_tx_vfo_freq(freq)

    #async def cmd_set_split_vfo(self, cmd, onoff, vfo):
        #vfoflag = getattr(VFO, vfo.decode().upper())
        #await self.rigproto.set_tx_vfo(onoff == b'1', vfoflag)

    async def cmd_get_vfo(self, cmd):
        state = self.rigstate
        vfo = str(state.rxvfo)
        self._stream_writer.write(f'{vfo}\n'.encode())

    async def cmd_set_vfo(self, cmd, vfo):
        vfoflag = getattr(VFO, vfo.upper())
        self.rigproto.set_rxvfo(vfoflag)

    async def cmd_send_morse(self, cmd, buf):
        self.rigproto.send_morse(buf)

    async def cmd_cancel_morse(self, cmd):
        self.rigproto.cancel_morse()

    async def cmd_set_powerstat(self, cmd, val):
        self.rigproto.set_powerstate(int(val))


class Server:
    def __init__(self, rig):
        self._rig = rig

    async def start(self, host='127.0.0.1', port=4532, loop=None):
        logging.info('TCP server started on %s:%s', host, port)
        await asyncio.start_server(
            self.handle_new_connection,
            host,
            port,
            loop=loop)

    def handle_new_connection(self, stream_reader, stream_writer):
        session = Session(self._rig, stream_reader, stream_writer)
        asyncio.Task(session.run())


if __name__ == '__main__':
    import unittest

    class CommandParserTestCase(unittest.TestCase):
        def test_zero_args(self):
            cmdline = 'fmv'
            cmds = list(parse_command(cmdline))
            self.assertEqual(3, len(cmds))
            self.assertEqual(('get_freq',), cmds[0])
            self.assertEqual(('get_mode',), cmds[1])
            self.assertEqual(('get_vfo',), cmds[2])

            cmdline = 'f m v'
            cmds = list(parse_command(cmdline))
            self.assertEqual(3, len(cmds))
            self.assertEqual(('get_freq',), cmds[0])
            self.assertEqual(('get_mode',), cmds[1])
            self.assertEqual(('get_vfo',), cmds[2])

            cmdline = '\get_freq \get_mode'
            cmds = list(parse_command(cmdline))
            self.assertEqual(2, len(cmds))
            self.assertEqual(('get_freq',), cmds[0])
            self.assertEqual(('get_mode',), cmds[1])

            cmdline = '\get_freq mv'
            cmds = list(parse_command(cmdline))
            self.assertEqual(3, len(cmds))
            self.assertEqual(('get_freq',), cmds[0])
            self.assertEqual(('get_mode',), cmds[1])
            self.assertEqual(('get_vfo',), cmds[2])

        def test_with_args(self):
            cmdline = 'fmvF 7074000 \set_mode PKTUSB 2700'
            cmds = list(parse_command(cmdline))
            self.assertEqual(5, len(cmds))
            self.assertEqual(('get_freq',), cmds[0])
            self.assertEqual(('get_mode',), cmds[1])
            self.assertEqual(('get_vfo',), cmds[2])
            self.assertEqual(('set_freq', '7074000'), cmds[3])
            self.assertEqual(('set_mode', 'PKTUSB', '2700'), cmds[4])

    unittest.main()
