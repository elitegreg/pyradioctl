_all_protocols = {}

def register_protocol(name, protocol_class):
    _all_protocols[name] = protocol_class

def create_protocol(name, *args, **kwargs):
    protocol_class = _all_protocols[name]
    return protocol_class(*args, **kwargs)

