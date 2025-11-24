import json
import importlib.util
from amaranth import *
from pathlib import Path
from typing import final
from functools import partial
from .registry import FU_REGISTRY
from .core import TTA_Core


@final
class UnimplementedFU(Exception):
    """Exception raised when there is no implementation file matching a functional_units entry."""


def load_all_fu_classes(fu_dir: Path):
    for f in fu_dir.glob("*.py"):
        spec = importlib.util.spec_from_file_location(f.stem, f)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


def gen_core(directory: Path, instr_memory_init=[]):
    target_dir = directory.resolve()
    fu_dir = target_dir / "fu"
    config_path = target_dir / "config_detail.json"

    load_all_fu_classes(fu_dir)

    with config_path.open() as f:
        configuration = json.load(f)

    fu_partial = []
    for f_unit in configuration["functional_units"]:
        name = f_unit["name"]
        if name in FU_REGISTRY:
            fu_partial += [
                (
                    name,
                    partial(
                        FU_REGISTRY[name],
                        input_count=f_unit["inputs"],
                        output_count=f_unit["outputs"],
                        inout_count=f_unit["inouts"],
                        input_address=f_unit["input_address"],
                        inout_address=f_unit["inout_address"],
                        output_address=f_unit["output_address"],
                    ),
                )
            ]
        else:
            raise UnimplementedFU(f"No implementation file found for {name}.")

    core = TTA_Core(
        src_addr_width=configuration["src_addr_width"],
        dest_addr_width=configuration["dest_addr_width"],
        data_width=configuration["word_size"],
        FUs=fu_partial,
        instr_memory_depth=configuration["instruction_memory_depth"],
        instr_memory_init=instr_memory_init,
        instr_memory_rports=configuration["instruction_memory_read_ports"],
    )
    return core
