"""Meaningful scoring/data edge cases. Fixtures never enter real results/."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from ocr_dataset import (device_key, load_labels, load_mapping, load_runs, name_score,
                         safe_path, snapshot, strength_score, timing, validate_run, valid_timing)


def workbook(root, names=('Decolgen Forte',), shared=False, formula=False, duplicate=False):
    root.mkdir(parents=True, exist_ok=True)
    (root / 'images/box').mkdir(parents=True, exist_ok=True)
    rows = [['image_id', 'relative_path', 'drug_name', 'strength']]
    for i, name in enumerate(names):
        iid = 'img1' if duplicate else f'img{i + 1}'
        (root / f'images/box/{iid}.jpg').write_bytes(f'image-{i}'.encode())
        rows.append([iid, f'images/box/{iid}.jpg', name, '500mg'])
    strings, xmlrows = [], []
    for r, row in enumerate(rows, 2):
        cells = []
        for col, value in zip('BCDE', row):
            if shared:
                strings.append(value)
                content = f'<v>{len(strings)-1}</v>'
                kind = 's'
            else:
                content = f'<is><t>{escape(value)}</t></is>'
                kind = 'inlineStr'
            if formula and r == 3 and col == 'D':
                content = '<f>"fake"</f><v>fake</v>'
            cells.append(f'<c r="{col}{r}" t="{kind}">{content}</c>')
        xmlrows.append(f'<row r="{r}">{"".join(cells)}</row>')
    ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    path = root / 'labels.xlsx'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('xl/workbook.xml', f'<workbook xmlns="{ns}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Data" sheetId="1" r:id="r1"/></sheets></workbook>')
        archive.writestr('xl/_rels/workbook.xml.rels', '<Relationships><Relationship Id="r1" Target="worksheets/sheet1.xml"/></Relationships>')
        archive.writestr('xl/worksheets/sheet1.xml', f'<worksheet xmlns="{ns}"><sheetData>{"".join(xmlrows)}</sheetData></worksheet>')
        if shared:
            archive.writestr('xl/sharedStrings.xml', f'<sst xmlns="{ns}">'+''.join(f'<si><t>{escape(v)}</t></si>' for v in strings)+'</sst>')
    return path


def run(rid='run1', iid='img1', text='Decolgen\nFORTE', status='text', date='2026-10-28T12:00:00+07:00', **extra):
    return {'schemaVersion': 1, 'runId': rid, 'imageId': iid, 'rawText': text,
            'status': status, 'createdAt': date, 'elapsedMs': 20,
            'metadata': {'platform': 'android', 'deviceModel': 'test', 'osVersion': '17',
                         'deviceKind': 'emulator', 'engine': 'google_mlkit_text_recognition',
                         'packageVersion': '0.17.1', 'nativeSdkVersion': '16.0.1',
                         'script': 'latin', 'preprocessing': 'none', 'appRevision': 'test-rev'},
            'imagePath': f'{rid}/image.jpg', **extra}


def save_run(directory, value, filename=None):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (filename or value['runId'] + '.json')
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    return path


class ScoringTests(unittest.TestCase):
    def test_exact_newline_case_nfc(self):
        self.assertEqual(name_score('xxx DECOLGEN\nFORTE 500 mg', 'Decolgen Forte'), 'exact_name')
        self.assertEqual(name_score('Thuốc A\u0301', 'Thuốc Á'), 'exact_name')

    def test_boundaries_and_typo_are_not_fixed(self):
        self.assertEqual(name_score('xDecolgen Forte', 'Decolgen Forte'), 'partial_name')
        self.assertEqual(name_score('DEC0LGEN FORTE', 'Decolgen Forte'), 'partial_name')
        self.assertEqual(name_score('thuoc', 'thuốc'), 'name_not_found')

    def test_layout_and_order_are_diagnostic_only(self):
        for raw in ('Decolgen PHARMA FORTE', 'FORTE Decolgen'):
            self.assertEqual(name_score(raw, 'Decolgen Forte'), 'tokens_present_noncontiguous')
        self.assertEqual(name_score('Decolgen', 'Decolgen Forte'), 'partial_name')

    def test_repeated_tokens_need_repeated_occurrences(self):
        self.assertEqual(name_score('A', 'A A'), 'partial_name')

    def test_strength_single_occurrence_boundaries(self):
        self.assertEqual(strength_score('500 mg', '500mg'), 'correct')
        self.assertEqual(strength_score('1500 mg', '500mg'), 'incorrect')
        self.assertEqual(strength_score('0.500 mg', '500 mg'), 'incorrect')
        self.assertEqual(strength_score('500 mg/ml', '500mg'), 'correct')

    def test_strength_no_guessing_multiple_components(self):
        self.assertEqual(strength_score('500 mg', ''), 'unscored')
        self.assertEqual(strength_score('500 mg', 'Paracetamol 500 mg + X 2 mg'), 'requires_component_protocol')
        self.assertEqual(strength_score('500 mg', '500mg', False), 'incorrect')

    def test_timing_and_nearest_rank(self):
        self.assertEqual(timing([0, 10, 100]), {'n': 3, 'median_ms': 10, 'p95_ms': 100})
        self.assertIsNone(timing([])['median_ms'])
        for value in (True, -1, float('nan'), float('inf'), None):
            self.assertFalse(valid_timing(run(elapsedMs=value)))
        self.assertTrue(valid_timing(run(elapsedMs=0)))
        self.assertFalse(valid_timing(run(status='engine_error')))


class DataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_xlsx_shifted_header_inline_and_shared_unchanged(self):
        for shared in (False, True):
            path = workbook(self.root, shared=shared)
            before = path.read_bytes()
            labels, errors = load_labels(path)
            self.assertEqual(errors, [])
            self.assertEqual(labels[0]['drug_name'], 'Decolgen Forte')
            self.assertEqual(labels[0]['row'], 3)
            self.assertEqual(path.read_bytes(), before)

    def test_duplicate_ids_invalidate_all_rows(self):
        labels, errors = load_labels(workbook(self.root, ('A', 'B'), duplicate=True))
        self.assertEqual(len(labels), 2)
        self.assertTrue(all(not row['valid'] for row in labels))
        self.assertEqual(len(errors), 2)

    def test_missing_name_image_and_formula_not_silent(self):
        path = workbook(self.root, ('',))
        (self.root/'images/box/img1.jpg').unlink()
        labels, errors = load_labels(path)
        self.assertFalse(labels[0]['valid'])
        self.assertGreaterEqual(len(errors), 2)
        labels, errors = load_labels(workbook(self.root, formula=True))
        self.assertFalse(labels[0]['valid'])
        self.assertTrue(any('Formula' in error for error in errors))

    def test_ambiguous_header_rejected(self):
        path = workbook(self.root, ('image_id',))
        with zipfile.ZipFile(path) as archive:
            files = {name: archive.read(name) for name in archive.namelist()}
        sheet = files['xl/worksheets/sheet1.xml'].decode()
        header = sheet[sheet.index('<row'):sheet.index('</row>')+6]
        files['xl/worksheets/sheet1.xml'] = sheet.replace('</sheetData>', header+'</sheetData>').encode()
        with zipfile.ZipFile(path, 'w') as archive:
            for key, value in files.items():
                archive.writestr(key, value)
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            load_labels(path)

    def test_path_escape_and_symlink_rejected(self):
        for value in ('../labels.xlsx', '/etc/a', 'C:/secret', '..\\outside'):
            with self.assertRaises(ValueError):
                safe_path(self.root, value)
        link = self.root/'link'
        try:
            link.symlink_to(self.root.parent, target_is_directory=True)
        except OSError:
            return  # Windows may not grant symlink privilege; other path checks still run.
        with self.assertRaises(ValueError):
            safe_path(self.root, 'link/outside')

    def test_run_schema_and_timezone(self):
        for change in ({'schemaVersion': True}, {'runId': '../bad'}, {'createdAt': '2026-01-01'},
                       {'metadata': {}}, {'rawText': None}, {'status': 'whatever'}):
            with self.assertRaises((ValueError, TypeError)):
                validate_run(run(**change))

    def test_duplicate_conflicting_and_malformed_run_reported(self):
        directory = self.root/'raw'
        save_run(directory, run(), 'a.json')
        save_run(directory, run(text='changed'), 'b.json')
        (directory/'bad.json').write_text('{')
        entries, errors = load_runs(directory)
        self.assertEqual(len(entries), 3)
        self.assertEqual(len(errors), 3)

    def test_mapping_needs_verification_and_known_label(self):
        labels, _ = load_labels(workbook(self.root))
        path = self.root/'run-map.csv'
        path.write_text('run_id,image_id,verified_by,reason\nr,img1,,guess\ns,missing,Bao,check\nt,img1,Bao,hash\n')
        mapping, errors = load_mapping(path, labels)
        self.assertEqual(mapping, {'t': 'img1'})
        self.assertEqual(len(errors), 2)

    def test_snapshot_tracks_actual_image_bytes(self):
        path = workbook(self.root)
        first = snapshot(path, load_labels(path)[0])
        (self.root/'images/box/img1.jpg').write_bytes(b'changed')
        second = snapshot(path, load_labels(path)[0])
        self.assertNotEqual(first['dataset_hash'], second['dataset_hash'])

    def test_devices_separate_unknown_kind_and_os(self):
        first = run()
        second = run()
        second['metadata'].pop('deviceKind')
        self.assertNotEqual(device_key(first), device_key(second))
        second['metadata']['deviceKind'] = 'emulator'
        second['metadata']['osVersion'] = '16'
        self.assertNotEqual(device_key(first), device_key(second))


if __name__ == '__main__':
    unittest.main()
