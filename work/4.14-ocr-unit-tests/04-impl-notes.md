---
task: 4.14-ocr-unit-tests
stage: implement
owner: Duc1445
started_at: 2026-11-12 14:25
status: approved
approved_by: Duc1445
approved_at: 2026-11-12 15:48 +0700
content_hash: sha256:49f56a10192ff15a
inputs:
  01-requirement.md: sha256:c2de613be77ae8ff
---

# 4.14 · Implement: Unit tests with real OCR output (PB31)

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | Tạo `backend/tests/unit/test_ocr_real_output.py` với 12 mẫu raw OCR thực tế từ `datasets/results/pilot-002/raw/*.json` (đối soát khớp 12/12 byte-for-byte) và 8 test case bao phủ AC1–AC5. | [`evidence/fixture-source-check.log`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/work/4.14-ocr-unit-tests/evidence/fixture-source-check.log) |
| P2 | xong | Chạy pytest cho bộ test mới và bộ hồi quy OCR: 8/8 test mới pass (0.22s), 117/117 bộ OCR pass (0.29s). | [`evidence/test-run.log`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/work/4.14-ocr-unit-tests/evidence/test-run.log) |
| P3 | xong | Tạo bộ test case Excel (`work/4.14-ocr-unit-tests/testcases.json`, `testcases.xlsx`) và gộp sheet `Chuẩn hóa OCR thực tế` (`OCRREAL`) vào `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` qua `testcase_xlsx.py` (exit 0). | [`evidence/testcase-xlsx.log`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/work/4.14-ocr-unit-tests/evidence/testcase-xlsx.log) |

## 2. File đã thay đổi

| Submodule | Nhánh | File | Trạng thái Git hiện tại |
|---|---|---|---|
| `backend` | `test/4.14-ocr-unit-tests` | `tests/unit/test_ocr_real_output.py` | Chưa commit (`untracked`, chờ người dùng yêu cầu commit) |
| `docs` | `test/4.14-ocr-unit-tests` | `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` | Chưa commit (`modified`, chờ người dùng yêu cầu commit) |

Kết quả `python .agents/scripts/scope.py 4.14-ocr-unit-tests --stage implement`: **OK** (mọi thay đổi nằm trong phạm vi, bao gồm file tổng `testcase-book` theo `scope.py:12`) — log: [`evidence/implement-scope.log`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/work/4.14-ocr-unit-tests/evidence/implement-scope.log)

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| `backend` | `python -m pytest tests/unit/test_ocr_real_output.py -v` | 8 passed, 0 failed, 0 skipped (0.22s) | [`evidence/test-run.log`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/work/4.14-ocr-unit-tests/evidence/test-run.log) |
| `backend` | Đối soát 12 fixture với 49 JSON gốc | 12/12 exact rawText matches (100% byte-for-byte fidelity) | [`evidence/fixture-source-check.log`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/work/4.14-ocr-unit-tests/evidence/fixture-source-check.log) |
| `backend` | `python -m pytest tests/unit/test_catalog_ocr_normalization.py tests/unit/test_ocr_real_output.py` | 117 passed (109 synthetic + 8 real OCR) trong 0.29s | [`evidence/test-run.log`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/work/4.14-ocr-unit-tests/evidence/test-run.log) |
| `backend` (Full suite) | `pytest tests/unit tests/architecture` | 1910 passed, 17 failed (`test_profile_http.py`: 6, `test_contract_notification.py`: 4, `test_contract_medication.py`: 3, `test_contract_device_tokens.py`: 2, `test_contract_openapi_semantics.py`: 2), 58 errors (`test_build_knowledge_seed.py`: 56, `test_fcm_gateway.py`: 2 — lỗi `PermissionError: [WinError 5] Access is denied: 'E:\\temp\\pytest-of-Admin'`). Chưa có log baseline trước thay đổi để đối chiếu; không có test OCR nào nằm trong danh sách fail/error. | [`evidence/implement-final-backend.log`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/work/4.14-ocr-unit-tests/evidence/implement-final-backend.log) |
| `backend` (Lint) | `ruff check .` / `python -m py_compile` | Môi trường Python 3.14 hiện hành không có lệnh hay module `ruff`, chưa xác minh lint tự động. Kiểm tra cú pháp bằng `python -m py_compile backend/tests/unit/test_ocr_real_output.py` đạt 0 lỗi. | [`evidence/verification-ruff-module.log`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/work/4.14-ocr-unit-tests/evidence/verification-ruff-module.log) |

