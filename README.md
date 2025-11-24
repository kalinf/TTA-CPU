# TTA-CPU
Transport Triggered Architecture cores generator

`python3 generate_fu.py <directory> [<config_file>]` generates template files for functional units implementation. 
Based on config_file (default config.json) file it produces directory `fu` with files `FUname.py` (where FUName corresponds to `name` field of fu in configuration file). 
It also produces a `config_detail.json` which contains detailed core configuration with fu's addresses and instruction elements length computed.

Functional units operations should be performed on the falling clock edge.

To access instruction memory, the unit called `Fetcher` has to be defined. It can operate on memory using two ports `instr_read_ports[0:instruction_memory_read_ports-1]` already defined in the generated file (`instruction_memory_read_ports` is defined in config file).