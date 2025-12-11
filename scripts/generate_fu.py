#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from typing import Iterable

TEMPLATE = """from amaranth import *{extraImports}
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu

class {FUname}(FU):   
    \"\"\"
    {FUdescription}
     
    Communication ports:
    ----------
    {inputCount} Inputs: 
    {outputCount} Outputs: 
    {inoutCount} Inouts: 
    \"\"\"
    def __init__(
        self,
        instr_bus: Bus,
        data_bus: Bus,
        input_count: int,
        output_count: int,
        inout_count: int,
        input_address: int,
        inout_address: int,
        output_address: int,{extraArgs}
    ):
        super().__init__(
            instr_bus=instr_bus,
            data_bus=data_bus,
            input_count=input_count,
            output_count=output_count,
            inout_count=inout_count,
            input_address=input_address,
            inout_address=inout_address,
            output_address=output_address,
        )
        {extraCodeInit}
    
    def elaborate(self, platform):
        m = super().elaborate(platform)
        {extraCodeElaborate}
        # here you can react on writes into trigger addresses 
        # here place your code, for example:
        # with m.If(self.instr_bus.data.dst_addr == self.inputs[0]["addr"]):
        #   m.d.falling += ...

        return m

register_fu("{FUname}", {FUname})
"""

NEWLINE = """
        """

FETCHER_IMPORTS = """
from core.utils.ReadPort import ReadPort"""

FETCHER_ARGS = """instruction_memory_depth: int,
        instruction_memory_read_ports: int,"""

FETCHER_CODE_INIT = """self.instruction_memory_depth = instruction_memory_depth
        self.instruction_memory_read_ports = instruction_memory_read_ports
        self.instr_read_ports = [ReadPort(depth=instruction_memory_depth, shape=self.instr_bus.data.shape()) for _ in range(instruction_memory_read_ports)]"""

RESOURCE_CODE_INIT = """self.resources = resources"""

RESOURCE_IMPORTS = """
from amaranth.build import Resource"""

RESOURCE_ARGS = """resources: dict[str, Resource],"""

RESOURCE_SIGNAL_DECLARATION = """{resource} = Signal.like(self.resources["{resource}"].{inout}, name="{resource}")"""

COMBINATIONAL = """m.d.comb += [{assignments}]"""

RESOURCE_ASSIGNMENT = """{signal0}.eq({signal1}),"""


def get_rsrc(resources, name):
    for rsrc in resources:
        if rsrc["name"] == name:
            return rsrc
    raise KeyError(f"No resource named {name}.")


def get_extra_code_elaborate(fu, resrcs):
    res = ""
    if "resources" in fu:
        for resource in fu["resources"]:
            res += NEWLINE
            res += RESOURCE_SIGNAL_DECLARATION.format(
                resource=resource, inout=get_rsrc(resrcs, resource)["pins"]["dir"]
            )
        res += NEWLINE
        assignments = ""
        for resource in fu["resources"]:
            assignments += RESOURCE_ASSIGNMENT.format(
                signal0=(
                    resource
                    if get_rsrc(resrcs, resource)["pins"]["dir"] == "i"
                    else ('self.resources["' + resource + '"].o')
                ),
                signal1=(
                    ('self.resources["' + resource + '"].i')
                    if get_rsrc(resrcs, resource)["pins"]["dir"] == "i"
                    else resource
                ),
            )
        res += COMBINATIONAL.format(assignments=assignments)
    return res


def get_extra_code_init(fu):
    res = ""
    if fu["name"] == "Fetcher":
        res += NEWLINE + FETCHER_CODE_INIT
    if "resources" in fu:
        res += NEWLINE + RESOURCE_CODE_INIT
    return res


def get_extra_imports(fu):
    res = ""
    if fu["name"] == "Fetcher":
        res += FETCHER_IMPORTS
    if "resources" in fu:
        res += RESOURCE_IMPORTS
    return res


def get_extra_args(fu):
    res = ""
    if fu["name"] == "Fetcher":
        res += NEWLINE + FETCHER_ARGS
    if "resources" in fu:
        res += NEWLINE + RESOURCE_ARGS
    return res


def generate_fu(
    target_dir: Path,
    fu_name: str,
    fu_description: str = "",
    input_count: int = 0,
    output_count: int = 0,
    inout_count: int = 0,
    extra_args: str = "",
    extra_code_elaborate: str = "",
    extra_code_init: str = "",
    extra_imports: str = "",
):
    fu_file = target_dir / f"{fu_name}.py"
    if fu_file.exists():
        return
    content = TEMPLATE.format(
        FUname=fu_name,
        FUdescription=fu_description,
        extraCodeInit=extra_code_init,
        extraCodeElaborate=extra_code_elaborate,
        extraImports=extra_imports,
        extraArgs=extra_args,
        inputCount=input_count,
        outputCount=output_count,
        inoutCount=inout_count,
    )
    fu_file.write_text(content)


def main():
    if not len(sys.argv) in {2, 3}:
        print("Usage: python3 generate_fu.py <directory> [<config_file>]")
        sys.exit(1)

    target_dir = Path(sys.argv[1]).resolve()
    config_path = Path(sys.argv[2]).resolve() if len(sys.argv) == 3 else (target_dir / "config.json")
    fu_dir = target_dir / "fu"
    fu_dir.mkdir(exist_ok=True)

    with config_path.open() as f:
        configuration = json.load(f)

    resources = configuration["resources"]
    input_count = 1  # address 0 is reserved and contains 0
    output_count = 0
    inout_count = 0
    for f_unit in configuration["functional_units"]:
        f_unit["input_address"] = input_count
        input_count += f_unit["inputs"]
        generate_fu(
            fu_dir,
            f_unit["name"],
            fu_description=f_unit["description"],
            extra_args=get_extra_args(f_unit),
            extra_imports=get_extra_imports(f_unit),
            extra_code_init=get_extra_code_init(f_unit),
            extra_code_elaborate=get_extra_code_elaborate(f_unit, resources),
            input_count=f_unit["inputs"],
            output_count=f_unit["outputs"],
            inout_count=f_unit["inouts"],
        )
    for f_unit in configuration["functional_units"]:
        f_unit["inout_address"] = input_count + inout_count
        inout_count += f_unit["inouts"]
    for f_unit in configuration["functional_units"]:
        f_unit["output_address"] = input_count + inout_count + output_count
        output_count += f_unit["outputs"]
    configuration["src_addr_width"] = src_addr_width = max(
        (output_count + inout_count).bit_length(),
        min(configuration["minimal_constant_size"], configuration["word_size"]),
    )
    configuration["dest_addr_width"] = dest_addr_width = (input_count + inout_count).bit_length()
    configuration["src_addr_width"] += (
        (1 << (src_addr_width + dest_addr_width).bit_length()) - src_addr_width - dest_addr_width - 1
        if configuration["i_really_like_powers_of_2"]
        else 0
    )
    configuration.pop("i_really_like_powers_of_2")
    configuration.pop("minimal_constant_size")

    config_detail_path = target_dir / "config_detail.json"
    with config_detail_path.open(mode="w", encoding="utf-8") as f:
        json.dump(configuration, f, ensure_ascii=False)

    # odpal tutaj formatting


if __name__ == "__main__":
    main()
