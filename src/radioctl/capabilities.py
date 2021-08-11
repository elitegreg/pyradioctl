from .bands import Band

def khz(x):
    return 1000*x

def mhz(x):
    return 1000000*x

_bands_by_itu = {
    2: {
        '2200m' : (135700, 137800),
        '630m' : (khz(472), khz(479)),
        '160m' : (khz(1800), mhz(2)),
        '80m' : (khz(3500), mhz(4)),
        '60m' : (5330500, 5406500),
        '40m' : (mhz(7), khz(7300)),
        '30m' : (khz(10100), khz(10150)),
        '20m' : (mhz(14), khz(14350)),
        '17m' : (khz(18068), khz(18168)),
        '15m' : (mhz(21), khz(21450)),
        '12m' : (khz(24890), khz(24990)),
        '10m' : (mhz(28), khz(29700)),
        '6m' : (mhz(50), mhz(54)),
        '2m' : (mhz(144), mhz(148)),
        '1.25m' : (mhz(222), mhz(225)),
        '70cm' : (mhz(420), mhz(450)),
        '33cm' : (mhz(902), mhz(928)),
        '23cm' : (mhz(1240), mhz(1300)),
    }
}


class Capabilities:
    def __init__(self, itu_region):
        self._itu_region = itu_region
        self._modes = set()
        self._vfos = set()
        self._rx_bands = []
        self._tx_bands = []
        self._rf_power = (0, 0)

    def add_modes(self, *modes):
        self._modes.update(set(modes))

    def add_vfos(self, *vfos):
        self._vfos.update(set(vfos))

    def add_rx_band(self, start, end):
        self._rx_bands.append(self._create_band(start, end, self._vfos))

    def add_tx_band(self, band_name):
        (start, end) = _bands_by_itu[self._itu_region][band_name]
        self._tx_bands.append(self._create_band(start, end, self._vfos, self._rf_power))

    def _create_band(self, start, end, vfos, rf_power=(0, 0)):
        band = Band()
        band.add_vfos(*vfos)
        band.set_freq_range(start, end)
        band.set_power(*rf_power)
        return band

    def set_rf_power(self, low, high):
        self._rf_power = (low, high)

    def freeze(self):
        self._modes = frozenset(self._modes)
        self._vfos = frozenset(self._vfos)
        self._rx_bands = tuple(self._rx_bands)
        self._tx_bands = tuple(self._tx_bands)

        for band in self._tx_bands:
            band.freeze()

    @property
    def itu_region(self):
        return self._itu_region

    @property
    def modes(self):
        return self._modes

    @property
    def rf_power(self):
        return self._rf_power

    @property
    def rx_bands(self):
        return self._rx_bands

    @property
    def tx_bands(self):
        return self._tx_bands

    @property
    def vfos(self):
        return self._vfos


def load_rig_definition(rig_def, itu_region):
    cap = Capabilities(itu_region)
    cap.add_modes(*rig_def['modes'])

    vfos = rig_def['vfos']
    if vfos == 'A/B':
        cap.add_vfos('A', 'B')
    else:
        raise RuntimeError(f'Unknown vfo type in rig definition: {vfos}')

    (rf_power_low, rf_power_high) = rig_def['rf_power'].split('-', 1)
    cap.set_rf_power(float(rf_power_low), float(rf_power_high))

    for band in rig_def['rx_bands']:
        (start, end) = band['range'].split('-', 1)
        cap.add_rx_band(int(start), int(end))

    for band in rig_def['tx_bands']:
        cap.add_tx_band(band)

    cap.freeze()
    return cap

