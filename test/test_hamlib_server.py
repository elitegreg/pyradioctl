from radioctl.hamlib.server import *

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

