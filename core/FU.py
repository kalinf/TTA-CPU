from amaranth import *
from typing import final, Iterable
from .bus import Bus

__all__ = ["FU"]


@final
class IncorrectTriggerPosition(Exception):
    """Exception raised when an incorrect trigger port position was entered."""


class FU(Elaboratable):
    def __init__(
        self,
        instr_bus: Bus,
        data_bus: Bus,
        input_count: int,
        output_count: int,
        address: int,
        trigger_pos: Iterable[int],
    ):
        self.instr_bus = instr_bus
        self.data_bus = data_bus

        self.input_count = input_count
        self.output_count = output_count
        self.port_count = self.input_count + self.output_count

        self.address = address
        for trigger in trigger_pos:
            if trigger >= self.port_count:
                raise IncorrectTriggerPosition(
                    f"Given trigger port position {trigger} is greater than number of ports ({self.port_count}) of functional unit."
                )
        self.trigger_pos = trigger_pos
        self.trigger_addrs = [Const(self.address + trigger) for trigger in trigger_pos]
        self.regs = [
            {"addr": Const(self.address + i), "data": Signal.like(data_bus.data.data)} for i in range(self.port_count)
        ]

    def elaborate(self, platform):
        m = Module()

        for i in range(self.port_count):
            if i < self.input_count:
                with m.If(self.instr_bus.data.dst_addr == self.regs[i]["addr"]):
                    m.d.falling += self.regs[i]["data"].eq(
                        Mux(~self.instr_bus.data.constant, self.data_bus.data.data, self.instr_bus.data.src_addr)
                    )
            else:
                with m.If((self.instr_bus.data.src_addr == self.regs[i]["addr"]) & ~self.instr_bus.data.constant):
                    m.d.rising += self.data_bus.data.data.eq(self.regs[i]["data"])

        return m
