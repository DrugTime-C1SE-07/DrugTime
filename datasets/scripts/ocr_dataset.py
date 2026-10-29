"""Read-only dataset helpers and deterministic OCR occurrence measurements."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import posixpath
import re
import statistics
import unicodedata
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path, PurePosixPath, PureWindowsPath
from xml.etree import ElementTree as ET

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
HEADERS = ('image_id', 'relative_path', 'drug_name', 'strength')
STATUSES = {'text', 'no_text', 'input_error', 'engine_error'}
SAFE_ID = re.compile(r'^[A-Za-z0-9_-]+$')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'), parse_constant=_reject_constant)


def _reject_constant(value):
    raise ValueError(f'Non-finite JSON number: {value}')


def timestamp(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError('createdAt requires timezone')
    return result


def safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError('Empty relative path')
    rel = PurePosixPath(relative.replace('\\', '/'))
    if rel.is_absolute() or PureWindowsPath(relative).drive or '..' in rel.parts:
        raise ValueError('Path must stay relative to dataset')
    resolved = (root / Path(*rel.parts)).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError('Path escapes dataset (including symlinks)')
    return resolved


def _cell_text(cell, strings):
    if cell.find('s:f', NS) is not None:
        return None, 'Formula labels are unsupported'
    kind = cell.get('t')
    if kind == 'inlineStr':
        return ''.join(n.text or '' for n in cell.findall('.//s:t', NS)), None
    value = cell.findtext('s:v', '', NS)
    if kind == 's':
        return strings[int(value)], None
    if kind == 'e':
        return None, f'Excel error: {value}'
    return value, None


def load_labels(path: Path):
    """Return every nonempty label row and errors; never modify the workbook."""
    candidates = []
    with zipfile.ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
            strings = [''.join(n.text or '' for n in si.findall('.//s:t', NS))
                       for si in root.findall('s:si', NS)]
        rels = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        targets = {r.get('Id'): r.get('Target') for r in rels if r.get('TargetMode') != 'External'}
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        for sheet in workbook.findall('s:sheets/s:sheet', NS):
            rid = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            target = targets.get(rid, '')
            member = posixpath.normpath(target.lstrip('/') if target.startswith('/') else 'xl/' + target)
            if not member.startswith('xl/') or member not in archive.namelist():
                raise ValueError('Invalid worksheet relationship')
            cells = []
            root = ET.fromstring(archive.read(member))
            for row in root.findall('s:sheetData/s:row', NS):
                values, issues = {}, {}
                for cell in row.findall('s:c', NS):
                    match = re.fullmatch(r'([A-Z]+)(\d+)', cell.get('r', ''))
                    if not match:
                        raise ValueError('Missing/invalid cell address')
                    value, issue = _cell_text(cell, strings)
                    values[match[1]] = value
                    if issue:
                        issues[match[1]] = issue
                cells.append((int(row.get('r', '0')), values, issues))
            for i, (row_num, values, issues) in enumerate(cells):
                lookup = {}
                for col, value in values.items():
                    lookup.setdefault(str(value or '').strip().casefold(), []).append(col)
                if all(key in lookup for key in HEADERS):
                    if issues or any(len(lookup[key]) != 1 for key in HEADERS):
                        raise ValueError('Ambiguous/formula header')
                    candidates.append((sheet.get('name'), row_num,
                                       {key: lookup[key][0] for key in HEADERS}, cells[i + 1:]))
    if len(candidates) != 1:
        raise ValueError('Expected exactly one sheet/header containing ' + ', '.join(HEADERS))
    name, _, columns, source_rows = candidates[0]
    rows, errors = [], []
    for row_num, values, issues in source_rows:
        fields = {key: str(values.get(col) or '').strip() for key, col in columns.items()}
        if not any(fields.values()) and not issues:
            continue
        row = {**fields, 'row': row_num, 'sheet': name, 'errors': []}
        for key, col in columns.items():
            if col in issues:
                row['errors'].append(f'{key}: {issues[col]}')
        if not fields['image_id'] or not SAFE_ID.fullmatch(fields['image_id']):
            row['errors'].append('Missing/invalid image_id')
        if not fields['drug_name']:
            row['errors'].append('Missing drug_name')
        try:
            image = safe_path(path.parent, fields['relative_path'])
            if not image.is_file():
                raise ValueError('Image not found')
            row['image_sha256'] = sha256(image.read_bytes())
        except (ValueError, OSError) as exc:
            row['errors'].append(str(exc))
        parts = PurePosixPath(fields['relative_path'].replace('\\', '/')).parts
        row['product'] = parts[1] if len(parts) >= 3 and parts[0] == 'images' else 'unknown'
        row['package_type'] = parts[-2] if len(parts) >= 2 else 'unknown'
        rows.append(row)
    counts = Counter(row['image_id'] for row in rows)
    for row in rows:
        if counts[row['image_id']] > 1:
            row['errors'].append('Duplicate image_id')
        row['valid'] = not row['errors']
        errors.extend(f'{name}!row {row["row"]}: {issue}' for issue in row['errors'])
    return rows, errors


def validate_run(run):
    if not isinstance(run, dict) or type(run.get('schemaVersion')) is not int or run['schemaVersion'] != 1:
        raise ValueError('Unsupported run schema')
    if not isinstance(run.get('runId'), str) or not SAFE_ID.fullmatch(run['runId']):
        raise ValueError('Invalid runId')
    if not isinstance(run.get('imageId'), str) or not run['imageId'].strip():
        raise ValueError('Missing imageId')
    if not isinstance(run.get('rawText'), str) or run.get('status') not in STATUSES:
        raise ValueError('Invalid rawText/status')
    timestamp(run.get('createdAt', ''))
    meta = run.get('metadata')
    if not isinstance(meta, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in meta.items()):
        raise ValueError('Invalid metadata')
    if any(not meta.get(k, '').strip() for k in ('platform', 'deviceModel', 'osVersion')):
        raise ValueError('Missing device metadata')
    return run


def normalize(text):
    return ' '.join(unicodedata.normalize('NFC', text).casefold().split())


def name_score(raw, target):
    raw, target = normalize(raw), normalize(target)
    if re.search(r'(?<!\w)' + re.escape(target) + r'(?!\w)', raw):
        return 'exact_name'
    expected = Counter(re.findall(r'\w+', target))
    actual = Counter(re.findall(r'\w+', raw))
    if expected and not (expected - actual):
        return 'tokens_present_noncontiguous'
    return 'partial_name' if expected & actual else 'name_not_found'


def strength_score(raw, target, usable=True):
    if not target:
        return 'unscored'
    match = re.fullmatch(r'(\d+(?:[.,]\d+)?)\s*(mg|mcg|µg|μg|g|ml|iu|%)', normalize(target))
    if not match:
        return 'requires_component_protocol'
    number, unit = match.groups()
    pattern = r'(?<![\w.,])' + re.escape(number) + r'\s*' + re.escape(unit) + r'(?!\w)'
    return 'correct' if usable and re.search(pattern, normalize(raw)) else 'incorrect'


def timing(values):
    values = sorted(values)
    return {'n': len(values), 'median_ms': statistics.median(values) if values else None,
            'p95_ms': values[math.ceil(.95 * len(values)) - 1] if values else None}


def valid_timing(run):
    value = run.get('elapsedMs')
    return (type(value) in (int, float) and math.isfinite(value) and value >= 0
            and run['status'] in ('text', 'no_text'))


def device_key(run, observed=None):
    meta = observed or run['metadata']
    return '/'.join(str(meta.get(k, 'unknown')).strip() or 'unknown'
                    for k in ('platform', 'deviceModel', 'osVersion', 'deviceKind'))


def load_mapping(path, labels):
    if path is None or not path.exists():
        return {}, []
    known = {r['image_id'] for r in labels if r['valid']}
    result, errors = {}, []
    with path.open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            rid = row.get('run_id', '')
            if (not SAFE_ID.fullmatch(rid) or row.get('image_id') not in known
                    or not row.get('verified_by', '').strip() or not row.get('reason', '').strip()):
                errors.append(f'Invalid/unverified mapping: {rid}')
            elif rid in result:
                errors.append(f'Duplicate mapping: {rid}')
                result[rid] = None
            else:
                result[rid] = row['image_id']
    return {k: v for k, v in result.items() if v}, errors


def load_runs(directory):
    entries, errors, ids = [], [], {}
    for path in sorted(directory.glob('*.json')):
        entry = {'path': str(path), 'run': None, 'error': ''}
        try:
            payload = path.read_bytes()
            run = validate_run(json.loads(payload.decode('utf-8-sig'), parse_constant=_reject_constant))
            entry.update(run=run, sha256=sha256(payload))
            if run['runId'] in ids:
                other = ids[run['runId']]
                if other['sha256'] != entry['sha256']:
                    other['error'] = 'Conflicting duplicate runId'
                    entry['error'] = 'Conflicting duplicate runId'
                else:
                    entry['error'] = 'Duplicate runId (identical bytes)'
            else:
                ids[run['runId']] = entry
        except (ValueError, TypeError, KeyError, UnicodeError, OSError) as exc:
            entry['error'] = str(exc)
        entries.append(entry)
    for entry in entries:
        if entry['error']:
            errors.append(f'{entry["path"]}: {entry["error"]}')
    return entries, errors


def snapshot(labels_path, labels):
    data = {'labels_sha256': sha256(labels_path.read_bytes()), 'images': [
        {key: row.get(key, '') for key in ('image_id', 'relative_path', 'drug_name', 'strength', 'image_sha256')}
        for row in sorted(labels, key=lambda row: (row['image_id'], row['row']))]}
    data['dataset_hash'] = sha256(json.dumps(data, ensure_ascii=False, sort_keys=True,
                                            separators=(',', ':')).encode())
    return data
