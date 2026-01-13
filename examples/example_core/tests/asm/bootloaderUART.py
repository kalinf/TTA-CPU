def turn_jumping_off_instr(core):
    return {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]}


def jump_to_addr_instr(core, addr):
    return [
        {
            "constant": 0,
            "src_addr": addr,
            "dst_addr": core.Fetcher.inputs[1],
        },
        {
            "constant": 1,
            "src_addr": 1,
            "dst_addr": core.Fetcher.inputs[0],
        },
    ]


def jump_to_addr_const_instr(core, addr):
    return [
        {
            "constant": 1,
            "src_addr": addr,
            "dst_addr": core.Fetcher.inputs[1],
        },
        {
            "constant": 1,
            "src_addr": 1,
            "dst_addr": core.Fetcher.inputs[0],
        },
    ]


def return_instr(core):
    return jump_to_addr_instr(core, core.Stack.inouts[0])


def save_return_address_instr(core):
    return [
        {
            "constant": 1,
            "src_addr": 4,
            "dst_addr": core.Adder.inputs[0],
        },
        {
            "constant": 0,
            "src_addr": core.Fetcher.outputs[0],
            "dst_addr": core.Adder.inputs[1],
        },
        {
            "constant": 0,
            "src_addr": core.Adder.outputs[0],
            "dst_addr": core.Stack.inouts[0],
        },
    ]


def call_function_instr(core, function):
    return [
        *save_return_address_instr(core),
        *jump_to_addr_const_instr(core, function),
        turn_jumping_off_instr(core),
    ]


