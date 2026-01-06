import serial
import argparse
import json
from pathlib import Path

PORT = "/dev/ttyACM0"

# Format of frame:
# 1. Start symbol - AAAA (2 bytes/1 word)
# 2. Data length in words (2 bytes/1 word)
# 3. Address (2 bytes/1 word)
# 4. Last frame - 0/1 (1 byte)
# 5. Program transfer - 5050 / Data transfer - 0505 (2 bytes/1 word)
# 6. Data (n words/2n bytes)
# 7. Stop sequence - 5555 (2 bytes/1 word)

START_SYMBOL = (0xAAAA).to_bytes(2, "little")
PROGRAM_TRANSFER = (0x5050).to_bytes(2, "little")
DATA_TRANSFER = (0x0505).to_bytes(2, "little")
STOP_SYMBOL = (0x5555).to_bytes(2, "little")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--mode",
        default="program",
        choices=["program", "data"],
        help="Selects if transfer will be program or data. Default: %(default)s",
    )
    parser.add_argument(
        "-s",
        "--source-file",
        default="",
        help="Provide path to program file. Default: empty",
    )
    parser.add_argument(
        "-l",
        "--last-transfer",
        action="store_true",
        help="Is this transfer the last. Default: %(default)s",
    )
    parser.add_argument(
        "-o",
        "--offset",
        default=0,
        help="Offset at which data will be saved. Default: %(default)s",
    )
    parser.add_argument(
        "-b",
        "--baud-rate",
        default=115200,
        help="Baud rate of UART communication. Default: %(default)s",
    )

    args = parser.parse_args()

    with serial.Serial(PORT, int(args.baud_rate)) as ser:
        with open(Path(args.source_file)) as f:
            data = json.load(f)

        binary_payload = bytearray()
        binary_payload.extend(START_SYMBOL)
        binary_payload.extend(len(data).to_bytes(2, "little"))
        binary_payload.extend(int(args.offset).to_bytes(2, "little"))
        binary_payload.append(1 if args.last_transfer else 0)
        binary_payload.extend(PROGRAM_TRANSFER if args.mode == "program" else DATA_TRANSFER)
        for d in data:
            binary_payload.extend(d["data"].to_bytes(2, "little"))
        binary_payload.extend(STOP_SYMBOL)

        print(f"Prepared {len(binary_payload)} bytes (frame of {len(data)} data words).")

        ser.write(binary_payload)

        print(f"{len(binary_payload)} bytes sent.")