## 3b. Bộ test case Excel (chỉ task size S)

- **Spec JSON**: [`work/4.14-ocr-unit-tests/testcases.json`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/work/4.14-ocr-unit-tests/testcases.json)
- **File Excel riêng của task**: [`work/4.14-ocr-unit-tests/testcases.xlsx`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/work/4.14-ocr-unit-tests/testcases.xlsx)
- **File tổng**: [`docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx) — Sheet `Chuẩn hóa OCR thực tế` (Mã `OCRREAL`).
- **Số liệu Pass/Fail/Pending**:
  - `OCRREAL` (Chuẩn hóa văn bản OCR thực tế): **10 test case** — **Pass 9, Fail 0, Pending 1**.
  - Test case `Pending` cần chạy ở môi trường tách rời: `TC-OCRREAL-10` (kiểm tra hành vi `pytest.skip()` khi chạy ở môi trường chỉ mount `backend` mà không có thư mục `datasets/results/pilot-002/raw`).
  - Không có Bug Report (`Fail 0`).
- **Log thực thi `validate | build | merge`**: [`work/4.14-ocr-unit-tests/evidence/testcase-xlsx.log`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/work/4.14-ocr-unit-tests/evidence/testcase-xlsx.log) (cả 3 lệnh đều exit 0).

## 4. Migration

Không có.

## 5. Ghi chú cho người review

- **Giới hạn phạm vi PB31**: Task `4.14` là task con kỹ thuật kiểm thử unit test bộ chuẩn hóa OCR backend (`normalize_ocr.py`). Task này không kiểm thử và không chứng minh hoàn tất các yêu cầu còn lại của `PB31` (camera trên mobile, ảnh không rời thiết bị, ngưỡng confidence, fallback tìm kiếm thủ công — `PB31` trong `Product-and-Sprint-backlog-DrugTime.xlsx` vẫn đang `Not started`, còn đánh giá accuracy nhiều bao bì thuộc Task `4.17`).
- **Fidelity dữ liệu nguồn**: 12 mẫu thực tế (`atorvastatin_10_box_001`, `metformin_500_blister_001`, `candesartan_htz_32_25_box_001`, `bisoprolol_2_point_5_box_002`, `efferalgan_blister_002`, `metformin_500_blister_002`, `tiffy_dey_blister_002`, `strepsils_blister_001`, `decolgen_forte_box_002`, `metformin_500_box_003`, `atorvastatin_10_blister_001`, `candesartan_htz_32_25_blister_001`) khớp 12/12 byte-for-byte với `rawText` trong `datasets/results/pilot-002/raw/*.json`.
- **Tình trạng full-suite & lint**: Chưa có log baseline full-suite trước task để kết luận nguyên nhân gốc của 17 failed (contract/profile), còn 58 errors ở knowledge-seed và fcm đều có lỗi quyền tạo thư mục tạm `E:\temp\pytest-of-Admin`. Môi trường hiện hành thiếu `ruff` nên chưa chạy được lint tự động.
- **Trạng thái Git**: Các thay đổi ở `backend` và `docs` đang nằm ở working tree trên nhánh `test/4.14-ocr-unit-tests` (chưa commit theo quy tắc chờ người dùng yêu cầu / sau khi duyệt).

## 6. Phát sinh

- Đã bổ sung bộ test case Excel (`testcases.json`, `testcases.xlsx`, gộp `Test_Cases.xlsx` trên nhánh `test/4.14-ocr-unit-tests` của `docs` xuất phát từ `docs/origin/main` `31fc34c` để tránh xung đột nhị phân với PR #36) nhằm khắc phục phát hiện High từ lần review trước.

## Bước tiếp theo

- Đang chờ: người duyệt kiểm tra và phê duyệt `04-impl-notes.md`
- Việc cần làm: Chạy `python .agents/scripts/gate.py approve 4.14-ocr-unit-tests implement` trong terminal để phê duyệt lại giai đoạn `implement`, sau đó sang giai đoạn `review`.
- Cập nhật lần cuối: 2026-11-12 14:35, Antigravity
