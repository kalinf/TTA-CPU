import os
import argparse
import importlib
from amaranth import *
from pathlib import Path
from core.generate_core import gen_core
from constants.ecp5_platform import Colorlight_i9_R72Platform
from core.utils.resources import create_resources, add_resources, get_requested_resources_names
from scripts.translator import json2python

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CORE_PATH = (SCRIPT_DIR / ".." / "examples" / "basic_core").resolve()


class Top(Elaboratable):
    def __init__(self, core, resources):
        self.core = core
        self.resources = resources

    def elaborate(self, platform):
        m = Module()

        clk25 = platform.request("clk25")

        resource_dict = {"clk25": clk25}
        for resource in self.resources:
            print(resource)
            resource_dict[resource] = platform.request(resource)
            print(resource_dict[resource])

        m.submodules.core = core = self.core(resources=resource_dict)

        return m


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--platform",
        default="ecp5",
        choices=["ecp5"],
        help="Selects platform to synthesize circuit on. Default: %(default)s",
    )

    parser.add_argument(
        "-d",
        "--config-directory",
        default=str(DEFAULT_CORE_PATH),
        help="Provide directory containing FUs and configuration file. Default: %(default)s",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enables verbose output. Default: %(default)s",
    )

    parser.add_argument(
        "-f",
        "--flash",
        action="store_true",
        help="Enables flashing device after synthesis. Default: %(default)s",
    )

    parser.add_argument(
        "--init-instr-memory",
        default="",
        help="Provide json file containing initial values for instruction memory. Default: empty",
    )

    args = parser.parse_args()

    os.environ["AMARANTH_verbose"] = "true" if args.verbose else "false"

    dir_path = Path(args.config_directory).resolve()
    if not dir_path.exists():
        raise FileNotFoundError(f"Invalid core directory path: {dir_path}")

    instr_memory_init = json2python(Path(args.init_instr_memory).resolve()) if args.init_instr_memory != "" else []
    platform = Colorlight_i9_R72Platform()
    add_resources(platform, create_resources(dir_path))
    print(platform.resources)
    core = Top(
        gen_core(dir_path, instr_memory_init=instr_memory_init, synthesis=True),
        resources=get_requested_resources_names(dir_path),
    )
    platform.build(core, do_program=args.flash)


if __name__ == "__main__":
    main()
