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


def resolve_bb_labels(init):
    addr_map = {}
    resolved_init = []
    current_addr = 0

    # First pass: map labels to addresses
    for item in init:
        if isinstance(item, tuple):
            label, instructions = item
            addr_map[label] = current_addr
            current_addr += len(instructions)
        else:
            current_addr += 1

    # Second pass: replace labels with addresses
    for item in init:
        if isinstance(item, tuple):
            _, instructions = item
            for instr in instructions:
                if isinstance(instr["src_addr"], str):
                    if instr["src_addr"] in addr_map:
                        instr["src_addr"] = addr_map[instr["src_addr"]]
                    else:
                        raise ValueError(f"Undefined label: {instr['src_addr']}")
                if isinstance(instr["dst_addr"], str):
                    if instr["dst_addr"] in addr_map:
                        instr["dst_addr"] = addr_map[instr["dst_addr"]]
                    else:
                        raise ValueError(f"Undefined label: {instr['dst_addr']}")
                resolved_init.append(instr)
        else:
            if isinstance(item["src_addr"], str):
                if item["src_addr"] in addr_map:
                    item["src_addr"] = addr_map[item["src_addr"]]
                else:
                    raise ValueError(f"Undefined label: {item['src_addr']}")
            if isinstance(item["dst_addr"], str):
                if item["dst_addr"] in addr_map:
                    item["dst_addr"] = addr_map[item["dst_addr"]]
                else:
                    raise ValueError(f"Undefined label: {item['dst_addr']}")
            resolved_init.append(item)

    return resolved_init


def build_addresses_core_model(config_detail_file: Path):
    with config_detail_file.open() as f:
        configuration = json.load(f)

    class CoreModel:
        def __init__(self, configuration):
            for fu in configuration["functional_units"]:
                setattr(self, fu["name"], self.FUModel(fu))

        class FUModel:
            def __init__(self, fu):
                self.inputs = list(range(fu["input_address"], fu["input_address"] + fu["inputs"]))
                self.outputs = list(range(fu["output_address"], fu["output_address"] + fu["outputs"]))
                self.inouts = list(range(fu["inout_address"], fu["inout_address"] + fu["inouts"]))

    return CoreModel(configuration)


def mock_resources(config_detail_file: Path):
    with config_detail_file.open() as f:
        configuration = json.load(f)

    class ResourceModel:
        def __init__(self, dir="i", length=1):
            setattr(self, dir, Signal(length))

    mock_rsrcs = {}
    if "resources" in configuration:
        for resource in configuration["resources"]:
            mock_resources[resource["name"]] = ResourceModel(
                dir=resource["pins"]["dir"], length=len(resource["pins"]["pins"].split())
            )

    return mock_rsrcs
