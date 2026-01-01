from amaranth import *
from core.utils.MemoryPorts import ReadPort, WritePort
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu

class DataMemory(FU):   
    """
    Operates on data memory.
     
    Communication ports:
    ----------
    3 Inputs: 
        - 0: Read address
        - 1: Write address
        - 2: Write data (triggers write to memory)
    1 Outputs: 
        - 0: Read data
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
        data_memory_depth: int,
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
        
        self.data_memory_depth = data_memory_depth
        self.data_read_port = ReadPort(depth=data_memory_depth, shape=self.data_bus.data.shape())
        self.data_write_port = WritePort(depth=data_memory_depth, shape=self.data_bus.data.shape())
    
    def elaborate(self, platform):
        m = super().elaborate(platform)
        
        m.d.comb += [
            self.data_read_port.en.eq(1),
            self.data_read_port.addr.eq(self.inputs[0]["data"]),
            self.outputs[0]["data"].eq(self.data_read_port.data),
            self.data_write_port.addr.eq(self.inputs[1]["data"]),
            self.data_write_port.data.eq(self.inputs[2]["data"]),
        ]
        
        with m.If(self.instr_bus.data.dst_addr == self.inputs[2]["addr"]):
            m.d.falling += self.data_write_port.en.eq(1)
        with m.Else():
            m.d.falling += self.data_write_port.en.eq(0)

        return m

register_fu("DataMemory", DataMemory)
