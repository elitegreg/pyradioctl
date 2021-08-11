from radioctl.capabilities import *
from radioctl.hamlib.formatters import *

import os
import unittest
import yaml

RIGSDB = os.getenv('RIGSDB')

class ElecraftK3Capabilities(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(RIGSDB, 'elecraft_k3.yaml')) as f:
            rig_def = yaml.full_load(f)
        self.caps = load_rig_definition(rig_def, itu_region=2)

    def test_capabilities(self):
        expected_modes = frozenset('AM CW CWR FM LSB PKTLSB PKTUSB RTTY RTTYR USB'.split())
        expected_vfos = frozenset('A B'.split())
        self.assertEquals(expected_modes, self.caps.modes)
        self.assertEquals(expected_vfos, self.caps.vfos)
        self.assertEquals((0.01, 100), self.caps.rf_power)
        # TODO more here

    def test_hamlib_dump_state(self):
        f = CapabilitiesFormatter(self.caps)
        expected = \
'''0
2
2
310000 32000000 0xdbf 0 0 0x3 0x0
44000000 54000000 0xdbf 0 0 0x3 0x0
0 0 0 0 0 0 0
1800000 2000000 0xdbf 10 100000 0x3 0x0
3500000 4000000 0xdbf 10 100000 0x3 0x0
5330500 5406500 0xdbf 10 100000 0x3 0x0
7000000 7300000 0xdbf 10 100000 0x3 0x0
10100000 10150000 0xdbf 10 100000 0x3 0x0
14000000 14350000 0xdbf 10 100000 0x3 0x0
18068000 18168000 0xdbf 10 100000 0x3 0x0
21000000 21450000 0xdbf 10 100000 0x3 0x0
24890000 24990000 0xdbf 10 100000 0x3 0x0
28000000 29700000 0xdbf 10 100000 0x3 0x0
50000000 54000000 0xdbf 10 100000 0x3 0x0
0 0 0 0 0 0 0
0 0
0 0
0
0
0
0
0
0
0x0
0x0
0x0
0x0
0x0
0x0
'''
        self.assertEquals(expected, str(f))
