#!/usr/bin/env python3
"""Run installed Android build tools on a local APK; no device or network access."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apk', type=Path, required=True)
    parser.add_argument('--build-tools', type=Path, required=True, help='directory containing aapt, apksigner, dexdump')
    parser.add_argument('--output', type=Path, required=True, help='new private output directory')
    args = parser.parse_args()
    tools = {name: args.build_tools / name for name in ('aapt', 'apksigner', 'dexdump')}
    if not args.apk.is_file() or any(not p.is_file() for p in tools.values()):
        parser.error('APK or one or more required build tools do not exist')
    os.umask(0o077)
    args.output.mkdir(mode=0o700, parents=True, exist_ok=False)
    def run(name, argv):
        result = subprocess.run([str(x) for x in argv], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        (args.output / (name + '.txt')).write_bytes(result.stdout)
        return result.returncode
    exits = {
        'badging': run('badging', [tools['aapt'], 'dump', 'badging', args.apk]),
        'manifest': run('manifest', [tools['aapt'], 'dump', 'xmltree', args.apk, 'AndroidManifest.xml']),
        'signer': run('signer', [tools['apksigner'], 'verify', '--verbose', '--print-certs', args.apk]),
    }
    with zipfile.ZipFile(args.apk) as apk:
        for entry in apk.infolist():
            if not re.fullmatch(r'classes(?:[2-9]|[1-9][0-9]+)?\.dex', entry.filename):
                continue
            dest = args.output / entry.filename
            with apk.open(entry) as source, dest.open('xb') as output:
                while chunk := source.read(1024 * 1024):
                    output.write(chunk)
            exits[entry.filename] = run(entry.filename + '.disassembly', [tools['dexdump'], '-d', dest])
    digest = hashlib.sha256()
    with args.apk.open('rb') as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    (args.output / 'index.json').write_text(json.dumps({'sha256': digest.hexdigest(), 'exit_codes': exits}, indent=2) + '\n')
    print('Output may contain proprietary code or sensitive strings; keep it private. Exit codes:', exits)
    if any(exits.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
