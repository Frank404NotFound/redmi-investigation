#!/usr/bin/env python3
"""Search a local dexdump disassembly by method name or instruction text."""
import argparse
from pathlib import Path
import re


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('disassembly', type=Path)
    p.add_argument('--mode', required=True, choices=['method', 'refs'])
    p.add_argument('--query', required=True, help='literal substring; keep output private')
    a = p.parse_args()
    if not a.query:
        p.error('query must not be empty')
    method = None
    matched = False
    with a.disassembly.open(errors='replace') as source:
        for number, line in enumerate(source, 1):
            header = re.match(r'^[0-9a-f]+:\s+\|\[[0-9a-f]+\] (.+)', line)
            if header:
                method = header.group(1).strip()
                matched = a.mode == 'method' and a.query in method
                if matched:
                    print(f'\n{number}: {method}')
            elif method and ((matched and a.mode == 'method') or (a.mode == 'refs' and a.query in line)):
                if a.mode == 'refs':
                    print(f'{number}: {method}')
                print(f'{number}: {line.rstrip()}')


if __name__ == '__main__':
    main()
