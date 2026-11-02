#!/usr/bin/env python3
"""Compare two private snapshots produced by adb_snapshot_public.py; do not contact a phone."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    args = parser.parse_args()
    for label, path in [('before', args.before), ('after', args.after)]:
        records = {r['file']: r for r in json.loads((path / 'commands.json').read_text())}
        for name in ('package.txt', 'enabled.txt', 'disabled.txt', 'process.txt', 'services.txt', 'alarms.txt'):
            if name not in records or not (path / name).is_file():
                parser.error(f'{label}: missing {name}; snapshot incomplete')
        print(f'{label}:')
        for name in ('enabled.txt', 'disabled.txt', 'process.txt'):
            value = (path / name).read_text(errors='replace').strip()
            code = records[name]['exit']
            if code and name != 'process.txt':
                print(f'  {name}: command failed (exit {code}); state unknown')
            elif code and value:
                print(f'  {name}: command failed or returned diagnostic text; state unknown')
            else:
                print(f'  {name}:', value or '(empty; inspect exit status and platform behavior)', f'exit={code}')
        print('  Review package.txt, services.txt and alarms.txt locally; historical alarms are not new firings.')
    print('These snapshots do not prove activation is impossible or that network reporting stopped.')


if __name__ == '__main__':
    main()
