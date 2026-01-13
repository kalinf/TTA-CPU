def handlers_base(core, handler=[], prep=[]):
    init = [
        (
            "turn_jumping_off",
            [{"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]}],
        )
    ]
    # this instruction is infinite loop when jump condition is true
    init += [("end", [{"constant": 0, "src_addr": 0, "dst_addr": 0}])]
    init += [
        (
            "b0",
            [
                # set handler address
                {
                    "constant": 1,
                    "src_addr": "handler",
                    "dst_addr": core.Fetcher.inouts[0],
                },
            ],
        )
    ]
    init += prep

    init += [
        (
            "b1",
            [
                # jump to end and lock
                {"constant": 1, "src_addr": "end", "dst_addr": core.Fetcher.inputs[1]},
                {"constant": 1, "src_addr": 1, "dst_addr": core.Fetcher.inputs[0]},
            ],
        )
    ]

    init += handler

    return init


def wandering_led_prep(core):
    return [
        (
            "led_prep",
            [
                {"constant": 1, "src_addr": 1, "dst_addr": core.Pins.inouts[0]},
                # value in register indicates direction
                {
                    "constant": 1,
                    "src_addr": 0b111111111,
                    "dst_addr": core.ConstantLoader.inputs[0],
                },
                {
                    "constant": 1,
                    "src_addr": 0b111111111,
                    "dst_addr": core.ConstantLoader.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.ConstantLoader.outputs[0],
                    "dst_addr": core.Regs.inouts[0],
                },
            ],
        )
    ]


def wandering_led_handler(core):
    return [
        (
            "handler",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                {
                    "constant": 0,
                    "src_addr": core.Pins.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                # check if lighted led is at the edge
                {
                    "constant": 1,
                    "src_addr": 0b10001,
                    "dst_addr": core.Logical.inputs[0],
                },
                {"constant": 1, "src_addr": 1 << 6, "dst_addr": core.Logical.inputs[2]},
                {
                    "constant": 1,
                    "src_addr": "shift",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                # wandering led has to change direction
                {
                    "constant": 0,
                    "src_addr": core.Regs.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[3],
                    "dst_addr": core.Regs.inouts[0],
                },
            ],
        ),
        (
            "shift",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                {
                    "constant": 0,
                    "src_addr": core.Pins.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                {"constant": 1, "src_addr": 1, "dst_addr": core.Logical.inputs[0]},
                {
                    "constant": 1,
                    "src_addr": "shift_right",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Regs.inouts[0],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[7],
                    "dst_addr": core.Pins.inouts[0],
                },
                {
                    "constant": 1,
                    "src_addr": "return",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {"constant": 1, "src_addr": 1, "dst_addr": core.Fetcher.inputs[0]},
            ],
        ),
        (
            "shift_right",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[6],
                    "dst_addr": core.Pins.inouts[0],
                },
            ],
        ),
        (
            "return",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                {"constant": 1, "src_addr": "end", "dst_addr": core.Fetcher.inputs[1]},
                {"constant": 1, "src_addr": 1, "dst_addr": core.Fetcher.inputs[0]},
            ],
        ),
    ]


def wandering_led(core):
    return handlers_base(core, wandering_led_handler(core), wandering_led_prep(core))
