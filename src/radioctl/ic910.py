from .icom import IcomXcvr
from .rigcap import *

from copy import deepcopy


class IC910(IcomXcvr):
    @staticmethod
    def rig_name():
        return 'Icom IC-910'

    @staticmethod
    def capabilities(itu_region):
        # TODO support other itu regions
        caps = RigCapabilities(IC910.rig_name(), itu_region)

        rband_2m = Band()
        rband_2m.set_freq(136000000, 174000000)
        rband_2m.add_mode(Mode.CW)
        rband_2m.add_mode(Mode.LSB)
        rband_2m.add_mode(Mode.USB)
        rband_2m.add_mode(Mode.FM)
        rband_2m.add_vfo(VFO.VFO_A)
        rband_2m.add_vfo(VFO.VFO_B)
        rband_2m.add_vfo(VFO.SUB)
        rband_2m.add_vfo(VFO.MAIN)
        rband_2m.add_vfo(VFO.MEM)
        caps.add_rx_band(rband_2m)

        tband_2m = deepcopy(rband_2m)
        tband_2m.set_freq(144000000, 148000000)
        tband_2m.set_power(5000, 100000)
        caps.add_tx_band(tband_2m)

        rband_70cm = deepcopy(rband_2m)
        rband_70cm.set_freq(420000000, 480000000)
        caps.add_rx_band(rband_70cm)

        tband_70cm = deepcopy(rband_70cm)
        tband_70cm.set_freq(420000000, 450000000)
        tband_70cm.set_power(5000, 75000)
        caps.add_tx_band(tband_70cm)

        rband_23cm = deepcopy(rband_70cm)
        rband_23cm.set_freq(1240000000, 1320000000)
        caps.add_rx_band(rband_23cm)

        tband_23cm = deepcopy(rband_23cm)
        tband_23cm.set_freq(1240000000, 1300000000)
        tband_23cm.set_power(1000, 10000)
        caps.add_tx_band(tband_23cm)

        caps.add_tuning_step(Mode.CW | Mode.LSB | Mode.USB, 1)
        caps.add_tuning_step(Mode.CW | Mode.LSB | Mode.USB, 10)
        caps.add_tuning_step(Mode.CW | Mode.LSB | Mode.USB, 50)
        caps.add_tuning_step(Mode.CW | Mode.LSB | Mode.USB, 100)
        caps.add_tuning_step(Mode.FM, 100)
        caps.add_tuning_step(Mode.FM, 5000)
        caps.add_tuning_step(Mode.FM, 6250)
        caps.add_tuning_step(Mode.FM, 10000)
        caps.add_tuning_step(Mode.FM, 12500)
        caps.add_tuning_step(Mode.FM, 20000)
        caps.add_tuning_step(Mode.FM, 25000)
        caps.add_tuning_step(Mode.FM, 100000)

        caps.add_filter(Mode.CW | Mode.LSB | Mode.USB, 2300)
        caps.add_filter(Mode.CW, 600)
        caps.add_filter(Mode.FM, 15000)
        caps.add_filter(Mode.FM, 6000)

        caps.add_preamp(20)
        caps.add_attenuator(20)

        caps.add_func(Function.FAGC)
        caps.add_func(Function.NB)
        caps.add_func(Function.COMP)
        caps.add_func(Function.VOX)
        caps.add_func(Function.TONE)
        caps.add_func(Function.TSQL)
        caps.add_func(Function.FBKIN)
        caps.add_func(Function.ANF)
        caps.add_func(Function.NR)
        caps.add_func(Function.AFC)
        caps.add_func(Function.SATMODE)
        caps.add_func(Function.SCOPE)
        caps.add_func(Function.RESUME, getit=False)

        caps.add_level(Level.PREAMP)
        caps.add_level(Level.ATT)
        caps.add_level(Level.VOXDELAY)
        caps.add_level(Level.AF)
        caps.add_level(Level.RF)
        caps.add_level(Level.SQL)
        caps.add_level(Level.IF)
        caps.add_level(Level.NR)
        caps.add_level(Level.CWPITCH)
        caps.add_level(Level.RFPOWER)
        caps.add_level(Level.MICGAIN)
        caps.add_level(Level.KEYSPD)
        caps.add_level(Level.COMP)
        caps.add_level(Level.VOXGAIN)
        caps.add_level(Level.ANTIVOX)
        caps.add_level(Level.RAWSTR, setit=False)
        caps.add_level(Level.STRENGTH, setit=False)

        return caps

