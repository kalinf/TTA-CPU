#!/bin/sh

MAX_LINE_LENGTH=120

python3 -m black \
    --line-length $MAX_LINE_LENGTH .