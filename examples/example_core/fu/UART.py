from amaranth import *
from amaranth.build import Resource
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu, IP_REGISTRY
from amaranth.lib.cdc import FFSynchronizer, PulseSynchronizer


class UART(FU):
    """
    UART Transmitter Receiver.

    Baud rate mapping:
    0:  50 
    1:  75 
    2:  110
    3:  134
    4:  150
    5:  200
    6:  300
    7:  600
    8:  1200
    9:  1800
    10: 4800
    11: 9600
    12: 19200
    13: 28800
    14: 38400
    15: 57600
    16: 76800
    17: 115200
    
    Communication ports:
    ----------
    4 Inputs:
        - 0: Transmit data (on lower 8 bits, write triggers transmission)
        - 1: Baud rate (number of baud rate value from list above)
        - 2: Data bits (up to 15)
        - 3: Stop bits (up to 3)
    3 Outputs:
        - 0: Received data
        - 1: Received data ready (destructive read)
        - 2: Transmission done (destructive read)
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

        uart_rx = Signal.like(self.resources["uart_rx"].i, name="uart_rx")
        uart_tx = Signal.like(self.resources["uart_tx"].o, name="uart_tx")
        m.d.comb += [
            uart_rx.eq(self.resources["uart_rx"].i),
            self.resources["uart_tx"].o.eq(uart_tx),
        ]

        m.submodules.UARTTranceiver = UARTTranceiver = IP_REGISTRY["UARTTranceiver"]()

        rx_data = Signal(8)
        rx_ready_pulse = Signal()
        rx_ready = Signal()
        tx_data = Signal(8)
        tx_done_pulse = Signal()
        tx_done = Signal()
        tx_start = Signal()

        m.d.comb += [
            self.outputs[0]["data"].eq(rx_data),
            self.outputs[1]["data"][0].eq(rx_ready),
            self.outputs[2]["data"][0].eq(tx_done),
        ]

        # Flip-Flop synchronizatory to za mało dla sygnałów wielobitowych!!!
        # popraw jak się wyśpisz i napisz własny moduł (pamiętaj o synchronizacji data i start)
        m.submodules += [
            FFSynchronizer(tx_data, UARTTranceiver.tx_data[0:8], o_domain="sync"),
            FFSynchronizer(tx_start, UARTTranceiver.tx_start, o_domain="sync"),
            FFSynchronizer(UARTTranceiver.rx_data, rx_data[0:8], o_domain="falling"),
            PulseSynchronizer(i_domain="sync", o_domain="falling"),
            FFSynchronizer(self.inputs[1]["data"][0:5], UARTTranceiver.baud_rate, o_domain="sync"),
            FFSynchronizer(self.inputs[2]["data"][0:4], UARTTranceiver.data_bits, o_domain="sync"),
            FFSynchronizer(self.inputs[3]["data"][0:2], UARTTranceiver.stop_bits, o_domain="sync"),
        ]

        ps = PulseSynchronizer(i_domain="sync", o_domain="falling")
        m.d.comb += [ps.i.eq(UARTTranceiver.tx_done), tx_done_pulse.eq(ps.o)]
        m.submodules += ps
        ps = PulseSynchronizer(i_domain="sync", o_domain="falling")
        m.d.comb += [ps.i.eq(UARTTranceiver.rx_ready), rx_ready_pulse.eq(ps.o)]
        m.submodules += ps

        with m.If(tx_done_pulse):
            m.d.falling += tx_done.eq(1)

        with m.If(rx_ready_pulse):
            m.d.falling += rx_ready.eq(1)

        # write triggers transmission
        with m.If(self.instr_bus.data.dst_addr == self.inputs[0]["addr"]):
            m.d.falling += [tx_data.eq(self.data_bus.data.data[:8]), tx_start.eq(1)]
        with m.Else():
            m.d.falling += tx_start.eq(0)

        # read of ready signal is destructive
        with m.If((self.instr_bus.data.src_addr == self.outputs[1]["addr"]) & rx_ready):
            m.d.falling += rx_ready.eq(0)

        # read of done signal is destructive
        with m.If((self.instr_bus.data.src_addr == self.outputs[2]["addr"]) & tx_done):
            m.d.falling += tx_done.eq(0)

        m.d.comb += [uart_tx.eq(UARTTranceiver.tx), UARTTranceiver.rx.eq(uart_rx)]

        return m


register_fu("UART", UART)
