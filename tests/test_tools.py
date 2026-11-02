"""Synthetic offline checks; no phone, real APK, Android SDK, or network required."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_tool(self, path, *args, success=True):
        result = subprocess.run([sys.executable, str(path), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stderr)
        return result

    def fake_command(self, path, body):
        path.write_text('#!/bin/sh\n' + body + '\n')
        path.chmod(0o700)
        return path

    def test_adb_snapshots_and_comparison(self):
        adb = self.fake_command(self.root / 'adb',
                                'if [ "$3" = get-state ]; then echo device; '
                                'elif [ "$4" = pidof ]; then exit 1; else echo fixture; fi')
        tool = SCRIPTS / 'adb_snapshot_public.py'
        for label in ('before', 'after'):
            self.run_tool(tool, '--adb', adb, '--serial', 'test-serial', '--package',
                          'org.example.app', '--output', self.root / label)
        journal = json.loads((self.root / 'before/commands.json').read_text())
        self.assertEqual(journal[0]['command'][2], '<SERIAL>')
        self.assertNotIn('test-serial', json.dumps(journal))
        result = self.run_tool(ROOT / 'disable-test/compare_snapshots_public.py',
                               self.root / 'before', self.root / 'after')
        self.assertIn('before:', result.stdout)
        self.assertIn('after:', result.stdout)
        self.run_tool(tool, '--adb', adb, '--serial', 'test-serial', '--package',
                      'org.example.app', '--output', self.root / 'before', success=False)
        self.run_tool(tool, '--adb', adb, '--serial', 'test-serial', '--package',
                      'invalid;package', '--output', self.root / 'bad', success=False)

    def test_comparison_rejects_incomplete_snapshots(self):
        for label in ('before', 'after'):
            path = self.root / label
            path.mkdir()
            (path / 'commands.json').write_text('[]')
        self.run_tool(ROOT / 'disable-test/compare_snapshots_public.py',
                      self.root / 'before', self.root / 'after', success=False)

    def test_netstats_excludes_tagged_buckets(self):
        dump = self.root / 'netstats.txt'
        dump.write_text('header\nUID stats:\n uid=42\n st=1 rb=5 rp=1 tb=7\n'
                        ' st=2 rb=3 rp=1 tb=4\nUID tag stats:\n uid=42\n st=3 rb=99 rp=1 tb=99\n')
        result = self.run_tool(SCRIPTS / 'netstats_summary_public.py', dump, '--uid', '42')
        data = json.loads(result.stdout)
        self.assertEqual((data['42']['rx'], data['42']['tx'], data['42']['buckets']), (8, 11, 2))
        dump.write_text('unsupported format')
        self.run_tool(SCRIPTS / 'netstats_summary_public.py', dump, '--uid', '42', success=False)

    def test_dex_method_and_reference_search(self):
        dex = self.root / 'dump.txt'
        dex.write_text('0000: |[0001] sample.caller\n0001:  |0001: invoke-virtual targetMethod\n'
                       '0002: |[0002] sample.other\n0003:  |0003: return-void\n')
        tool = SCRIPTS / 'dex_evidence_public.py'
        result = self.run_tool(tool, dex, '--mode', 'refs', '--query', 'targetMethod')
        self.assertIn('sample.caller', result.stdout)
        self.assertNotIn('sample.other', result.stdout)
        result = self.run_tool(tool, dex, '--mode', 'method', '--query', 'sample.other')
        self.assertIn('return-void', result.stdout)
        self.assertNotIn('targetMethod', result.stdout)

    def test_method_index_and_references(self):
        dex = self.root / 'dump.txt'
        dex.write_text('0000: |[0001] sample.caller\n0001:  |0001: invoke-virtual targetMethod\n'
                       '0002: |[0002] sample.other\n0003:  |0003: return-void\n')
        tool = SCRIPTS / 'dex_index_public.py'
        result = self.run_tool(tool, dex, '--mode', 'index')
        records = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual([record['line'] for record in records], [1, 3])
        result = self.run_tool(tool, dex, '--mode', 'refs', '--query', 'targetMethod')
        self.assertEqual(json.loads(result.stdout)['method'], 'sample.caller')
        self.run_tool(tool, dex, '--mode', 'refs', success=False)

    def make_apk(self):
        apk = self.root / 'sample.apk'
        with zipfile.ZipFile(apk, 'w') as archive:
            archive.writestr('classes.dex', b'https://example.org/path?token=fixture')
            archive.writestr('classes10.dex', b'synthetic dex')
        return apk

    def test_apk_url_candidates_omit_query(self):
        result = self.run_tool(SCRIPTS / 'apk_urls_public.py', self.make_apk())
        self.assertIn('https://example.org/path', result.stdout)
        self.assertNotIn('token=fixture', result.stdout)

    def test_apk_static_invokes_tools_and_handles_multidex(self):
        apk = self.make_apk()
        sdk = self.root / 'build-tools'
        sdk.mkdir()
        for name in ('aapt', 'apksigner', 'dexdump'):
            self.fake_command(sdk / name, 'echo synthetic-output')
        out = self.root / 'static'
        tool = SCRIPTS / 'apk_static_public.py'
        self.run_tool(tool, '--apk', apk, '--build-tools', sdk, '--output', out)
        self.assertTrue((out / 'classes10.dex.disassembly.txt').is_file())
        self.assertEqual(json.loads((out / 'index.json').read_text())['exit_codes']['classes10.dex'], 0)
        self.run_tool(tool, '--apk', apk, '--build-tools', sdk, '--output', out, success=False)


if __name__ == '__main__':
    unittest.main()
