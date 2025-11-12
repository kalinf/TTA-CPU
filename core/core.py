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
        self.instr_bus = Bus(self.instr_layout)
        self.data_bus = Bus(self.data_layout)

    def elaborate(self, platform):
        m = Module()

        m.domains.rising = cd_rising = ClockDomain(local=True)
        m.domains.falling = cd_falling = ClockDomain(local=True, clk_edge="neg")

        m.d.comb += [
            cd_falling.clk.eq(cd_rising.clk),
        ]

        m.submodules.data_bus = self.data_bus
        m.submodules.instr_bus = self.instr_bus

        for fu in self.FUs:
            m.submodules[fu[0]] = fu[1](instr_bus=self.instr_bus, data_bus=self.data_bus)
            setattr(self, fu[0], m.submodules[fu[0]])

        return m
