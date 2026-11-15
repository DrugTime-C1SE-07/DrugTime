---
task: 5.13
stage: implement
owner: Bao Nguyen
started_at: 2026-11-10 13:17
status: approved
approved_by: Bao Nguyen
approved_at: 2026-11-10 13:47 +0700
content_hash: sha256:49570617e4a65030
inputs:
  01-requirement.md: sha256:eb0cc2ee1b9c43b1
  02-contract.md: sha256:d57a06a4057ba520
  03-plan.md: sha256:62e63b8e7ead5259
---

# 5.13 · Implement

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong phần tạo/review | Supabase CLI 3.1.0 tạo 20261110061954 scope và 20261110062000 request audit; additive enum/CHECK, không sửa migration cũ. DB kiểm ở P7. | `evidence/implement-P1.log` |
| P2 | xong | pytest SQL family links + facade audit: 29 passed, 1 cảnh báo cache do sandbox. | `evidence/implement-P2.log` |
| P3 | xong | pytest access authorize/rules: 42 passed, 1 cảnh báo cache do sandbox. | `evidence/implement-P3.log` |
| P4 | xong | pytest use case/gateway: 25 passed; lọc PEP, audit trước tên, null/trùng tên, revocation, error propagation. | `evidence/implement-P4.log` |
| P5 | xong | HTTP + contract parity + registry + dependency tests: 42 passed; audit/commit SQL lỗi 503, auth 401, selector/body 422, no-store. | `evidence/implement-P5-P6.log` |
| P6 | xong phần task; toàn repo chưa đạt | Bộ unit trong phạm vi task + tất cả architecture: 137 passed. Full suite: 1964 passed, 11 failed, 1 skipped; cùng 11 lỗi tái hiện với contract trước task. Lint file task sạch; full lint 63 lỗi trong 13 file không đổi so HEAD. Không sửa baseline ngoài plan. | `evidence/implement-task-final.log`, `evidence/implement-final-backend.log`, `evidence/implement-contract-baseline.log`, `evidence/implement-final-lint.log`, `evidence/implement-lint-baseline.log` |
| P7 | xong | Full reset local đến mới nhất exit 0. Reset riêng đến 20261030025813, seed fixture 5 scope/7 operation cũ, apply 2 migration và verify: dữ liệu cũ/grant không đổi, 6 ca CHECK sai bị chặn, 36 role/table/mutation bị chặn. | `evidence/implement-db-reset.log`, `evidence/implement-db-upgrade.log`, snapshot before/after |
| P8 | thuộc giai đoạn test | Chưa viết hoặc sửa file integration trong implement. | Chưa có |
| P9 | đã chạy kiểm tra phần implement; còn baseline | Đã chạy full unit/architecture, lint và scope; không báo toàn repo pass vì lỗi có trước. P8 và full integration thuộc stage test. | `evidence/implement-final-backend.log`, `evidence/implement-final-lint.log`, `evidence/implement-scope.log` |

## 2. File đã thay đổi

Backend bắt đầu sạch trên `feat/list-linked-patients`. Đã thay đổi **22 file** trong phạm vi plan (3 file integration của plan chưa tạo, dành cho stage test).

| Submodule | Nhánh | File |
|---|---|---|
| backend | feat/list-linked-patients | `src/drugtime/main.py` |
| backend | feat/list-linked-patients | `src/drugtime/modules/access/api.py` |
| backend | feat/list-linked-patients | `src/drugtime/modules/access/domain/rules.py` |
| backend | feat/list-linked-patients | `src/drugtime/modules/access/application/authorize.py` |
| backend | feat/list-linked-patients | `src/drugtime/modules/access/application/ports.py` |
| backend | feat/list-linked-patients | `src/drugtime/modules/access/application/list_linked_patients.py` |
| backend | feat/list-linked-patients | `src/drugtime/modules/access/adapters/inbound/linked_patients_http.py` |
| backend | feat/list-linked-patients | `src/drugtime/modules/access/adapters/outbound/linked_patients_gateway.py` |
| backend | feat/list-linked-patients | `src/drugtime/modules/family/api.py` |
| backend | feat/list-linked-patients | `src/drugtime/modules/family/application/ports.py` |
| backend | feat/list-linked-patients | `src/drugtime/modules/family/adapters/outbound/sql_links.py` |
| backend | feat/list-linked-patients | `src/drugtime/modules/family/adapters/outbound/sql_link_audit.py` |
| backend | feat/list-linked-patients | `supabase/migrations/20261110061954_linked_patient_access_scope.sql` |
| backend | feat/list-linked-patients | `supabase/migrations/20261110062000_linked_patient_request_audit.sql` |
| backend | feat/list-linked-patients | `tests/unit/test_access_rules.py` |
| backend | feat/list-linked-patients | `tests/unit/test_access_authorize.py` |
| backend | feat/list-linked-patients | `tests/unit/test_sql_family_links.py` |
| backend | feat/list-linked-patients | `tests/unit/test_linked_patients.py` |
| backend | feat/list-linked-patients | `tests/unit/test_linked_patients_http.py` |
| backend | feat/list-linked-patients | `tests/unit/test_linked_patients_gateway.py` |
| backend | feat/list-linked-patients | `tests/unit/test_contract_linked_patients.py` |
| backend | feat/list-linked-patients | `tests/architecture/test_health_route_enforcement.py` |

