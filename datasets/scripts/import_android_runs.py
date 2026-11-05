"""Import unchanged ML Kit JSON from exports or a selected debug Android app."""
from __future__ import annotations

import argparse
import base64
import csv
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from ocr_dataset import SAFE_ID, _reject_constant, load_labels, read_json, sha256, validate_run

PACKAGE = 'vn.drugtime.drugtime_mobile'
DATASET = Path(__file__).resolve().parents[1]


def write_original(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f'Refusing to overwrite conflicting file: {path}')
        return 'unchanged'
    with path.open('xb') as stream:
        stream.write(data)
    return 'imported'


def adb_call(adb, serial, *args):
    result = subprocess.run([str(adb), '-s', serial, *args], capture_output=True,
                            timeout=30, check=False)
    if result.returncode:
        raise ValueError(result.stderr.decode('utf-8', errors='replace').strip() or 'ADB failed')
    return result.stdout


def image_path(value):
    if not isinstance(value, str) or '\\' in value:
        raise ValueError('Invalid sandbox imagePath')
    path = PurePosixPath(value)
    if (len(path.parts) != 2 or not SAFE_ID.fullmatch(path.parts[0])
            or not re.fullmatch(r'image\.[A-Za-z0-9]+', path.parts[1])):
        raise ValueError('Unsafe sandbox imagePath')
    return 'files/ocr_runs/' + value


def import_runs(output, labels_path, source=None, adb=None, serial=None):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    labels, label_errors = load_labels(labels_path)
    by_hash = {}
    for label in labels:
        if label['valid']:
            by_hash.setdefault(label['image_sha256'], []).append(label['image_id'])
    index_path = output / 'import-index.json'
    previous = read_json(index_path) if index_path.exists() else {'runs': {}}
    index = {'schema_version': 1, 'imported_at': datetime.now(timezone.utc).isoformat(),
             'runs': dict(previous.get('runs', {})), 'errors': list(label_errors),
             'skipped_legacy': []}
    observed = None
    if adb:
        if not serial:
            raise ValueError('--serial is required for ADB')
        def prop(name):
            return adb_call(adb, serial, 'shell', 'getprop', name).decode().strip()
        observed = {'platform': 'android', 'deviceModel': prop('ro.product.model'),
                    'osVersion': prop('ro.build.version.release'),
                    'deviceKind': 'emulator' if prop('ro.kernel.qemu') == '1' else 'physical'}
        listing = adb_call(adb, serial, 'exec-out', 'run-as', PACKAGE,
                           'ls', '-1', 'files/ocr_runs').decode().splitlines()
        names = [name for name in listing if name.endswith('.json')]
    else:
        if source is None or not source.is_dir():
            raise ValueError('--source must be an existing directory')
        names = [path.name for path in sorted(source.glob('*.json'))]
    mappings = []
    for name in sorted(names):
        try:
            if not SAFE_ID.fullmatch(Path(name).stem) or Path(name).name != name:
                raise ValueError('Unsafe JSON filename')
            data = (base64.b64decode(adb_call(adb, serial, 'exec-out', 'run-as', PACKAGE,
                                             'base64', f'files/ocr_runs/{name}'), validate=False)
                    if adb else (source / name).read_bytes())
            run = validate_run(json.loads(data.decode('utf-8-sig'), parse_constant=_reject_constant))
            rid = run['runId']
            if rid != Path(name).stem:
                raise ValueError('Filename does not match runId')
            legacy = output.parent / 'legacy-pilot' / 'raw' / name
            if output.name != 'legacy-pilot' and legacy.exists():
                if legacy.read_bytes() != data:
                    raise ValueError('RunId conflicts with archived legacy run')
                index['skipped_legacy'].append(rid)
                continue
            state = write_original(output / 'raw' / name, data)
            record = {'run_id': rid, 'sha256': sha256(data), 'source':
                      f'adb:{serial}/files/ocr_runs/{name}' if adb else str(source / name),
                      'raw_path': f'raw/{name}'}
            if observed:
                record['observed_device'] = observed
            if rid in index['runs']:
                record = {**index['runs'][rid], **record}
            if adb and run.get('imagePath'):
                try:
                    remote = image_path(run['imagePath'])
                    digest = adb_call(adb, serial, 'exec-out', 'run-as', PACKAGE,
                                      'sha256sum', remote).decode().split()[0]
                    if not re.fullmatch(r'[a-f0-9]{64}', digest):
                        raise ValueError('Invalid image SHA-256 from ADB')
                    candidates = by_hash.get(digest, [])
                    record.update(image_sha256=digest, image_candidates=candidates,
                                  image_check='matched' if len(candidates) == 1 else
                                  'ambiguous' if candidates else 'not_in_dataset')
                    if len(candidates) == 1:
                        mappings.append({'run_id': rid, 'image_id': candidates[0],
                                         'verified_by': f'adb_sha256:{serial}',
                                         'reason': f'Exact input bytes SHA-256={digest}'})
                except (ValueError, OSError, subprocess.SubprocessError, IndexError) as exc:
                    record['image_check'] = 'unavailable'
                    record['image_check_error'] = str(exc)
                    index['errors'].append(f'{name}/image: {exc}')
            index['runs'][rid] = record
            print(f'{state}: {rid}')
        except (ValueError, OSError, UnicodeError, TypeError, subprocess.SubprocessError) as exc:
            index['errors'].append(f'{name}: {exc}')
    if source:
        for filename in ('native-smoke-index.json', 'user-pilot-index.json'):
            origin = source.parent / filename
            if origin.exists():
                write_original(output / 'provenance' / filename, origin.read_bytes())
    mapping_path = output / 'run-map.csv'
    if mappings:
        existing = []
        if mapping_path.exists():
            with mapping_path.open(encoding='utf-8-sig', newline='') as stream:
                existing = list(csv.DictReader(stream))
        grouped = {row['run_id']: row for row in existing}
        for row in mappings:
            if row['run_id'] in grouped and grouped[row['run_id']]['image_id'] != row['image_id']:
                index['errors'].append(f'Conflicting mapping: {row["run_id"]}')
            else:
                grouped.setdefault(row['run_id'], row)
        with mapping_path.open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=('run_id', 'image_id', 'verified_by', 'reason'))
            writer.writeheader()
            writer.writerows(grouped[key] for key in sorted(grouped))
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
    if source and output.name == 'legacy-pilot':
        provenance = output / 'provenance'
        provenance.mkdir(exist_ok=True)
        (provenance / 'migration.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--source', type=Path)
    group.add_argument('--adb', type=Path)
    parser.add_argument('--serial')
    parser.add_argument('--labels', type=Path, default=DATASET / 'labels.xlsx')
    parser.add_argument('--output', type=Path, default=DATASET / 'results/pilot-001')
    args = parser.parse_args()
    try:
        result = import_runs(args.output, args.labels, args.source, args.adb, args.serial)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        parser.exit(2, f'Import failed: {exc}\n')
    print(f'Indexed: {len(result["runs"])}; legacy skipped: {len(result["skipped_legacy"])}; errors: {len(result["errors"])}')
    for error in result['errors']:
        print('ERROR:', error)
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
