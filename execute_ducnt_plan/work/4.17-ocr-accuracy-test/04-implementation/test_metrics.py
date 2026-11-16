"""Unit tests for OCR accuracy benchmark metrics (PB31 / Task 4.17).

Tests:
1. Group A1 in-seed active ingredient match accuracy (70.0%).
2. Groups A2..A4 safety fallback rate (100.0%, status NO_MATCH/LOW_CONFIDENCE, preselected_id=None).
3. Diagnostic 14-pair ground truth catalog accuracy (Top-1 72.7%, Top-3 72.7%, MRR 0.727).
4. Latency percentiles (median < 50ms, p95 < 100ms).
"""

import sys
from pathlib import Path
import pytest

# Add 04-implementation directory to path to import helpers from run_accuracy_test
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from run_accuracy_test import (
    load_33_samples,
    load_seed_catalog,
    load_diagnostic_catalog,
    FakeCatalogReader,
    match_ocr_text,
    POLICY,
    S,
)


def test_sample_count_and_integrity():
    """Verify 33 unique physical packaging samples are loaded."""
    samples = load_33_samples()
    assert len(samples) == 33
    a1 = [s for s in samples if s["group"] == "A1"]
    a2 = [s for s in samples if s["group"] == "A2"]
    a3 = [s for s in samples if s["group"] == "A3"]
    a4 = [s for s in samples if s["group"] == "A4"]
    assert len(a1) == 10
    assert len(a2) == 4
    assert len(a3) == 12
    assert len(a4) == 7


def test_in_seed_active_ingredient_accuracy():
    """Metric 1: Group A1 (10 samples) active ingredient accuracy >= 70% on seed."""
    catalog, aliases = load_seed_catalog()
    reader = FakeCatalogReader(catalog, aliases)
    samples = [s for s in load_33_samples() if s["group"] == "A1"]
    assert len(samples) == 10

    hits = 0
    for s in samples:
        expected = "Paracetamol" if s["drug_name"] == "Efferalgan" else "Atorvastatin"
        out = match_ocr_text(None, s["raw_text"], limit=5, policy=POLICY, reader=reader)
        assert out.preselected_id is None, "In-seed sample must not auto-select wrong seed drug"
        if out.items:
            cand = out.items[0].medication
            if cand.active_ingredient and expected.lower() in cand.active_ingredient.lower():
                hits += 1

    assert hits == 7
    acc = hits / len(samples)
    assert acc >= 0.70


def test_safety_fallback_rate():
    """Metric 2: Groups A2..A4 (23 samples) must achieve 100% safety fallback rate."""
    catalog, aliases = load_seed_catalog()
    reader = FakeCatalogReader(catalog, aliases)
    samples = [s for s in load_33_samples() if s["group"] in ("A2", "A3", "A4")]
    assert len(samples) == 23

    safe_count = 0
    for s in samples:
        out = match_ocr_text(None, s["raw_text"], limit=5, policy=POLICY, reader=reader)
        assert out.status in (S.NO_MATCH, S.LOW_CONFIDENCE), (
            f"Sample {s['image_id']} returned {out.status} instead of fallback"
        )
        assert out.preselected_id is None, (
            f"Sample {s['image_id']} wrongly auto-selected preselected_id {out.preselected_id}"
        )
        safe_count += 1

    assert safe_count == 23
    assert (safe_count / len(samples)) == 1.0


def test_diagnostic_accuracy_and_mrr():
    """Metric 3: Diagnostic 14-pair catalog Top-1/Top-3 >= 70% and MRR >= 0.70."""
    catalog, aliases = load_diagnostic_catalog()
    reader = FakeCatalogReader(catalog, aliases)
    samples = load_33_samples()

    gt_map = {
        "Efferalgan": {1},
        "Atorvastatin": {2, 3},
        "A.TATORVASTATIN": {2, 3},
        "A.TBisoprolol": {4, 5},
        "Bisoheart": {4, 5},
        "A.TCANDESARTAN HTZ": {6, 7},
        "ACANTANHTZ": {6, 7},
        "Decolgen Forte": {8},
        "Tiffy Dey": {9},
        "Cilapress": {10, 11},
        "Cildip": {10, 11},
        "Candesartan Krka": {12},
        "Strepsils Original": {13},
        "Hapacol Extra": {14},
    }

    t1_hits = 0
    t3_hits = 0
    reciprocal_ranks = []

    for s in samples:
        out = match_ocr_text(None, s["raw_text"], limit=5, policy=POLICY, reader=reader)
        target_ids = gt_map.get(s["drug_name"], set())
        candidate_ids = [c.medication.id for c in out.items]

        if candidate_ids and candidate_ids[0] in target_ids:
            t1_hits += 1
        if any(cid in target_ids for cid in candidate_ids[:3]):
            t3_hits += 1

        rr = 0.0
        for rank, cid in enumerate(candidate_ids[:3], 1):
            if cid in target_ids:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)

    t1_acc = t1_hits / len(samples)
    t3_acc = t3_hits / len(samples)
    mrr = sum(reciprocal_ranks) / len(samples)

    assert t1_hits == 24
    assert t3_hits == 24
    assert t1_acc >= 0.70
    assert t3_acc >= 0.70
    assert mrr >= 0.70


def test_latency_budget():
    """Metric 4: Median latency < 50ms and P95 < 100ms."""
    import time
    catalog, aliases = load_diagnostic_catalog()
    reader = FakeCatalogReader(catalog, aliases)
    samples = load_33_samples()

    latencies = []
    for s in samples:
        t0 = time.perf_counter()
        match_ocr_text(None, s["raw_text"], limit=5, policy=POLICY, reader=reader)
        ms = (time.perf_counter() - t0) * 1000
        latencies.append(ms)

    latencies.sort()
    med = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    assert med < 50.0
    assert p95 < 100.0
