_radios = dict()

def register_radio(name, factory):
    _radios[name] = factory

def radio_factory(name):
    return _radios[name]

def radio_choices():
    return _radios.keys()
