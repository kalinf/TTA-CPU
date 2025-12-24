from amaranth import *
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu


class Regs(FU):
    """
    General purpose registers.

    Communication ports:
    ----------
    0 Inputs:
    0 Outputs:
    2 Inouts:
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

        # here you can react on writes into trigger addresses
        # here place your code, for example:
        # with m.If(self.instr_bus.data.dst_addr == self.inputs[0]["addr"]):
        #   m.d.falling += ...

        return m


register_fu("Regs", Regs)
