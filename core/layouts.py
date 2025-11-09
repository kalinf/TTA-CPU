from amaranth import *
from amaranth.hdl.rec import Layout

__all__ = ["InstrucionLayout", "DataLayout"]


def InstructionLayout(src_addr_width=7, dest_addr_width=8):
    return Layout(
        [
            ("constant", 1),
            ("src_addr", src_addr_width),
            ("dst_addr", dest_addr_width),
        ]
    )


def DataLayout(data_width=16):
    return Layout(
        [
            ("data", data_width),
        ]
    )
