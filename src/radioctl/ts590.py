from .antennas import Antenna
from .bands import Band
from .kenwood import KenwoodProtocol
from .modes import Mode
from .radio_registry import register_radio
from .rig import Rig
from .vfos import VFO

from copy import deepcopy


class TS590(Rig):
    @staticmethod
    def rig_name():
        return 'Kenwood TS-590'

    def __init__(self, itu_region, **kwargs):
        super().__init__(self.rig_name(), itu_region, lambda state: KenwoodProtocol(state))
        self._setup_capabilities(itu_region)

    def _setup_capabilities(self, itu_region):
        if itu_region not in {1, 2}:
            raise ValueError(f'Unsupported ITU region {itu_region}')
        
        all_modes = (Mode.AM | Mode.CW | Mode.CWR | Mode.FM | Mode.FMN |
                     Mode.LSB | Mode.PKTAM | Mode.PKTFM | Mode.PKTLSB |
                     Mode.PKTUSB | Mode.RTTY | Mode.RTTYR | Mode.USB)
        all_vfos = (VFO.VFOA | VFO.VFOB | VFO.MEM)
        tx_ants = (Antenna.ANT_1 | Antenna.ANT_2)

        rxband = Band()
        rxband.set_freq(30000, 59999999)
        rxband.add_modes(all_modes)
        rxband.add_vfos(all_vfos)
        rxband.add_antennas(Antenna.RXANT_1 | tx_ants)
        self.capabilities.add_rx_band(rxband)

        txband160 = Band()
        txband160.set_freq(1800000 if itu_region == 2 else 1810000,
                           2000000 if itu_region == 2 else 1850000)
        txband160.add_modes(all_modes)
        txband160.add_vfos(all_vfos)
        txband160.add_antennas(tx_ants)
        txband160.set_power(Band.AllModes, 5000, 100000)
        txband160.set_power(Mode.AM, 5000, 100000)
        self.capabilities.add_tx_band(txband160)

        txband80 = deepcopy(txband160)
        txband80.set_freq(3500000, 4000000 if itu_region == 2 else 3800000)
        self.capabilities.add_tx_band(txband80)

        if itu_region == 2:
            txband60 = deepcopy(txband160)
            txband60.set_freq(5250000, 5450000)
            self.capabilities.add_tx_band(txband60)

        txband40 = deepcopy(txband160)
        txband40.set_freq(7000000, 7300000 if itu_region == 2 else 7200000)
        self.capabilities.add_tx_band(txband40)

        txband30 = deepcopy(txband160)
        txband30.set_freq(10100000, 10150000)
        self.capabilities.add_tx_band(txband30)

        txband20 = deepcopy(txband160)
        txband20.set_freq(14000000, 14350000)
        self.capabilities.add_tx_band(txband20)

        txband17 = deepcopy(txband160)
        txband17.set_freq(18068000, 18168000)
        self.capabilities.add_tx_band(txband17)

        txband15 = deepcopy(txband160)
        txband15.set_freq(21000000, 21450000)
        self.capabilities.add_tx_band(txband15)

        txband12 = deepcopy(txband160)
        txband12.set_freq(24890000, 24990000)
        self.capabilities.add_tx_band(txband12)

        txband10 = deepcopy(txband160)
        txband10.set_freq(28000000, 29700000)
        self.capabilities.add_tx_band(txband10)

        txband6 = deepcopy(txband160)
        txband6.set_freq(50000000, 54000000 if itu_region == 2 else 52000000)
        self.capabilities.add_tx_band(txband6)

        self.capabilities.add_tuning_step(all_modes, 1)

        # TODO add data modes
        # TODO I don't think these are right
        self.capabilities.add_filter(Mode.LSB | Mode.USB, 2700)
        self.capabilities.add_filter(Mode.CW | Mode.CWR | Mode.RTTY | Mode.RTTYR, 500)
        self.capabilities.add_filter(Mode.FM, 12000)
        self.capabilities.add_filter(Mode.AM | Mode.FMN, 6000)

        self.capabilities.add_preamp(12)
        self.capabilities.add_attenuator(12)

        # TODO rit/xit/ifshift
        # TODO funcs levels


register_radio('TS-590', TS590)
register_radio(TS590.rig_name(), TS590)

