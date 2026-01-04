import json
from pathlib import Path


def resolve_bb_labels(init, offset=0):
    addr_map = {}
    resolved_init = []
    current_addr = offset

    # First pass: map labels to addresses
    for item in init:
        if isinstance(item, tuple):
            label, instructions = item
            addr_map[label] = current_addr
            current_addr += len(instructions)
        else:
            current_addr += 1

    # Second pass: replace labels with addresses
    for item in init:
        if isinstance(item, tuple):
            _, instructions = item
            for instr in instructions:
                if isinstance(instr["src_addr"], str):
                    if instr["src_addr"] in addr_map:
                        instr["src_addr"] = addr_map[instr["src_addr"]]
                    else:
                        raise ValueError(f"Undefined label: {instr['src_addr']}")
                if isinstance(instr["dst_addr"], str):
                    if instr["dst_addr"] in addr_map:
                        instr["dst_addr"] = addr_map[instr["dst_addr"]]
                    else:
                        raise ValueError(f"Undefined label: {instr['dst_addr']}")
                resolved_init.append(instr)
        else:
            if isinstance(item["src_addr"], str):
                if item["src_addr"] in addr_map:
                    item["src_addr"] = addr_map[item["src_addr"]]
                else:
                    raise ValueError(f"Undefined label: {item['src_addr']}")
            if isinstance(item["dst_addr"], str):
                if item["dst_addr"] in addr_map:
                    item["dst_addr"] = addr_map[item["dst_addr"]]
                else:
                    raise ValueError(f"Undefined label: {item['dst_addr']}")
            resolved_init.append(item)

    return resolved_init


def build_addresses_core_model(config_detail_file: Path):
    with config_detail_file.open() as f:
        configuration = json.load(f)

    class CoreModel:
        def __init__(self, configuration):
            for fu in configuration["functional_units"]:
                setattr(self, fu["name"], self.FUModel(fu, 0))
                if "instances" in fu:
                    for i in range(1, fu["instances"]):
                        setattr(self, fu["name"] + str(i), self.FUModel(fu, i))

        class FUModel:
            def __init__(self, fu, nr):
                self.inputs = list(range(fu["input_address"][nr], fu["input_address"][nr] + fu["inputs"]))
                self.outputs = list(range(fu["output_address"][nr], fu["output_address"][nr] + fu["outputs"]))
                self.inouts = list(range(fu["inout_address"][nr], fu["inout_address"][nr] + fu["inouts"]))

    return CoreModel(configuration)
