import pytest
from amaranth import *
from amaranth.sim import Simulator
from utils.utils import resolve_bb_labels
from examples.core_external_int.tests.asm.data_memory import data_memory
from core.generate_core import gen_core

def test_data_memory(core_address_model, dir_path, vcd_file, mock_resources):
    init = data_memory(core_address_model)
    resolved_init = resolve_bb_labels(init)
    core = gen_core(dir_path, resolved_init, resources=mock_resources)
    sim = Simulator(core)
    sim.add_clock(4e-8, domain="mem")
    sim.add_clock(4e-8, domain="sync")

    async def tb(ctx):
        await ctx.tick(domain="falling").repeat(20000)

    sim.add_testbench(tb)
    if vcd_file is not None:
        with sim.write_vcd(str(vcd_file)):
            sim.run()
    else:
        sim.run()