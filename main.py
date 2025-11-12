import sys
import json
import importlib.util
from amaranth import *
from pathlib import Path
from typing import final
from functools import partial
from core.registry import FU_REGISTRY
from core.core import TTA_Core
from testing.fibbonacci import run_sim_fib


@final
class UnimplementedFU(Exception):
    """Exception raised when there is no implementation file matching a functional_units entry."""


def load_all_fu_classes(fu_dir: Path):
    for f in fu_dir.glob("*.py"):
        spec = importlib.util.spec_from_file_location(f.stem, f)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <directory>")
        sys.exit(1)

    target_dir = Path(sys.argv[1]).resolve()
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
                        address=f_unit["address"],
                        trigger_pos=f_unit["trigger_positions"],
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
    )

    run_sim_fib(core)


if __name__ == "__main__":
    main()
