from enum import auto, IntFlag


_rigctld_prot_ver = 0


Mode = IntFlag('Mode', 'AM CW USB LSB RTTY FM WFM CWR RTTYR AMS PKTLSB '
               'PKTUSB PKTFM ECSSUSB ECSSLSB FAX SAM SAL SAH DSB FMN '
               'PKTAM P25 DSTAR DPMR NXDNVN NXDN_N DXR AMN PSK PSKR DD')


Function = IntFlag('Function', 'FAGC NB COMP VOX TONE TSQL SBKIN FBKIN '
                   'ANF NR AIP APF MON MN RF ARO LOCK MUTE VSC REV SQL '
                   'ABM BC MBC RIT AFC SATMODE SCOPE RESUME TBURST TUNER '
                   'XIT NB2 DSQL AFLT ANL BC2 DUAL_WATCH DIVERSITY')

Level = IntFlag('Level', 'PREAMP ATT VOXDELAY AF RF SQL IF APF NR '
                'PBT_IN PBT_OUT CWPITCH RFPOWER MICGAIN KEYSPD NOTCHF '
                'COMP AGC BKINDL BALANCE METER VOXGAIN ANTIVOX SLOPE_LOW '
                'SLOPE_HIGH BKIN_DLYMS RAWSTR SQLSTAT SWR ALC STRENGTH '
                'EL_BWC RFPOWER_METER COMP_METER VD_METER ID_METER '
                'NOTCHF_RAW MONITOR_GAIN NB')

class VFO(IntFlag):
    VFOA = auto()
    VFOB = auto()
    VFOC = auto()
    SUB  = (1<<25)
    MAIN = (1<<26)
    VFO  = (1<<27)
    MEM  = (1<<28)

Antenna = IntFlag('Antenna', 'ANT_1 ANT_2 ANT_3 ANT_4 ANT_5')


def bit_or(bitset):
    r = 0
    for bit in bitset:
        r |= int(bit)
    return r


class Band:
    def __init__(self):
        self._freq_range = (None, None)
        self._modes = set()
        self._vfos = set()
        self._antennas = set()
        self._low_power = -1
        self._high_power = -1

    def add_mode(self, mode):
        self._modes.add(mode)

    def add_vfo(self, vfo):
        self._vfos.add(vfo)

    def add_antenna(self, antenna):
        self._antennas.add(antenna)

    def set_freq(self, start, end):
        self._freq_range = (start, end)

    def set_power(self, low_power, high_power):
        self._low_power = low_power
        self._high_power = high_power

    def format_for_rigctl(self):
        return '{:d} {:d} 0x{:x} {:d} {:d} 0x{:x} 0x{:x}'.format(
            self._freq_range[0], self._freq_range[1], bit_or(self._modes),
            self._low_power, self._high_power, bit_or(self._vfos),
            bit_or(self._antennas))


class RigCapabilities:
    def __init__(self, model, itu_region):
        self._model = model
        self._itu_region = itu_region
        self._rx_bands = []
        self._tx_bands = []
        self._tuning_steps = []
        self._filters = []
        self._max_rit = 0
        self._max_xit = 0
        self._max_ifshift = 0
        self._announces = 0
        self._preamps = []
        self._attenuators = []
        self._get_funcs = set()
        self._set_funcs = set()
        self._get_levels = set()
        self._set_levels = set()
        self._get_parms = set()
        self._set_parms = set()

    def add_rx_band(self, band):
        self._rx_bands.append(band)

    def add_tx_band(self, band):
        self._tx_bands.append(band)

    def add_tuning_step(self, modes, step):
        self._tuning_steps.append((modes, step))

    def add_filter(self, modes, filter_width):
        self._filters.append((modes, filter_width))

    def add_preamp(self, preamp):
        self._preamps.append(preamp)

    def add_attenuator(self, att):
        self._attenuators.append(att)

    def add_func(self, func, getit=True, setit=True):
        if getit:
            self._get_funcs.add(func)
        if setit:
            self._set_funcs.add(func)

    def add_level(self, level, getit=True, setit=True):
        if getit:
            self._get_levels.add(level)
        if setit:
            self._set_levels.add(level)

    def add_parm(self, parm, getit=True, setit=True):
        if getit:
            self._get_parms.add(parm)
        if setit:
            self._set_parms.add(parm)

    def set_max_rit(self, maxrit):
        self._max_rit = maxrit

    def set_max_xit(self, maxxit):
        self._max_xit = maxxit

    def set_max_ifshift(self, maxifshift):
        self._max_ifshift = maxifshift

    def set_announces(self, announces):
        self._announces = announces

    def format_for_rigctl(self):
        rxbands = '\n'.join((band.format_for_rigctl() for band in self._rx_bands))
        txbands = '\n'.join((band.format_for_rigctl() for band in self._tx_bands))
        tuning_steps = '\n'.join('0x{:x} {:d}'.format(ts[0], ts[1]) for ts in self._tuning_steps)
        filters = '\n'.join('0x{:x} {:d}'.format(f[0], f[1]) for f in self._filters)
        preamps = ' '.join((str(x) for x in self._preamps))
        attenuators = ' '.join((str(x) for x in self._attenuators))
        return (
            '{}\n'
            '2\n' # rigctld
            '{}\n'
            '{}\n'
            '0 0 0 0 0 0 0\n'
            '{}\n'
            '0 0 0 0 0 0 0\n'
            '{}\n'
            '0 0\n'
            '{}\n'
            '0 0\n'
            '{}\n'
            '{}\n'
            '{}\n'
            '{}\n'
            '{}\n'
            '{}\n'
            '0x{:x}\n'
            '0x{:x}\n'
            '0x{:x}\n'
            '0x{:x}\n'
            '0x{:x}\n'
            '0x{:x}\n'
            ).format(
                _rigctld_prot_ver,
                self._itu_region,
                rxbands,
                txbands,
                tuning_steps,
                filters,
                self._max_rit,
                self._max_xit,
                self._max_ifshift,
                self._announces,
                preamps,
                attenuators,
                bit_or(self._get_funcs),
                bit_or(self._set_funcs),
                bit_or(self._get_levels),
                bit_or(self._set_levels),
                bit_or(self._get_parms),
                bit_or(self._set_parms))

