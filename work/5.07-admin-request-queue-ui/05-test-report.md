---
task: 5.07-admin-request-queue-ui
stage: test
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-19 15:06 +0700
content_hash: sha256:cb7c4abe5a130e7d
inputs:
  01-requirement.md: sha256:821055c7aa5e683a
  03-plan.md: sha256:85421c949dc367bb
  04-impl-notes.md: sha256:79a97af4212edd02
---

# 5.07-admin-request-queue-ui · Test tích hợp

## 1. Môi trường

- **Không dựng được backend thật.** Máy này không có `docker` và `supabase` CLI (`where.exe docker supabase` không tìm thấy), nên không chạy được `cd backend && supabase start && supabase db reset`. Không dùng `backend/.env` hay DB dùng chung.
- Thay thế để kiểm giao diện: `work/5.07-admin-request-queue-ui/scratch/run-admin-mock.mjs`.
  - API giả `GET /admin/deletion-requests` trên `127.0.0.1:8799`, đúng hình dạng contract 5.06: `skip`/`limit`, `{items,total}`, `Cache-Control: no-store`, các lỗi 401/403/422/503.
  - `next dev` cổng 3107 với `DRUGTIME_API_BASE_URL=http://127.0.0.1:8799`.
  - Cookie `dt_admin_session` là JWT thử không ký, `exp` sau 24 giờ. Middleware chỉ kiểm `exp`.
  - Thao tác bằng trình duyệt trong app.
- Nhánh: `frontend` `feat/5.07-admin-request-queue-ui` (chưa commit). Task không sửa vùng `integration-test`, vì không có AC nào cần test tích hợp mới. Endpoint đã có test tích hợp của 5.06.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Test | Kết quả |
|---|---|---|
| AC1 bảng, thứ tự, giờ VN | TC-DELQUEUE-01 (kiểm tay, API giả), TC-DELQUEUE-02 (unit) | pass |
| AC2 phân trang, vượt cuối | TC-DELQUEUE-03, 04, 05 | pass |
| AC3 làm mới | TC-DELQUEUE-06 | pass |
| AC4 đang tải / rỗng / lỗi / thử lại | TC-DELQUEUE-07, 08 pass; TC-DELQUEUE-09 (đang tải) | pass một phần; 09 Pending |
| AC5 401/403 không lộ dữ liệu | TC-DELQUEUE-10, 11 | pass |
| AC6 bàn phím, UUID đầy đủ | TC-DELQUEUE-12 | pass |
| AC7 60 giây (QA.01) | TC-DELQUEUE-13 | Pending (cần backend thật) |
| AC8 lint, build | TC-DELQUEUE-14 | pass |

Mọi kết quả "pass" của kiểm tay là trên API giả. Chúng chứng minh giao diện xử lý đúng mọi dạng phản hồi trong contract, không chứng minh backend thật trả đúng dữ liệu.

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Test | Kết quả |
|---|---|---|
| Không phải admin → 403, không lộ dữ liệu (bất biến 1, 4) | TC-DELQUEUE-10: trang không chứa `user_id` nào | pass (API giả) |
| Phiên bị backend từ chối → không lộ dữ liệu, không vòng lặp chuyển trang | TC-DELQUEUE-11 | pass (API giả) |
| Endpoint 403 `admin_only` và dòng `access_logs` ở backend | `backend/tests/integration/test_admin_deletion_requests_api.py` (TC-DELQUEUE-15) | Pending: chưa chạy lại |

Các kịch bản truy cập chéo patient, rút consent, `client_uuid`, Worker chạy đua và quy tắc tương tác không áp dụng. Task chỉ là UI đọc một endpoint admin có sẵn.

## 4. Toàn bộ bộ test tích hợp

- Lệnh: `cd backend && supabase start && supabase db reset && pytest tests/integration`
- Kết quả: **chưa chạy**. Không có Supabase local (mục 1).
- Test chạy được trong phiên này:
  - `npm run test:deletion-queue`: 8 pass, 0 fail, 0 skip. Log: `evidence/test-unit.log`
  - `npm run lint`: exit 0. Log: `evidence/test-lint.log`
  - Kiểm tay trên API giả. Log: `evidence/test-manual-mock.log`, `evidence/test-mock-api-requests.json`
- `scope.py --stage test`: exit 1, 24 file `[NGOÀI]`. Không file nào do giai đoạn test tạo (mục 7). Log: `evidence/test-scope.log`

## 5. Bộ test case Excel

- Spec: `testcases.json` · File task: `testcases.xlsx` · File tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`, **chưa merge** (mục 7).
- Log: `evidence/testcase-xlsx.log` (validate và build exit 0)

| Chức năng (mã) | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| Hàng chờ yêu cầu xóa dữ liệu (admin) (DELQUEUE) | 15 | 12 | 0 | 3 |

- Test case `Pending` cần người có Supabase local chạy:
  - TC-DELQUEUE-09: trạng thái đang tải.
  - TC-DELQUEUE-13: AC7, 60 giây với backend thật.
  - TC-DELQUEUE-15: chạy lại `pytest tests/integration/test_admin_deletion_requests_api.py`.
- Bug đã ghi vào Bug Report: không có.

## 5b. Lỗi sản phẩm tìm thấy

Không có.

## 6. Test không ổn định hoặc bị skip

Không có test bị skip hay nới lỏng. Ba test case Pending ở mục 5 chưa chạy vì thiếu môi trường, không phải vì bị skip.

## 7. Phát sinh

- **Chưa merge vào file tổng.** Submodule `docs` đang ở nhánh `feat/adhoc-20261118-mobile-profile-flow-ui`, của task khác. Nhánh này còn thay đổi chưa commit của người dùng (2 file backlog `.ods`/`.xlsx`). Merge lúc này sẽ ghi `Test_Cases.xlsx` lên nhánh của task khác.
  - Cần người dùng chọn: tạo nhánh `feat/5.07-admin-request-queue-ui` trong `docs`, hoặc merge sau.
  - Lệnh merge: `python .agents/scripts/testcase_xlsx.py merge 5.07-admin-request-queue-ui`
- `scope.py --stage test` báo 24 file `[NGOÀI]`:
  - 11 file `frontend/admin/...` là code của giai đoạn implement đã duyệt. Chúng còn hiện vì chưa commit.
  - 13 file là thay đổi sẵn có, không thuộc task, giống `04` mục 6: speckit, `.specify/feature.json`, backlog.
- File `.claude/launch.json` tạm tạo để chạy preview đã xóa sau khi kiểm.
- Script kiểm tay nằm trong `scratch/`, không commit.

## Bước tiếp theo

- Đang chờ: người dùng, rồi người duyệt.
- Việc cần làm:
  - Quyết định nhánh `docs` để merge bộ test case.
  - Người có Supabase local chạy TC-DELQUEUE-09, 13, 15 rồi cập nhật file tổng.
  - Duyệt: `python .agents/scripts/gate.py approve 5.07-admin-request-queue-ui test`.
  - Sau đó giai đoạn review (`wf-review`).
- Cập nhật lần cuối: 2026-11-19 15:00, Claude Code
