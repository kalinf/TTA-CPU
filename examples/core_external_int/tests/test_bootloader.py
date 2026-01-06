import pytest
import json
from amaranth import *
from amaranth.sim import Simulator
from utils.utils import resolve_bb_labels
from examples.core_external_int.tests.asm.bootloaderUART import bootloaderUART
from examples.core_external_int.tests.asm.uart import uart_echo
from examples.core_external_int.tests.test_uart import uart_transmit, to_binary
from examples.core_external_int.tests.data.bootloader_data import bootloader_data
from core.generate_core import gen_core
from scripts.translator import prog2data

# Format of frame:
# 1. Start symbol - AAAA (2 bytes/1 word)
# 2. Data length in words (2 bytes/1 word)
# 3. Address (2 bytes/1 word)
# 4. Last frame - 0/1 (1 byte)
# 5. Program transfer - 5050 / Data transfer - 0505 (2 bytes/1 word)
# 6. Data (n words/2n bytes)
# 7. Stop sequence - 5555 (2 bytes/1 word)

START_SYMBOL = 0xAAAA
PROGRAM_TRANSFER = 0x5050
DATA_TRANSFER = 0x0505
STOP_SYMBOL = 0x5555
OFFSET = 150

BAUD_RATE = 115200


async def transmit_word(ctx, data, period, baud_rate, core):
    await uart_transmit(ctx, data, period, baud_rate, core)
    await uart_transmit(ctx, data >> 8, period, baud_rate, core)


def test_bootloaderUART(core_address_model, dir_path, vcd_file, mock_resources):
    configuration_path = dir_path / "config_detail.json"
    with configuration_path.open() as f:
        configuration = json.load(f)
    bootloader_init = bootloaderUART(core_address_model)
    resolved_bootloader_init = resolve_bb_labels(bootloader_init)
    program_init = uart_echo(core_address_model)
    resolved_program_init = resolve_bb_labels(program_init, offset=150)
    main_program = prog2data(
        resolved_program_init,
        src_width=configuration["src_addr_width"],
        dest_width=configuration["dest_addr_width"],
        data_width=configuration["word_size"],
        start_length=False,
    )
    core = gen_core(
        dir_path,
        instr_memory_init=resolved_bootloader_init,
        data_memory_init=bootloader_data,
        resources=mock_resources,
    )
    sim = Simulator(core)
    sim.add_clock(4e-8, domain="mem")
    sim.add_clock(4e-8, domain="sync")

    async def tb(ctx):
        ctx.set(core.resources["uart_rx"].i, 1)
        await ctx.tick(domain="falling").repeat(100)
        await transmit_word(ctx, START_SYMBOL, 4e-8, BAUD_RATE, core)
        await transmit_word(ctx, len(main_program), 4e-8, BAUD_RATE, core)
        await transmit_word(ctx, OFFSET, 4e-8, BAUD_RATE, core)
        await uart_transmit(ctx, 1, 4e-8, BAUD_RATE, core)
        await transmit_word(ctx, PROGRAM_TRANSFER, 4e-8, BAUD_RATE, core)
        for d in main_program:
            await transmit_word(ctx, d["data"], 4e-8, BAUD_RATE, core)
        await transmit_word(ctx, STOP_SYMBOL, 4e-8, BAUD_RATE, core)
        await ctx.tick(domain="falling").repeat(100)
        await transmit_word(ctx, 42, 4e-8, BAUD_RATE, core)
        await ctx.tick(domain="falling").repeat(700)
        # TODO: actually check the correctness of transmitted data

    sim.add_testbench(tb)
    if vcd_file is not None:
        with sim.write_vcd(str(vcd_file)):
            sim.run()
    else:
        sim.run()
