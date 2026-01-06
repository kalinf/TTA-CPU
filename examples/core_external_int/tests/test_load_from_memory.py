import pytest
import json
from amaranth import *
from amaranth.sim import Simulator
from utils.utils import resolve_bb_labels
from examples.core_external_int.tests.asm.load_program_from_memory import (
    bootloader_data_memory,
)
from examples.core_external_int.tests.asm.data_memory import data_memory
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

    async def tb(ctx):
        await ctx.tick(domain="falling").repeat(20000)
        # TODO: actually check the correctness of transmitted data

    sim.add_testbench(tb)
    if vcd_file is not None:
        with sim.write_vcd(str(vcd_file)):
            sim.run()
    else:
        sim.run()
