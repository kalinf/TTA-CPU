from amaranth import *


def fibonacci_no_loop(dut, n: int):
    init = []
    init += [{"constant": 1, "src_addr": 0, "dst_addr": dut.Adder.inputs[0]["addr"]}]
    if n == 0:
        return init
    init += [{"constant": 1, "src_addr": 1, "dst_addr": dut.Adder.inputs[1]["addr"]}]
    for i in range(2, n):
        init += [
            {"constant": 0, "src_addr": dut.Adder.outputs[0]["addr"], "dst_addr": dut.Adder.inputs[(i % 2)]["addr"]}
        ]
    init += [{"constant": 0, "src_addr": dut.Adder.outputs[0]["addr"], "dst_addr": dut.Result.inputs[0]["addr"]}]
    return init


def fibonacci_loop(dut, n: int):
    init = []
    # first instruction is infinite loop when jump condition is true
    init += [("end", [{"constant": 0, "src_addr": 0, "dst_addr": 0}])]
    init += [
        (
            "b0",
            [
                # setting iterator to 1 (to treat n==1 and n==2 the same way as an edge case)
                {"constant": 1, "src_addr": 2, "dst_addr": dut.Increaser.inouts[0]["addr"]},
                {"constant": 1, "src_addr": 1, "dst_addr": dut.Increaser.inouts[1]["addr"]},
                # reading n (saving as the comparison base value)
                {"constant": 1, "src_addr": n, "dst_addr": dut.Logical.inputs[0]["addr"]},
                {"constant": 1, "src_addr": 0, "dst_addr": dut.Logical.inputs[1]["addr"]},
                # masking < and > condition (not equal)
                {"constant": 1, "src_addr": ((1 << 1) | (1 << 2)), "dst_addr": dut.Logical.inputs[2]["addr"]},
                # escaping to general case
                {"constant": 1, "src_addr": "b1", "dst_addr": dut.Fetcher.inputs[1]["addr"]},
                {"constant": 0, "src_addr": dut.Logical.outputs[5]["addr"], "dst_addr": dut.Fetcher.inputs[0]["addr"]},
                # edge case for n == 0
                {"constant": 1, "src_addr": 0, "dst_addr": dut.Result.inputs[0]["addr"]},
                # jump to end and lock
                {"constant": 1, "src_addr": "end", "dst_addr": dut.Fetcher.inputs[1]["addr"]},
                {"constant": 1, "src_addr": 1, "dst_addr": dut.Fetcher.inputs[0]["addr"]},
            ],
        )
    ]
    init += [
        (
            "b1",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": dut.Fetcher.inputs[0]["addr"]},
                # initializing Adder with first two fibonacci numbers
                {"constant": 1, "src_addr": 0, "dst_addr": dut.Adder.inputs[0]["addr"]},
                {"constant": 1, "src_addr": 1, "dst_addr": dut.Adder.inputs[1]["addr"]},
                # masking == and > condition (grater then or equal)
                {"constant": 1, "src_addr": ((1 << 0) | (1 << 2)), "dst_addr": dut.Logical.inputs[2]["addr"]},
                # check if n <= 2 (iterator)
                {"constant": 0, "src_addr": dut.Increaser.inouts[0]["addr"], "dst_addr": dut.Logical.inputs[1]["addr"]},
                {"constant": 1, "src_addr": "result", "dst_addr": dut.Fetcher.inputs[1]["addr"]},
                {"constant": 0, "src_addr": dut.Logical.outputs[5]["addr"], "dst_addr": dut.Fetcher.inputs[0]["addr"]},
            ],
        )
    ]
    init += [
        (
            "loop",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": dut.Fetcher.inputs[0]["addr"]},
                {"constant": 0, "src_addr": dut.Adder.outputs[0]["addr"], "dst_addr": dut.Adder.inputs[0]["addr"]},
                # jump to end if iterator >= n
                {"constant": 1, "src_addr": ((1 << 0) | (1 << 2)), "dst_addr": dut.Logical.inputs[2]["addr"]},
                {"constant": 0, "src_addr": dut.Increaser.inouts[0]["addr"], "dst_addr": dut.Logical.inputs[1]["addr"]},
                {"constant": 1, "src_addr": "result", "dst_addr": dut.Fetcher.inputs[1]["addr"]},
                {"constant": 0, "src_addr": dut.Logical.outputs[5]["addr"], "dst_addr": dut.Fetcher.inputs[0]["addr"]},
                #
                {"constant": 0, "src_addr": dut.Adder.outputs[0]["addr"], "dst_addr": dut.Adder.inputs[1]["addr"]},
                # jump to beginning of the loop when iterator < n
                {"constant": 1, "src_addr": (1 << 1), "dst_addr": dut.Logical.inputs[2]["addr"]},
                {"constant": 0, "src_addr": dut.Increaser.inouts[0]["addr"], "dst_addr": dut.Logical.inputs[1]["addr"]},
                {"constant": 1, "src_addr": "loop", "dst_addr": dut.Fetcher.inputs[1]["addr"]},
                {"constant": 0, "src_addr": dut.Logical.outputs[5]["addr"], "dst_addr": dut.Fetcher.inputs[0]["addr"]},
            ],
        )
    ]
    init += [
        (
            "result",
            [
                # turn jumping off
                {"constant": 1, "src_addr": 0, "dst_addr": dut.Fetcher.inputs[0]["addr"]},
                # put result in correct register
                {"constant": 0, "src_addr": dut.Adder.outputs[0]["addr"], "dst_addr": dut.Result.inputs[0]["addr"]},
                # jump to end and lock
                {"constant": 1, "src_addr": "end", "dst_addr": dut.Fetcher.inputs[1]["addr"]},
                {"constant": 1, "src_addr": 1, "dst_addr": dut.Fetcher.inputs[0]["addr"]},
            ],
        )
    ]
    return init
