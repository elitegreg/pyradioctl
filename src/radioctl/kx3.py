from .antennas import Antenna
from .bands import Band
from .elecraft import ElecraftProtocol
from .modes import Mode
from .radio_registry import register_radio
from .rig import Rig
from .vfos import VFO

from copy import deepcopy


class KX3(Rig):
    @staticmethod
    def rig_name():
        return 'Elecraft KX-3'

    def __init__(self, **kwargs):
        super().__init__(self.rig_name(), kwargs['itu_region'], lambda state: ElecraftProtocol(state))
        self._setup_capabilities()

    def _setup_capabilities(self):
        all_modes = (Mode.AM | Mode.CW | Mode.CWR | Mode.FM | Mode.LSB |
                     Mode.PKTLSB | Mode.PKTUSB | Mode.RTTY | Mode.RTTYR |
                     Mode.USB)
        all_vfos = (VFO.VFOA | VFO.VFOB)

        rxband1 = Band()
        rxband1.set_freq(310000, 32000000)
        rxband1.add_modes(all_modes)
        rxband1.add_vfos(all_vfos)
        rxband1.add_antennas(Antenna.ANT_1)
        self.capabilities.add_rx_band(rxband1)

        rxband2 = Band()
        rxband2.set_freq(44000000, 54000000)
        rxband2.add_modes(all_modes)
        rxband2.add_vfos(all_vfos)
        rxband2.add_antennas(Antenna.ANT_1)
        self.capabilities.add_rx_band(rxband2)

        txband160 = Band()
        txband160.set_freq(1800000, 2000000)
        txband160.add_modes(all_modes)
        txband160.add_vfos(all_vfos)
        txband160.add_antennas(Antenna.ANT_1)
        txband160.set_power(Band.AllModes, 10, 15000)
        self.capabilities.add_tx_band(txband160)

        txband80 = deepcopy(txband160)
        txband80.set_freq(3500000, 4000000)
        self.capabilities.add_tx_band(txband80)

        txband60 = deepcopy(txband160)
        txband60.set_freq(5250000, 5450000)
        self.capabilities.add_tx_band(txband60)

        txband40 = deepcopy(txband160)
        txband40.set_freq(7000000, 7300000)
        self.capabilities.add_tx_band(txband40)

        txband30 = deepcopy(txband160)
        txband30.set_freq(10100000, 10150000)
        self.capabilities.add_tx_band(txband30)

        txband20 = deepcopy(txband160)
        txband20.set_freq(14000000, 14350000)
        self.capabilities.add_tx_band(txband20)

        txband17 = deepcopy(txband160)
        txband17.set_freq(18068000, 18168000)
        txband17.set_power(Band.AllModes, 10, 10000)
        self.capabilities.add_tx_band(txband17)

        txband15 = deepcopy(txband17)
        txband15.set_freq(21000000, 21450000)
        self.capabilities.add_tx_band(txband15)

        txband12 = deepcopy(txband17)
        txband12.set_freq(24890000, 24990000)
        txband12.set_power(Band.AllModes, 10, 8000)
        self.capabilities.add_tx_band(txband12)

        txband10 = deepcopy(txband12)
        txband10.set_freq(28000000, 29700000)
        self.capabilities.add_tx_band(txband10)

        txband6 = deepcopy(txband12)
        txband6.set_freq(50000000, 54000000)
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


register_radio('KX-3', KX3)
register_radio(KX3.rig_name(), KX3)

