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


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--mode",
        default="python2json",
        choices=["python2json", "json2python", "json2binary", "binary2json"],
        help="Selects operation to perform. Default: %(default)s",
    )
    parser.add_argument(
        "-d",
        "--config-directory",
        default=str(DEFAULT_CORE_PATH),
        help="Provide directory containing FUs and configuration file. Default: %(default)s",
    )
    parser.add_argument(
        "-p",
        "--program-file",
        default=str(DEFAULT_CORE_PATH),
        help="Provide path to program file. Default: %(default)s",
    )
    parser.add_argument(
        "-f",
        "--function-name",
        default="program",
        help="Name of function to import from program file. Default: %(default)s",
    )

    args = parser.parse_args()

    if args.mode == "python2json":
        core_model = build_addresses_core_model(Path(args.config_directory) / "config_detail.json")
        func = import_function_from_file(args.program_file, args.function_name)
        program = resolve_bb_labels(func(core_model))
        json_path = Path(args.config_directory) / "program.json"
        with json_path.open("w") as f:
            json.dump(program, f, indent=4)
    elif args.mode == "json2python":
        print(json2python(Path(args.program_file).resolve()))
    elif args.mode == "json2binary":
        ...
    elif args.mode == "binary2json":
        ...
