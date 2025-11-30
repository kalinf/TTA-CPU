from amaranth import *

from core.FU import FU
from core.bus import Bus
from core.registry import register_fu


class Increaser(FU):
    """
    Increments the main value by another value during each readout. Previous value is returned.

    Communication ports:
    ----------
    0 Inputs:
    0 Outputs:
    2 Inouts:
        - 0: main value
        - 1: increment value
    """

    def __init__(
        self,
        instr_bus: Bus,
        data_bus: Bus,
        input_count: int,
        output_count: int,
        inout_count: int,
        input_address: int,
        inout_address: int,
        output_address: int,
    ):
        super().__init__(
            instr_bus=instr_bus,
            data_bus=data_bus,
            input_count=input_count,
            output_count=output_count,
            inout_count=inout_count,
            input_address=input_address,
            inout_address=inout_address,
            output_address=output_address,
        )

    def elaborate(self, platform):
        m = super().elaborate(platform)

        with m.If((self.instr_bus.data.src_addr == self.inouts[0]["addr"]) & ~self.instr_bus.data.constant):
            m.d.falling += self.inouts[0]["data"].eq(self.inouts[0]["data"] + self.inouts[1]["data"])

        return m


register_fu("Increaser", Increaser)
