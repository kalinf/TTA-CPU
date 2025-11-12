from amaranth import *
from amaranth.sim import Simulator
from amaranth.back import verilog

# test na konfiguracji gdzie jest Adder o adresach 0, 1, 2 i triggerach na 0, 1


def run_sim_fib(core):
    dut = core

    async def testbench_fib(ctx):
        await ctx.tick(domain="falling")
        ctx.set(dut.instr_bus.data, {"constant": 1, "src_addr": 0, "dst_addr": 0})
        await ctx.tick(domain="rising")
        print(ctx.get(dut.data_bus.data.data))
        print(ctx.get(dut.Adder.regs[2]["data"]))
        await ctx.tick(domain="falling")
        ctx.set(dut.instr_bus.data, {"constant": 1, "src_addr": 1, "dst_addr": 1})
        await ctx.tick(domain="rising")
        print(ctx.get(dut.data_bus.data.data))
        await ctx.tick(domain="falling")
        ctx.set(dut.instr_bus.data, {"constant": 0, "src_addr": 2, "dst_addr": 0})
        await ctx.tick(domain="rising")
        print(ctx.get(dut.data_bus.data.data))
        await ctx.tick(domain="falling")
        ctx.set(dut.instr_bus.data, {"constant": 0, "src_addr": 2, "dst_addr": 1})
        await ctx.tick(domain="rising")
        print(ctx.get(dut.data_bus.data.data))
        await ctx.tick(domain="falling")
        ctx.set(dut.instr_bus.data, {"constant": 0, "src_addr": 2, "dst_addr": 0})
        await ctx.tick(domain="rising")
        print(ctx.get(dut.data_bus.data.data))
        await ctx.tick(domain="falling")
        ctx.set(dut.instr_bus.data, {"constant": 0, "src_addr": 2, "dst_addr": 1})
        await ctx.tick(domain="rising")
        print(ctx.get(dut.data_bus.data.data))
        await ctx.tick(domain="falling")
        ctx.set(dut.instr_bus.data, {"constant": 0, "src_addr": 2, "dst_addr": 0})
        await ctx.tick(domain="rising")
        print(ctx.get(dut.data_bus.data.data))
        await ctx.tick(domain="falling")
        ctx.set(dut.instr_bus.data, {"constant": 0, "src_addr": 2, "dst_addr": 1})
        await ctx.tick(domain="rising")
        print(ctx.get(dut.data_bus.data.data))

    sim = Simulator(dut)
    sim.add_clock(1e-6, domain="rising")  # 1 µs period, or 1 MHz
    sim.add_testbench(testbench_fib)
    with sim.write_vcd("fib.vcd"):
        sim.run_until(1e-6 * 15)  # 15 periods of the clock
