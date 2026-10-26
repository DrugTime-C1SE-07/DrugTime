---
task: 3.25
stage: test
status: draft
---

# 3.25 · Kiểm thử lịch sử tuân thủ người thân

**Đã khôi phục contract và chạy API/DB/Postman thật. Chưa đạt toàn bộ AC:** BUG-3.25-01 (Medium, xác nhận sớm) tái hiện ở cả unit và API/DB; BUG-3.25-02 (High, giữ dữ liệu khi offline/background) vẫn tái hiện ở widget. Không sửa sản phẩm hoặc đổi assertion để báo xanh.

## 1. Phạm vi và môi trường

- Yêu cầu bổ sung trực tiếp của người dùng ngày 25/10/2026: “thế test luôn đi, sẵn tiện cập nhật contract với thư mục postman luôn”. Phạm vi được bổ sung là `api_contract/openapi.json` và tài nguyên local dưới `postman/`. Không sửa 01/03/04 đã approved, không tự approve/reopen hoặc đổi contract_change của requirement.
- Gate test được chạy lại, exit 0: `evidence/test-contract-gate-final.log`. Trạng thái 01/03/04 approved, 05/06 draft.
- Backend HEAD `49f2f11`, frontend `a147ed4`, contract `585e99c`, docs `3077e2e`, tests `ac207f4`; các thay đổi lượt này chưa commit. Superproject/backend/frontend/contract/docs trên nhánh `test/3.25-family-adherence-history-tests`; tests giữ nhánh 3.15. Không đổi gitlink/push.
- Supabase/PostgreSQL **local** reset sạch từ backend: `../node_modules/.bin/supabase.cmd db reset`, exit 0, tới migration `20261021115000_access_logs_admin_self_denied.sql`; thiếu seed.sql là cảnh báo. Log `test-contract-db-reset.log`. Không sửa migration.
- Pytest dùng FastAPI TestClient + PostgreSQL thật bằng api_role, PEP thật. Clock lịch sử cố định 19/10/2026, Asia/Ho_Chi_Minh; fault injection chỉ ở test fail-closed hiện có. Postman gọi HTTP qua một tiến trình uvicorn mới bind 127.0.0.1, DB local/api_role, fixture giả dùng Factory/HistoryData có sẵn.
- Postman CLI 1.75.0 chạy local với `--no-report-events`; không publish workspace. Bearer chỉ tồn tại trong môi trường runtime tạm ở scratch, đã xóa khi kết thúc; không ghi token vào collection/environment/evidence. Tiến trình API thử nghiệm đã dừng. Dữ liệu DB test/audit giữ lại theo thiết kế append-only; không xóa access_logs.
- Áp dụng wf-test, wf-health-endpoint, wf-git, wf-testcase, Spreadsheets và các skill Postman api-engineer/api-documentation/api-testing/collection-schema-v3/variables. Các log test-contract và test-postman nêu dưới đây được thực thi trong lượt này, không lấy kết quả cũ để ghi Pass.

## 2. Contract và Postman đã cập nhật

### Contract

- Khôi phục **GET /adherence và đúng bảy schema Adherence** từ blob `382fb13:openapi.json`, là phần bị mất khi merge `d9a466e` vào main. Không dùng OpenAPI sinh từ backend làm oracle hoặc ghi đè toàn spec cũ lên các API hiện hành.
- Đối chiếu cấu trúc trước/sau: bỏ path và bảy schema vừa khôi phục thì toàn bộ phần còn lại bằng baseline; 16 local $ref liên quan phân giải được. Diff +547 dòng. `evidence/test-contract-restore.log`, `test-contract-final-audit.log`.
- 20 ca contract adherence đều Pass: ví dụ JSON, nullable/rate, bigint, trường bắt buộc, enum, query/security/status/no-store; `test-contract-targeted.log/xml`.
- Mô tả contract gốc chỉ trả liều đã đến as_of. Điều này còn khác ngoại lệ AC3 người dùng chốt 23/10 (xác nhận sớm hợp lệ phải xuất hiện ngay); giữ bất đồng này tường minh và giữ test AC3 đỏ. Chưa thay quy tắc API hoặc tự tuyên bố contract mới được duyệt.

