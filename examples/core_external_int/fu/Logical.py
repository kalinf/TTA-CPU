from amaranth import *
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu
from amaranth.utils import ceil_log2


class Logical(FU):
    """
    Logical operations.

    Communication ports:
    ----------
    3 Inputs:
        - 0: base value
        - 1: compared value
        - 2: mask for single-bit results output
    7 Outputs:
        - 0: base AND compared
        - 1: base OR compared
        - 2: base XOR compared
        - 3: NOT compared
        - 4: one-bit values combined, each bit has a meaning:
            - bit 0: compared == base
            - bit 1: compared < base
            - bit 2: compared > base
            - bit 3: reduction AND on compared
            - bit 4: reduction OR on compared
            - bit 5: reduction XOR on compared
            - bit 6: reduction OR on (base NAND compared)
        - 5: masked output 4
        - 6: compared >> base
        - 7: compared << base
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
        base = Signal.like(self.data_bus.data.data, name="base")
        compared = Signal.like(self.data_bus.data.data, name="compared")
        mask = Signal.like(self.data_bus.data.data, name="mask")

        m.d.comb += [
            base.eq(self.inputs[0]["data"]),
            compared.eq(self.inputs[1]["data"]),
            mask.eq(self.inputs[2]["data"]),
        ]
        # writing compared value triggers computation
        # with m.If(self.instr_bus.data.dst_addr == self.inputs[1]["addr"]):
        # m.d.falling += [
        m.d.comb += [
            self.outputs[0]["data"].eq(base & compared),
            self.outputs[1]["data"].eq(base | compared),
            self.outputs[2]["data"].eq(base ^ compared),
            self.outputs[3]["data"].eq(~compared),
            self.outputs[4]["data"].eq(
                Cat(
                    (compared == base),
                    (compared < base),
                    (compared > base),
                    compared.all(),
                    compared.any(),
                    compared.xor(),
                    ~((compared & base).any()), # bardzo sus rozszerzalne bitowo
                )
            ),
            self.outputs[5]["data"].eq(self.outputs[4]["data"] & mask),
            self.outputs[6]["data"].eq(compared >> base),
            self.outputs[7]["data"].eq(compared << (base[: ceil_log2(len(compared))])),
        ]

        return m


register_fu("Logical", Logical)
