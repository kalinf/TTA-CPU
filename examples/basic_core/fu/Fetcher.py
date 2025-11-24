from amaranth import *
from core.utils.ReadPort import ReadPort
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu


class Fetcher(FU):
    """
    Fetches correct instruction from instruction memory.

    Communication ports:
    ----------
    2 Inputs:
        - 0: jump condition (if any bit is set, jump is taken)
        - 1: jump address
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
        instruction_memory_read_ports: int,
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
        self.instruction_memory_read_ports = instruction_memory_read_ports
        self.instr_read_ports = [
            ReadPort(depth=instruction_memory_depth, shape=self.instr_bus.data.shape())
            for _ in range(instruction_memory_read_ports)
        ]

    def elaborate(self, platform):
        m = super().elaborate(platform)

        jump_condition = Signal()
        following_addr = Signal().like(self.data_bus.data.data, name="following_addr")
        jump_addr = Signal().like(self.data_bus.data.data, name="jump_addr")
        taken_addr = Signal().like(self.data_bus.data.data, name="taken_addr")
        following_instr = Signal().like(self.instr_bus.data, name="following_instr")
        jump_instr = Signal().like(self.instr_bus.data, name="jump_instr")
        taken_instr = Signal().like(self.instr_bus.data, name="taken_instr")
        m.d.comb += [
            jump_condition.eq(
                Mux(
                    self.instr_bus.data.dst_addr == self.inputs[0]["addr"],
                    Mux(~self.instr_bus.data.constant, self.data_bus.data.data, self.instr_bus.data.src_addr),
                    self.inputs[0]["data"],
                ).any()
            ),
            jump_addr.eq(self.inputs[1]["data"]),
            jump_instr.eq(self.instr_read_ports[1].data),
            following_instr.eq(self.instr_read_ports[0].data),
        ]

        with m.If(jump_condition):
            m.d.comb += [taken_addr.eq(jump_addr), taken_instr.eq(jump_instr)]
        with m.Else():
            m.d.comb += [taken_addr.eq(following_addr), taken_instr.eq(following_instr)]

        m.d.mem += [
            self.instr_read_ports[0].addr.eq(following_addr),
            self.instr_read_ports[1].addr.eq(jump_addr),
        ]

        m.d.falling += [
            self.instr_bus.data.eq(taken_instr),
            following_addr.eq(taken_addr + 1),
        ]

        return m


register_fu("Fetcher", Fetcher)