### Postman

- `postman/collections/DrugTime-Adherence`: sáu GET có bearer/assertion dùng chung và năm ví dụ dựa trên contract. Khởi tạo từ spec bằng CLI, thay UUID/ngày/header giả sinh tự động bằng biến runtime và nội dung chuẩn.
- `postman/environments/Adherence local.environment.yaml`: base_url, patient_id, denied_patient_id, from_date, to_date và family_access_token rỗng; không có credential literal.
- `postman/README.md`: lệnh lint/run, dựng điều kiện family/P/Q, request 200/401/403/422 và bốn tình huống thu hồi với cùng bearer; hướng dẫn không ghi token vào Git.
- Lint collection: **6 request, 0 error/0 warning**, exit 0; lint environment với fail-severity warning: 0 issue, exit 0. Tám script JavaScript compile. Log `test-postman-lint-final.log`, `test-postman-environment-lint.log`, `test-postman-script-syntax.log`.
- Guard target được kiểm bằng HTTP listener loopback không token: URL sai bị chặn trước HTTP, listener nhận **0 request**, CLI exit 1 đúng kỳ vọng. `test-postman-target-guard.log`. Không dùng guard này làm bằng chứng nghiệp vụ.
- Live collection: **9 lượt, 14 request, 75 assertion, 0 failure**, tất cả lượt exit 0. Lượt đầu gồm date/medication 200, thiếu bearer 401, cross-patient 403, group sai/quá 90 ngày 422. Bốn lượt trước thu hồi 200 và bốn request kế tiếp cùng bearer 403; DB kiểm audit allowed→denied, đúng actor/scope và dose_logs không đổi. `test-postman-live.log`, `test-postman-live-summary.json`.
- CLI báo chưa login nhưng collection local vẫn chạy exit 0. Không cần login hoặc xuất dữ liệu lên workspace để có kết quả trên. Workflow generator tự tạo trỏ tới spec scratch đã được gỡ riêng sau khi đối chiếu nội dung; `.postman/resources.yaml` giữ nguyên.

## 3. Kết quả theo AC và vùng rủi ro

Hậu tố __ACn ở test cũ thuộc task 3.23; bảng dưới ánh xạ theo hành vi AC1–AC9 của 3.25.

| AC | Bằng chứng | Kết quả/giới hạn |
|---|---|---|
| AC1 | self_and_family_success_are_audited; family_history_rate_transitions; TC01/30/52/53 | Pass phần API/DB và HTTP Postman: payload contract, audit metadata tối thiểu; không thay bằng chứng Android. |
| AC2 | nhóm/ngày/biên, TC20–26/30–36/52 | Các biên -30−1µs/+30−1µs, +120/+1µs, grouping/timezone/idempotency/race đã chạy; vẫn có lỗi -30 hợp lệ trong TC20. Chưa đạt toàn AC. |
| AC3 | family_early_confirmation_counts_immediately và unit delay0; TC20/52 | **Fail BUG-3.25-01** ở cả date/medication qua API/DB. +10/+120/+1µs trong ca family mới Pass. Không gộp test cũ kỳ vọng loại liều sớm thành bằng chứng AC3 đạt. |
| AC4 | unlinked/missing_consents/sharing_off; patient_selector_tamper; auth; Postman | Pass API/DB: 403/no health/no-store + denied, patient chéo bị chặn sau đọc P thành công; auth 401. TC02–06/16–19/53. |
| AC5 | revoke health_data/family_sharing/sharing/unlink; Postman same bearer | **Pass** cả pytest và HTTP thật: ngay request kế tiếp 403, audit denied; không cache quyền. TC07–10/53. |
| AC6 | 16 family_adherence repository/controller/widget | **14 Pass/2 Fail**, BUG-3.25-02 offline/background. Đổi patient, clear/response muộn, refresh denied/network/401, logout/read-only đã có test. Manual lifecycle OS/cache bền và Android E2E chưa chạy. |
| AC7 | audit_permission_and_commit_failure; denied_audit_survives_rollback | **5 Pass**, PEP trước đọc, không trả sức khỏe khi lỗi quyền/audit/commit, denied bền sau rollback, dose_logs không đổi. TC11–15. |
| AC8 | TC37/38; contract/schema và schedule-stop/soft-delete test | Contract đã có /adherence, nhưng chưa đặc tả field/công thức tỷ lệ đúng giờ riêng, xung đột/đối soát; phần đó vẫn Pending. Không tự tạo oracle. |
| AC9 | spec/workbook/log và contract/Postman local | Pass phần truy vết và workbook: 53 ID/trạng thái nhất quán, giữ 20 sheet cũ. Chưa nghiệm thu toàn PB21 do lỗi và E2E còn thiếu. |

