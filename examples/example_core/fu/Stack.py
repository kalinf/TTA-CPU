from amaranth import *
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu


class Stack(FU):
    """
    Last In First Out Queue.

    Communication ports:
    ----------
    0 Inputs:
    0 Outputs:
        - 0: empty
        - 1: full
    1 Inouts:
        - 0: Top element
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

        depth = 16

        # inout register is stage 0
        stack = [Signal().like(self.data_bus.data.data, name=f"stack_stage{i}") for i in range(1, depth)]
        level = Signal(range(depth + 1))
        empty = Signal(init=1)
        full = Signal()
        m.d.comb += [
            empty.eq(level == 0),
            full.eq(level == depth),
            self.outputs[0]["data"].eq(empty),
            self.outputs[1]["data"].eq(full),
        ]
        with m.If(self.instr_bus.data.dst_addr == self.inouts[0]["addr"]):
            with m.If((self.instr_bus.data.src_addr != self.inouts[0]["addr"]) | self.instr_bus.data.constant):
                m.d.falling += level.eq(Mux(level < depth, level + 1, depth))
                for i in range(1, depth - 1):
                    m.d.falling += stack[i].eq(stack[i - 1])
                m.d.falling += stack[0].eq(self.inouts[0]["data"])
        with m.Elif((self.instr_bus.data.src_addr == self.inouts[0]["addr"]) & ~self.instr_bus.data.constant):
            m.d.falling += level.eq(Mux(level > 0, level - 1, 0))
            for i in range(depth - 2):
                m.d.falling += stack[i].eq(stack[i + 1])
            m.d.falling += self.inouts[0]["data"].eq(stack[0])

        return m


register_fu("Stack", Stack)
