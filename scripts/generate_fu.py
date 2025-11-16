#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from typing import Iterable

TEMPLATE = """from amaranth import *
from core.FU import FU
from core.bus import Bus
from core.registry import register_fu

class {FUname}(FU):        
    def __init__(
        self,
        instr_bus: Bus,
        data_bus: Bus,
        input_count: int,
        output_count: int,
        inout_count: int,
        input_address: int,
        inout_address: int,
        output_address: int,
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
    
    def elaborate(self, platform):
        m = super().elaborate(platform)

        # here you can react on writes into trigger addresses 
        # here place your code, for example:
        # with m.If(self.instr_bus.data.dst_addr == self.inputs[0]["addr"]):
        #   m.d.falling += ...

        return m

register_fu("{FUname}", {FUname})
"""


def generate_fu(target_dir: Path, fu_name: str):
    fu_file = target_dir / f"{fu_name}.py"
    if fu_file.exists():
        return
    content = TEMPLATE.format(FUname=fu_name)
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

    input_count = 1  # address 0 is reserved and contains 0
    output_count = 0
    inout_count = 0
    for f_unit in configuration["functional_units"]:
        f_unit["input_address"] = input_count
        input_count += f_unit["inputs"]
        generate_fu(fu_dir, f_unit["name"])
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


if __name__ == "__main__":
    main()
