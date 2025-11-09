from amaranth import *
from typing import final
from .layouts import DataLayout, InstructionLayout
from .bus import Bus
import json


class TTA_Core(Elaboratable):
    """
    Parameters
    ----------
    src_addr_width: int
        ...
    dest_addr_width: int
        ...
    data_width: int
        ...
    FUs
        ...
    """

    def __init__(self, src_addr_width, dest_addr_width, data_width, FUs):
        self.instr_layout = InstructionLayout(src_addr_width=src_addr_width, dest_addr_width=dest_addr_width)
        self.data_layout = DataLayout(data_width=data_width)
        self.FUs = FUs

    def elaborate(self, platform):
        m = Module()

        m.submodules.data_bus = data_bus = Bus(self.data_layout)
        m.submodules.instr_bus = instr_bus = Bus(self.instr_layout)

        for fu in self.FUs:
            m.submodules[fu[0]] = fu[1](instr_bus, data_bus)

        return m
