#!/usr/bin/env python3
import sys
import json
import argparse
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
from core.utils.MemoryPorts import ReadPort"""

FETCHER_ARGS = """instruction_memory_depth: int,
        instruction_memory_read_ports: int,"""

FETCHER_CODE_INIT = """self.instruction_memory_depth = instruction_memory_depth
        self.instruction_memory_read_ports = instruction_memory_read_ports
        self.instr_read_ports = [ReadPort(depth=instruction_memory_depth, shape=self.instr_bus.data.shape()) for _ in range(instruction_memory_read_ports)]"""

PROG_MEMORY_IMPORTS = """
from core.utils.MemoryPorts import WritePort"""

PROG_MEMORY_ARGS = """instruction_memory_depth: int,"""

PROG_MEMORY_CODE_INIT = """self.instruction_memory_depth = instruction_memory_depth
        self.instr_write_port = WritePort(depth=instruction_memory_depth, shape=self.instr_bus.data.shape())"""

DATA_MEMORY_IMPORTS = """
from core.utils.MemoryPorts import ReadPort, WritePort"""

DATA_MEMORY_ARGS = """data_memory_depth: int,"""

DATA_MEMORY_CODE_INIT = """self.data_memory_depth = data_memory_depth
        self.data_read_port = ReadPort(depth=data_memory_depth, shape=self.data_bus.data.shape())
        self.data_write_port = WritePort(depth=data_memory_depth, shape=self.data_bus.data.shape())"""

RESOURCE_CODE_INIT = """self.resources = resources"""

RESOURCE_IMPORTS = """
from amaranth.build import Resource"""

RESOURCE_ARGS = """resources: dict[str, Resource],"""

RESOURCE_SIGNAL_DECLARATION = """{resource} = Signal.like(self.resources["{resource}"].{inout}, name="{resource}")"""

COMBINATIONAL = """m.d.comb += [{assignments}]"""

RESOURCE_ASSIGNMENT = """{signal0}.eq({signal1}),"""

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CORE_PATH = (SCRIPT_DIR / ".." / "examples" / "example_core").resolve()


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
    if fu["name"] == "DataMemory":
        res += NEWLINE + DATA_MEMORY_CODE_INIT
    if fu["name"] == "ProgMemory":
        res += NEWLINE + PROG_MEMORY_CODE_INIT
    if "resources" in fu:
        res += NEWLINE + RESOURCE_CODE_INIT
    return res


def get_extra_imports(fu):
    res = ""
    if fu["name"] == "Fetcher":
        res += FETCHER_IMPORTS
    if fu["name"] == "DataMemory":
        res += DATA_MEMORY_IMPORTS
    if fu["name"] == "ProgMemory":
        res += PROG_MEMORY_IMPORTS
    if "resources" in fu:
        res += RESOURCE_IMPORTS
    return res


def get_extra_args(fu):
    res = ""
    if fu["name"] == "Fetcher":
        res += NEWLINE + FETCHER_ARGS
    if fu["name"] == "DataMemory":
        res += NEWLINE + DATA_MEMORY_ARGS
    if fu["name"] == "ProgMemory":
        res += NEWLINE + PROG_MEMORY_ARGS
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--config-directory",
        default=str(DEFAULT_CORE_PATH),
        help="Provide directory containing FUs and configuration file. Default: %(default)s",
    )
    parser.add_argument(
        "--config-path",
        default="",
        help="Provide configuration file. Default: %(default)s",
    )
    args = parser.parse_args()
    target_dir = Path(args.config_directory).resolve()
    config_path = Path(args.config_path).resolve() if args.config_path != "" else (target_dir / "config.json")
    fu_dir = target_dir / "fu"
    fu_dir.mkdir(exist_ok=True)

    with config_path.open() as f:
        configuration = json.load(f)

    resources = configuration["resources"] if "resources" in configuration else []
    input_count = 0
    output_count = 0
    inout_count = 1  # address 0 is reserved and contains 0
    for f_unit in configuration["functional_units"]:
        instances = f_unit["instances"] if "instances" in f_unit else 1
        f_unit["input_address"] = [None] * instances
        f_unit["output_address"] = [None] * instances
        f_unit["inout_address"] = [None] * instances
        for i in range(instances):
            f_unit["inout_address"][i] = inout_count
            inout_count += f_unit["inouts"]
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
        instances = f_unit["instances"] if "instances" in f_unit else 1
        for i in range(instances):
            f_unit["input_address"][i] = inout_count + input_count
            input_count += f_unit["inputs"]
            f_unit["output_address"][i] = inout_count + output_count
            output_count += f_unit["outputs"]
    configuration["src_addr_width"] = src_addr_width = max(
        (inout_count + output_count).bit_length(),
        (
            # constant longer than word size is not useful
            min(configuration["minimal_constant_size"], configuration["word_size"])
            if "minimal_constant_size" in configuration
            else 0
        ),
    )
    configuration["dest_addr_width"] = dest_addr_width = (inout_count + input_count).bit_length()
    configuration["src_addr_width"] += (
        (1 << (src_addr_width + dest_addr_width).bit_length()) - src_addr_width - dest_addr_width - 1
        if ("i_really_like_powers_of_2" in configuration and configuration["i_really_like_powers_of_2"])
        else 0
    )
    configuration.pop("i_really_like_powers_of_2", None)
    configuration.pop("minimal_constant_size", None)

    config_detail_path = target_dir / "config_detail.json"
    with config_detail_path.open(mode="w", encoding="utf-8") as f:
        json.dump(configuration, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
