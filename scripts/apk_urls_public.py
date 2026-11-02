#!/usr/bin/env python3
"""Extract literal URL candidates from local APK DEX and native-library entries."""
import argparse
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit
import zipfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('apk', type=Path)
    args = p.parse_args()
    rows = {}
    with zipfile.ZipFile(args.apk) as archive:
        for entry in archive.infolist():
            if not entry.filename.endswith(('.dex', '.so')):
                continue
            # Read one entry at a time; the APK is untrusted input.
            data = archive.read(entry)
            for m in re.finditer(rb'https?://[a-zA-Z0-9.:-]+(?:/[a-zA-Z0-9_./%=-]*)?', data):
                candidate = m.group().decode('ascii')
                parsed = urlsplit(candidate)
                if not parsed.hostname:
                    continue
                url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, '', ''))
                rows.setdefault(url, set()).add(entry.filename)
    for url, entries in sorted(rows.items()):
        print(url, ','.join(sorted(entries)), sep='\t')
    print('Static literals are candidates, not evidence of traffic; paths may still contain sensitive values.', file=__import__('sys').stderr)


if __name__ == '__main__':
    main()
