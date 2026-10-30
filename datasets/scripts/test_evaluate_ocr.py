import copy
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from evaluate_ocr import csv_safe, evaluate, write_reports
from ocr_dataset import device_key, load_labels, snapshot
from test_ocr_dataset import run, save_run, workbook


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.labels = workbook(self.root/'dataset', ('Decolgen Forte', 'Efferalgan'))
        self.raw = self.root/'pilot/raw'

    def tearDown(self):
        self.temp.cleanup()

    def test_no_runs_lists_every_image_and_no_fake_accuracy(self):
        report = evaluate(self.labels, self.raw)
        self.assertEqual(report['row_counts'], {'not_run': 2})
        self.assertIsNone(report['scores']['no_device']['accuracy'])
        self.assertEqual(report['decision'], 'not_decided')
        self.assertEqual(report['scores']['no_device']['coverage'], 0)

    def test_earliest_failed_run_is_not_replaced_by_good_retry(self):
        save_run(self.raw, run('early', status='engine_error', text=''))
        save_run(self.raw, run('later', date='2026-10-28T12:01:00+07:00'))
        report = evaluate(self.labels, self.raw)
        score = report['scores'][device_key(run())]
        self.assertEqual((score['correct'], score['evaluated'], score['coverage']), (0, 1, .5))
        chosen = [row for row in report['rows'] if row.get('selected')]
        self.assertEqual(chosen[0]['run_id'], 'early')
        self.assertEqual(report['raw_files'], 2)

    def test_name_layout_diagnostic_not_counted_exact(self):
        save_run(self.raw, run(text='DECOLGEN PHARMA FORTE'))
        report = evaluate(self.labels, self.raw)
        self.assertEqual(report['row_counts']['tokens_present_noncontiguous'], 1)
        self.assertEqual(report['scores'][device_key(run())]['correct'], 0)

    def test_no_text_counts_failed_not_excluded(self):
        save_run(self.raw, run(status='no_text', text=''))
        score = evaluate(self.labels, self.raw)['scores'][device_key(run())]
        self.assertEqual((score['evaluated'], score['accuracy']), (1, 0))

    def test_invalid_time_and_unmapped_remain_visible(self):
        save_run(self.raw, run('invalid', date='2026-10-28'))
        save_run(self.raw, run('unknown', iid='1'))
        report = evaluate(self.labels, self.raw)
        self.assertEqual(report['row_counts']['invalid_run'], 1)
        self.assertEqual(report['row_counts']['unmapped'], 1)
        self.assertEqual(report['row_counts']['not_run'], 2)
        self.assertEqual(len(report['data_errors']), 2)

    def test_two_device_types_and_os_are_scored_separately(self):
        a, b = run('a'), run('b')
        b['metadata']['deviceKind'] = 'physical'
        save_run(self.raw, a)
        save_run(self.raw, b)
        report = evaluate(self.labels, self.raw)
        self.assertEqual(len(report['scores']), 2)
        self.assertTrue(all(s['evaluated'] == 1 for s in report['scores'].values()))

    def test_mapping_and_image_hash_mismatch(self):
        save_run(self.raw, run(iid='1'))
        mapping = self.raw.parent/'run-map.csv'
        mapping.write_text('run_id,image_id,verified_by,reason\nrun1,img1,Bao,hash\n')
        self.assertEqual(evaluate(self.labels, self.raw, mapping)['scores'][device_key(run())]['correct'], 1)
        (self.raw.parent/'import-index.json').write_text(json.dumps({'runs': {'run1': {'image_sha256': 'wrong'}}}))
        report = evaluate(self.labels, self.raw, mapping)
        self.assertEqual(report['row_counts']['invalid_run'], 1)
        self.assertEqual(report['row_counts']['not_run'], 2)

    def test_reports_and_cli_preserve_sources(self):
        raw = save_run(self.raw, run())
        before = (raw.read_bytes(), self.labels.read_bytes())
        output = self.root/'out'
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('evaluate_ocr.py')),
                                 '--labels', str(self.labels), '--runs', str(self.raw), '--output', str(output)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((raw.read_bytes(), self.labels.read_bytes()), before)
        self.assertEqual(json.loads((output/'summary.json').read_text())['decision'], 'not_decided')
        self.assertIn('1/2', (output/'report.md').read_text(encoding='utf-8'))
        with (output/'per_image.csv').open(encoding='utf-8-sig', newline='') as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 2)

    def test_csv_formula_injection(self):
        for value in ('=SUM(1,2)', '+1', '-1', '@name', '  =BAD'):
            self.assertTrue(csv_safe(value).startswith("'"))
        self.assertEqual(csv_safe('normal'), 'normal')

    def test_raw_hash_differs_from_import_provenance(self):
        save_run(self.raw, run())
        (self.raw.parent/'import-index.json').write_text(json.dumps({'runs': {'run1': {'sha256': 'wrong'}}}))
        report = evaluate(self.labels, self.raw)
        self.assertEqual(report['row_counts']['invalid_run'], 1)
        self.assertTrue(report['data_errors'])

    def benchmark_fixture(self, text='Decolgen Forte'):
        self.labels = workbook(self.root/'benchmark')
        cold = run('cold', text=text)
        warm = run('warm', text=text, date='2026-10-28T12:00:01+07:00')
        save_run(self.raw, cold)
        save_run(self.raw, warm)
        snap = snapshot(self.labels, load_labels(self.labels)[0])
        manifest = {**snap, 'images': [{**snap['images'][0], 'labels_verified': True,
                                       'verified_by': 'tester', 'verified_at': '2026-10-27', 'condition': 'frontal'}],
                    'runs': {'cold': {'phase': 'cold'}, 'warm': {'phase': 'warm'}}}
        config = {key: cold['metadata'][key] for key in ('engine', 'packageVersion', 'nativeSdkVersion',
                                                        'script', 'preprocessing', 'appRevision')}
        protocol = {'status': 'frozen', 'version': 'test-only', 'frozenAt': '2026-10-28T11:00:00+07:00',
                    'dataset_hash': snap['dataset_hash'], 'required_devices': [device_key(cold)],
                    'required_conditions': ['frontal'], 'required_config': config,
                    'min_images_per_condition': 1, 'repetitions': 1,
                    'threshold_name': 1, 'latency_p95_ms': 100}
        return protocol, manifest

    def test_benchmark_missing_or_draft_is_pending(self):
        self.assertEqual(evaluate(self.labels, self.raw, mode='benchmark')['decision'], 'pending')
        protocol, manifest = self.benchmark_fixture()
        protocol['status'] = 'draft'
        self.assertEqual(evaluate(self.labels, self.raw, mode='benchmark', protocol=protocol, manifest=manifest)['decision'], 'pending')

    def test_benchmark_fixture_go_and_no_go(self):
        for text, decision in [('Decolgen Forte', 'go'), ('wrong', 'no-go')]:
            protocol, manifest = self.benchmark_fixture(text)
            report = evaluate(self.labels, self.raw, mode='benchmark', protocol=protocol, manifest=manifest)
            self.assertEqual(report['decision'], decision, report.get('benchmark'))

    def test_benchmark_actual_image_change_is_pending(self):
        protocol, manifest = self.benchmark_fixture()
        (self.labels.parent/'images/box/img1.jpg').write_bytes(b'changed')
        report = evaluate(self.labels, self.raw, mode='benchmark', protocol=protocol, manifest=manifest)
        self.assertEqual(report['decision'], 'pending')
        self.assertIn('Actual dataset hash', ' '.join(report['benchmark']['reasons']))

    def test_malformed_manifest_does_not_produce_go(self):
        protocol, manifest = self.benchmark_fixture()
        manifest['images'] = [{'image_id': 'img1'}]
        report = evaluate(self.labels, self.raw, mode='benchmark', protocol=protocol, manifest=manifest)
        self.assertEqual(report['decision'], 'pending')

    def test_benchmark_pre_freeze_config_coverage_verification_phase(self):
        protocol, manifest = self.benchmark_fixture()
        for kind in ('timestamp', 'config', 'count', 'verification', 'phase', 'device'):
            p, m = copy.deepcopy(protocol), copy.deepcopy(manifest)
            if kind == 'timestamp':
                p['frozenAt'] = '2026-10-29T00:00:00+07:00'
            elif kind == 'config':
                p['required_config']['appRevision'] = 'other'
            elif kind == 'count':
                p['repetitions'] = 2
            elif kind == 'verification':
                m['images'][0]['labels_verified'] = False
            elif kind == 'phase':
                m['runs'] = {}
            else:
                p['required_devices'] = ['other/device']
            with self.subTest(kind=kind):
                report = evaluate(self.labels, self.raw, mode='benchmark', protocol=p, manifest=m)
                self.assertEqual(report['decision'], 'pending')


if __name__ == '__main__':
    unittest.main()
