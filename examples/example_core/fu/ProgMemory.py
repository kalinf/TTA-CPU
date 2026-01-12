from amaranth import *
from core.utils.MemoryPorts import WritePort
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu


class ProgMemory(FU):
    """
    Modifies program memory.

    Communication ports:
    ----------
    2 Inputs:
        - 0: Write address
        - 1: Write data (triggers write)
    0 Outputs:
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
        instruction_memory_depth: int,
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

        self.instruction_memory_depth = instruction_memory_depth
        self.instr_write_port = WritePort(depth=instruction_memory_depth, shape=self.instr_bus.data.shape())

    def elaborate(self, platform):
        m = super().elaborate(platform)

        m.d.comb += [
            self.instr_write_port.addr.eq(self.inputs[0]["data"]),
            self.instr_write_port.data.constant.eq(self.inputs[1]["data"][15]),
            self.instr_write_port.data.src_addr.eq(self.inputs[1]["data"][5:15]),
            self.instr_write_port.data.dst_addr.eq(self.inputs[1]["data"][0:5]),
        ]

        with m.If(self.instr_bus.data.dst_addr == self.inputs[1]["addr"]):
            m.d.falling += self.instr_write_port.en.eq(1)
        with m.Else():
            m.d.falling += self.instr_write_port.en.eq(0)

        return m


register_fu("ProgMemory", ProgMemory)
