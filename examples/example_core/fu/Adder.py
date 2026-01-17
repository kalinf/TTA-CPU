from amaranth import *
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu


class Adder(FU):
    """
    Adds the operands.

    Communication ports:
    ----------
    2 Inputs:
    1 Outputs:
    0 Inouts:
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

        m.d.comb += self.outputs[0]["data"].eq(self.inputs[0]["data"] + self.inputs[1]["data"])

        return m


register_fu("Adder", Adder)
