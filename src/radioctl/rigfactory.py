from .capabilities import load_rig_definition
from .msgbus import MsgBus
from .protocol import factory
from .radio_registry import radio_definition
from .rig import *


def create_rig(name, cfg, itu_region):
    assert(itu_region in (1, 2, 3))
    rig_def = radio_definition(name)
    caps = load_rig_definition(rig_def, itu_region)
    protocol_name = rig_def['protocol']
    dialect_name = rig_def['dialect']
    protocol = factory.create_protocol(
        protocol_name, dialect_name, cfg, MsgBus(), rig_def)
    return Rig(caps, protocol)
