from amaranth import *
from transactron import *
from transactron.utils import MethodLayout, SrcLoc, get_src_loc
from transactron.utils.transactron_helpers import from_method_layout


class Bus(Elaboratable):
    """Bus.

    ...

    Attributes
    ----------
    ...
    """

    def __init__(self, layout, *, src_loc: int | SrcLoc = 0):
        """
        Parameters
        ----------
        layout: method layout
            The format of structures transfered by the bus.
        """
        self.layout = layout

        src_loc = get_src_loc(src_loc)
        self.data = Signal(self.layout)
        self.int_data = Signal(self.layout)

    def elaborate(self, platform):
        m = Module()
        m.d.comb += self.int_data.eq(self.data)
        return m
