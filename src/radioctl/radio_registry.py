from . import rigloader

import logging
import os

_radios = dict()

def register_radio(name, definition):
    _radios[name] = definition

def radio_definition(name):
    return _radios[name]

def radio_choices():
    return _radios.keys()

def clear():
    _radios.clear()

def load_all():
    rigsdb = os.getenv('RIGSDB', '/usr/share/pyradioctl/rigs')

    if not os.path.exists(rigsdb):
        raise FileNotFoundError(f"RIGSDB ({rigsdb}) does not exist")
    elif not os.path.isdir(rigsdb):
        raise FileNotFoundError(f"RIGSDB ({rigsdb}) is not a directory")

    listing = os.listdir(rigsdb)

    for rig_item in listing:
        if rig_item.endswith('.yaml'):
            try:
                (name, aliases, rig_definition) = \
                    rigloader.load_file(os.path.join(rigsdb, rig_item))
                register_radio(name, rig_definition)
                for alias in aliases:
                    register_radio(alias, rig_definition)
            except Exception as e:
                logging.exception("Unable to load rig definition: {}", rig_item)
