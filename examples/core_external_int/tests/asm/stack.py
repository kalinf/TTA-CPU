def stack(core):
    init = [("turn_jump_off", [{"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]}])]
    # first instruction is infinite loop when jump condition is true
    init += [("end", [{"constant": 0, "src_addr": 0, "dst_addr": 0}])]
    init += [
        (
            "setup",
            [
                # set up iterator increaser
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
                # number of numbers to write
                {
                    "constant": 1,
                    "src_addr": 16,
                    "dst_addr": core.Logical.inputs[0],
                },
                # set mask
                {
                    "constant": 1,
                    "src_addr": 1 << 1,
                    "dst_addr": core.Logical.inputs[2],
                },
            ],
        ),
        (
            "push",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                {
                    "constant": 0,
                    "src_addr": core.Increaser.inouts[0],
                    "dst_addr": core.Regs.inouts[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.Regs.inouts[0],
                    "dst_addr": core.Stack.inouts[0],
                },
                {
                    "constant": 0,
                    "src_addr": core.Regs.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                # repete if iterator < 16
                {
                    "constant": 1,
                    "src_addr": "push",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
            ],
        ),
        (
            "check_full",
            [
                {
                    "constant": 0,
                    "src_addr": core.Stack.outputs[1],
                    "dst_addr": core.Result.inputs[0],
                },
                # decreaser
                {
                    "constant": 1,
                    "src_addr": -1,
                    "dst_addr": core.Increaser.inouts[1],
                },
                {
                    "constant": 1,
                    "src_addr": 0,
                    "dst_addr": core.Logical.inputs[0],
                },
                # set mask
                {
                    "constant": 1,
                    "src_addr": 1 << 2,
                    "dst_addr": core.Logical.inputs[2],
                },
            ],
        ),
        (
            "pop",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                {
                    "constant": 0,
                    "src_addr": core.Increaser.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Stack.inouts[0],
                    "dst_addr": core.Result.inputs[0],
                },
                # repete if iterator > 0
                {
                    "constant": 1,
                    "src_addr": "pop",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
            ],
        ),
        (
            "check_empty",
            [
                {
                    "constant": 0,
                    "src_addr": core.Stack.outputs[0],
                    "dst_addr": core.Result.inputs[0],
                },
            ],
        ),
    ]

    return init
