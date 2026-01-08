from amaranth import *
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu


class ConstantLoader(FU):
    """
    Loads constants wider than source addresses.

    Communication ports:
    ----------
    2 Inputs:
        0: lower bits of constant ([len(src_addr)-1:0])
        1: higher bits of constant  ([word_size-1:len(src_addr)])
    1 Outputs:
        0: concatenated input values
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

        # here you can react on writes into trigger addresses
        # here place your code, for example:
        # with m.If(self.instr_bus.data.dst_addr == self.inputs[0]["addr"]):
        #   m.d.falling += ...
        m.d.comb += self.outputs[0]["data"].eq(
            Cat(
                self.inputs[0]["data"][0 : len(self.instr_bus.data.src_addr)],
                self.inputs[1]["data"][0 : (len(self.data_bus.data.data) - len(self.instr_bus.data.src_addr))],
            )
        )

        return m


register_fu("ConstantLoader", ConstantLoader)
