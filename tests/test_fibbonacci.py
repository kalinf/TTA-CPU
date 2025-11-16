import pytest
from amaranth import *
from amaranth.sim import Simulator
from functools import partial

# test na konfiguracji gdzie jest Adder o adresach 0, 1, 2 i triggerach na 0, 1


def fibbonacci(n):
    f = [0, 1]
    if n < 2:
        return f[n]
    for i in range(2, n + 1):
        new = f[0] + f[1]
        f[0] = f[1]
        f[1] = new
    return new


def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)


async def sim_fib(ctx, dut, n):
    await ctx.tick(domain="falling")
    ctx.set(dut.instr_bus.data, {"constant": 1, "src_addr": 0, "dst_addr": 0})
    await ctx.tick(domain="falling")
    if n == 0:
        return ctx.get(dut.Adder.regs[2]["data"])
    ctx.set(dut.instr_bus.data, {"constant": 1, "src_addr": 1, "dst_addr": 1})
    if n == 1:
        await ctx.tick(domain="falling")
        return ctx.get(dut.Adder.regs[2]["data"])
    for i in range(2, n + 1):
        await ctx.tick(domain="falling")
        ctx.set(dut.instr_bus.data, {"constant": 0, "src_addr": 2, "dst_addr": (i % 2)})
    await ctx.tick(domain="rising")
    return ctx.get(dut.data_bus.data.data)


@pytest.mark.parametrize("n", [0, 1, 2, 5, 10])
def test_fib(core, vcd_file, n):
    expected = fib(n)

    sim = Simulator(core)
    sim.add_clock(1e-6, domain="rising")

    async def tb(ctx):
        result = await sim_fib(ctx, core, n)
        assert result == expected

    sim.add_testbench(tb)
    if vcd_file is not None:
        with sim.write_vcd(str(vcd_file)):
            sim.run()
    else:
        sim.run()
