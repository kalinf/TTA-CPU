from amaranth import *
from core.utils.ReadPort import ReadPort
from amaranth.build import Resource
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu

class Fetcher(FU):   
    """
    Drives instruction bus: Fetches correct instruction from instruction memory and does the indirect operations.
     
    Communication ports:
    ----------
    4 Inputs: 
    2 Outputs: 
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
        resources: dict[str, Resource],
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
        self.instr_read_ports = [ReadPort(depth=instruction_memory_depth, shape=self.instr_bus.data.shape()) for _ in range(instruction_memory_read_ports)]
        self.resources = resources
    
    def elaborate(self, platform):
        m = super().elaborate(platform)
        
        button = Signal.like(self.resources["button"].i, name="button")
        m.d.comb += [button.eq(self.resources["button"].i),]
        # here you can react on writes into trigger addresses 
        # here place your code, for example:
        # with m.If(self.instr_bus.data.dst_addr == self.inputs[0]["addr"]):
        #   m.d.falling += ...

        return m

register_fu("Fetcher", Fetcher)
