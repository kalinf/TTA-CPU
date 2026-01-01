import pytest
from amaranth import *
from amaranth.sim import Simulator
from utils.utils import resolve_bb_labels
from examples.core_external_int.tests.asm.uart import uart_echo
from core.generate_core import gen_core


def to_binary(data, length):
    result = ""
    while data > 0 and len(result) < length:
        if data % 2:
            result = "1" + result
        else:
            result = "0" + result
        data = data // 2
    while len(result) < length:
        result = "0" + result

    return result


def char_bit_to_number(character):
    return 0 if character == "0" else 1


async def uart_transmit(ctx, data, period, baud_rate, core):
    bin_data = to_binary(data, 8)
    bit_period = 1 / baud_rate
    cycles_per_bit = int(bit_period / period)

    ctx.set(core.resources["uart_rx"].i, 0)
    for i in range(8):
        await ctx.tick(domain="sync").repeat(cycles_per_bit)
        ctx.set(core.resources["uart_rx"].i, char_bit_to_number(bin_data[7 - i]))
    await ctx.tick(domain="sync").repeat(cycles_per_bit)
    ctx.set(core.resources["uart_rx"].i, 1)
    await ctx.tick(domain="sync").repeat(cycles_per_bit)


def test_uart_echo(core_address_model, dir_path, vcd_file, mock_resources):
    init = uart_echo(core_address_model)
    resolved_init = resolve_bb_labels(init)
    core = gen_core(dir_path, resolved_init, resources=mock_resources)
    sim = Simulator(core)
    sim.add_clock(4e-8, domain="mem")
    sim.add_clock(4e-8, domain="sync")

    async def tb(ctx):
        ctx.set(core.resources["uart_rx"].i, 1)
        await ctx.tick(domain="falling").repeat(100)
        await uart_transmit(ctx, 71, 4e-8, 9600, core)
        await ctx.tick(domain="falling").repeat(1000)

    sim.add_testbench(tb)
    if vcd_file is not None:
        with sim.write_vcd(str(vcd_file)):
            sim.run()
    else:
        sim.run()
