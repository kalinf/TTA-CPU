from amaranth import *
from pathlib import Path
import json
from amaranth.sim import Simulator


def base_asm_test(core, vcd_file, instr_memory_init, expected):
    sim = Simulator(core)
    sim.add_clock(1e-6, domain="mem")

    async def tb(ctx):
        # while ctx.get(core.instr_bus.data["dst_addr"]) != core.Result.inputs[0]["addr"].value:
        # await ctx.tick(domain="falling")
        await ctx.tick(domain="falling").repeat(1000)
        result = ctx.get(core.Result.inputs[0]["data"])
        assert result == expected

    sim.add_testbench(tb)
    if vcd_file is not None:
        with sim.write_vcd(str(vcd_file)):
            sim.run()
    else:
        sim.run()


def mock_resources(config_detail_file: Path):
    with config_detail_file.open() as f:
        configuration = json.load(f)

    class ResourceModel:
        def __init__(self, dir="i", length=1):
            setattr(self, dir, Signal(length))

    mock_rsrcs = {}
    if "resources" in configuration:
        for resource in configuration["resources"]:
            mock_rsrcs[resource["name"]] = ResourceModel(
                dir=resource["pins"]["dir"], length=len(resource["pins"]["pins"].split())
            )

    return mock_rsrcs
