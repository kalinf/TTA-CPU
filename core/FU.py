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
        inout_count: int,
        input_address: int,
        output_address: int,
        inout_address: int,
    ):
        self.instr_bus = instr_bus
        self.data_bus = data_bus

        self.input_count = input_count
        self.output_count = output_count
        self.inout_count = inout_count

        self.input_address = input_address
        self.output_address = output_address
        self.inout_address = inout_address

        self.inputs = [
            {"addr": Const(self.input_address + i), "data": Signal.like(data_bus.data.data, name="input")}
            for i in range(self.input_count)
        ]
        self.outputs = [
            {"addr": Const(self.output_address + i), "data": Signal.like(data_bus.data.data, name="output")}
            for i in range(self.output_count)
        ]
        self.inouts = [
            {"addr": Const(self.inout_address + i), "data": Signal.like(data_bus.data.data, name="inout")}
            for i in range(self.inout_count)
        ]

    def elaborate(self, platform):
        m = Module()

        for i in range(self.input_count):
            with m.If(self.instr_bus.data.dst_addr == self.inputs[i]["addr"]):
                m.d.falling += self.inputs[i]["data"].eq(
                    Mux(~self.instr_bus.data.constant, self.data_bus.data.data, self.instr_bus.data.src_addr)
                )

        for i in range(self.output_count):
            with m.If((self.instr_bus.data.src_addr == self.outputs[i]["addr"]) & ~self.instr_bus.data.constant):
                m.d.rising += self.data_bus.data.data.eq(self.outputs[i]["data"])

        for i in range(self.inout_count):
            with m.If(self.instr_bus.data.dst_addr == self.inouts[i]["addr"]):
                m.d.falling += self.inouts[i]["data"].eq(
                    Mux(~self.instr_bus.data.constant, self.data_bus.data.data, self.instr_bus.data.src_addr)
                )
            with m.If((self.instr_bus.data.src_addr == self.inouts[i]["addr"]) & ~self.instr_bus.data.constant):
                m.d.rising += self.data_bus.data.data.eq(self.inouts[i]["data"])

        return m
