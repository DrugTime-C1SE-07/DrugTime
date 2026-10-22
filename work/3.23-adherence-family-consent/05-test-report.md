---
task: 3.23-adherence-family-consent
stage: test
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-21 19:08 +0700
content_hash: sha256:ea2f0480b2c00db3
inputs:
  01-requirement.md: sha256:59d6784f453d27aa
  02-contract.md: sha256:e50bcda374a39752
  03-plan.md: sha256:50da5a783bd24265
  04-impl-notes.md: sha256:8b2da5c24bddbce8
---

# 3.23-adherence-family-consent · Test tích hợp sau migration

## 1. Môi trường

- Backend/docs: nhánh `feat/3.23-adherence-family-consent`; Python 3.12.14, dependency riêng tại scratch/python-deps.
- Gate test trả OK sau khi implement được duyệt lại lúc 19:00 ngày 2026-10-21.
- Postgres thật tại 127.0.0.1:54322. Chỉ dùng DB riêng của task; đặt TEST_ADMIN_DATABASE_URL và DATABASE_URL về loopback. Fixture xác nhận app dùng api_role.
- Tạo database từ template0, tạo schema extensions, chạy toàn bộ migration từ rebuild 20260927082912 đến 20261021115000. DB cho test liên quan: drugtime_test_323_493161b1; DB mới cho full suite: drugtime_test_323_49db8994. Log: `evidence/test-db-reset-after-migration.log`.
- Supabase CLI chưa có trong PATH, chưa chạy lệnh supabase db reset và chưa kiểm seed/Supabase Auth. Cách dựng DB riêng như lượt implement đã ghi rõ; không thay .agents. Các DB test hiện chưa dọn.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Test | Kết quả hiện hành |
|---|---|---|
| AC1 | Self/family success; history groups/summary | Pass |
| AC2 | Chính chủ đọc thành công, audit allowed tối thiểu | Pass |
| AC3 | Không link/sharing-off/admin bị 403; admin-self và admin-linked có denied | Pass |
| AC4 | Thiếu từng consent health_data/family_sharing | Pass |
| AC5 | Rút consent/tắt chia sẻ/unlink rồi request ngay bằng cùng token | Pass |
| AC6 | Đổi patient_id sang patient khác; admin có link | Pass |
| AC7 | Audit/permission/commit failure fail-closed; denied tồn tại sau rollback; matrix CHECK và append-only | Pass |
| AC8 | Missing/invalid/expired/erased token; query sai UUID/ngày/enum | Pass |
| AC9 | OpenAPI runtime/query/security/status/header/schema và response history trên wire | Pass |

Bằng chứng cho AC1–AC8 và runtime AC9: `evidence/test-migration.log` (85 pass). Đối chiếu OpenAPI: `evidence/test-openapi-after-migration.log` (2 pass).

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Kết quả |
|---|---|
| Self/family được phép, audit allowed; dữ liệu tối thiểu | Pass |
| Không link/thiếu consent/tắt sharing/cross-patient: 403 và denied | Pass |
| Thu hồi consent/hủy link có hiệu lực ở request kế tiếp | Pass |
| Ghi audit/đọc quyền/commit lỗi không trả dữ liệu; denied không rollback theo request | Pass |
| Admin-self và admin-linked bị 403, audit denied vai admin | Pass |
| 16 tổ hợp self/other × role × allowed/denied theo CHECK; ca thử rollback | Pass |
| UPDATE/DELETE/TRUNCATE audit bằng api_role, worker_role và postgres bị chặn; dòng cũ không đổi | Pass, 9 ca |
| Idempotency, worker chạy đua với xác nhận muộn trong suite lịch sử hiện có | Pass |

File mới `backend/tests/integration/test_access_log_actor_identity.py` có 25 ca; dùng fixture DB thật và api_role, kiểm đúng SQLSTATE 23514 cho CHECK, 42501 cho thiếu quyền mutation, P0001 cho trigger chủ bảng. Không skip hay nới assertion.

## 4. Lệnh và kết quả

Các lệnh pytest chạy từ backend, PYTHONPATH gồm scratch/python-deps và backend/src; dùng Python bundled.

| Lệnh | Kết quả | Log |
|---|---|---|
| Pytest test_access_log_actor_identity.py + test_adherence_history_access.py + test_adherence_history_api.py, -q -rA -p no:cacheprovider --tb=short | 85 pass, 12.16s | `evidence/test-migration.log` |
| `pytest tests/integration -q -rsxX -p no:cacheprovider --tb=short` trên DB mới | 803 pass, 2 fail, 159 skip, 1 xpass, 5859 warning, 145.37s | `evidence/test-integration-after-migration.log` |
| Export OpenAPI vào scratch và 2 test query/security/status/header/schema | 2 pass, 3.14s | `evidence/test-openapi-after-migration.log` |
| Ruff hai file integration của task | Pass | `evidence/test-lint-after-migration.log` |
| `git diff --check` backend | Exit 0 | `evidence/test-diff-check-after-migration.log` |
| Scope test | Exit 1, 7 file ngoài phạm vi | `evidence/test-scope-after-migration.log` |

Full unit/architecture ở lượt implement vừa được duyệt: 1183 pass, 34 fail ở các nhóm contract khác/missed-dose window; chưa xác nhận baseline sạch (`evidence/implement-final-backend-amended.log`). Không chạy lại vì giai đoạn này chỉ thêm test tích hợp và cập nhật workbook.

Scope báo nguyên văn:

