from amaranth import *
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu


class Looper(FU):
    """
    Loops through a range of numbers.

    Communication ports:
    ----------
    3 Inputs:
        - 0: start address
        - 1: end address
        - 2: step
    1 Outputs:
        - 0: current address
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
        fresh_data = Signal.like(self.data_bus.data.data, name="fresh_data")
        next_value = Signal.like(self.data_bus.data.data, name="next_value")
        m.d.comb += [
            fresh_data.eq(
                Mux(
                    ~self.instr_bus.data.constant,
                    self.data_bus.data.data,
                    self.instr_bus.data.src_addr,
                )
            ),
            next_value.eq(self.outputs[0]["data"] + self.inputs[2]["data"]),
        ]

        with m.If((self.instr_bus.data.dst_addr == self.inputs[0]["addr"])):
            m.d.falling += self.outputs[0]["data"].eq(fresh_data)

        with m.If((self.instr_bus.data.src_addr == self.outputs[0]["addr"]) & ~self.instr_bus.data.constant):
            m.d.falling += self.outputs[0]["data"].eq(
                Mux(
                    next_value <= self.inputs[1]["data"],
                    next_value,
                    self.inputs[0]["data"],
                )
            )

        return m


register_fu("Looper", Looper)
