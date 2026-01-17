import pytest
import json
from amaranth import *
from amaranth.sim import Simulator
from utils.utils import resolve_bb_labels
from examples.example_core.tests.asm.load_program_from_memory import bootloader_data_memory
from examples.example_core.tests.asm.data_memory import data_memory
from examples.example_core.tests.test_uart import uart_receive, uart_transmit
from core.generate_core import gen_core
from scripts.translator import prog2data


def test_bootloader_data_memory(core_address_model, dir_path, vcd_file, mock_resources):
    configuration_path = dir_path / "config_detail.json"
    with configuration_path.open() as f:
        configuration = json.load(f)
    bootloader_init = bootloader_data_memory(core_address_model)
    resolved_bootloader_init = resolve_bb_labels(bootloader_init)
    program_init = data_memory(core_address_model)
    resolved_program_init = resolve_bb_labels(program_init, offset=50)
    data_init = prog2data(
        resolved_program_init,
        src_width=configuration["src_addr_width"],
        dest_width=configuration["dest_addr_width"],
        data_width=configuration["word_size"],
        start_length=True,
    )
    core = gen_core(
        dir_path,
        instr_memory_init=resolved_bootloader_init,
        data_memory_init=data_init,
        resources=mock_resources,
    )
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
