def uart_echo(core):
    # first instruction is infinite loop when jump condition is true
    init = [
        (
            "turn_jumping_off",
            [{"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]}],
        )
    ]
    init += [("end", [{"constant": 0, "src_addr": 0, "dst_addr": 0}])]
    init += [
        (
            "prep_receive",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                # set a proper mask
                {
                    "constant": 1,
                    "src_addr": 1 << 7,
                    "dst_addr": core.Logical.inputs[2],
                },
            ],
        )
    ]
    init += [
        (
            "receive",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                # check if not rx_ready
                {
                    "constant": 0,
                    "src_addr": core.UART.outputs[1],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 1,
                    "src_addr": "receive",
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
            "transmit",
            [
                {
                    "constant": 0,
                    "src_addr": core.UART.outputs[0],
                    "dst_addr": core.UART.inputs[0],
                },
                {
                    "constant": 1,
                    "src_addr": "prep_receive",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {"constant": 1, "src_addr": 1, "dst_addr": core.Fetcher.inputs[0]},
            ],
        )
    ]

    return init
