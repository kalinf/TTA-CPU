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
        self.dest_addr_0 = Signal(name="dest_addr_0")
        self.dest_addr_1 = Signal(name="dest_addr_1")

    def elaborate(self, platform):
        m = super().elaborate(platform)

        m.d.comb += [
            self.dest_addr_0.eq(self.instr_bus.data.dst_addr == 0),
            self.dest_addr_1.eq(self.instr_bus.data.dst_addr == 1),
        ]

        with m.If(self.dest_addr_0):
            # place for your code
            m.d.falling += self.regs[2]["data"].eq(self.data_bus.data.data + self.regs[1]["data"])

        with m.If(self.dest_addr_1):
            # place for your code
            m.d.falling += self.regs[2]["data"].eq(self.data_bus.data.data + self.regs[0]["data"])

        return m


register_fu("Adder", Adder)
