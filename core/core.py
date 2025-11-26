from amaranth import *
from amaranth.lib.memory import Memory
from .layouts import DataLayout, InstructionLayout
from .bus import Bus


class TTA_Core(Elaboratable):
    """
    Parameters
    ----------
    src_addr_width: int
        ...
    dest_addr_width: int
        ...
    data_width: int
        ...
    FUs
        ...
    """

    def __init__(
        self,
        src_addr_width,
        dest_addr_width,
        data_width,
        FUs,
        instr_memory_depth,
        instr_memory_rports=1,
        instr_memory_init=[],
    ):
        self.instr_layout = InstructionLayout(src_addr_width=src_addr_width, dest_addr_width=dest_addr_width)
        self.data_layout = DataLayout(data_width=data_width)
        self.instr_memory_depth = instr_memory_depth
        self.instr_memory_rports = instr_memory_rports
        self.instr_memory_init = instr_memory_init
        self.FUs = FUs
        self.instr_bus = Bus(self.instr_layout)
        self.data_bus = Bus(self.data_layout)

    def elaborate(self, platform):
        m = Module()

        clk = platform.request("clk25")
        m.domains.mem = cd_mem = ClockDomain(local=True)
        m.domains.neg_mem = cd_neg_mem = ClockDomain(local=True, clk_edge="neg")
        m.domains.rising = cd_rising = ClockDomain(local=True)
        m.domains.falling = cd_falling = ClockDomain(local=True, clk_edge="neg")

        m.d.comb += [
            cd_mem.clk.eq(clk.i),
            cd_falling.clk.eq(cd_rising.clk),
            cd_neg_mem.clk.eq(cd_mem.clk),
        ]
        m.d.neg_mem += [cd_rising.clk.eq(~cd_rising.clk)]

        m.submodules.data_bus = self.data_bus
        m.submodules.instr_bus = self.instr_bus

        m.submodules.instr_mem = self.instr_mem = instr_mem = Memory(
            shape=self.instr_layout, depth=self.instr_memory_depth, init=self.instr_memory_init
        )
        instr_write_port = instr_mem.write_port(domain="mem")
        instr_read_ports = [instr_mem.read_port(domain="mem") for _ in range(self.instr_memory_rports)]

        for fu in self.FUs:
            if fu[0] == "Fetcher":
                m.submodules[fu[0]] = fu[1](
                    instr_bus=self.instr_bus,
                    data_bus=self.data_bus,
                    instruction_memory_depth=self.instr_memory_depth,
                    instruction_memory_read_ports=self.instr_memory_rports,
                )
                for i, instr_read_port in enumerate(m.submodules[fu[0]].instr_read_ports):
                    m.d.comb += [
                        instr_read_ports[i].addr.eq(instr_read_port.addr),
                        instr_read_ports[i].en.eq(instr_read_port.en),
                        instr_read_port.data.eq(instr_read_ports[i].data),
                    ]
            else:
                m.submodules[fu[0]] = fu[1](instr_bus=self.instr_bus, data_bus=self.data_bus)

            setattr(self, fu[0], m.submodules[fu[0]])

        with m.If(~self.instr_bus.data.constant):
            with m.Switch(self.instr_bus.data.src_addr):
                for fu in self.FUs:
                    for output in m.submodules[fu[0]].outputs:
                        with m.Case(output["addr"]):
                            m.d.rising += self.data_bus.data.data.eq(output["data"])
                    for inout in m.submodules[fu[0]].inouts:
                        with m.Case(inout["addr"]):
                            m.d.rising += self.data_bus.data.data.eq(inout["data"])

        # DEBUG PURPOSES ONLY
        result = platform.request("result")
        write_port = platform.request("write_port")
        m.d.comb += [
            result.o.eq(m.submodules["Result"].inputs[0]["data"]),
            instr_write_port.addr.eq(write_port.addr.i),
            instr_write_port.en.eq(write_port.en.i),
            instr_write_port.data.eq(write_port.data.i),
        ]

        return m
