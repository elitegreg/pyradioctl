_dialects = {}

def register_dialect(name, dialect_class):
    _dialects[name] = dialect_class

def create_dialect(cfg, name):
    return _dialects[name](cfg)
