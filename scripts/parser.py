import re
from dataclasses import dataclass
from typing import Union
from pathlib import Path

@dataclass
class PortRef:
    unit: str
    port: str
    index: int

@dataclass
class Label:
    name: str

Value = Union[PortRef, int]

@dataclass
class Const:
    value: Value | Label

@dataclass
class Assign:
    dst: Value
    src: Value | Const

@dataclass
class Block:
    name: str
    instructions: list[Assign]


def strip_comment(line):
    return line.split("//", 1)[0].strip()

PORT_RE = re.compile(r"(\w+)\.(\w+)\[(\d+)\]")

def parse_port(s: str) -> PortRef:
    m = PORT_RE.fullmatch(s)
    if not m:
        raise SyntaxError(f"Illegal port format: {s}")
    return PortRef(m[1], m[2], int(m[3]))

def parse_value(s: str) -> Value:
    if s.startswith("b"):
        return int(s[1:], 2)
    if s.startswith("x"):
        return int(s[1:], 16)
    if s.isdigit():
        return int(s)
    return parse_port(s)

def parse_src(s: str):
    if s.startswith("C "):
        val = s[2:].strip()
        if val.startswith('"'):
            return Const(Label(val.strip('"')))
        else:        
            return Const(parse_value(val))
    return parse_value(s)

def parse_assign(line: str) -> Assign:
    dst, src = map(str.strip, line.split("<-"))
    return Assign(parse_value(dst), parse_src(src))

def parse_program(text: str) -> list[Block]:
    blocks = []
    current = None

    for raw in text.splitlines():
        line = strip_comment(raw)
        if not line:
            continue

        if line.endswith(":"):
            current = Block(line[:-1], [])
            blocks.append(current)
        else:
            current.instructions.append(parse_assign(line))

    return blocks

def resolve_value(v: Value, core) -> int:
    if isinstance(v, int):
        return v
    if isinstance(v, PortRef):
        return getattr(getattr(core, v.unit), v.port)[v.index]

def compile_blocks(blocks, core):
    result = []

    for block in blocks:
        instrs = []
        for a in block.instructions:
            if isinstance(a.src, Const):
                constant = 1
                if isinstance(a.src.value, Label):
                    src_addr = a.src.value.name
                else:
                    src_addr = resolve_value(a.src.value, core)
            else:
                constant = 0
                src_addr = resolve_value(a.src, core)
            dst_addr = resolve_value(a.dst, core)
            instrs.append({
                "constant": constant,
                "src_addr": src_addr,
                "dst_addr": dst_addr,
            })
        result.append((block.name, instrs))
    return result

def compile_file(path: Path, core):
    with path.open() as f:
        text = f.read()
    program = parse_program(text)
    return compile_blocks(program, core)