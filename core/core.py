import inspect
from amaranth import *
from amaranth.lib.memory import Memory
from amaranth.utils import ceil_log2
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
        data_memory_depth=64,
        data_memory_init=[],
        resources={},
        synthesis=False,
    ):
        self.instr_layout = InstructionLayout(src_addr_width=src_addr_width, dest_addr_width=dest_addr_width)
        self.data_layout = DataLayout(data_width=data_width)
        self.instr_memory_depth = instr_memory_depth
        self.instr_memory_rports = instr_memory_rports
        self.instr_memory_init = instr_memory_init
        self.data_memory_depth = data_memory_depth
        self.data_memory_init = data_memory_init
        self.FUs = FUs
        self.instr_bus = Bus(self.instr_layout)
        self.data_bus = Bus(self.data_layout)
        self.synthesis = synthesis
        self.resources = resources

    def elaborate(self, platform):
        m = Module()

        m.domains.sync = cd_sync = ClockDomain(local=True)
        m.domains.mem = cd_mem = ClockDomain(local=True)
        m.domains.neg_mem = cd_neg_mem = ClockDomain(local=True, clk_edge="neg")
        m.domains.rising = cd_rising = ClockDomain(local=True)
        m.domains.falling = cd_falling = ClockDomain(local=True, clk_edge="neg")

        if self.synthesis:
            m.d.comb += [cd_mem.clk.eq(self.resources["clk25"].i), cd_sync.clk.eq(self.resources["clk25"].i)]

        m.d.comb += [
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

        m.submodules.data_mem = self.data_mem = data_mem = Memory(
            shape=self.data_layout, depth=self.data_memory_depth, init=self.data_memory_init
        )
        data_write_port = data_mem.write_port(domain="mem")
        data_read_port = data_mem.read_port(domain="mem")

        for fu in self.FUs:
            sig = inspect.signature(fu[1].func)
            parameters = {"instr_bus": self.instr_bus, "data_bus": self.data_bus}
            if "instruction_memory_depth" in [name for (name, _) in sig.parameters.items()]:
                parameters["instruction_memory_depth"] = self.instr_memory_depth
            if "instruction_memory_read_ports" in [name for (name, _) in sig.parameters.items()]:
                parameters["instruction_memory_read_ports"] = self.instr_memory_rports
            if "data_memory_depth" in [name for (name, _) in sig.parameters.items()]:
                parameters["data_memory_depth"] = self.data_memory_depth
            if "resources" in [name for (name, _) in sig.parameters.items()]:
                parameters["resources"] = self.resources

            m.submodules[fu[0]] = fu[1](**parameters)
            if fu[0] == "Fetcher":
                for i, instr_read_port in enumerate(m.submodules[fu[0]].instr_read_ports):
                    m.d.comb += [
                        instr_read_ports[i].addr.eq(instr_read_port.addr),
                        instr_read_ports[i].en.eq(instr_read_port.en),
                        instr_read_port.data.eq(instr_read_ports[i].data),
                    ]
            if fu[0] == "DataMemory":
                m.d.comb += [
                    data_read_port.addr.eq(m.submodules[fu[0]].data_read_port.addr),
                    data_read_port.en.eq(m.submodules[fu[0]].data_read_port.en),
                    m.submodules[fu[0]].data_read_port.data.eq(data_read_port.data),
                    data_write_port.addr.eq(m.submodules[fu[0]].data_write_port.addr),
                    data_write_port.en.eq(m.submodules[fu[0]].data_write_port.en),
                    data_write_port.data.eq(m.submodules[fu[0]].data_write_port.data),
                ]
            if fu[0] == "ProgMemory":
                m.d.comb += [
                    instr_write_port.addr.eq(m.submodules[fu[0]].instr_write_port.addr),
                    instr_write_port.en.eq(m.submodules[fu[0]].instr_write_port.en),
                    instr_write_port.data.eq(m.submodules[fu[0]].instr_write_port.data),
                ]

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
        with m.Else():
            m.d.rising += self.data_bus.data.data.eq(self.instr_bus.data.src_addr)

        return m
