import pytest
from amaranth import *
from amaranth.sim import Simulator
from tests.utils import base_asm_test
from utils.utils import resolve_bb_labels
from examples.core_external_int.tests.asm.handlers import wandering_led
from core.generate_core import gen_core

wandering = [0b1, 0b10, 0b100, 0b1000, 0b10000]


def ping_pong(array):
    i = 0
    direction = 1

    while True:
        yield array[i]

        if i == len(array) - 1:
            direction = -1
        elif i == 0:
            direction = 1

        i += direction


@pytest.mark.parametrize("asm_code", [wandering_led])
def test_wandering_led_asm(
    core_address_model, dir_path, vcd_file, mock_resources, asm_code
):
    init = asm_code(core_address_model)
    resolved_init = resolve_bb_labels(init)
    core = gen_core(dir_path, resolved_init, resources=mock_resources)
    sim = Simulator(core)
    sim.add_clock(1e-6, domain="mem")
    expected = ping_pong(wandering)

    async def tb(ctx):
        # however button is pulled down by default, but inversinon is made in resource, mock resources don't do that
        ctx.set(core.resources["button"].i, 0)
        await ctx.tick(domain="falling").repeat(10)
        for _ in range(16):
            result = ctx.get(core.Pins.inouts[0]["data"])
            assert result == next(expected)
            ctx.set(core.resources["button"].i, 1)
            await ctx.tick(domain="falling").repeat(10)
            ctx.set(core.resources["button"].i, 0)
            await ctx.tick(domain="falling").repeat(150)

    sim.add_testbench(tb)
    if vcd_file is not None:
        with sim.write_vcd(str(vcd_file)):
            sim.run()
    else:
        sim.run()