API contract có hai file đã được duyệt từ giai đoạn trước, không đổi trong implement. Không sửa artifact đã approved, không commit/push.

`scope.py --stage implement` exit 1: **22 file Backend đều [OK]**, năm [NGOÀI] là `api_contract/README.md`, `api_contract/openapi.json` và ba file Firebase đã ghi nhận trong plan approved. Không có file ứng dụng mới ngoài plan. Log: `evidence/implement-scope.log`. Scope toàn workspace chưa pass; không xóa/restore baseline để làm pass.

## 3. Kết quả test cuối

Các lệnh đều chạy trong lượt implement này, dùng `backend/.venv/Scripts/python.exe` và `-p no:cacheprovider` để tránh cache bị sandbox khóa. HTTP suite chạy ngoài sandbox vì Windows asyncio socketpair bị chặn.

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| backend | `python -m pytest tests/unit tests/architecture -q -p no:cacheprovider` | **1964 passed / 11 failed / 1 skipped**, không phải full pass | `evidence/implement-final-backend.log` |
| backend | `python work/5.13/scratch/run_task_tests.py` (root) | **137 passed**, gồm 7 file unit trong plan + tất cả architecture; chạy sau upgrade DB | `evidence/implement-task-final.log` |
| backend | `python work/5.13/scratch/reproduce_baseline.py` | Xác nhận cùng **11 test lỗi** với snapshot OpenAPI trước task; script chẩn đoán exit 0 khi tái hiện đúng tập lỗi. Không thay test/contract thật. | `evidence/implement-contract-baseline.log` |
| backend | `python -m ruff check . --no-cache --output-format concise` | **63 lỗi có trước**, trong 13 file không đổi HEAD; task không thêm lint error | `evidence/implement-final-lint.log`, `evidence/implement-lint-baseline.log` |
| backend | Ruff check/format giới hạn file Python trong plan, bỏ integration | **All checks passed** sau format; không chạy fix trên file ngoài phạm vi | `evidence/implement-format.log` |
| backend | `git -C backend diff --check` | Exit 0 | `evidence/implement-diff-check.log` |

Cảnh báo thư viện: Starlette cảnh báo dùng httpx cũ; một số test identity có key test ngắn. Không đổi thư viện hoặc test baseline ngoài plan. Một test skipped trong full suite vẫn giữ nguyên trạng thái, không báo thành pass.

## 3b. Bộ test case Excel

Task L: làm ở giai đoạn test theo wf-test/wf-testcase.

## 4. Migration

- Supabase CLI thiếu trong PATH: đã dùng npm cache/CLI `supabase@3.1.0`, kiểm help thực tế trước dùng cờ `--version`; không thêm dependency vào project.
- Tạo đúng hai file mới bằng `supabase migration new`; nội dung ở log P1. Scope enum commit riêng trước khi ứng dụng sử dụng. Ràng buộc mới chỉ cho operation `list_linked_patients` có subject/link null; operation cũ giữ yêu cầu cũ.
- Đã khởi động Docker Desktop để dùng local Supabase, xác minh container project DrugTime map port 54322; mọi lệnh reset/up chạy target **local 127.0.0.1:54322**, không đọc DATABASE_URL production.
- `npx supabase@3.1.0 db reset --no-seed`: exit 0, chạy toàn bộ migration gồm hai file mới. Log `evidence/implement-db-reset.log`.
- Quy trình upgrade riêng: `db reset --version 20261030025813 --no-seed`, seed fixture vào schema cũ, snapshot, `migration up`, verify bằng psycopg. Log `evidence/implement-db-upgrade.log`; snapshot `evidence/implement-upgrade-snapshot-before.json` và `evidence/implement-upgrade-snapshot-after.json`. Dữ liệu audit cũ giữ nguyên, đủ 5 scope và 7 operation cũ hợp lệ; scope/request events mới ghi được.
- Xác minh 6 tổ hợp operation/subject/link/reason không hợp lệ bị DB chặn; 2 bảng × 6 role × 3 thao tác = 36 UPDATE/DELETE/TRUNCATE bị chặn; grant trước/sau không đổi. Đây là kiểm migration P7, không thay thế bộ API integration P8.
- DB local hiện ở schema mới nhất với dữ liệu fixture kiểm migration, không có dữ liệu bệnh nhân thật được đưa vào script. Output Supabase có khả năng chứa key được lọc khỏi evidence; không lưu token/credential. Không sửa migration đã áp dụng, không sửa dữ liệu log cũ.

## 5. Ghi chú cho người review

