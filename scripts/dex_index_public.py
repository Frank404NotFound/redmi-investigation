#!/usr/bin/env python3
"""Index method headers or locate literal references in a local dexdump file."""
import argparse
import json
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('disassembly', type=Path)
    parser.add_argument('--mode', choices=['index', 'refs'], required=True)
    parser.add_argument('--query', help='required literal substring for refs; optional method filter for index')
    args = parser.parse_args()
    if args.mode == 'refs' and not args.query:
        parser.error('--query is required for refs')
    method = None
    with args.disassembly.open(errors='replace') as source:
        for number, line in enumerate(source, 1):
            header = re.match(r'^[0-9a-f]+:\s+\|\[[0-9a-f]+\] (.+)', line)
            if header:
                method = header.group(1).strip()
                if args.mode == 'index' and (not args.query or args.query in method):
                    print(json.dumps({'method': method, 'line': number}))
            elif args.mode == 'refs' and method and args.query in line:
                print(json.dumps({'method': method, 'line': number, 'text': line.rstrip()}))


if __name__ == '__main__':
    main()
