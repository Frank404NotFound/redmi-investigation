#!/usr/bin/env python3
"""Sum retained untagged UID buckets from an existing dumpsys netstats detail file."""
import argparse
import json
from pathlib import Path
import re


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('dump', type=Path)
    p.add_argument('--uid', type=int, action='append', required=True, help='repeat for multiple UIDs')
    a = p.parse_args()
    text = a.dump.read_text(errors='replace')
    if '\nUID stats:' not in text or '\nUID tag stats:' not in text:
        p.error('expected UID stats and UID tag stats sections; format may differ on this Android build')
    section = text.split('\nUID stats:', 1)[1].split('\nUID tag stats:', 1)[0]
    stats, uid = {}, None
    for line in section.splitlines():
        match = re.search(r'\buid=(\d+)', line)
        if match:
            uid = int(match.group(1))
        if uid not in a.uid:
            continue
        match = re.search(r'\bst=(\d+) rb=(\d+) rp=\d+ tb=(\d+)', line)
        if match:
            timestamp, rx, tx = map(int, match.groups())
            record = stats.setdefault(uid, {'rx': 0, 'tx': 0, 'min': timestamp, 'max': timestamp, 'buckets': 0})
            record['rx'] += rx
            record['tx'] += tx
            record['min'] = min(timestamp, record['min'])
            record['max'] = max(timestamp, record['max'])
            record['buckets'] += 1
    print(json.dumps(stats, indent=2))
    print('Retained UID totals are incomplete and do not identify payloads or destinations.', file=__import__('sys').stderr)


if __name__ == '__main__':
    main()
