import sys
import json
import argparse
import importlib.util
from pathlib import Path
from utils.utils import build_addresses_core_model, resolve_bb_labels

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CORE_PATH = (SCRIPT_DIR / ".." / "examples" / "basic_core").resolve()


def import_function_from_file(file_path, function_name):
    file_path = Path(file_path).resolve()

    spec = importlib.util.spec_from_file_location("dynamic_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, function_name):
        raise AttributeError(f"Module does not contain function '{function_name}'")

    return getattr(module, function_name)


def json2python(json_path):
    with json_path.open() as f:
        program = json.load(f)
    return program


def prog2data(program, src_width, dest_width, data_width):
    data = []
    if src_width + dest_width < data_width:
        # at address 0x0 is program length
        data.append({"data": len(program)})
        for instr in program:
            word = (
                instr["dst_addr"] + (instr["src_addr"] << dest_width) + (instr["constant"] << (src_width + dest_width))
            )
            data.append({"data": word})
    else:
        raise NotImplementedError(
            f"Translation for instruction ({src_width + dest_width + 1} bits) longer than word ({data_width} bits) is yet unimplemented."
        )

    return data


def json_prog2json_data(prog_json_path, src_width, dest_width, data_width, data_json_path=None):
    with prog_json_path.open() as f:
        program = json.load(f)
    data = prog2data(program=program, src_width=src_width, dest_width=dest_width, data_width=data_width)

    if data_json_path is not None:
        with data_json_path.open("w") as f:
            json.dump(data, f, indent=4)

    return data


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--mode",
        default="python2json",
        choices=["python2json", "json2python", "json2binary", "binary2json", "json_prog2json_data"],
        help="Selects operation to perform. Default: %(default)s",
    )
    parser.add_argument(
        "-d",
        "--config-directory",
        default=str(DEFAULT_CORE_PATH),
        help="Provide directory containing FUs and configuration file. Default: %(default)s",
    )
    parser.add_argument(
        "--program-file",
        default=str(Path(DEFAULT_CORE_PATH) / "program.json"),
        help="Provide path to program file. Default: %(default)s",
    )
    parser.add_argument(
        "--data-file",
        default=str(Path(DEFAULT_CORE_PATH) / "data.json"),
        help="Provide path to data file. Default: %(default)s",
    )
    parser.add_argument(
        "-f",
        "--function-name",
        default="program",
        help="Name of function to import from program file. Default: %(default)s",
    )
    parser.add_argument(
        "-o",
        "--offset",
        default=0,
        help="Offset of program file. Default: %(default)s",
    )

    args = parser.parse_args()

    if args.mode == "python2json":
        core_model = build_addresses_core_model(Path(args.config_directory) / "config_detail.json")
        func = import_function_from_file(args.program_file, args.function_name)
        program = resolve_bb_labels(func(core_model), offset=int(args.offset))
        json_path = Path(args.config_directory) / "program.json"
        with json_path.open("w") as f:
            json.dump(program, f, indent=4)
    elif args.mode == "json2python":
        print(json2python(Path(args.program_file).resolve()))
    elif args.mode == "json2binary":
        ...
    elif args.mode == "binary2json":
        ...
    elif args.mode == "json_prog2json_data":
        prog_json_path = Path(args.config_directory) / "program.json"
        data_json_path = Path(args.config_directory) / "data.json"

        configuration_path = Path(args.config_directory) / "config_detail.json"
        with configuration_path.open() as f:
            configuration = json.load(f)

        json_prog2json_data(
            prog_json_path=prog_json_path,
            src_width=configuration["src_addr_width"],
            dest_width=configuration["dest_addr_width"],
            data_width=configuration["word_size"],
            data_json_path=data_json_path,
        )
