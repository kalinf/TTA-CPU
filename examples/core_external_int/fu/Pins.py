from amaranth import *
from amaranth.build import Resource
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu

class Pins(FU):   
    """
    External pins for input/output.
     
    Communication ports:
    ----------
    1 Inputs: 
    1 Outputs: 
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
        
        self.resources = resources
    
    def elaborate(self, platform):
        m = super().elaborate(platform)
        
        button = Signal.like(self.resources["button"].i, name="button")
        leds = Signal.like(self.resources["leds"].o, name="leds")
        m.d.comb += [button.eq(self.resources["button"].i),self.resources["leds"].o.eq(leds),]
        # here you can react on writes into trigger addresses 
        # here place your code, for example:
        # with m.If(self.instr_bus.data.dst_addr == self.inputs[0]["addr"]):
        #   m.d.falling += ...

        return m

register_fu("Pins", Pins)