```text
  [OK]        backend/tests/integration/test_access_log_actor_identity.py
  [OK]        backend/tests/integration/test_adherence_history_access.py
  [OK]        docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx
  [NGOÀI]     api_contract/openapi.json
  [NGOÀI]     backend/src/drugtime/modules/access/domain/rules.py
  [NGOÀI]     backend/supabase/migrations/20261021115000_access_logs_admin_self_denied.sql
  [NGOÀI]     backend/tests/unit/test_access_authorize.py
  [NGOÀI]     backend/tests/unit/test_access_rules.py
  [NGOÀI]     backend/tests/unit/test_contract_adherence.py
  [NGOÀI]     docs/Team1_DTU/01_Proposal_&_Planning/drugtime_quyet_dinh_theo_chuc_nang.md
CHẶN: 7 file ngoài phạm vi. Ghi vào mục 'Phát sinh' và hỏi người dùng.
```

Sáu file đầu thuộc contract/implement đã duyệt, file cuối từ trạng thái nhánh docs. Bản scope gốc tính mọi thay đổi trên nhánh, không phân biệt giai đoạn. Giai đoạn test chỉ sửa hai file integration đã cho phép và workbook; không sửa .agents hoặc che trạng thái Git để làm scope pass.

## 5. Bộ test case Excel

- Spec: `testcases.json`; file task: `testcases.xlsx`.
- Đã validate/build/merge bằng testcase_xlsx.py, cả ba exit 0: `evidence/testcase-xlsx-after-migration.log`.
- File tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`.
- Trước merge đã xác nhận sheet ADHERENCE hiện có giống hoàn toàn file task trước sửa; thay đổi chưa commit của workbook chỉ là sheet task và Report. Sao lưu vào `scratch/testcases-master-before-after-migration.xlsx`.
- Script cảnh báo TC-ADHERENCE-14 từ Fail sang Pass: đây là cùng kết quả task được sinh trước migration, không phải kết quả tester khác ghi đè; cập nhật dựa trên hồi quy mới đã pass. Giữ bằng chứng fail cũ trong evidence.
- Sau merge đã kiểm sheet khác giữ nguyên values/formulas/styles/merged cells: `evidence/testcase-merge-preservation.log`.

| Chức năng | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| ADHERENCE | 23 | 23 | 0 | 0 |

Không còn bug đang fail trong sheet ADHERENCE. BUG-ADHERENCE-14 là lỗi đã sửa local và pass hồi quy; lịch sử còn ở mục 5b và log trước migration.

## 5b. Lỗi sản phẩm

**BUG-ADHERENCE-14: đã sửa và kiểm hồi quy.** Trước migration, admin-self có consent/lịch sử trả 500 thay vì 403 vì CHECK access_logs_actor_identity_check cấm vai admin khi actor=patient. Migration 20261021115000 chỉ thêm ngoại lệ admin-self denied, giữ các CHECK/grant/RLS/trigger khác. Hiện API trả 403 và có denied vai admin; matrix và append-only đều pass. Bằng chứng trước: `evidence/implement-migration-before.log`; sau: `evidence/test-migration.log`. Chưa coi task đã hoàn tất vì còn review/PR.

Hai fail của full integration cũng xuất hiện trước migration, nằm ngoài các file sản phẩm task sửa; chưa xác nhận trên baseline sạch:

| Test | Kỳ vọng / thực tế |
|---|---|
| test_post_doses_batch_creates_dose_log_for_authenticated_patient__AC1_AC10_AC18 | scheduled_at mong 01:00:00Z, thực tế 01:00:59.999000Z |
| test_profile_get_put_incomplete_complete__AC01_AC04 | Response có thêm email so với dict kỳ vọng |

Không sửa sản phẩm hoặc nới test ngoài phạm vi. Không mở issue theo yêu cầu tạm bỏ qua issue của người dùng.

## 6. Skip, xpass và tính ổn định

- 159 skip đều có lý do không đọc được supabase status vì thiếu CLI; thuộc các ca Auth/mobile login. Không tính skip là pass.
- Một xpass: test_post_doses_batch_requires_authentication__AC9 vốn đánh dấu xfail trong repo.
- 5859 warning phần lớn từ SQLAlchemy Row.t của schedule invariants và một warning Starlette.
- Admin-self trước migration fail ổn định; sau migration pass ở lượt implement, nhóm 85 ca và full suite. Không thêm retry hoặc sleep.

## 7. Phát sinh

- P6/P8/P9/P10 của plan đã có bằng chứng mới: API regression pass, test DB lâu dài, full integration và workbook đã cập nhật.
- Scope còn chặn 7 file từ giai đoạn trước/nhánh docs; đây là giới hạn chưa giải quyết, không báo scope xanh.
- .agents giữ nguyên và status sạch. Không commit/push hoặc tạo issue.
- Task chưa đạt Definition of Done: báo cáo test còn draft, chưa review và chưa có PR được người khác approve. Hai fail suite ngoài phần sửa và 159 skip cần người duyệt đánh giá.

## Bước tiếp theo

- Đang chờ: người duyệt xem kết quả, giới hạn scope/CLI và các lỗi ngoài phạm vi.
- Việc cần làm: nếu chấp nhận báo cáo cùng các giới hạn đã ghi, người duyệt chạy `python .agents/scripts/gate.py approve 3.23-adherence-family-consent test` trong terminal của họ. Sau đó agent mới làm review theo gate.
- Cập nhật lần cuối: 2026-10-21 19:07 +0700, Codex.
