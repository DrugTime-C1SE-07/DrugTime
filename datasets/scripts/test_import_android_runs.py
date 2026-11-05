import base64
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from import_android_runs import image_path, import_runs, write_original
from ocr_dataset import sha256
from test_ocr_dataset import run, save_run, workbook


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.labels = workbook(self.root/'dataset')
        self.source = self.root/'source'
        self.output = self.root/'results/pilot-001'

    def tearDown(self):
        self.temp.cleanup()

    def execute(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return import_runs(self.output, self.labels, **kwargs)

    def test_import_preserves_bytes_unicode_newlines_and_idempotence(self):
        path = save_run(self.source, run(text='Thuốc Á\n\nFORTE'))
        first = self.execute(source=self.source)
        self.assertFalse(first['errors'])
        self.assertEqual((self.output/'raw/run1.json').read_bytes(), path.read_bytes())
        self.assertEqual(first['runs']['run1']['sha256'], sha256(path.read_bytes()))
        self.assertFalse(self.execute(source=self.source)['errors'])

    def test_conflict_never_overwrites(self):
        path = save_run(self.source, run())
        self.execute(source=self.source)
        original = (self.output/'raw/run1.json').read_bytes()
        path.write_text(json.dumps(run(text='changed')))
        result = self.execute(source=self.source)
        self.assertTrue(result['errors'])
        self.assertEqual((self.output/'raw/run1.json').read_bytes(), original)

    def test_filename_must_match_run_id(self):
        save_run(self.source, run(), 'other.json')
        self.assertTrue(self.execute(source=self.source)['errors'])
        self.assertFalse((self.output/'raw/run1.json').exists())

    def test_safe_sandbox_image_paths(self):
        self.assertEqual(image_path('run1/image.jpg'), 'files/ocr_runs/run1/image.jpg')
        for value in ('../outside', 'r/../x', '/r/image.jpg', 'r/image.jpg;cat', 'r\\image.jpg'):
            with self.assertRaises(ValueError):
                image_path(value)

    def test_legacy_runs_are_not_reimported_into_pilot(self):
        path = save_run(self.source, run())
        write_original(self.output.parent/'legacy-pilot/raw/run1.json', path.read_bytes())
        result = self.execute(source=self.source)
        self.assertEqual(result['skipped_legacy'], ['run1'])
        self.assertFalse((self.output/'raw/run1.json').exists())

    def test_adb_hash_mapping_and_device_observation_do_not_rewrite_raw(self):
        payload = json.dumps(run(iid='1')).encode()
        digest = sha256((self.labels.parent/'images/box/img1.jpg').read_bytes())
        def fake(adb, serial, *args):
            if args[:2] == ('shell', 'getprop'):
                return {'ro.product.model': b'test', 'ro.build.version.release': b'17',
                        'ro.kernel.qemu': b'1'}[args[2]]
            if 'ls' in args:
                return b'run1\nrun1.json\n'
            if 'base64' in args:
                return base64.b64encode(payload)
            return (digest+'  image.jpg').encode()
        with patch('import_android_runs.adb_call', side_effect=fake):
            result = self.execute(adb='adb', serial='emulator-5554')
        self.assertFalse(result['errors'])
        self.assertEqual((self.output/'raw/run1.json').read_bytes(), payload)
        self.assertEqual(result['runs']['run1']['observed_device']['deviceKind'], 'emulator')
        self.assertIn('img1', (self.output/'run-map.csv').read_text())

    def test_hash_ambiguity_does_not_create_mapping(self):
        self.labels = workbook(self.root/'two', ('A', 'B'))
        image = self.labels.parent/'images/box/img1.jpg'
        (self.labels.parent/'images/box/img2.jpg').write_bytes(image.read_bytes())
        payload = json.dumps(run(iid='unknown')).encode()
        def fake(adb, serial, *args):
            if 'getprop' in args:
                return b'1'
            if 'ls' in args:
                return b'run1.json'
            if 'base64' in args:
                return base64.b64encode(payload)
            return sha256(image.read_bytes()).encode()
        with patch('import_android_runs.adb_call', side_effect=fake):
            result = self.execute(adb='adb', serial='emulator')
        self.assertEqual(result['runs']['run1']['image_check'], 'ambiguous')
        self.assertFalse((self.output/'run-map.csv').exists())

    def test_malformed_base64_json_is_reported(self):
        def fake(adb, serial, *args):
            return b'run1.json' if 'ls' in args else b'not-base64' if 'base64' in args else b'1'
        with patch('import_android_runs.adb_call', side_effect=fake):
            self.assertTrue(self.execute(adb='adb', serial='e')['errors'])

    def test_explicit_serial_required(self):
        with self.assertRaisesRegex(ValueError, 'serial'):
            self.execute(adb='adb')


if __name__ == '__main__':
    unittest.main()
