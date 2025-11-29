import os
import argparse
from pathlib import Path
from constants.ecp5_platform import Colorlight_i9_R72Platform
from amaranth import *
from core.generate_core import gen_core

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CORE_PATH = (SCRIPT_DIR / ".." / "examples" / "basic_core").resolve()


class Top(Elaboratable):
    def __init__(self, core):
        self.core = core

    def elaborate(self, platform):
        m = Module()
        m.submodules.core = self.core

        clk25 = platform.request("clk25")
        result = platform.request("result")
        write_port = platform.request("write_port")
        m.d.comb += [
            self.core.clk.eq(clk25.i),
            result.o.eq(self.core.result),
            self.core.write_port.addr.eq(write_port.addr.i),
            self.core.write_port.en.eq(write_port.en.i),
            self.core.write_port.data.eq(write_port.data.i),
        ]

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

    args = parser.parse_args()

    os.environ["AMARANTH_verbose"] = "true" if args.verbose else "false"

    dir_path = Path(args.config_directory).resolve()
    if not dir_path.exists():
        raise FileNotFoundError(f"Invalid core directory path: {dir_path}")

    core = Top(gen_core(dir_path, synthesis=True))
    Colorlight_i9_R72Platform().build(core, do_program=args.flash)


if __name__ == "__main__":
    main()
