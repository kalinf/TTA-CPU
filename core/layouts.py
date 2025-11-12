from amaranth import *
from amaranth.lib.data import StructLayout

__all__ = ["InstrucionLayout", "DataLayout"]


def InstructionLayout(src_addr_width=7, dest_addr_width=8):
    return StructLayout(
        {"constant": 1, "src_addr": src_addr_width, "dst_addr": dest_addr_width},
    )


def DataLayout(data_width=16):
    return StructLayout(
        {"data": data_width},
    )
