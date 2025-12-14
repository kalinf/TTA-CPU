import pytest
from amaranth import *
from amaranth.sim import Simulator
from tests.utils import base_asm_test, resolve_bb_labels
from examples.basic_core.tests.asm.fibonacci import fibonacci_no_loop, fibonacci_loop_direct
from core.generate_core import gen_core


def fibonacci(n):
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
    ctx.set(dut.instr_bus.data, {"constant": 1, "src_addr": 0, "dst_addr": dut.Adder.inputs[0]["addr"]})
    await ctx.tick(domain="falling")
    if n == 0:
        return ctx.get(dut.Adder.outputs[0]["data"])
    ctx.set(dut.instr_bus.data, {"constant": 1, "src_addr": 1, "dst_addr": dut.Adder.inputs[1]["addr"]})
    if n == 1:
        await ctx.tick(domain="falling")
        return ctx.get(dut.Adder.outputs[0]["data"])
    for i in range(2, n + 1):
        await ctx.tick(domain="falling")
        ctx.set(
            dut.instr_bus.data,
            {"constant": 0, "src_addr": dut.Adder.outputs[0]["addr"], "dst_addr": dut.Adder.inputs[(i % 2)]["addr"]},
        )
    await ctx.tick(domain="rising")
    return ctx.get(dut.data_bus.data.data)


@pytest.mark.parametrize("n", [0, 1, 2, 5, 10])
def test_fib_no_memory(core, vcd_file, n):
    expected = fib(n)

    sim = Simulator(core)
    sim.add_clock(1e-6, domain="mem")

    async def tb(ctx):
        result = await sim_fib(ctx, core, n)
        assert result == expected

    sim.add_testbench(tb)
    if vcd_file is not None:
        with sim.write_vcd(str(vcd_file)):
            sim.run()
    else:
        sim.run()


@pytest.mark.parametrize("n", [0, 1, 2, 5, 10])
def test_fib_no_loop_asm(core_address_model, dir_path, vcd_file, mock_resources, n):
    expected = fib(n)
    init = fibonacci_no_loop(core_address_model, n)
    core = gen_core(dir_path, init, resources=mock_resources)
    base_asm_test(core=core, vcd_file=vcd_file, instr_memory_init=init, expected=expected)


@pytest.mark.parametrize("n", [0, 1, 2, 5, 10])
def test_fib_loop_direct_asm(core_address_model, dir_path, vcd_file, mock_resources, n):
    expected = fib(n)
    init = fibonacci_loop_direct(core_address_model, n)
    resolved_init = resolve_bb_labels(init)
    core = gen_core(dir_path, resolved_init, resources=mock_resources)
    base_asm_test(core=core, vcd_file=vcd_file, instr_memory_init=init, expected=expected)
