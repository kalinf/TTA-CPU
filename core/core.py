from amaranth import *
from typing import final
from layouts import DataLayout, InstructionLayout
from bus import Bus
import json


class TTA_Core(Elaboratable):
    def __init__(self, src_addr_width, dest_addr_width, data_width):
        self.instr_layout = InstructionLayout(src_addr_width=src_addr_width, dest_addr_width=dest_addr_width)
        self.data_layout = DataLayout(data_width=data_width)

    def elaborate(self, platform):
        m = Module()

        return m
