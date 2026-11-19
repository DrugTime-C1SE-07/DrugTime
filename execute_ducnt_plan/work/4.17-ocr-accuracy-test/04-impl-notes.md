---
task: 4.17-ocr-accuracy-test
stage: implement
owner: Duc1445
started_at: 2026-11-14 10:35 +0700
status: approved
approved_by: Duc1445
approved_at: 2026-11-16 09:16 +0700
content_hash: sha256:f858084690ba58c3
inputs:
  01-requirement.md: sha256:95d4f73b8f3d2a81
  03-plan.md: sha256:91a7c5f2ee7e1d5d
---

# 4.17 · Implement: Test OCR accuracy across multiple packaging samples (PB31)

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `python work/4.17-ocr-accuracy-test/scratch/verify_p1_images.py` -> 33/33 ảnh khớp SHA256, 0 curly quotes | `evidence/implement-P1.log` |
| P2 | xong | `pytest backend/tests/unit/test_ocr_accuracy_benchmark.py -k test_load_and_validate_33_samples_and_labels` -> 1 passed | `evidence/implement-P2.log` |
| P3 | xong | `pytest backend/tests/unit/test_ocr_accuracy_benchmark.py -k "test_in_seed_accuracy_group_a1 or test_safety_fallback_out_of_seed_groups_a2_a3_a4"` -> 2 passed (Safety Fallback = 23/23 = 100%) | `evidence/implement-P3.log` |
| P4 | xong | `pytest backend/tests/unit/test_ocr_accuracy_benchmark.py -k "test_diagnostic_catalog_accuracy_and_latency or test_ocr_benchmark_logging_metadata_only"` -> 2 passed (Top-1/Top-3 = 72.7%, Median latency = 6.01ms) | `evidence/implement-P4.log` |
| P5 | xong | `python backend/scripts/benchmark_ocr_accuracy.py` -> In bảng 33 mẫu và xuất log chi tiết | `evidence/accuracy_report.log` |
| P6 | xong | `python .agents/scripts/testcase_xlsx.py validate|build|merge 4.17-ocr-accuracy-test` -> Pass 6, Fail 0, Pending 0 | `evidence/testcase-xlsx.log` |
| P7 | xong | `pytest backend/tests/unit/test_ocr_accuracy_benchmark.py backend/tests/unit/test_ocr_real_output.py backend/tests/unit/test_catalog_ocr_match_scoring.py` -> 85 passed | `evidence/implement-final-backend.log` |

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| `superproject` | `test/4.17-ocr-accuracy-test` | `datasets/manifest.v1.json` |
| `superproject` | `test/4.17-ocr-accuracy-test` | `datasets/annotations.v1.csv` |
| `superproject` | `test/4.17-ocr-accuracy-test` | `datasets/labels.xlsx` |
| `superproject` | `test/4.17-ocr-accuracy-test` | `datasets/images/README.md` |
| `superproject` | `test/4.17-ocr-accuracy-test` | `datasets/images/hapacol_extra/box/hapacol_extra_front_01.jpg` |
| `superproject` | `test/4.17-ocr-accuracy-test` | `datasets/results/pilot-002/raw/15f29db3-510a-4f8f-a041-9d1ccfdf322c.json` |
| `backend` | `test/4.17-ocr-accuracy-test` | `tests/unit/test_ocr_accuracy_benchmark.py` |
| `backend` | `test/4.17-ocr-accuracy-test` | `scripts/benchmark_ocr_accuracy.py` |
| `docs` | `test/4.17-ocr-accuracy-test` | `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` |

Kết quả `python .agents/scripts/scope.py 4.17-ocr-accuracy-test --stage implement`: OK (100% file nằm trong phạm vi) — log: `evidence/implement-scope.log`

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| `backend` | `pytest tests/unit/test_ocr_accuracy_benchmark.py tests/unit/test_ocr_real_output.py tests/unit/test_catalog_ocr_match_scoring.py` | 85 passed in 1.72s | `evidence/implement-final-backend.log` |
| `backend` | `pytest tests/architecture` | 22 passed in 7.50s | console |

## 3b. Bộ test case Excel (chỉ task size S)

Task size M, thực hiện theo checklist P6 đã duyệt trong plan:
- Spec: `work/4.17-ocr-accuracy-test/testcases.json`
- File task: `work/4.17-ocr-accuracy-test/testcases.xlsx`
- File tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (Sheet: `Độ chính xác OCR (PB31)`, Module: `OCRACC`)
- Thống kê: Pass 6, Fail 0, Pending 0
- Log: `evidence/testcase-xlsx.log`