Đã đọc lại QD-27–QD-30, QD-32, QD-33 mục 8–9 của `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` và đối chiếu truy vết trong requirement/plan. HBR-18 toàn hệ thống vẫn mở; scope của API 5.13 dùng health_data + family_sharing theo quyết định trong requirement. Bằng chứng test/AC sẽ cập nhật ở đây.

| Quy tắc / AC | Đã thực hiện và bằng chứng |
|---|---|
| QD-27/28; AC1, AC2, AC7, AC8, AC9 | Read-only list dùng caller, reuse `_ACTIVE` gồm bằng chứng đúng cặp; PEP resolve dùng facts DB và decide chung. Strict ID/tên response, distinct/sort/nullable tên; không dùng consent caller để cấp quyền patient khác. Unit/facade/SQL/HTTP/contract trong task-final pass. |
| QD-29/30; AC3, AC7 | Không cache facts, loại patient ngay lần gọi lại khi facts đổi; sharing của link mới không tự khôi phục. Unit pass; scenario API/DB thật cùng token dành cho P8. |
| QD-32; AC4, AC6, AC11 | Admin denied trước candidates, request-level audit subject/link null, writer transaction riêng; lỗi audit không bị nuốt. Unit/HTTP tests pass. |
| QD-33; AC5, AC10, AC11, AC14 | Allowed theo từng patient trước đọc tên, UoW commit trước response; filtered không ghi denied; empty audit request-level. Insert/commit fault HTTP tests pass; DB fault/concurrency integration P8 chưa làm. |
| AGENTS append-only/schema; AC12, AC13 | Reset sạch + upgrade với audit cũ + 36 tổ hợp role/mutation đạt trên DB thật; log/snapshot ở mục Migration. |
| Ranh giới module/route | Health registry có scope mới/bearer/identity; dependency architecture suite pass trong 137 test; không đổi ALLOWED hoặc thêm family → access. |

Đã sửa trùng tên schema `ValidationError` với FastAPI bằng model tên riêng của route; wire schema parity hiện pass. Không sửa OpenAPI approved để làm test qua.

## 6. Phát sinh

Baseline đã được ghi nhận trong plan approved: hai file contract của task và ba file Firebase untracked từ trước; không chạm các file đó trong implement. Thiếu công cụ/môi trường DB nếu gặp phải sẽ ghi rõ, không coi skip là pass hoặc tự thay plan.

- Windows sandbox chặn socketpair nội bộ của asyncio, làm TestClient treo trước request. Đã xác định stack, dừng đúng tiến trình pytest bị treo và rerun ngoài sandbox: 42 tests pass. Không đổi code để né hạn chế môi trường. Log chẩn đoán: `evidence/implement-http-diagnostic.log`.
- Full lint có 63 diagnostics trong 13 file không đổi so Git HEAD; đã xác nhận bằng script đọc Git, không chỉ suy đoán. Log `evidence/implement-lint-baseline.log`.
- Full unit/architecture chưa xanh vì 11 test contract baseline: thiếu `/me/device-tokens`, `/medications/search`, `/notifications` và `/notifications/{id}` trong contract đang checkout; hai assertion semantics cũ cho interaction/profile không khớp contract hiện có. Cùng 11 lỗi đã tái hiện với snapshot contract trước khi thêm endpoint 5.13. Những file/contract phần này nằm ngoài thay đổi được phép; không tự sửa/skip/xóa assertion. Đây là hạn chế toàn repo, không phải task test đã pass.
- Điều kiện P6 toàn repo xanh và scope toàn workspace sạch chưa đạt vì baseline trên. Cần người duyệt ghi nhận khi xem impl-notes; nếu yêu cầu sửa những phần đó trong task này thì phải reopen plan và duyệt phạm vi mới theo wf-implement bước 5, không tiện tay sửa ngoài bảng.

## Bước tiếp theo

- Phần code P1–P7 đã viết/kiểm theo phạm vi; 6/7 bước đạt toàn bộ điều kiện riêng, P6 chưa đạt điều kiện full repo xanh do 11 test/63 lint baseline. P9 đã chạy kiểm tra và ghi nhận các hạn chế, không đánh dấu toàn repo pass.
- Đang chờ: người duyệt xem code/impl-notes và quyết định chấp nhận baseline ngoài task hoặc mở rộng phạm vi sửa chúng. Nếu cần sửa ngoài plan: người dùng chạy `python .agents/scripts/gate.py reopen 5.13 plan`, agent cập nhật plan trước khi sửa.
- Nếu người duyệt chấp nhận baseline ngoài task khi duyệt giai đoạn implement: chạy `python .agents/scripts/gate.py approve 5.13 implement` trong terminal của người duyệt. Agent không tự duyệt. Sau đó mới làm P8 theo wf-test, chưa bắt đầu stage test trong lượt này.
- Không commit/push, không tạo/sửa 3 file integration dành cho stage test. Bằng chứng đầy đủ nằm trong evidence của task.
- Cập nhật lần cuối: 2026-11-10, Codex.
