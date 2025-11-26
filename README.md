# TTA-CPU
Transport Triggered Architecture cores generator

`python3 generate_fu.py <directory> [<config_file>]` generates template files for functional units implementation. 
Based on config_file (default config.json) file it produces directory `fu` with files `FUname.py` (where FUName corresponds to `name` field of fu in configuration file). 
It also produces a `config_detail.json` which contains detailed core configuration with fu's addresses and instruction elements length computed.

There are 2 clocks available in the design, actions take place on edges of those two clocks. Slower clock controls instructions and data flow 
(domains `rising` and `falling`) while the second, 2 times faster, is used to access memory (domain `mem`).
Data appears on the data bus on the `rising` edge and is catched by destination unit's registers on the `falling` edge.
In the classical approach functional units operations should be performed and instructions should appear on the instruction bus on the `falling` clock edge.

To access instruction memory, the unit called `Fetcher` has to be defined. It can operate on memory using ports `instr_read_ports[0:instruction_memory_read_ports-1]` already defined in the generated file (`instruction_memory_read_ports` is defined in config file by user).