FU_REGISTRY = {}


def register_fu(name, cls):
    FU_REGISTRY[name] = cls
