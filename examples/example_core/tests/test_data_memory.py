import pytest
from amaranth import *
from amaranth.sim import Simulator
from utils.utils import resolve_bb_labels
from examples.example_core.tests.asm.data_memory import data_memory
from examples.example_core.tests.test_uart import uart_receive, uart_transmit
from core.generate_core import gen_core


def test_data_memory(core_address_model, dir_path, vcd_file, mock_resources):
    init = data_memory(core_address_model)
    resolved_init = resolve_bb_labels(init)
    core = gen_core(dir_path, resolved_init, resources=mock_resources)
    sim = Simulator(core)
    sim.add_clock(4e-8, domain="mem")
    sim.add_clock(4e-8, domain="sync")

    data = 97  # 'a'

    async def tb(ctx):
        await ctx.tick(domain="falling").repeat(100)
        # program waits for trigger to start transmitting
        await uart_transmit(ctx, data, 4e-8, 115200, core)
        for i in range(10):
            await uart_receive(ctx, data + i, 4e-8, 115200, core)

    sim.add_testbench(tb)
    if vcd_file is not None:
        with sim.write_vcd(str(vcd_file)):
            sim.run()
    else:
        sim.run()