Kịch bản chất lượng bắt buộc: cross-patient, thiếu consent, thu hồi ngay, fail-closed và denied rollback đã Pass; retry client_uuid và Worker race một liều đã Pass trong các test lịch sử hiện có. Không thay engine/rule tương tác nên không có thay đổi golden-scenario oracle.

## 4. Các kiểm tra đã thực thi

Lệnh backend từ `backend/`, tiền tố `.venv/Scripts/python.exe -X utf8 -m`; log/XML cùng tiền tố trong evidence.

| Bộ | Lệnh / phạm vi | Kết quả thực tế |
|---|---|---|
| Lịch sử trước bổ sung | pytest hai file test_adherence_history_api.py/access.py | **60 Pass**, 0 Fail/skip; 16.41s; exit 0. test-contract-history.log/xml. |
| Contract + unit/PEP/registry | pytest test_contract_adherence, test_get_adherence_history, test_adherence_history, test_access_authorize, test_adherence_history_http, health_route_enforcement | **138 Pass/2 Fail**, 6.40s; exit 1. Hai Fail unit xác nhận sớm; riêng contract 20 Pass. test-contract-targeted.log/xml. |
| Toàn unit/architecture | pytest tests/unit tests/architecture -q --continue-on-collection-errors -p no:cacheprovider --tb=short --junitxml=../work/3.25/evidence/test-contract-unit.xml | **1353 Pass/32 Fail, 0 collection error**, 64.85s, 8 warning; exit 1. |
| Toàn integration | pytest tests/integration -q --continue-on-collection-errors -p no:cacheprovider --tb=short --junitxml=../work/3.25/evidence/test-contract-integration.xml | **1083 Pass/18 Fail/1 XPASS**, 473.07s, 5859 warning; exit 1. Suite được collect trước khi thêm tám ca mới dưới đây. |
| Lịch sử cuối, gồm test mới | Từ root: pytest backend/tests/integration/test_adherence_history_api.py backend/tests/integration/test_adherence_history_access.py -q -p no:cacheprovider --tb=short --junitxml=work/3.25/evidence/test-contract-history-final.xml | **66 Pass/2 Fail**, 16.16s; exit 1. Tám ca mới gồm 6 Pass/2 Fail xác nhận sớm; không có skip. |
| Family Mobile liên quan | dart flutter_tools.snapshot test --no-pub --reporter json, ba file family_adherence_* | **14 Pass/2 Fail**, exit 1. test-contract-mobile.jsonl và stderr.log. Không chạy lại toàn Flutter vì lượt này chỉ đổi contract và test API. |
| Postman HTTP thật | collection run ... -e environment-runtime --no-report-events | **14 request/75 assertion Pass**, 9 lượt exit 0; DB effects cũng kiểm. test-postman-live.log/summary.json. |
| Lint/format | ruff check và format cho file integration; Postman lint/script syntax; git diff --check | Ruff check Pass, đã format file test; Postman 0 issue và 8 script compile; diff check không có whitespace error. |

