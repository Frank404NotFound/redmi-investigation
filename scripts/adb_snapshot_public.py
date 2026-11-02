#!/usr/bin/env python3
"""Collect read-only ADB snapshots into a new, private directory."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True, help='ADB serial (never stored in journal)')
    parser.add_argument('--package', required=True, help='Android package name')
    parser.add_argument('--output', required=True, type=Path, help='new directory for sensitive output')
    parser.add_argument('--adb', default='adb', help='ADB executable')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+', args.package):
        parser.error('invalid Android package name')
    if not args.serial or any(c.isspace() for c in args.serial):
        parser.error('invalid ADB serial')
    os.umask(0o077)
    args.output.mkdir(mode=0o700, parents=True, exist_ok=False)
    pkg = args.package
    commands = {
        'state': ['get-state'],
        'model': ['shell', 'getprop', 'ro.product.model'],
        'device': ['shell', 'getprop', 'ro.product.device'],
        'release': ['shell', 'getprop', 'ro.build.version.release'],
        'firmware': ['shell', 'getprop', 'ro.build.version.incremental'],
        'package': ['shell', 'dumpsys', 'package', pkg],
        'path': ['shell', 'pm', 'path', pkg],
        'enabled': ['shell', 'pm', 'list', 'packages', '-e', '--user', '0', pkg],
        'disabled': ['shell', 'pm', 'list', 'packages', '-d', '--user', '0', pkg],
        'appops': ['shell', 'cmd', 'appops', 'get', pkg],
        'process': ['shell', 'pidof', pkg],
        'services': ['shell', 'dumpsys', 'activity', 'services', pkg],
        'alarms': ['shell', 'dumpsys', 'alarm'],
        'jobs': ['shell', 'dumpsys', 'jobscheduler'],
        'connectivity': ['shell', 'dumpsys', 'connectivity'],
        'mobile_data': ['shell', 'settings', 'get', 'global', 'mobile_data'],
        'crash_log': ['logcat', '-d', '-b', 'crash', '-v', 'threadtime', '-t', '500'],
    }
    records = []
    for name, command in commands.items():
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            result = subprocess.run([args.adb, '-s', args.serial, *command], stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=90, check=False)
            data, code = result.stdout, result.returncode
        except subprocess.TimeoutExpired as exc:
            data, code = exc.stdout or b'', 124
        except OSError as exc:
            data, code = str(exc).encode(), 127
        (args.output / (name + '.txt')).write_bytes(data)
        records.append({'utc': started, 'command': ['adb', '-s', '<SERIAL>', *command],
                        'file': name + '.txt', 'exit': code, 'sha256': hashlib.sha256(data).hexdigest()})
        print(f'{name}: exit={code}, bytes={len(data)}')
    (args.output / 'commands.json').write_text(json.dumps(records, indent=2) + '\n')
    print('Outputs can contain personal data; keep the directory private.')
    if records[0]['exit'] != 0 or (args.output / 'state.txt').read_text(errors='replace').strip() != 'device':
        raise SystemExit('ADB device was not available; snapshot is incomplete')
    if any(record['exit'] != 0 for record in records[1:]):
        print('Some commands failed or returned nonzero; inspect their outputs (a missing process can be normal).')


if __name__ == '__main__':
    main()
