from amaranth import *
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu


class Adder(FU):
    def __init__(
        self, instr_bus: Bus, data_bus: Bus, input_count: int, output_count: int, address: int, trigger_pos: int
    ):
        super().__init__(
            instr_bus=instr_bus,
            data_bus=data_bus,
            input_count=input_count,
            output_count=output_count,
            address=address,
            trigger_pos=trigger_pos,
        )

    def elaborate(self, platform):
        m = super().elaborate(platform)

        with m.If(self.instr_bus.data.dst_addr == self.trigger_addr):
            # place for your code
            # m.d.falling += ...
            ...

        return m


register_fu("Adder", Adder)
