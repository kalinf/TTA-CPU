import pytest
from amaranth import *
from amaranth.sim import Simulator
from utils.utils import resolve_bb_labels
from examples.core_external_int.tests.asm.stack import stack
from core.generate_core import gen_core

def test_stack(
    core_address_model, dir_path, vcd_file, mock_resources,
):
    init = stack(core_address_model)
    resolved_init = resolve_bb_labels(init)
    core = gen_core(dir_path, resolved_init, resources=mock_resources)
    sim = Simulator(core)
    sim.add_clock(1e-6, domain="mem")
    expected = reversed(list(range(1, 16+1)))

    async def tb(ctx):
        while ctx.get(core.instr_bus.data.dst_addr) != ctx.get(core.Result.inputs[0]["addr"]):
            await ctx.tick(domain="falling")
        await ctx.tick(domain="falling")
        assert ctx.get(core.Result.inputs[0]["data"]) == 1
        for elem in expected:
            while ctx.get(core.instr_bus.data.dst_addr) != ctx.get(core.Result.inputs[0]["addr"]):
                await ctx.tick(domain="falling")
            await ctx.tick(domain="falling")
            assert ctx.get(core.Result.inputs[0]["data"]) == elem
        while ctx.get(core.instr_bus.data.dst_addr) != ctx.get(core.Result.inputs[0]["addr"]):
            await ctx.tick(domain="falling")
        await ctx.tick(domain="falling")
        assert ctx.get(core.Result.inputs[0]["data"]) == 1

    sim.add_testbench(tb)
    if vcd_file is not None:
        with sim.write_vcd(str(vcd_file)):
            sim.run()
    else:
        sim.run()
