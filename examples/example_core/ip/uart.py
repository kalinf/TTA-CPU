from amaranth import *
from core.registry import register_ip


class UARTTranceiver(Elaboratable):
    def __init__(
        self,
        oversampling: int = 16,
        clk_freq: int = 25_000_000,
    ):
        self.oversampling = oversampling
        self.clk_freq = clk_freq
        
        baud_rates = [
            50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 4800, 9600,
            19200, 28800, 38400, 57600, 76800, 115200
        ]
        sampling_rates = [baud_rate * oversampling for baud_rate in baud_rates]
        self.sampling_periods = Array([clk_freq // sampling_rate for sampling_rate in sampling_rates])
        self.bit_periods = Array([clk_freq // baud_rate for baud_rate in baud_rates])

        max_data_bits = 8

        self.baud_rate = Signal(range(len(baud_rates))) # number of baud_rate in array
        self.data_bits = Signal(4)
        self.stop_bits = Signal(2)
        self.tx = Signal()
        self.rx = Signal()
        self.tx_data = Signal(max_data_bits)
        self.tx_start = Signal()
        self.tx_done = Signal()
        self.rx_data = Signal(max_data_bits)
        self.rx_ready = Signal()

    def elaborate(self, platform):
        m = Module()

        tx_cycles_counter = Signal(range(self.bit_periods[-1]))
        tx_counter = Signal.like(self.data_bits)
        
        bit_period = Signal(range(self.bit_periods[-1]))
        sampling_period = Signal(range(self.sampling_periods[-1]))
        m.d.sync += [
            bit_period.eq(self.bit_periods[self.baud_rate]),
            sampling_period.eq(self.sampling_periods[self.baud_rate])
        ]

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
                with m.If(tx_cycles_counter == bit_period - 1):
                    m.d.sync += tx_cycles_counter.eq(0)
                    m.next = "DATA"
            with m.State("DATA"):
                m.d.sync += tx_cycles_counter.eq(tx_cycles_counter + 1)
                with m.If(tx_cycles_counter == bit_period - 1):
                    m.d.sync += [tx_cycles_counter.eq(0), tx_counter.eq(tx_counter + 1)]
                    with m.If(tx_counter == self.data_bits - 1):
                        m.d.sync += tx_counter.eq(0)
                        m.next = "STOP"
                m.d.comb += self.tx.eq(self.tx_data.bit_select(tx_counter, 1))
            with m.State("STOP"):
                m.d.sync += tx_cycles_counter.eq(tx_cycles_counter + 1)
                with m.If(tx_cycles_counter == bit_period - 1):
                    m.d.sync += [tx_cycles_counter.eq(0), tx_counter.eq(tx_counter + 1)]
                    with m.If(tx_counter == self.stop_bits - 1):
                        m.next = "IDLE"
                        m.d.sync += self.tx_done.eq(1)
                m.d.comb += self.tx.eq(1)

        rx_samples_counter = Signal(range(self.oversampling))
        rx_sample_cycles_counter = Signal.like(sampling_period)
        rx_bit_counter = Signal.like(self.data_bits)
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
                with m.If(rx_sample_cycles_counter == sampling_period - 1):
                    m.d.sync += [
                        rx_samples_counter.eq(rx_samples_counter + 1),
                        rx_sample_cycles_counter.eq(0),
                    ]
                    with m.If(rx_samples_counter == self.oversampling - 1):
                        m.d.sync += rx_samples_counter.eq(0)
                        m.next = "DATA"
            with m.State("DATA"):
                m.d.sync += rx_sample_cycles_counter.eq(rx_sample_cycles_counter + 1)
                with m.If(rx_sample_cycles_counter == sampling_period - 1):
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
                with m.If(rx_sample_cycles_counter == sampling_period - 1):
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
