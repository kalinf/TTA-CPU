from amaranth import *


def fibonacci_no_loop(core, n: int):
    init = []
    init += [{"constant": 1, "src_addr": 0, "dst_addr": core.Adder.inputs[0]}]
    if n == 0:
        return init
    init += [{"constant": 1, "src_addr": 1, "dst_addr": core.Adder.inputs[1]}]
    for i in range(2, n):
        init += [
            {
                "constant": 0,
                "src_addr": core.Adder.outputs[0],
                "dst_addr": core.Adder.inputs[(i % 2)],
            }
        ]
    init += [
        {
            "constant": 0,
            "src_addr": core.Adder.outputs[0],
            "dst_addr": core.Result.inouts[0],
        }
    ]
    return init


def loop_direct(core):
    return [
        (
            "loop",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                {
                    "constant": 0,
                    "src_addr": core.Adder.outputs[0],
                    "dst_addr": core.Adder.inputs[0],
                },
                # jump to end if iterator >= n
                {
                    "constant": 1,
                    "src_addr": ((1 << 0) | (1 << 2)),
                    "dst_addr": core.Logical.inputs[2],
                },
                {
                    "constant": 0,
                    "src_addr": core.Increaser.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 1,
                    "src_addr": "result",
                    "dst_addr": core.Fetcher.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                #
                {
                    "constant": 0,
                    "src_addr": core.Adder.outputs[0],
                    "dst_addr": core.Adder.inputs[1],
                },
                # jump to beginning of the loop when iterator < n
                {
                    "constant": 1,
                    "src_addr": (1 << 1),
                    "dst_addr": core.Logical.inputs[2],
                },
                {
                    "constant": 0,
                    "src_addr": core.Increaser.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                {"constant": 1, "src_addr": "loop", "dst_addr": core.Fetcher.inputs[1]},
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
            ],
        )
    ]


def indirect_extra_preparation(core):
    return [
        (
            "prepare_indirect",
            [
                # setting looper
                {
                    "constant": 1,
                    "src_addr": core.Adder.inputs[0],
                    "dst_addr": core.Looper.inputs[0],
                },
                {
                    "constant": 1,
                    "src_addr": core.Adder.inputs[1],
                    "dst_addr": core.Looper.inputs[1],
                },
                {"constant": 1, "src_addr": 1, "dst_addr": core.Looper.inputs[2]},
                # masking comparator (jump to beginning of the loop when iterator < n)
                {
                    "constant": 1,
                    "src_addr": (1 << 1),
                    "dst_addr": core.Logical.inputs[2],
                },
                # setting jump address
                {"constant": 1, "src_addr": "loop", "dst_addr": core.Fetcher.inputs[1]},
            ],
        )
    ]


def loop_indirect(core):
    return [
        (
            "loop",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                # set indirect addresses for Adder inputs
                {
                    "constant": 0,
                    "src_addr": core.Looper.outputs[0],
                    "dst_addr": core.Fetcher.inputs[3],
                },
                {
                    "constant": 0,
                    "src_addr": core.Adder.outputs[0],
                    "dst_addr": core.Fetcher.inouts[2],
                },
                {
                    "constant": 0,
                    "src_addr": core.Increaser.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
            ],
        )
    ]


def fibonacci_loop(core, n: int, loop, extra_preparation=[]):
    init = []
    # first instruction is infinite loop when jump condition is true
    init += [("end", [{"constant": 0, "src_addr": 0, "dst_addr": 0}])]
    init += [
        (
            "b0",
            [
                # setting iterator to 1 (to treat n==1 and n==2 the same way as an edge case)
                {"constant": 1, "src_addr": 2, "dst_addr": core.Increaser.inouts[0]},
                {"constant": 1, "src_addr": 1, "dst_addr": core.Increaser.inouts[1]},
                # reading n (saving as the comparison base value)
                {"constant": 1, "src_addr": n, "dst_addr": core.Logical.inputs[0]},
                {"constant": 1, "src_addr": 0, "dst_addr": core.Logical.inputs[1]},
                # masking < and > condition (not equal)
                {
                    "constant": 1,
                    "src_addr": ((1 << 1) | (1 << 2)),
                    "dst_addr": core.Logical.inputs[2],
                },
                # escaping to general case
                {"constant": 1, "src_addr": "b1", "dst_addr": core.Fetcher.inputs[1]},
                {
                    "constant": 0,
                    "src_addr": core.Logical.outputs[5],
                    "dst_addr": core.Fetcher.inputs[0],
                },
                # edge case for n == 0
                {"constant": 1, "src_addr": 0, "dst_addr": core.Result.inouts[0]},
                # jump to end and lock
                {"constant": 1, "src_addr": "end", "dst_addr": core.Fetcher.inputs[1]},
                {"constant": 1, "src_addr": 1, "dst_addr": core.Fetcher.inputs[0]},
            ],
        )
    ]
    init += [
        (
            "b1",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                # initializing Adder with first two fibonacci numbers
                {"constant": 1, "src_addr": 0, "dst_addr": core.Adder.inputs[0]},
                {"constant": 1, "src_addr": 1, "dst_addr": core.Adder.inputs[1]},
                # masking == and > condition (grater then or equal)
                {
                    "constant": 1,
                    "src_addr": ((1 << 0) | (1 << 2)),
                    "dst_addr": core.Logical.inputs[2],
                },
                # check if n <= 2 (iterator)
                {
                    "constant": 0,
                    "src_addr": core.Increaser.inouts[0],
                    "dst_addr": core.Logical.inputs[1],
                },
                {
                    "constant": 1,
                    "src_addr": "result",
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
    init += extra_preparation
    init += loop
    init += [
        (
            "result",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": core.Fetcher.inputs[0]},
                # put result in correct register
                {
                    "constant": 0,
                    "src_addr": core.Adder.outputs[0],
                    "dst_addr": core.Result.inouts[0],
                },
                # jump to end and lock
                {"constant": 1, "src_addr": "end", "dst_addr": core.Fetcher.inputs[1]},
                {"constant": 1, "src_addr": 1, "dst_addr": core.Fetcher.inputs[0]},
            ],
        )
    ]
    return init


def fibonacci_loop_direct(core, n: int):
    return fibonacci_loop(core, n, loop_direct(core))


def fibonacci_loop_indirect(core, n: int):
    return fibonacci_loop(core, n, loop_indirect(core), indirect_extra_preparation(core))


def fibonacci_loop_indirect5(core):
    return fibonacci_loop(core, 5, loop_indirect(core), indirect_extra_preparation(core))
