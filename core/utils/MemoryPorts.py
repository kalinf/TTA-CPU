from amaranth import *
from amaranth.utils import ceil_log2


class ReadPort:
    def __init__(self, depth, shape):
        self.en = Signal(init=1, name="read_port_en")
        self.addr = Signal(ceil_log2(depth), name="read_port_addr")
        self.data = Signal(shape, name="read_port_data")


class WritePort:
    def __init__(self, depth, shape):
        self.en = Signal(init=1, name="write_port_en")
        self.addr = Signal(ceil_log2(depth), name="write_port_addr")
        self.data = Signal(shape, name="write_port_data")
