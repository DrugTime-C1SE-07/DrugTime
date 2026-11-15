---
task: 4.14-ocr-unit-tests
stage: review
status: approved
approved_by: Duc1445
approved_at: 2026-11-12 16:12 +0700
content_hash: sha256:62d78cbda27dd851
inputs:
  01-requirement.md: sha256:c2de613be77ae8ff
  04-impl-notes.md: sha256:49f56a10192ff15a
---

# 4.14 · Review: Unit tests with real OCR output (PB31)

## 1. Kết luận

**Đạt, kèm lưu ý** (0 Critical, 0 High, 0 Medium, 7 Low).

> Phát hiện **High** từ vòng review trước (thiếu `testcases.json`, `testcases.xlsx` và cập nhật file tổng `Test_Cases.xlsx`) cùng các sai lệch diễn giải log full-suite/CI trong `04-impl-notes.md` đã được khắc phục đầy đủ và kiểm chứng lại sau khi `reopen implement`.

## 2. Phạm vi đã review

| Submodule | Lệnh diff / kiểm tra |
|---|---|
| `backend` | `git -C backend status` & đọc toàn bộ `backend/tests/unit/test_ocr_real_output.py` (295 dòng, file mới trên nhánh `test/4.14-ocr-unit-tests`, hiện chưa commit) |
| `docs` | `git -C docs status` & kiểm tra `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (sheet `Chuẩn hóa OCR thực tế` mã `OCRREAL` và `Report` trên nhánh `test/4.14-ocr-unit-tests` tách từ `docs/origin/main` `31fc34c`, hiện chưa commit) |

Kết quả `python .agents/scripts/scope.py 4.14-ocr-unit-tests --stage implement`: **OK** (`backend/tests/unit/test_ocr_real_output.py`, `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`).

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | Đạt đầy đủ AC1–AC5 của Task 4.14: 12 mẫu OCR thực tế (≥ 10) từ `datasets/results/pilot-002/raw/*.json` khớp `12/12` byte-for-byte với JSON nguồn (`test_ocr_real_output.py:23-142`), lọc số đăng ký `VD-`, xử lý thận trọng confusables (`50Omg`, `5o0mg`, `Atotis l0`, `500 ma`), fold dấu tiếng Việt (`đ`/`Đ` -> `d`), bỏ qua LOT/EXP. Lưu ý giới hạn: 4.14 chỉ kiểm thử bộ chuẩn hóa OCR backend, không chứng minh hoàn tất các yêu cầu mobile/E2E của PB31 (camera, ảnh không rời thiết bị, confidence threshold, manual fallback — PB31 trong `Product-and-Sprint-backlog-DrugTime.xlsx` vẫn `Not started`, còn đo accuracy bao bì là Task 4.17). |
| Phạm vi & Ngoại lệ quy trình | `scope.py --stage implement` trả **OK** cho cả `backend/tests/unit/test_ocr_real_output.py` và `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`. **Giải trình ngoại lệ phạm vi**: `01-requirement.md` đã duyệt ghi `affected: [backend]` (`:8`), bảng submodule ghi `docs` là `Không` (`:58`) và bảng "File sẽ thay đổi" chỉ liệt kê 01 file trong `backend` (`:103`). Tuy nhiên, workbook `docs/.../Test_Cases.xlsx` vẫn được cập nhật vì `wf-implement/SKILL.md:64` bắt buộc task size S phải thực hiện `wf-testcase` ở cuối giai đoạn implement, và `.agents/scripts/scope.py:12` chủ động cấp ngoại lệ cho file `testcase-book` ở giai đoạn implement/test để không chặn quy trình. |
| Contract | Không áp dụng (`contract_change: no`). |
| Bất biến kiến trúc | Đạt — Chỉ thêm unit test nội bộ cho `normalize_ocr.py`, không chạm DB, PEP, `access_logs` hay LLM. |
| Bảo mật | Đạt — Không có secret, token, credential hay dữ liệu bệnh nhân. Mẫu văn bản thuộc bộ dữ liệu bao bì công khai `datasets/results/pilot-002/raw/`. |
| Xử lý lỗi | Đạt — `_find_dataset_raw_dir()` xử lý bằng `pytest.skip()` khi chạy tách rời khỏi repo gốc thiếu `datasets/`. |
| Hiệu năng | Đạt — `test_ocr_real_output.py` chạy xong trong `0.22s`; toàn bộ suite chuẩn hóa OCR (`117` tests) chạy xong trong `0.29s`. |
| Chất lượng test | Đạt — Khẳng định rõ trên ca hợp lệ, ca nhiễu/confusables, tính bất biến (`FrozenInstanceError`), byte-for-byte matching (`12/12`), không skip vô lý do. |
| Dễ đọc và nhất quán | Đạt về cú pháp (`py_compile` 0 lỗi, bám pattern `test_catalog_ocr_normalization.py`). Chưa xác minh được `ruff check .` do môi trường thiếu module `ruff`. |
| Đối chiếu `04-impl-notes.md` và `testcases.json` với `evidence/` | Đạt — Khớp 100%: `evidence/fixture-source-check.log` (`12/12`), `evidence/test-run.log` (`8/8` test mới & `117/117` bộ OCR), `evidence/testcase-xlsx.log` (`validate`, `build`, `merge` exit 0; `OCRREAL`: 10 test case — Pass 9, Fail 0, Pending 1), `evidence/implement-final-backend.log` (`1910 passed, 17 failed, 58 errors` được mô tả chính xác kèm `PermissionError` ở `E:\temp\pytest-of-Admin`, không khẳng định pre-existing). Sheet `Chuẩn hóa OCR thực tế` và dòng 50 trong `Report` của `Test_Cases.xlsx` đã xác minh tồn tại; bảo toàn toàn bộ **40 sheet** từ `docs/origin/main` (`31fc34c`) và tổng workbook sau gộp là **41 sheets**. |

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| **Low** | `01-requirement.md:8,58,103` vs `docs/.../Test_Cases.xlsx` | `01-requirement.md` đã duyệt không liệt kê `docs` nhưng workbook `Test_Cases.xlsx` vẫn được sửa ở implement theo quy tắc `wf-testcase` cho task size S (`wf-implement/SKILL.md:64`, được `scope.py:12` cấp ngoại lệ). | Ghi nhận công khai ngoại lệ quy trình này trong review (đã bổ sung giải trình tại Mục 3) để người duyệt và người review PR nắm rõ lý do `docs` thay đổi. |
| **Low** | `work/4.14-ocr-unit-tests/04-impl-notes.md:71-72` | Frontmatter của `04-impl-notes.md` đã là `status: approved` (`approved_at: 2026-11-12 15:48 +0700`), nhưng mục "Bước tiếp theo" cuối file vẫn còn câu cũ "Đang chờ: người duyệt kiểm tra và phê duyệt `04-impl-notes.md`...". | Do `04-impl-notes.md` đã khóa `content_hash` (`sha256:49f56a10192ff15a`), theo `AGENTS.md` agent **không được tự sửa** để tránh làm hỏng approval. Để nguyên trạng nếu chấp nhận ghi chú nhỏ này, hoặc chạy `gate.py reopen 4.14-ocr-unit-tests implement` nếu muốn đồng bộ chữ rồi duyệt lại. |
| **Low** | `evidence/verification-ruff-module.log` & `.github/workflows/` | Môi trường Python 3.14 hiện hành thiếu `ruff`, nên chưa chạy được `ruff check .`. Kiểm tra `.github/workflows/agents-check.yml` và `backend/.github/workflows/deploy-supabase.yml` không thấy workflow nào chạy `ruff`. | Cài `ruff` ở môi trường dev nếu cần kiểm tra lint tự động trước khi merge; không khẳng định CI tự chạy `ruff`. |
| **Low** | `work/4.14-ocr-unit-tests/evidence/implement-final-backend.log` | `pytest tests/unit tests/architecture` có 17 failed (`test_profile_http.py`: 6, `test_contract_notification.py`: 4, `test_contract_medication.py`: 3, `test_contract_device_tokens.py`: 2, `test_contract_openapi_semantics.py`: 2) và 58 errors (`test_build_knowledge_seed.py`: 56, `test_fcm_gateway.py`: 2 — `PermissionError: [WinError 5] Access is denied: 'E:\\temp\\pytest-of-Admin'`). Chưa có baseline log trước thay đổi. | Không liên quan đến file test OCR (`117/117` OCR unit test đều PASS). Ghi nhận rõ tình trạng chưa xác minh baseline để team theo dõi tách biệt. |
| **Low** | `backend/tests/unit/test_ocr_real_output.py:127-129` | Nếu chạy test độc lập chỉ trong `backend/` (không có `datasets/`), `test_ac1_fixtures_match_source_raw_json_byte_for_byte` sẽ `pytest.skip()`. | Đã phản ánh trung thực bằng test case `TC-OCRREAL-10` trạng thái `Pending` trong `testcases.json` / `Test_Cases.xlsx`. |
| **Low** | `git -C backend status` & `git -C docs status` | Các thay đổi (`tests/unit/test_ocr_real_output.py` trong `backend`, `Test_Cases.xlsx` trong `docs`) hiện vẫn chưa được commit/push trên nhánh `test/4.14-ocr-unit-tests`. | Sau khi duyệt `review`, thực hiện commit & push submodule trước rồi mới bump con trỏ superproject theo `wf-git`. |
| **Low** | `.gitignore:42-43` & `work/4.14-ocr-unit-tests/scratch/` | Dòng `/work/` trong `.gitignore` ignore toàn bộ `work/`, còn thư mục `work/4.14-ocr-unit-tests/scratch/` đang chứa file nháp (`generate_test.py`, `main_tc.xlsx`). Dùng `git add -f work/4.14-ocr-unit-tests/` sẽ ép đưa cả `scratch/` lên PR. | Khi stage artifact ở superproject, **chỉ liệt kê tường minh từng file/thư mục artifact và `evidence/`**, tuyệt đối bỏ qua `scratch/`:<br>`git add -f work/4.14-ocr-unit-tests/01-requirement.md work/4.14-ocr-unit-tests/04-impl-notes.md work/4.14-ocr-unit-tests/06-review.md work/4.14-ocr-unit-tests/testcases.json work/4.14-ocr-unit-tests/testcases.xlsx work/4.14-ocr-unit-tests/evidence/` |

## 5. Mô tả PR

### Thứ tự merge (theo `wf-git`)
1. Commit & push nhánh `test/4.14-ocr-unit-tests` trong submodule **`backend`** → mở PR và merge vào `backend/main`.
2. Commit & push nhánh `test/4.14-ocr-unit-tests` trong submodule **`docs`** → mở PR và merge vào `docs/main` (base `31fc34c`).
3. Sau khi cả 2 PR submodule đã merge (hoặc trỏ đúng commit đã push), bump con trỏ `backend` & `docs` trên nhánh `test/4.14-ocr-unit-tests` của **superproject `DrugTime`**, mở PR và merge vào `main`.

---

### PR 1 — Submodule `backend`
- **Title**: `test(ocr): add real-world packaging OCR normalization unit tests (PB31 / 4.14)`
- **Branch**: `test/4.14-ocr-unit-tests` -> `main`
- **Tóm tắt**:
  - Thêm bộ unit test [`tests/unit/test_ocr_real_output.py`](file:///C:/Users/Admin/.gemini/antigravity/worktrees/DrugTIme_main/execute_ducnt_plan/backend/tests/unit/test_ocr_real_output.py) kiểm thử module `normalize_ocr.py` trên 12 mẫu văn bản OCR thực tế (hộp & vỉ) từ `datasets/results/pilot-002/raw/*.json`.
- **Tiêu chí & Kết quả kiểm chứng**:
  - Đối soát **12/12 mẫu khớp 100% byte-for-byte** với JSON gốc (`test_ac1_fixtures_match_source_raw_json_byte_for_byte`).
  - Lọc chính xác số đăng ký thuốc (`SDK: VD-13882-11`, `SDK VD-1388-11`) không parse nhầm thành hàm lượng.
  - Xử lý thận trọng ký tự nhầm lẫn (`50Omg`, `5o0mg`, `Atotis l0`, `500 ma`), LOT/EXP và fold dấu tiếng Việt.
  - Kết quả pytest: **8/8 passed** (`test_ocr_real_output.py`, `0.22s`); **117/117 passed** (`test_catalog_ocr_normalization.py` + `test_ocr_real_output.py`, `0.29s`).
- **Rủi ro**: Thấp (chỉ thêm unit test, không sửa production code).

---

### PR 2 — Submodule `docs`
- **Title**: `test(docs): add OCRREAL unit test cases to Test_Cases.xlsx (task 4.14)`
- **Branch**: `test/4.14-ocr-unit-tests` -> `main` (tách từ `31fc34c`)
- **Tóm tắt**:
  - Gộp sheet `Chuẩn hóa OCR thực tế` (`OCRREAL`) gồm 10 test case (Pass 9, Fail 0, Pending 1) và cập nhật sheet `Report` trong `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` bằng `testcase_xlsx.py merge 4.14-ocr-unit-tests`.
  - Bảo toàn toàn bộ **40 sheet** hiện có trên `docs/origin/main` (`31fc34c`), tổng workbook sau gộp là **41 sheets**.
- **Ngoại lệ phạm vi**: `01-requirement.md` chỉ liệt kê `backend`, nhưng `Test_Cases.xlsx` được cập nhật theo quy tắc `wf-testcase` cho task size S (được `scope.py:12` cho phép).
- **Cách kiểm tra**: `python .agents/scripts/testcase_xlsx.py validate 4.14-ocr-unit-tests` (exit 0).

---

### PR 3 — Superproject `DrugTime`
- **Title**: `test(ocr): bump backend & docs submodules for task 4.14 real OCR unit tests (PB31)`
- **Branch**: `test/4.14-ocr-unit-tests` -> `main`
- **Liên kết PR**: Phụ thuộc PR submodule `backend` và PR submodule `docs` trên nhánh `test/4.14-ocr-unit-tests`.
- **Thay đổi**:
  - Bump con trỏ submodule `backend` và `docs` sau khi push/merge.
  - (Nếu chọn đưa artifact lên PR): Chỉ `git add -f` tường minh các file artifact + `evidence/`, **không** stage thư mục `scratch/`:
    `git add -f work/4.14-ocr-unit-tests/01-requirement.md work/4.14-ocr-unit-tests/04-impl-notes.md work/4.14-ocr-unit-tests/06-review.md work/4.14-ocr-unit-tests/testcases.json work/4.14-ocr-unit-tests/testcases.xlsx work/4.14-ocr-unit-tests/evidence/`
- **Phạm vi PB31**: Task 4.14 kiểm thử lớp chuẩn hóa OCR backend; toàn bộ PB31 vẫn còn các phần của Task 4.17 và luồng mobile/camera.

## 6. Ghi chú cho quy trình

- Cần kiểm tra `.gitignore:42-43` trước khi force-add trong `work/<task-id>/` để đảm bảo chỉ định rõ danh sách file/thư mục cần thiết và không kéo theo thư mục `scratch/`.
- Khi `wf-testcase` phát sinh thay đổi ở `testcase-book` ngoài danh sách `affected` của `01-requirement.md`, cần giải trình minh bạch ngoại lệ `scope.py:12` trong `06-review.md`.

## Bước tiếp theo

- Đang chờ: **người duyệt** phê duyệt `06-review.md` (hoặc quyết định có cần `reopen implement` chỉ để sửa dòng chữ "Bước tiếp theo" ở `04-impl-notes.md:71-72` hay không).
- Việc cần làm: Chạy `python .agents/scripts/gate.py approve 4.14-ocr-unit-tests review`, sau đó yêu cầu agent tiến hành **commit & push** nhánh `test/4.14-ocr-unit-tests` theo đúng thứ tự `backend` → `docs` → `superproject`.
- Cập nhật lần cuối: 2026-11-12 16:10, Antigravity
