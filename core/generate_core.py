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


def load_all_ip_classes(ip_dir: Path):
    for f in ip_dir.glob("*.py"):
        spec = importlib.util.spec_from_file_location(f.stem, f)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


def gen_core(directory: Path, instr_memory_init=[], data_memory_init=[], synthesis=False, resources=None):
    target_dir = directory.resolve()
    fu_dir = target_dir / "fu"
    ip_dir = target_dir / "ip"
    config_path = target_dir / "config_detail.json"

    if ip_dir.exists():
        load_all_ip_classes(ip_dir)
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
                        input_address=f_unit["input_address"][0],
                        inout_address=f_unit["inout_address"][0],
                        output_address=f_unit["output_address"][0],
                    ),
                )
            ]
            if "instances" in f_unit:
                for i in range(1, f_unit["instances"]):
                    fu_partial += [
                        (
                            name + str(i),
                            partial(
                                FU_REGISTRY[name],
                                input_count=f_unit["inputs"],
                                output_count=f_unit["outputs"],
                                inout_count=f_unit["inouts"],
                                input_address=f_unit["input_address"][i],
                                inout_address=f_unit["inout_address"][i],
                                output_address=f_unit["output_address"][i],
                            ),
                        )
                    ]
        else:
            raise UnimplementedFU(f"No implementation file found for {name}.")

    if resources is not None:
        return TTA_Core(
            src_addr_width=configuration["src_addr_width"],
            dest_addr_width=configuration["dest_addr_width"],
            data_width=configuration["word_size"],
            FUs=fu_partial,
            instr_memory_depth=configuration["instruction_memory_depth"],
            instr_memory_init=instr_memory_init,
            instr_memory_rports=(
                configuration["instruction_memory_read_ports"]
                if "instruction_memory_read_ports" in configuration
                else 1
            ),
            data_memory_depth=configuration["data_memory_depth"],
            data_memory_init=data_memory_init,
            synthesis=synthesis,
            resources=resources,
        )
    else:
        return partial(
            TTA_Core,
            src_addr_width=configuration["src_addr_width"],
            dest_addr_width=configuration["dest_addr_width"],
            data_width=configuration["word_size"],
            FUs=fu_partial,
            instr_memory_depth=configuration["instruction_memory_depth"],
            instr_memory_init=instr_memory_init,
            instr_memory_rports=(
                configuration["instruction_memory_read_ports"]
                if "instruction_memory_read_ports" in configuration
                else 1
            ),
            data_memory_depth=configuration["data_memory_depth"],
            data_memory_init=data_memory_init,
            synthesis=synthesis,
        )