def receive_byte_func(core):
    return [
        (
            "receive_byte_func",
            [
                turn_jumping_off_instr(core),
                # check if not rx_ready
                {
                    "constant": 0,
                    "src_addr": core.UART.outputs[1],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 1,
                    "src_addr": "receive_byte_func",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                # set a proper mask
                {
                    "constant": 1,
                    "src_addr": 1 << 7,
                    "dst_addr": core.Logical.inputs[2],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.UART.outputs[0],
                    "dst_addr": core.Result.inouts[0],
                },
                *return_instr(core),
            ],
        )
    ]


def receive_word_func(core):
    return [
        (
            "receive_word_func",
            [
                turn_jumping_off_instr(core),
                *call_function_instr(core, "receive_byte_func"),
                {
                    "constant": 0,
                    "src_addr": core.Result.inouts[0],
                    "dst_addr": core.Regs.inouts[0],
                },
                *call_function_instr(core, "receive_byte_func"),
                # older bits has to be shifted
                {
                    "constant": 0,
                    "src_addr": core.Result.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 1,
                    "src_addr": 8,
                    "dst_addr": core.Logical.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[7],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Regs.inouts[0],
                    "dst_addr": core.Logical.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[1],
                    "dst_addr": core.Result.inouts[0],
                },
                *return_instr(core),
            ],
        )
    ]


# memory addresses of bootloader data
START_SYMBOL = 0x0
STOP_SYMBOL = 0x1
PROGRAM_TRANSFER = 0x2
DATA_TRANSFER = 0x3
LENGTH = 0x4
ADDRESS = 0x5
LAST_FRAME = 0x6


# Format of frame:
# 1. Start symbol - AAAA (2 bytes/1 word)
# 2. Data length in words (2 bytes/1 word)
# 3. Address (2 bytes/1 word)
# 4. Last frame - 0/1 (1 byte)
# 5. Program transfer - 5050 / Data transfer - 0505 (2 bytes/1 word)
# 6. Data (n words/2n bytes)
# 7. Stop sequence - 5555 (2 bytes/1 word)


def receive_frame(core):
    return [
        (
            "receive_frame",
            [
                turn_jumping_off_instr(core),
                *call_function_instr(core, "receive_word_func"),
                {
                    "constant": 0,
                    "src_addr": core.Result.inouts[0],
                    "dst_addr": core.Logical.inputs[0],
                },
                {
                    "constant": 1,
                    "src_addr": START_SYMBOL,
                    "dst_addr": core.DataMemory.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.DataMemory.outputs[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                # XOR on two values is non-zero if and only if they are unequal
                {
                    "constant": 1,
                    "src_addr": "receive_frame",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[2],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                # Start symbol read
                # Now read length
                *call_function_instr(core, "receive_word_func"),
                {
                    "constant": 1,
                    "src_addr": LENGTH,
                    "dst_addr": core.DataMemory.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Result.inouts[0],
                    "dst_addr": core.DataMemory.inputs[2],
                },
                # Now read address
                *call_function_instr(core, "receive_word_func"),
                {
                    "constant": 1,
                    "src_addr": ADDRESS,
                    "dst_addr": core.DataMemory.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Result.inouts[0],
                    "dst_addr": core.DataMemory.inputs[2],
                },
                # set increaser to start address
                {
                    "constant": 0,
                    "src_addr": core.Result.inouts[0],
                    "dst_addr": core.Increaser.inouts[0],
                },
                {
                    "constant": 1,
                    "src_addr": 1,
                    "dst_addr": core.Increaser.inouts[1],
                },
                {
                    "constant": 1,
                    "src_addr": 1,
                    "dst_addr": core.Increaser1.inouts[0],
                },
                {
                    "constant": 1,
                    "src_addr": 1,
                    "dst_addr": core.Increaser1.inouts[1],
                },
                # Now read if last frame
                *call_function_instr(core, "receive_byte_func"),
                {
                    "constant": 1,
                    "src_addr": LAST_FRAME,
                    "dst_addr": core.DataMemory.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Result.inouts[0],
                    "dst_addr": core.DataMemory.inputs[2],
                },
                # Now decide if it will be program or data
                *call_function_instr(core, "receive_word_func"),
                {
                    "constant": 0,
                    "src_addr": core.Result.inouts[0],
                    "dst_addr": core.Logical.inputs[0],
                },
                {
                    "constant": 1,
                    "src_addr": PROGRAM_TRANSFER,
                    "dst_addr": core.DataMemory.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.DataMemory.outputs[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                # set proper mask
                {
                    "constant": 1,
                    "src_addr": 1 << 0,
                    "dst_addr": core.Logical.inputs[2],
                },
                {
                    "constant": 1,
                    "src_addr": "save_program",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                {
                    "constant": 1,
                    "src_addr": DATA_TRANSFER,
                    "dst_addr": core.DataMemory.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.DataMemory.outputs[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                # set proper mask
                {
                    "constant": 1,
                    "src_addr": 1 << 0,
                    "dst_addr": core.Logical.inputs[2],
                },
                {
                    "constant": 1,
                    "src_addr": "save_data",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                # read bytes unmatched
                *jump_to_addr_const_instr(core, "receive_frame"),
            ],
        ),
        (
            "save_program",
            [
                turn_jumping_off_instr(core),
                *call_function_instr(core, "receive_word_func"),
                {
                    "constant": 0,
                    "src_addr": core.Increaser.inouts[0],
                    "dst_addr": core.ProgMemory.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.Result.inouts[0],
                    "dst_addr": core.ProgMemory.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Increaser1.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 1,
                    "src_addr": LENGTH,
                    "dst_addr": core.DataMemory.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.DataMemory.outputs[0],
                    "dst_addr": core.Logical.inputs[0],
                },
                # is compared < base
                {
                    "constant": 1,
                    "src_addr": 1 << 1,
                    "dst_addr": core.Logical.inputs[2],
                },
                {
                    "constant": 1,
                    "src_addr": "save_program",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                *jump_to_addr_const_instr(core, "receive_stop"),
            ],
        ),
        (
            "save_data",
            [
                turn_jumping_off_instr(core),
                *call_function_instr(core, "receive_word_func"),
                {
                    "constant": 0,
                    "src_addr": core.Increaser.inouts[0],
                    "dst_addr": core.DataMemory.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Result.inouts[0],
                    "dst_addr": core.DataMemory.inputs[2],
                },
                {
                    "constant": 0,
                    "src_addr": core.Increaser1.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 1,
                    "src_addr": LENGTH,
                    "dst_addr": core.DataMemory.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.DataMemory.outputs[0],
                    "dst_addr": core.Logical.inputs[0],
                },
                # is compared < base
                {
                    "constant": 1,
                    "src_addr": 1 << 0,
                    "dst_addr": core.Logical.inputs[2],
                },
                {
                    "constant": 1,
                    "src_addr": "save_data",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                *jump_to_addr_const_instr(core, "receive_stop"),
            ],
        ),
        (
            "receive_stop",
            [
                turn_jumping_off_instr(core),
                *call_function_instr(core, "receive_word_func"),
                {
                    "constant": 0,
                    "src_addr": core.Result.inouts[0],
                    "dst_addr": core.Logical.inputs[0],
                },
                {
                    "constant": 1,
                    "src_addr": STOP_SYMBOL,
                    "dst_addr": core.DataMemory.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.DataMemory.outputs[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                # XOR on two values is non-zero if and only if they are unequal
                # if stop symbol unrecognized -> retry receiving
                {
                    "constant": 1,
                    "src_addr": "receive_frame",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[2],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                # Stop symbol read
                # if that was last frame jump to the loaded program
                {
                    "constant": 1,
                    "src_addr": ADDRESS,
                    "dst_addr": core.DataMemory.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.DataMemory.outputs[0],
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 1,
                    "src_addr": LAST_FRAME,
                    "dst_addr": core.DataMemory.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.DataMemory.outputs[0],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                # else receive frame again
                *jump_to_addr_const_instr(core, "receive_frame"),
            ],
        ),
    ]


def bootloaderUART(core):
    init = receive_frame(core)
    init += receive_byte_func(core)
    init += receive_word_func(core)
    return init
