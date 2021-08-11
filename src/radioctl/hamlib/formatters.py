from .modes import Mode
from .vfos import VFO
from ..utils.bitwise import bit_or


_rigctld_prot_ver = 0


class BandFormatter:
    def __init__(self, band, modes):
        self._band = band
        self._modes = modes

    def __getattr__(self, name):
        return getattr(self._band, name)

    def __str__(self):
        # TODO f-string
        antennas = 0
        vfos = 0
        for vfo in self.vfos:
            vfos |= getattr(VFO, f'VFO{vfo}')

        rf_low = int(self.low_power * 1000) # milliwatts
        rf_high = int(self.high_power * 1000) # milliwatts

        return '{:d} {:d} 0x{:x} {:d} {:d} 0x{:x} 0x{:x}'.format(
            self.freq_range[0], self.freq_range[1], self._modes.value,
            rf_low, rf_high, vfos.value, antennas)
    

class CapabilitiesFormatter:
    def __init__(self, caps):
        self._caps = caps

    def __getattr__(self, name):
        return getattr(self._caps, name)

    def __str__(self):
        modes = 0
        for mode in self.modes:
            modes |= getattr(Mode, mode)

        rxbands = '\n'.join((str(BandFormatter(band, modes)) for band in self.rx_bands))
        txbands = '\n'.join((str(BandFormatter(band, modes)) for band in self.tx_bands))
        # TODO f-string
        return (
            '{}\n'
            '2\n' # rigctld
            '{}\n'
            '{}\n'
            '0 0 0 0 0 0 0\n'
            '{}\n'
            '0 0 0 0 0 0 0\n'
            #'{}\n' filters
            '0 0\n'
            #'{}\n' tuning steps
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
                0, #self._max_rit,
                0, #self._max_xit,
                0, #self._max_ifshift,
                0, #self._announces,
                0, #preamps,
                0, #attenuators,
                0, #bit_or(self._get_funcs),
                0, #bit_or(self._set_funcs),
                0, #bit_or(self._get_levels),
                0, #bit_or(self._set_levels),
                0, #bit_or(self._get_parms),
                0) #bit_or(self._set_parms))
