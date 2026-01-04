def bootloader_data_memory(core):
    # first instruction is infinite loop when jump condition is true
    init = [("end", [{"constant": 0, "src_addr": 0, "dst_addr": 0}])]
    init += [
        (
            "setup",
            [
                # set up data memory iterator increaser
                # at address 0x0 is program length, instructions start from 0x1
                {
                    "constant": 1,
                    "src_addr": 1,
                    "dst_addr": core.Increaser.inouts[0],
                },
                {
                    "constant": 1,
                    "src_addr": 1,
                    "dst_addr": core.Increaser.inouts[1],
                },
                # set up instruction memory iterator increaser
                # bootloader's space is first 50 addresses
                {
                    "constant": 1,
                    "src_addr": 50,
                    "dst_addr": core.Increaser1.inouts[0],
                },
                {
                    "constant": 1,
                    "src_addr": 1,
                    "dst_addr": core.Increaser1.inouts[1],
                },
                # set limit to program length (0x0)
                {
                    "constant": 1,
                    "src_addr": 0,
                    "dst_addr": core.DataMemory.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.DataMemory.outputs[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                # set mask
                {
                    "constant": 1,
                    "src_addr": 1 << 2,
                    "dst_addr": core.Logical.inputs[2],
                },
            ],
        )
    ]
    init += [
        (
            "program_memory",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                # address
                {
                    "constant": 0,
                    "src_addr": core.Increaser.inouts[0],
                    "dst_addr": core.Regs.inouts[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.Regs.inouts[0],
                    "dst_addr": core.DataMemory.inputs[0],
                },
                # write instruction
                {
                    "constant": 0,
                    "src_addr": core.Increaser1.inouts[0],
                    "dst_addr": core.ProgMemory.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.DataMemory.outputs[0],
                    "dst_addr": core.ProgMemory.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Regs.inouts[0],
                    "dst_addr": core.Logical.inputs[0],
                },
                # repete
                {
                    "constant": 1,
                    "src_addr": "program_memory",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                # else jump to the main program
                {
                    "constant": 1,
                    "src_addr": 50,
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 1,
                    "src_addr": 1,
                    "dst_addr": core.Fetcher.inputs[0],
                },
            ],
        )
    ]

    return init
