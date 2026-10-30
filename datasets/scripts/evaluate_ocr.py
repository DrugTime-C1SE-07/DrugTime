"""Measure raw OCR occurrence against XLSX labels; never modify raw or labels."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from ocr_dataset import (device_key, load_labels, load_mapping, load_runs, name_score,
                         read_json, snapshot, strength_score, timestamp, timing, valid_timing)

DATASET = Path(__file__).resolve().parents[1]
RULES = {'name': 'NFC_casefold_whitespace_exact_word_boundary',
         'selection': 'earliest_createdAt_then_runId_per_image_device',
         'strength': 'single_number_unit_occurrence_only', 'p95': 'nearest_rank'}


def metric(rows, total):
    scored = [row for row in rows if row.get('selected') and row['classification'] not in
              ('not_run', 'invalid_label', 'invalid_run', 'unmapped')]
    correct = sum(row['classification'] == 'exact_name' for row in scored)
    strengths = [row for row in scored if row['strength_result'] in ('correct', 'incorrect')]
    return {'correct': correct, 'evaluated': len(scored), 'labelled_images': total,
            'accuracy': correct / len(scored) if scored else None,
            'coverage': len(scored) / total if total else None,
            'not_run': total - len(scored),
            'classifications': dict(Counter(row['classification'] for row in scored)),
            'strength': {'correct': sum(row['strength_result'] == 'correct' for row in strengths),
                         'evaluated': len(strengths)},
            'timing': timing([row['elapsed_ms'] for row in scored if row.get('timing_valid')])}


def evaluate(labels_path, runs_dir, mapping_path=None, mode='pilot', protocol=None, manifest=None):
    labels, errors = load_labels(labels_path)
    valid = {row['image_id']: row for row in labels if row['valid']}
    mapping, mapping_errors = load_mapping(mapping_path, labels)
    errors.extend(mapping_errors)
    entries, raw_errors = load_runs(runs_dir)
    errors.extend(raw_errors)
    provenance = runs_dir.parent / 'import-index.json'
    index = {}
    if provenance.exists():
        try:
            index = read_json(provenance).get('runs', {})
        except (ValueError, OSError, AttributeError) as exc:
            errors.append(f'Invalid import-index: {exc}')
    rows, candidates = [], defaultdict(list)
    for label in labels:
        if not label['valid']:
            rows.append({'image_id': label['image_id'], 'row': label['row'], 'selected': False,
                         'classification': 'invalid_label', 'error': '; '.join(label['errors'])})
    for entry in entries:
        run = entry['run']
        if entry['error']:
            rows.append({'run_id': run.get('runId', '') if run else '', 'raw_path': entry['path'],
                         'selected': False, 'classification': 'invalid_run', 'error': entry['error']})
            continue
        rid = run['runId']
        source = index.get(rid, {})
        if source.get('sha256') and source['sha256'] != entry['sha256']:
            entry['error'] = 'Raw SHA-256 differs from import provenance'
            errors.append(f'{rid}: {entry["error"]}')
            rows.append({'run_id': rid, 'raw_path': entry['path'], 'selected': False,
                         'classification': 'invalid_run', 'error': entry['error']})
            continue
        image_id = mapping.get(rid, run['imageId'])
        label = valid.get(image_id)
        observed = source.get('observed_device')
        if observed and (not isinstance(observed, dict) or any(not isinstance(v, str) for v in observed.values())):
            errors.append(f'{rid}: invalid observed device')
            observed = None
        device = device_key(run, observed)
        row = {'image_id': image_id, 'recorded_image_id': run['imageId'], 'run_id': rid,
               'raw_path': entry['path'], 'device': device,
               'device_source': 'adb_observed' if observed else 'recorded_metadata',
               'status': run['status'], 'created_at': run['createdAt'], 'selected': False,
               'elapsed_ms': run.get('elapsedMs') if valid_timing(run) else None,
               'timing_valid': valid_timing(run), 'error': ''}
        if label is None:
            row['classification'] = 'unmapped'
            row['error'] = 'imageId/mapping has no valid label'
            errors.append(f'{rid}: {row["error"]}')
        else:
            if source.get('image_sha256') and source['image_sha256'] != label['image_sha256']:
                row.update(classification='invalid_run', error='Input image hash does not match label')
                errors.append(f'{rid}: {row["error"]}')
                rows.append(row)
                continue
            row.update(drug_name=label['drug_name'], strength=label['strength'],
                       relative_path=label['relative_path'], product=label['product'],
                       package_type=label['package_type'])
            usable = run['status'] == 'text' and bool(run['rawText'].strip())
            row['classification'] = (name_score(run['rawText'], label['drug_name'])
                                     if usable else 'name_not_found' if run['status'] == 'text'
                                     else run['status'])
            row['strength_result'] = strength_score(run['rawText'], label['strength'], usable)
            if run['status'] in ('text', 'no_text') and not valid_timing(run):
                row['error'] = 'Missing/invalid engine timing'
                errors.append(f'{rid}: {row["error"]}')
            candidates[(image_id, device)].append((entry, row))
        rows.append(row)
    devices = sorted({device for _, device in candidates})
    for (image_id, device), group in candidates.items():
        group.sort(key=lambda pair: (timestamp(pair[0]['run']['createdAt']), pair[0]['run']['runId']))
        group[0][1]['selected'] = True
    for device in devices or ['no_device']:
        for image_id, label in valid.items():
            if (image_id, device) not in candidates:
                rows.append({'image_id': image_id, 'drug_name': label['drug_name'],
                             'strength': label['strength'], 'relative_path': label['relative_path'],
                             'product': label['product'], 'package_type': label['package_type'],
                             'device': device, 'selected': False, 'classification': 'not_run'})
    scores = {device: metric([row for row in rows if row.get('device') == device], len(valid))
              for device in devices or ['no_device']}
    groups = {}
    for device in devices or ['no_device']:
        for field in ('product', 'package_type'):
            for value in sorted({label[field] for label in valid.values()}):
                total = sum(label[field] == value for label in valid.values())
                groups[f'{device}|{field}={value}'] = metric([
                    row for row in rows if row.get('device') == device and row.get(field) == value], total)
    report = {'schema_version': 1, 'mode': mode, 'decision': 'not_decided', 'rules': RULES,
              'snapshot': snapshot(labels_path, labels), 'label_rows': len(labels),
              'valid_labels': len(valid), 'raw_files': len(entries), 'scores': scores, 'groups': groups,
              'row_counts': dict(Counter(row['classification'] for row in rows)),
              'selected_counts': dict(Counter(row['classification'] for row in rows if row.get('selected'))),
              'data_errors': errors, 'rows': rows,
              'limitations': ['OCR occurrence is not catalog matching accuracy.',
                              'Pilot samples are not automatically a representative benchmark.',
                              'Unknown deviceKind is not evidence of a physical device.']}
    if mode == 'benchmark':
        report['benchmark'] = benchmark(report, entries, labels, mapping, index, protocol, manifest)
        report['decision'] = report['benchmark']['decision']
    return report


def benchmark(report, entries, labels, mapping, index, protocol, manifest):
    """Require actual frozen evidence before making a go/no-go decision."""
    pending = {'decision': 'pending', 'reasons': []}
    reasons = pending['reasons']
    if not isinstance(protocol, dict) or not isinstance(manifest, dict):
        reasons.append('Frozen protocol and verified manifest are required.')
        return pending
    required = ('version', 'frozenAt', 'dataset_hash', 'required_devices', 'required_conditions',
                'required_config', 'min_images_per_condition', 'repetitions', 'threshold_name', 'latency_p95_ms')
    try:
        if protocol.get('status') != 'frozen' or any(key not in protocol for key in required):
            raise ValueError('Protocol must be complete and frozen')
        frozen = timestamp(protocol['frozenAt'])
        for key in ('min_images_per_condition', 'repetitions'):
            if type(protocol[key]) is not int or protocol[key] < 1:
                raise ValueError(f'Invalid {key}')
        for key in ('threshold_name', 'latency_p95_ms'):
            if type(protocol[key]) not in (float, int) or not math.isfinite(protocol[key]):
                raise ValueError(f'Invalid {key}')
        if not 0 <= protocol['threshold_name'] <= 1 or protocol['latency_p95_ms'] <= 0:
            raise ValueError('Invalid score/latency threshold')
        for key in ('required_devices', 'required_conditions'):
            values = protocol[key]
            if (not isinstance(values, list) or not values or any(not isinstance(v, str) or not v for v in values)
                    or len(values) != len(set(values))):
                raise ValueError(f'Invalid {key}')
        config = protocol['required_config']
        required_config = ('engine', 'packageVersion', 'nativeSdkVersion', 'script', 'preprocessing', 'appRevision')
        if not isinstance(config, dict) or any(not isinstance(config.get(k), str) or not config[k] for k in required_config):
            raise ValueError('Missing frozen engine/build configuration')
        if config['engine'] != 'google_mlkit_text_recognition' or config['script'] != 'latin' or config['preprocessing'] != 'none':
            raise ValueError('Unsupported OCR engine configuration')
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        reasons.append(str(exc))
        return pending
    if report['data_errors']:
        reasons.append('Dataset/run/import errors must be resolved.')
    actual = report['snapshot']
    if protocol['dataset_hash'] != actual['dataset_hash'] or manifest.get('dataset_hash') != actual['dataset_hash']:
        reasons.append('Actual dataset hash differs from frozen protocol/manifest.')
    if manifest.get('labels_sha256') != actual['labels_sha256']:
        reasons.append('Actual workbook hash mismatch.')
    verified = manifest.get('images', [])
    if not isinstance(verified, list) or any(not isinstance(item, dict) for item in verified):
        reasons.append('Invalid manifest images')
        return pending
    image_map = {item.get('image_id'): item for item in verified}
    if len(image_map) != len(verified) or set(image_map) != {row['image_id'] for row in labels if row['valid']}:
        reasons.append('Manifest image coverage/duplicates mismatch.')
    for image in actual['images']:
        item = image_map.get(image['image_id'], {})
        if any(item.get(key) != value for key, value in image.items()):
            reasons.append(f'Image bytes/labels mismatch: {image["image_id"]}')
        if item.get('labels_verified') is not True or not item.get('verified_by') or not item.get('verified_at'):
            reasons.append(f'Unverified label: {image["image_id"]}')
        if item.get('condition') not in protocol['required_conditions']:
            reasons.append(f'Unknown/missing condition: {image["image_id"]}')
    for condition in protocol['required_conditions']:
        if sum(item.get('condition') == condition for item in verified) < protocol['min_images_per_condition']:
            reasons.append(f'Insufficient condition samples: {condition}')
    if reasons:
        pending['reasons'] = sorted(set(reasons))
        return pending
    annotations = manifest.get('runs', {})
    if not isinstance(annotations, dict):
        reasons.append('Missing run phase sidecar')
        return pending
    slots = defaultdict(list)
    for entry in entries:
        if entry['error'] or not entry['run']:
            continue
        run = entry['run']
        rid = run['runId']
        device = device_key(run, index.get(rid, {}).get('observed_device'))
        iid = mapping.get(rid, run['imageId'])
        annotation = annotations.get(rid, {})
        phase = annotation.get('phase') if isinstance(annotation, dict) else None
        if device not in protocol['required_devices'] or iid not in image_map or phase not in ('cold', 'warm'):
            reasons.append(f'Unexpected/unannotated run: {rid}')
            continue
        slots[(iid, device, phase)].append(run)
    metrics = defaultdict(lambda: {'correct': 0, 'total': 0, 'times': []})
    for iid, image in image_map.items():
        for device in protocol['required_devices']:
            for phase in ('cold', 'warm'):
                runs = sorted(slots[iid, device, phase], key=lambda r: (timestamp(r['createdAt']), r['runId']))
                if len(runs) < protocol['repetitions']:
                    reasons.append(f'Missing repetitions: {iid}/{device}/{phase}')
                for run in runs[:protocol['repetitions']]:
                    if timestamp(run['createdAt']) <= frozen:
                        reasons.append(f'Run precedes frozen protocol: {run["runId"]}')
                    if any(run['metadata'].get(key) != value for key, value in config.items()):
                        reasons.append(f'Frozen config mismatch: {run["runId"]}')
                    key = f'{device}|{phase}|{image.get("condition", "unknown")}'
                    bucket = metrics[key]
                    bucket['total'] += 1
                    bucket['correct'] += int(run['status'] == 'text' and name_score(run['rawText'], image['drug_name']) == 'exact_name')
                    if valid_timing(run):
                        bucket['times'].append(run['elapsedMs'])
                    else:
                        reasons.append(f'Missing successful engine timing: {run["runId"]}')
    scored = {key: {'correct': value['correct'], 'total': value['total'],
                    'accuracy': value['correct'] / value['total'] if value['total'] else None,
                    'timing': timing(value['times'])} for key, value in metrics.items()}
    if not scored:
        reasons.append('No benchmark measurements')
    if reasons:
        pending.update(reasons=sorted(set(reasons)), groups=scored)
        return pending
    passed = all(row['accuracy'] >= protocol['threshold_name'] and row['timing']['p95_ms'] is not None
                 and row['timing']['p95_ms'] <= protocol['latency_p95_ms'] for row in scored.values())
    return {'decision': 'go' if passed else 'no-go', 'reasons': [], 'groups': scored}


def csv_safe(value):
    if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@')):
        return "'" + value
    return value


def write_reports(report, output):
    output.mkdir(parents=True, exist_ok=True)
    fields = ('image_id', 'recorded_image_id', 'drug_name', 'strength', 'relative_path', 'product',
              'package_type', 'run_id', 'raw_path', 'device', 'device_source', 'selected', 'created_at',
              'status', 'classification', 'strength_result', 'elapsed_ms', 'timing_valid', 'row', 'error')
    with (output / 'per_image.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows({key: csv_safe(value) for key, value in row.items()} for row in report['rows'])
    (output / 'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    lines = ['# Báo cáo OCR', '', f'Chế độ: {report["mode"]}; quyết định: **{report["decision"]}**.', '',
             f'Nhãn: {report["valid_labels"]}/{report["label_rows"]} hợp lệ; raw: {report["raw_files"]} file.', '',
             '| Thiết bị | Đúng/đã chạy | Accuracy | Coverage | Median / p95 ms |',
             '|---|---|---|---|---|']
    for device, score in report['scores'].items():
        accuracy = f'{score["accuracy"]:.1%}' if score['accuracy'] is not None else 'N/A'
        lines.append(f'| {device.replace("|", "/")} | {score["correct"]}/{score["evaluated"]} | {accuracy} | '
                     f'{score["evaluated"]}/{score["labelled_images"]} | '
                     f'{score["timing"]["median_ms"]} / {score["timing"]["p95_ms"]} |')
    lines += ['', 'Tên chỉ đạt khi đúng cả cụm; đủ token nhưng tách xa là chẩn đoán phụ.',
              'Hàm lượng chấm riêng; nhiều thành phần chưa có quy tắc thì chưa chấm.',
              'JSON raw không bị sửa. Xem per_image.csv cho từng ảnh/run và summary.json cho nhóm chi tiết.', '',
              '## Trạng thái các run được chọn để chấm', '',
              *[f'- {key}: {value}' for key, value in sorted(report['selected_counts'].items())], '',
              '## Từng ảnh theo run được chọn', '',
              '| Image ID | Tên kỳ vọng | Kết quả | Run ID |', '|---|---|---|---|']
    for row in report['rows']:
        if row.get('selected') or row['classification'] in ('not_run', 'invalid_label'):
            values = [str(row.get(key, '')).replace('|', '/').replace('\n', ' ')
                      for key in ('image_id', 'drug_name', 'classification', 'run_id')]
            lines.append('| ' + ' | '.join(values) + ' |')
    lines += ['', '## Nhóm sản phẩm và bao bì', '',
              '| Nhóm / thiết bị | Đúng/đã chạy | Đã chạy/tổng nhãn |', '|---|---|---|']
    for key, score in report['groups'].items():
        lines.append(f'| {key.replace("|", " / ")} | {score["correct"]}/{score["evaluated"]} | '
                     f'{score["evaluated"]}/{score["labelled_images"]} |')
    lines += ['', '## Tất cả hàng xuất (gồm run thừa/không ánh xạ/chưa chạy)', '',
              *[f'- {key}: {value}' for key, value in sorted(report['row_counts'].items())], '',
              '## Lỗi dữ liệu', '', *[f'- {error}' for error in report['data_errors'] or ['Không có.']], '',
              '## Giới hạn', '', *[f'- {item}' for item in report['limitations']]]
    if report.get('benchmark'):
        lines += ['', '## Benchmark', '', *[f'- {item}' for item in report['benchmark'].get('reasons', [])]]
    (output / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--labels', type=Path, default=DATASET / 'labels.xlsx')
    parser.add_argument('--runs', type=Path, default=DATASET / 'results/pilot-001/raw')
    parser.add_argument('--output', type=Path, default=DATASET / 'results/pilot-001')
    parser.add_argument('--mapping', type=Path)
    parser.add_argument('--mode', choices=('pilot', 'benchmark'), default='pilot')
    parser.add_argument('--protocol', type=Path)
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args()
    try:
        report = evaluate(args.labels, args.runs, args.mapping or args.runs.parent / 'run-map.csv',
                          args.mode, read_json(args.protocol) if args.protocol else None,
                          read_json(args.manifest) if args.manifest else None)
        write_reports(report, args.output)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, f'Evaluation failed: {exc}\n')
    print(f'Decision: {report["decision"]}; labels: {report["valid_labels"]}/{report["label_rows"]}; '
          f'raw: {report["raw_files"]}; data errors: {len(report["data_errors"])}')
    print(f'Reports: {args.output.resolve()}')
    return 1 if report['data_errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
