def data_memory(core):
    # first instruction is infinite loop when jump condition is true
    init = [("end", [{"constant": 0, "src_addr": 0, "dst_addr": 0}])]
    init += [
        (
            "setup",
            [
                # set up iterator increaser
                {
                    "constant": 1,
                    "src_addr": 0,
                    "dst_addr": core.Increaser.inouts[0],
                },
                {
                    "constant": 1,
                    "src_addr": 1,
                    "dst_addr": core.Increaser.inouts[1],
                },
                # set up ASCII increaser
                {
                    "constant": 1,
                    "src_addr": 97,
                    "dst_addr": core.Increaser1.inouts[0],
                },
                {
                    "constant": 1,
                    "src_addr": 1,
                    "dst_addr": core.Increaser1.inouts[1],
                },
                # number of letters to write
                {
                    "constant": 1,
                    "src_addr": 25,
                    "dst_addr": core.Logical.inputs[0],
                },
                # set mask
                {
                    "constant": 1,
                    "src_addr": 1 << 1,
                    "dst_addr": core.Logical.inputs[2],
                },
            ],
        )
    ]
    init += [
        (
            "write_letter",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                # write ascii code
                # address
                {
                    "constant": 0,
                    "src_addr": core.Increaser.inouts[0],
                    "dst_addr": core.Regs.inouts[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.Regs.inouts[0],
                    "dst_addr": core.DataMemory.inputs[1],
                },
                # data
                {
                    "constant": 0,
                    "src_addr": core.Increaser1.inouts[0],
                    "dst_addr": core.DataMemory.inputs[2],
                },
                {
                    "constant": 0,
                    "src_addr": core.Regs.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                # repete if iterator < 25
                {
                    "constant": 1,
                    "src_addr": "write_letter",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
            ],
        )
    ]
    init += [
        (
            "wait_for_start",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                # set a proper mask
                {
                    "constant": 1,
                    "src_addr": 1 << 7,
                    "dst_addr": core.Logical.inputs[2],
                },
                # check if not rx_ready
                {
                    "constant": 0,
                    "src_addr": core.UART.outputs[1],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 1,
                    "src_addr": "wait_for_start",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
            ]
        )
    ]
    init += [
        (
            "zero_iterator",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                # turn iterator increaser 0
                {
                    "constant": 1,
                    "src_addr": 0,
                    "dst_addr": core.Increaser.inouts[0],
                },
            ]
        )
    ]
    init += [
        (
            "transmit_letter",
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
                # transmit data
                {
                    "constant": 0,
                    "src_addr": core.DataMemory.outputs[0],
                    "dst_addr": core.UART.inputs[0],
                },
            ],
        )
    ]
    init += [
        (
            "wait_for_transmission_done",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                # set a proper mask
                {
                    "constant": 1,
                    "src_addr": 1 << 7,
                    "dst_addr": core.Logical.inputs[2],
                },
                # check if transmission not done
                {
                    "constant": 0,
                    "src_addr": core.UART.outputs[2],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 1,
                    "src_addr": "wait_for_transmission_done",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                # transmission already done 
                # set a proper mask
                {
                    "constant": 1,
                    "src_addr": 1 << 1,
                    "dst_addr": core.Logical.inputs[2],
                },
                {
                    "constant": 0,
                    "src_addr": core.Regs.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                # repete if iterator < 25
                {
                    "constant": 1,
                    "src_addr": "transmit_letter",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                # else zero iterator
                {
                    "constant": 1,
                    "src_addr": "zero_iterator",
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
