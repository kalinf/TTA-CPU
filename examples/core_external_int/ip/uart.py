from amaranth import *
from core.registry import register_ip


class UARTTranceiver(Elaboratable):
    def __init__(
        self,
        baud_rate: int = 9600,
        data_bits: int = 8,
        stop_bits: int = 1,
        oversampling: int = 16,
        clk_freq: int = 25_000_000,
    ):
        self.baud_rate = baud_rate
        self.data_bits = data_bits
        self.stop_bits = stop_bits
        self.oversampling = oversampling
        self.clk_freq = clk_freq
        self.sampling_rate = baud_rate * oversampling
        self.sampling_period = clk_freq // self.sampling_rate
        self.bit_period = clk_freq // baud_rate

        self.tx = Signal()
        self.rx = Signal()
        self.tx_data = Signal(self.data_bits)
        self.tx_start = Signal()
        self.tx_done = Signal()
        self.rx_data = Signal(self.data_bits)
        self.rx_ready = Signal()

    def elaborate(self, platform):
        m = Module()

        tx_cycles_counter = Signal(range(self.bit_period))
        tx_counter = Signal(range(self.data_bits))

        # Transmitter
        with m.FSM(domain="sync", name="uart_transmitter"):
            with m.State("IDLE"):
                m.d.comb += self.tx.eq(1)
                m.d.sync += self.tx_done.eq(0)
                with m.If(self.tx_start):
                    m.d.sync += [tx_counter.eq(0), tx_cycles_counter.eq(0)]
                    m.next = "START"
            with m.State("START"):
                m.d.comb += self.tx.eq(0)
                m.d.sync += tx_cycles_counter.eq(tx_cycles_counter + 1)
                with m.If(tx_cycles_counter == self.bit_period - 1):
                    m.d.sync += tx_cycles_counter.eq(0)
                    m.next = "DATA"
            with m.State("DATA"):
                m.d.sync += tx_cycles_counter.eq(tx_cycles_counter + 1)
                with m.If(tx_cycles_counter == self.bit_period - 1):
                    m.d.sync += [tx_cycles_counter.eq(0), tx_counter.eq(tx_counter + 1)]
                    with m.If(tx_counter == self.data_bits - 1):
                        m.d.sync += tx_counter.eq(0)
                        m.next = "STOP"
                m.d.comb += self.tx.eq(self.tx_data.bit_select(tx_counter, 1))
            with m.State("STOP"):
                m.d.sync += tx_cycles_counter.eq(tx_cycles_counter + 1)
                with m.If(tx_cycles_counter == self.bit_period - 1):
                    m.d.sync += [tx_cycles_counter.eq(0), tx_counter.eq(tx_counter + 1)]
                    with m.If(tx_counter == self.stop_bits - 1):
                        m.next = "IDLE"
                        m.d.sync += self.tx_done.eq(1)
                m.d.comb += self.tx.eq(1)

        rx_samples_counter = Signal(range(self.oversampling))
        rx_sample_cycles_counter = Signal(range(self.sampling_period))
        rx_bit_counter = Signal(range(self.data_bits))
        rx_stop = Signal()

        # Receiver
        with m.FSM(domain="sync", name="uart_receiver"):
            with m.State("IDLE"):
                m.d.sync += self.rx_ready.eq(0)
                with m.If(~self.rx):
                    m.d.sync += [
                        rx_samples_counter.eq(0),
                        rx_sample_cycles_counter.eq(0),
                        rx_bit_counter.eq(0),
                    ]
                    m.next = "START"
            with m.State("START"):
                m.d.sync += rx_sample_cycles_counter.eq(rx_sample_cycles_counter + 1)
                with m.If(rx_sample_cycles_counter == self.sampling_period - 1):
                    m.d.sync += [
                        rx_samples_counter.eq(rx_samples_counter + 1),
                        rx_sample_cycles_counter.eq(0),
                    ]
                    with m.If(rx_samples_counter == self.oversampling - 1):
                        m.d.sync += (rx_samples_counter.eq(0),)
                        m.next = "DATA"
            with m.State("DATA"):
                m.d.sync += rx_sample_cycles_counter.eq(rx_sample_cycles_counter + 1)
                with m.If(rx_sample_cycles_counter == self.sampling_period - 1):
                    m.d.sync += [
                        rx_samples_counter.eq(rx_samples_counter + 1),
                        rx_sample_cycles_counter.eq(0),
                    ]
                    with m.If(rx_samples_counter == self.oversampling // 2):
                        m.d.sync += self.rx_data.eq(Cat(self.rx_data[1:], self.rx))
                    with m.If(rx_samples_counter == self.oversampling - 1):
                        m.d.sync += [
                            rx_samples_counter.eq(0),
                            rx_bit_counter.eq(rx_bit_counter + 1),
                        ]
                        with m.If(rx_bit_counter == self.data_bits - 1):
                            m.d.sync += [rx_bit_counter.eq(0), rx_stop.eq(1)]
                            m.next = "STOP"
            with m.State("STOP"):
                m.d.sync += rx_sample_cycles_counter.eq(rx_sample_cycles_counter + 1)
                with m.If(rx_sample_cycles_counter == self.sampling_period - 1):
                    m.d.sync += [
                        rx_samples_counter.eq(rx_samples_counter + 1),
                        rx_sample_cycles_counter.eq(0),
                    ]
                    with m.If(rx_samples_counter == self.oversampling // 2):
                        with m.If(~self.rx):
                            m.d.sync += rx_stop.eq(0)
                    with m.If(rx_samples_counter == self.oversampling - 1):
                        m.d.sync += [
                            rx_samples_counter.eq(0),
                            rx_bit_counter.eq(rx_bit_counter + 1),
                        ]
                        with m.If(rx_bit_counter == self.stop_bits - 1):
                            m.d.sync += [
                                rx_bit_counter.eq(0),
                                self.rx_ready.eq(rx_stop),
                            ]
                            m.next = "IDLE"

        return m


register_ip("UARTTranceiver", UARTTranceiver)
