FU_REGISTRY = {}
IP_REGISTRY = {}


def register_fu(name, cls):
    FU_REGISTRY[name] = cls


def register_ip(name, cls):
    IP_REGISTRY[name] = cls
