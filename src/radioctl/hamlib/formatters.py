from ..utils.bitwise import bit_or


_rigctld_prot_ver = 0


class BandFormatter:
    def __init__(self, band):
        self._band = band

    def __getattr__(self, name):
        return getattr(self._band, name)

    def __str__(self):
        # TODO f-string
        return '{:d} {:d} 0x{:x} {:d} {:d} 0x{:x} 0x{:x}'.format(
            self.freq_lower_bound, self.freq_upper_bound, self.modes.value,
            self.low_power, self.high_power, self.vfos.value,
            self.antennas.value)
    

class CapabilitiesFormatter:
    def __init__(self, caps):
        self._caps = caps

    def __getattr__(self, name):
        return getattr(self._caps, name)

    def __str__(self):
        # TODO remove private member access
        rxbands = '\n'.join((str(BandFormatter(band)) for band in self._rx_bands))
        txbands = '\n'.join((str(BandFormatter(band)) for band in self._tx_bands))
        tuning_steps = '\n'.join('0x{:x} {:d}'.format(ts[0].value, ts[1]) for ts in self._tuning_steps)
        filters = '\n'.join('0x{:x} {:d}'.format(f[0].value, f[1]) for f in self._filters)
        preamps = ' '.join((str(x) for x in self._preamps))
        attenuators = ' '.join((str(x) for x in self._attenuators))
        # TODO f-string
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
