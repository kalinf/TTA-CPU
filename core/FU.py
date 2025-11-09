from amaranth import *
from typing import final
from layouts import DataLayout
from bus import Bus

__all__ = ["FU"]


@final
class IncorrectTriggerPosition(Exception):
    """Exception raised when an incorrect trigger port position was entered."""


class FU(Elaboratable):
    def __init__(
        self, instr_bus: Bus, data_bus: Bus, input_count: int, output_count: int, address: int, trigger_pos: int
    ):
        self.instr_bus = instr_bus
        self.data_bus = data_bus

        self.input_count = input_count
        self.output_count = output_count
        self.port_count = self.input_count + self.output_count

        self.address = address
        # niewykluczone, że chcę listę triggerów
        if trigger_pos >= self.port_count:
            raise IncorrectTriggerPosition(
                f"Given trigger port position {trigger_pos} is greater than number of ports ({self.port_count}) of functional unit."
            )
        self.trigger_pos = trigger_pos
        self.trigger_addr = Const(self.address + self.trigger_pos)
        self.regs = [{"addr": Const(self.address + i), "data": Signal(DataLayout)} for i in self.port_count]

    def elaborate(self, platform):
        m = Module()

        for i in self.port_count:
            if i < self.input_count:
                with m.If(self.instr_bus.data.dst_addr == self.regs[i]["addr"]):
                    m.d.falling += self.regs[i]["data"].eq(self.data_bus.data)
            else:
                with m.If(self.instr_bus.data.src_addr == self.regs[i]["addr"]):
                    m.d.rising += self.data_bus.data.eq(self.regs[i][1])

        return m