## 4. Migration

Không có.

## 5. Ghi chú cho người review

1. **Tuân thủ 4 lưu ý quan trọng của Reviewer**:
   - Sử dụng `csv` module với ASCII straight quotes (`0x22`). Tuyệt đối không dùng curly quotes (`0x201C`, `0x201D`).
   - Kiểm tra byte-level: 100% file tạo mới (`test_ocr_accuracy_benchmark.py`, `benchmark_ocr_accuracy.py`, `testcases.json`, `accuracy_report.log`) đều có 0 byte curly quotes.
   - Trình tự thực thi chuẩn: kiểm tra ảnh -> tính SHA256 -> viết script -> chạy test -> cập nhật workbook -> viết report.
   - Commit từng bước độc lập theo `wf-git`.

2. **Kết quả đo lường định lượng (33 mẫu độc lập)**:
   - **Góc nhìn 1 — Báo cáo trên Seed thực tế (`10_knowledge_base.sql`)**:
     + Nhóm A1 (10 mẫu, Efferalgan & Atorvastatin): 7/10 mẫu (70.0%) nhận diện đúng hoạt chất; 10/10 mẫu có `preselected_id = null` an toàn.
     + Nhóm A2, A3, A4 (23 mẫu, khác hàm lượng hoặc ngoài danh mục seed): Đạt tỷ lệ an toàn **100% (23/23 mẫu)** trả về `status in ("no_match", "low_confidence")` với `preselected_id = null`, kích hoạt tìm kiếm thủ công chuẩn theo PB31 và QD-39.
   - **Góc nhìn 2 — Chẩn đoán thuật toán (14 cặp từ điển Ground Truth)**:
     + Top-1 Accuracy: 24/33 (72.7%)
     + Top-3 Accuracy: 24/33 (72.7%)
     + Mean Reciprocal Rank (MRR): 0.727
     + Độ trễ xử lý: Average = 6.79ms, Median = 6.01ms, P95 = 14.14ms (< 100ms).
   - **Phân tích minh bạch 9 ca không khớp Top-3 trong benchmark chẩn đoán** (AGENTS.md §5):
     + `bisoprolol_2_point_5_blister_001`: raw OCR text rỗng (ảnh vỉ chụp quá tối/mờ).
     + `strepsils_box_002`: OCR đọc sai ký tự 'ESrepsils' -> trượt ngưỡng fuzzy matching.
     + `decolgen_forte_box_002`: OCR đọc sai 'Decolger' (thay vì Decolgen).
     + `decolgen_forte_blister_001`: chữ trên vỉ quá mờ, ML Kit trích xuất không đủ token.
     + `tiffy_dey_box_001`, `002` & `blister_001`, `002` (4 mẫu): OCR đọc thành 'TIFFYoEY' hoặc thiếu token Tiffy.
     + `atorvastatin_10_blister_003`: nhôm vỉ phản quang mạnh, mất hoàn toàn tên biệt dược và hoạt chất.

3. **Kết quả kiểm toán chuyên sâu bổ sung (Swarm Audit)**:
   - Đã chạy swarm kiểm toán độc lập (`audit-data`, `audit-code`, `audit-book`) với 100% PASS.
   - Kiểm tra 12 trường hợp giới hạn biên cực trị: chuỗi rỗng `""`, chuỗi toàn khoảng trắng, chuỗi rác > 10KB, ký tự Unicode confusable / zalgo. Xác nhận pipeline xử lý mượt mà, không bao giờ crash và luôn giữ vững bất biến an toàn `preselected_id = null`.
   - Toàn bộ 50 file raw JSON, file nhãn `labels.xlsx` (cells & XML), `manifest.v1.json` và `annotations.v1.csv` đều sạch 100% không có ký tự curly quotes.
   - Bằng chứng kiểm toán lưu tại `work/4.17-ocr-accuracy-test/evidence/audit-data-integrity.log`.

## 6. Phát sinh

Không có phát sinh ngoài plan. Toàn bộ thay đổi khớp 100% với bảng phạm vi đã duyệt.

## Bước tiếp theo

- Đang chờ: Reviewer kiểm tra và đánh giá kết quả triển khai giai đoạn implement.
- Việc cần làm: Người dùng chạy `python .agents/scripts/gate.py approve 4.17-ocr-accuracy-test implement` trong terminal riêng để phê duyệt giai đoạn implement, sau đó chuyển sang giai đoạn test (05-test-report.md).
- Cập nhật lần cuối: 2026-11-14 10:42, Antigravity
