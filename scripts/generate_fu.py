#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path

TEMPLATE = """from amaranth import *
from {path_to_core}.FU import FU
from {path_to_core}.bus import Bus

class {FUname}(FU):        
    def __init__(self, instr_bus : Bus, data_bus : Bus, input_count : int, output_count : int, address : int, trigger_pos : int):
        super().__init__(instr_bus=instr_bus, data_bus=data_bus, input_count=input_count, output_count=output_count, address=address, trigger_pos=trigger_pos)
    
    def elaborate(self, platform):
        m = super().elaborate(platform)
                
        with m.If(self.instr_bus.data.dst_addr == self.trigger_addr):
            # place for your code
            # m.d.falling += ...
            ...

        return m
"""


def python_import_relative_path(from_dir: Path, to_dir: Path) -> str:
    """
    Returns python relative import path from `from_dir` to `to_dir` (for example `....core`).
    """
    rel = os.path.relpath(to_dir, from_dir)
    parts = Path(rel).parts
    # this is legal, because relpath returns the shortest path
    prefix = "." * sum(1 for p in parts if p == "..")
    suffix = ".".join(p for p in parts if p not in ("..", "."))
    return prefix + (("." + suffix) if prefix and suffix else suffix or ".")


def generate_fu(target_dir: Path, fu_name: str):
    fu_file = target_dir / f"{fu_name}.py"
    if fu_file.exists():
        # tu chcę tylko zmienić relatywną ścieżkę do katalogu projektu
        ...
    relative_path_to_core = python_import_relative_path(target_dir, Path(__file__).resolve().parent.parent / "core")

    content = TEMPLATE.format(path_to_core=relative_path_to_core, FUname=fu_name)

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

    input_count = 0
    output_count = 0
    for f_unit in configuration["functional_units"]:
        f_unit["address"] = input_count + output_count
        input_count += f_unit["inputs"]
        output_count += f_unit["outputs"]
        generate_fu(fu_dir, f_unit["name"])
    configuration["src_addr_width"] = src_addr_width = max(
        output_count.bit_length(), min(configuration["minimal_constant_size"], configuration["word_size"])
    )
    configuration["dest_addr_width"] = dest_addr_width = input_count.bit_length()
    configuration["src_addr_width"] += (
        (1 << (src_addr_width + dest_addr_width).bit_length()) - src_addr_width - dest_addr_width - 1
        if configuration["i_really_like_powers_of_2"]
        else 0
    )
    configuration.pop("i_really_like_powers_of_2")

    config_detail_path = target_dir / "config_detail.json"
    with config_detail_path.open(mode="w", encoding="utf-8") as f:
        json.dump(configuration, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