- XML integration ghi XPASS như success nên đếm máy là 1084 success, không phải 1084 passed sạch. Marker xfail của ca auth dose batch đã có từ trước; không thêm/xóa skip/xfail/retry trong lượt này.
- 18 Fail full integration nằm ngoài nhóm lịch sử: alert dispatch (3), dose timestamp (1), notification snapshot/access (3), mobile login/profile validation (10), profile GET (1). Có log assertion; chưa điều tra baseline/root cause để gán thành lỗi mới 3.25. Một số lỗi auth provider có thể phụ thuộc môi trường local; không kết luận toàn suite không flaky.
- 32 Fail unit gồm hai ca sớm của task và 30 ca ngoài phạm vi (device token/catalog/notification/profile/OpenAPI, trong đó sáu auth profile). Không đồng bộ các API khác hoặc nới test để báo xanh.
- Không chạy lại full integration sau khi thêm tám ca vì chỉ thêm test, không đổi sản phẩm; đã chạy cả hai file lịch sử sau chỉnh sửa. Phân biệt hai lần collect như bảng, không báo suite tổng đã chứa các ca mới.

## 5. Bộ test case Excel

- Spec: `testcases.json`; task: `testcases.xlsx`; tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`.
- Một chức năng FADH, sheet `Lịch sử tuân thủ người thân`; giữ toàn bộ ID cũ, thêm TC52 (family rate transition) và TC53 (Postman HTTP/DB). Mười hai Pending cũ nay có test API/DB đầy đủ và chuyển Pass; không có xung đột Pass/Fail của tester.
- `testcase_xlsx.py validate 3.25`, `build 3.25`, `merge 3.25` đều exit 0; log `test-contract-testcase-xlsx.log`. Chỉ script chuẩn ghi XLSX.
- **53 ca: 44 Pass, 3 Fail, 6 Pending**. Pending TC37/38 (AC8 chưa đủ đặc tả), TC39/42/43/44 (manual OS/cache bền/Android journey); actual để trống. Widget không thay OS/E2E.
- Bug Report ba dòng BUG-FADH-20/40/41 tương ứng **hai lỗi sản phẩm**: 20 là BUG-3.25-01; 40/41 là BUG-3.25-02.
- Đối chiếu spec/task/master: ID/result/bước R4 khớp; 20 sheet chức năng khác giữ values/formulas/styles/formats/merges/panes/chart/image counts. Log `test-contract-workbook-verify.log`.
- Đã render và xem vùng quyền truy cập, hai biên BVA, hai ca mới, totals và Report; nội dung đọc được. Artifact-tool recalculate cho 44/3/6/53; đổi thử một Pending thành Pass trong bộ nhớ cho 45/3/5/53 rồi khôi phục; không export đè file chuẩn. `test-contract-workbook-render.log`, ảnh PNG tương ứng. Không kiểm bằng native Excel.

## 6. Lỗi sản phẩm còn mở

### BUG-3.25-01 · Medium · Task sở hữu 3.23

Lịch 08:00, patient xác nhận hợp lệ 07:30. POST nhận và DB có dose_log; family GET ngay cùng thời điểm trả 200 đúng schema, có audit allowed nhưng total/taken/counted=0 và rate=null thay vì 1/100. Hai ca API mới và hai ca unit Fail. Domain/SQL reader cùng lọc scheduled_at<=as_of; đây là loại liều khỏi lịch sử, chưa có bằng chứng mất dose_log. Contract gốc còn mô tả chỉ liều đến giờ, khác ngoại lệ AC3; task sản phẩm cần xử lý đồng bộ nghiệp vụ, SQL/domain, contract và các kỳ vọng cũ. Giữ test mới đỏ trước/xanh sau, không sửa sản phẩm ở task test này. Evidence test-contract-history-final và unit.

### BUG-3.25-02 · High · Task sở hữu 3.24

Offline/background vẫn còn bốn Text Thuốc A sau trigger; 2/16 widget test Fail lại. Screen chỉ refresh khi resumed; app offline callback chỉ clear FamilyAlertController, chưa clear family history. Controller có generation/clear nhưng chưa được nối đúng sự kiện. Chưa có bằng chứng dữ liệu thật bị lộ hoặc truy cập chéo; vi phạm AC6/QD-29 vẫn chặn nghiệm thu. Evidence test-contract-mobile.jsonl. Native OS kiểm sau khi có fix/runner.

## 7. Phát sinh, scope và bàn giao

- `scope.py 3.25 --stage test` **exit 1**, log `test-contract-scope-final.log`: backend integration và workbook đúng vùng; **15 file contract/Postman ngoài phạm vi plan cũ**. Không báo scope Pass hoặc sửa checker/nhánh/artifact approved để né. Mười lăm file này chính là mở rộng người dùng đã yêu cầu trực tiếp ở mục 1; không còn câu hỏi xin phép cùng hành động. Khi chốt quy trình review, người duyệt cần ghi nhận phạm vi bổ sung trong artifact qua reopen đúng quy trình; agent không tự sửa artifact approved.
- CLI spec generator từng tạo `.postman/workflows.yaml` trỏ spec scratch; đã đọc/đối chiếu rồi xóa riêng file mới này, giữ resources.yaml cũ. Không có thay đổi .postman còn lại. Các lỗi lint URL/query và escaping trong bản nháp đã sửa trước live run; log đầu giữ lại, kết quả cuối là lint-final/script-syntax/live.
- Không sửa code sản phẩm, contract API khác, migration, frontend hoặc tests E2E. Chỉ file test integration trong backend có delta mới; contract một file và Postman local được mở rộng theo yêu cầu. Không commit/push/bump gitlink.
- Các artifact đã duyệt 01/03/04 giữ nguyên SHA256 so với baseline. Test-stage gate vẫn cho phép; approval không được dùng để biến các ca Fail/Pending thành nghiệm thu.

## Bước tiếp theo

1. Owner 3.23 xử lý BUG-3.25-01 và bất đồng mô tả contract/ngoại lệ AC3; owner 3.24 xử lý BUG-3.25-02. Sau fix chạy lại các ca đỏ cùng API/PEP/DB liên quan; không bỏ assertion mới.
2. Hoàn tất AC8 theo đặc tả thật và P7 Android host runner/lifecycle OS, hành trình chọn patient. Contract không còn là blocker của các ca HTTP đã chạy; không tiếp tục ghi “thiếu /adherence”.
3. Giữ 05 draft, chưa nghiệm thu toàn task vì High còn mở. Khi đủ điều kiện, người duyệt chạy `python .agents/scripts/gate.py approve 3.25 test` trong terminal của họ; agent không chạy. 06-review cũ cần review lại sau đợt test mới; không bắt đầu giai đoạn review trong lượt này.
4. Chưa commit: `api_contract/openapi.json`, backend test integration, Postman mới, workbook docs và `work/3.25/` bị ignore. Commit hiện có của frontend a147ed4 giữ nguyên. Chỉ đề xuất lưu khi được yêu cầu: commit contract trước, backend test, docs, Postman/artifact ở superproject; không stage scratch. Gitlink chỉ bump sau khi commit submodule đã push và xác minh remote.
5. Lệnh đề xuất cho phần đang dở: `git -C api_contract add -- openapi.json`; `git -C backend add -- tests/integration/test_adherence_history_api.py`; `git -C docs add -- "Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx"`; `git add -f -- work/3.25/05-test-report.md work/3.25/testcases.json work/3.25/testcases.xlsx work/3.25/evidence`; thêm có chủ đích thư mục `postman/` rồi commit từng repo bằng Conventional Commits và Refs: 3.25. Đây là đề xuất, chưa thực thi; không stage gitlink/scratch tự động.

Cập nhật 2026-10-25 16:54 +0700, Codex. Tiếp tục bằng `continue task 3.25`, đọc gate và báo cáo hiện tại. Bàn giao theo wf-handoff.
