---
task: 4.12-ocr-text-normalization-catalog-index
stage: test
owner: phucnguyenngoc
started_at: 2026-10-30
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-30 14:06 +0700
content_hash: sha256:15eccd7a8701fba2
inputs:
  01-requirement.md: sha256:af09eb8e3be07716
  03-plan.md: sha256:1561587391291ad5
  04-impl-notes.md: sha256:524fa01907d961a8
---

# 4.12 · Test giữ dòng OCR, gom cụm và tra cứu catalog bằng index PostgreSQL

Hoàn tất P9–P11 theo 01/03 mới đã duyệt. **23 AC có bằng chứng, 50 test case Pass, 0 Fail, 0 Pending trong phạm vi task**. Không phát hiện lỗi sản phẩm mới của 4.12 qua các kiểm tra đã chạy. Toàn backend chưa xanh: full unit/architecture còn30 fail và full integration còn18 fail/1 XPASS; đã tái hiện đúng hai tập fail trên source HEAD nguyên bản trong lượt này.

Báo cáo trước đổi phạm vi lưu tại `evidence/test-refresh-report-before.md`. Không dùng kết quả cũ để nghiệm thu yêu cầu mới. 06-review.md hiện là draft, còn nội dung review lịch sử; đã giữ nguyên file này và chưa thực hiện review mới.

## 1. Môi trường và phạm vi

- Windows/PowerShell; backend Python3.14.7 trong `backend/.venv`, pytest9.1.1; source HEAD `2439aa66c914809d08c017f09379e03d0144da83`. Workflow dùng `C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe` vì alias WindowsApps không chạy; workbook dùng bundled Python có openpyxl và Artifact Tool để QA.
- Superproject/backend/docs đều ở `feat/4.12-ocr-text-normalization-catalog-index`, không detached. Giữ toàn bộ thay đổi task từ implement; không stash/reset/stage/commit/push hoặc đổi gitlink.
- Docker Desktop local được khởi động ẩn. Supabase CLI2.120.0 tại `C:/Users/admin/AppData/Local/npm-cache/_npx/aa8e5c70f9d8d161/node_modules/@supabase/cli-windows-x64/bin/supabase.exe`; project_id `DrugTime-backend`; PostgreSQL17 local tại127.0.0.1:54322. Fixture giữ local-host guard và đăng nhập reader bằng api_role; không DB deploy/chung. CLI start đã lọc dòng credential trước ghi log.
- Đã chạy `supabase start`, `supabase db reset --local`, exit0; áp dụng đủ migration tới20261030025813. CLI báo thiếu seed.sql; tests tự tạo dữ liệu tổng hợp. Log `evidence/test-refresh-supabase-start.log`, `test-refresh-db-reset.log`.
- Chỉ sửa `backend/tests/integration/test_catalog_index.py` và workbook tổng trong docs. Mọi artifact đầu vào được giữ nguyên. Artifact/spec/XLSX/evidence/scratch mới chỉ ở work task. 253 hash source/unit/migration/01/03/04/06 giữ nguyên (`test-refresh-protected-before.json`, `test-refresh-protected-audit.log`, `test-refresh-final-audit.json`).

## 2. Kết quả theo tiêu chí chấp nhận

U = file trong `backend/tests/unit/`; I = file trong `backend/tests/integration/`. Kết quả unit/architecture lấy từ `test-refresh-unit.xml`; integration từ `test-refresh-integration.xml`. Các invocation này chạy thật trong lượt test này, không dùng pass lịch sử.

| AC | Test/bằng chứng chính | Kết quả |
|---|---|---|
| AC1–AC2 | U/test_catalog_ocr_normalization.py::test_line_sources_and_clean_key; raw/offset/LF/CRLF/CR/trống/NFC/NFD/clean/key/idempotent | Pass |
| AC3 | test_names_and_confusables, test_whitelist_and_eligibility: B12/D3/5mg/O0l1/Metforrnin, không mở rộng Met. | Pass |
| AC4–AC5 | test_strength_whole_spans, test_combination_is_one_vote_with_ordered_parts_and_uncertain_tail: decimal/nồng độ/phối hợp/%/thứ tự | Pass |
| AC6 | test_invalid_unsupported_whole_group, test_valid_and_corrupted_groups_remain_separate, test_equal_name_different_signatures_and_ambiguous_line | Pass |
| AC7–AC8 | Whitelist/partial_registration/eligibility và cluster fragment guard: lọc sau trích, không xóa nhầm tên/số, không query mảnh thiếu context | Pass |
| AC9 | U/test_catalog_ocr_clusters.py exact repeats/every_line_at_most_once; I/large_small_clusters_query_dedup: count/nguồn không nhân | Pass |
| AC10 | ratio dưới/bằng/trên; complete-link; sáu hoán vị thiếu strength/16mg/160mg; số/substring/suffix/prefix65%; bốn nhãn raw thật | Pass |
| AC11 | exact support thắng dài ở probe T0.65; production T0.86 giữ singleton nếu không đủ giống; sort/count ổn định và giữ cụm nhỏ | Pass |
| AC12–AC14 | evidence_retains_minority_unknown_and_repeated_occurrences, combination/signature/unique_missing_attachment: một phiếu/canonical/line, giữ occurrence/thiểu số/hòa/unparsed/strength-only | Pass |
| AC15 | Unit non-string cố định TypeError không echo; I/test_ineligible_inputs_issue_no_catalog_read: 0 SQL với rỗng/noise/SDK/5mg/Met. | Pass |
| AC16 | DB reset sạch; upgrade clone có dữ liệu; I/test_expression_indexes_ready_and_used_in_eligibility_probe: ba GIN valid/ready và EXPLAIN đúng truy vấn | Pass, chi tiết mục4b |
| AC17 | I/test_sources_preserve_raw_nulls_ids_and_explicit_links; 12 ca bound literal ba nguồn: ID cùng tên/raw/null/strength/form, alias đủ nguồn/link thật/active only | Pass |
| AC18 | I/distinct_id_budget: 199/200/201 ID từng nguồn, hai alias/ID; large_small_clusters:60 hit+cụm nhỏ, dedup trong lượt; unit truncated riêng | Pass |
| AC19 | I/medication_commits, alias_and_link_commits: thêm/sửa/gỡ/restore/commit; ba ca ngắt đúng PID connection riêng ở nhánh0/1/2; unit iterator/lỗi không fallback | Pass |
| AC20 | 3 unit sync+10 unit search+19 CRUD+15 architecture; toàn43 integration search hai route, giữ expected cũ | Pass |
| AC21 | Unit I/O/log/writer guard; I/READ ONLY api_role và anon/authenticated không SELECT; bound query, ACL/RLS/EXECUTE upgrade không đổi | Pass |
| AC22 | U/test_two_facade_callers_fresh_uow_no_snapshot và DTO immutable: caller4.13/4.15 mô phỏng dùng cùng facade, UoW mới | Pass |
| AC23 | Bốn nhãn owner_confirmed/từ2 raw; unit regression; `test-refresh-cluster-calibration.log/.json`:49 raw giữ nguồn, thử5 ngưỡng chốt0.86 | Pass trong tập nhỏ, không là accuracy ngoài tập |

109 normalization +28 clustering +29 query/facade +3 sync +10 search +19 CRUD +15 architecture = **213 invocation liên quan đều pass** trong full unit. Full integration có **31 test catalog mới +43 search =74 pass**, không skip. Không phải đếm testcase Excel như số invocation tự động.

## 3. Kịch bản chất lượng đã phủ

| Kịch bản áp dụng | Bằng chứng | Kết quả |
|---|---|---|
| Schema/index áp dụng từ DB sạch và trên dữ liệu cũ | Reset toàn migration; upgrade clone local có thuốc/hoạt chất/alias/link; so payload/ACL/RLS/policies/function grants | Pass |
| Thuốc gỡ không chọn mới, không suy liên kết alias | Active predicate, explicit link và duplicate-ID fixtures | Pass |
| Freshness không snapshot/TTL/rebuild | Đọc bằng UoW mới cùng process sau commit thuốc/alias/link; object cũ giữ nguyên | Pass |
| Lỗi đọc fail thay vì trả dữ liệu cũ/một phần | Ngắt PID riêng trước mỗi nhánh0/1/2, DBAPIError; unit iterator sau hit | Pass |
| Catalog vượt limit cũ, đủ nguồn và cụm nhỏ | 60 hit;199/200/201 ID mỗi nguồn; hai alias/ID, truncated/dedup/source line | Pass |
| Ranh giới module và I/O OCR | Toàn15 architecture; guard unit; READ ONLY lookup | Pass |

Task không thêm/chạm endpoint dữ liệu patient, consent/caregiver, liều hoặc engine tương tác. Vì vậy không thêm test cross-patient/rút quyền/dose race riêng vào task. Các test liên quan hiện có vẫn nằm trong full integration đã chạy; không suy từ đó rằng các lỗi nền ngoài task được khắc phục.

## 4. Lệnh và toàn bộ suite

Các lệnh backend chạy tại `backend`, output `2>&1 | Tee-Object ../work/<task>/evidence/<log>`; workflow/script scratch chạy ở gốc. Dùng Python tuyệt đối mục1 tương ứng.

| Lệnh | Kết quả/exit | Log evidence |
|---|---|---|
| gate.py task test | exit0 sau user reopen | test-refresh-gate.log |
| .venv/Scripts/python.exe -m pytest -p no:cacheprovider tests/unit tests/architecture --tb=short --junitxml=... | **1523 passed,30 failed**,0 skip,8 warnings;70.46s; pytest exit1 | test-refresh-unit.log/.xml |
| .venv/Scripts/python.exe -m pytest -p no:cacheprovider tests/integration --tb=short --junitxml=... | **1127 passed,18 failed,1 XPASS**,0 skip,5860 warnings;498.45s; pytest exit1 | test-refresh-integration.log/.xml |
| scratch/run_test_refresh_baseline_unit.py | Source HEAD nguyên bản;86 pass/30 fail; exact failure set30=30,0 introduced; pytest exit1 | test-refresh-unit-baseline.log; test-refresh-unit-baseline-results.json |
| scratch/run_test_refresh_baseline_integration.py --failed-only | Tái chạy đúng18 nodeid trên source HEAD:18 fail,0 skip; exact failure set18=18,0 introduced; pytest exit1 | test-refresh-integration-baseline.log; test-refresh-baseline-integration.xml; test-refresh-integration-baseline-results.json |
| scratch/compare_lint_baseline.py (ruff check . JSON rồi đối chiếu signature source HEAD) | Ruff exit1 vì31 finding có sẵn; audit exit0,0 mới | test-refresh-lint-baseline.log |
| ruff check --no-cache tests/integration/test_catalog_index.py | exit0 All checks passed | test-refresh-lint-integration.log |
| scratch/test_refresh_calibration.py | exit0,4 nhãn thật+4 synthetic;49 raw bảo toàn nguồn/unique member;T0.86 | test-refresh-cluster-calibration.log/.json |
| scope.py task --stage test | **exit1**,12 path kế thừa từ implement; xem mục7 | test-refresh-scope.log |
| scratch/audit_test_refresh.py | exit0;50 ca/23AC/EP/decision;24 sheet XML giữ nguyên;253 hash không đổi; no bad refs/error cells | test-refresh-final-audit.log/.json |

30 unit fail thuộc contract thiếu path/semantics và invalid-auth profile401/422. 18 integration fail thuộc alert auth401, dose timestamp, notification schema, mobile-login validation và profile schema; toàn bộ tái hiện trên source HEAD trong lượt này. Baseline integration chỉ chạy failed-only18 ca, **không phải toàn baseline integration**. XPASS là marker xfail hiện hữu ở dose/auth; chưa sửa marker hay nới expected. 5860 warning chủ yếu là deprecation/Pydantic/response schema trong test nền, giữ nguyên output để review; không coi warning count là số lỗi mới.

### 4b. Migration và planner

- Chỉ index mới `20261030025813_catalog_ingredient_alias_search.sql`; migration cũ không đổi theo hash. Reset sạch exit0.
- `scratch/test_refresh_upgrade.py`: dump **toàn schema local** sang DB local dùng một lần; chỉ bỏ index mới trong clone để tạo baseline tương đương trước migration; thêm bốn dòng tổng hợp thuốc/hoạt chất/alias/link; áp dụng đúng file migration. Không sửa migration history/schema của DB gốc. Xóa đúng DB thử trong finally.
- So trước/sau:75 relation ACL/RLS,9 function permission rows,74 policies và4 payload giữ nguyên. Alias GIN valid/ready, đúng catalog_search_key(alias_text)/gin_trgm_ops. Log `test-refresh-migration-upgrade-final.log/.json`. Lần đầu restore schema bằng postgres không SET ROLE supabase_admin được; clone được dọn, chạy lại qua tài khoản quản trị nội bộ local thành công; không thay grant sản phẩm.
- Planner ban đầu chọn B-tree active-name trên catalog nhỏ/bulk GIN pending list. Test cuối flush pending list, ANALYZE hai bảng trên DB local riêng, rồi dùng SET LOCAL enable_seqscan=off và enable_indexscan=off trong UoW rollback để chứng minh **khả năng dùng** ba expression GIN của chính câu SQL adapter. Không đổi setting production, không bắt natural plan dùng GIN và không là benchmark/SLO.
- Migration GIN transactional có thể khóa writer/tốn disk; triển khai vẫn cần cửa sổ bảo trì. Task không thêm bảng/constraint/log hoặc grant nên không có RLS/append-only trigger/ràng buộc mới cần nghiệm thu.

## 5. Bộ test case Excel

Script dự án là đường ghi XLSX duy nhất. `testcase_xlsx.py validate`, `build`, `merge` đều exit0; log `test-refresh-testcase-validate-final.log`, `test-refresh-testcase-build-final.log`, `test-refresh-testcase-merge.log`.

- Spec: `testcases.json`; file task: `testcases.xlsx`; file tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`.
- Mỗi Pass có actual và node/log của chính lượt test này; cả23 AC,9+4 lớp EP và4 rule mỗi bảng quyết định có tham chiếu; có biên ratio dưới/bằng/trên, prefix65%, budget199/200/201. Không có giới hạn trên strength hoặc dải độ dài chưa được yêu cầu để tự đặt min/max.

| Chức năng | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| OCRNORM – Chuẩn hóa dòng và gom cụm |32|32|0|0|
| CATINDEX – Tra cứu DB |18|18|0|0|
| Tổng task |50|50|0|0|

- Không có ca Pending cần chạy tay hoặc Bug Report mở của4.12. Workbook tổng giữ17 Fail và34 Pending của chức năng khác; tổng toàn workbook701 Pass/17 Fail/34 Pending được kiểm độc lập, không gọi toàn workbook pass.
- Giữ ID ca còn đúng, bỏ17 ID lỗi thời và không tái dùng; danh sách tại `test-refresh-retired-case-ids.json`. Merge báo đúng17 cảnh báo Pass cũ→không còn; người dùng đã chọn **“Dùng bộ50 ca mới và giữ lịch sử trong backup”** trước merge (`test-refresh-workbook-decision.md`). Không bỏ qua cảnh báo hoặc gán Pass cho hành vi cũ đã bỏ.
- Backup đầy đủ file tổng cũ: `evidence/test-refresh-workbook-before.xlsx`; spec cũ: `test-refresh-testcases-before.json`; report cũ: `test-refresh-report-before.md`.
- QA: so byte XML của24 worksheet không thuộc task và native chart/data validation/freeze/merge; giữ thứ tự/tên sheet. So50 ID/actual/status của cả hai workbook với spec. Artifact Tool recalc/inspect/render hai sheet+Report; scan không lỗi công thức; thay H9 trong bộ nhớ làm tổng50→49 rồi khôi phục, không export bằng Artifact Tool. Log `test-refresh-workbook-final-qa.log`, `test-refresh-master-qa.log`; PNG ở scratch. Chưa mở Microsoft Excel native, nên không tuyên bố đã kiểm bằng Excel desktop.

## 5b. Lỗi sản phẩm tìm thấy

Không phát hiện lỗi sản phẩm mới của4.12 qua bộ kiểm này. Những fail của full backend đã được đối chiếu nguồn HEAD như mục4, giữ ngoài bộ Bug Report task thay vì đổi thành Pass hoặc sửa ngoài plan.

## 6. Lỗi kiểm thử, hạ tầng và skip

- Lượt targeted đầu:70 pass/4 fail; ba ca SQL literal gửi query_key còn uppercase, khác tiền điều kiện adapter; sửa fixture lowercase. Một ca EXPLAIN sai giả định planner luôn chọn GIN. Lượt targeted thứ hai73 pass/1 fail; sau thống kê/pending-list/controlled eligibility probe, probe pass và full suite cuối có toàn31+43 pass. Giữ `test-refresh-targeted.log/.xml`, `test-refresh-targeted-final.log/.xml`, `test-refresh-index-probe.log/.xml`, không ghi đè thành log pass.
- Lỗi Unicode của script chỉnh sửa được sửa bằng UTF-8; ruff E501 của test mới đã sửa. Không sửa code sản phẩm hoặc expected nghiệp vụ để test xanh.
- Full integration chạy8m18 do budget OTP300s của test login hiện hữu; không tăng retry/timeout/budget hoặc bỏ qua test. Không có skip;1 XPASS đã nêu riêng.
- Sandbox ban đầu chặn ghi evidence; retry escalation đã được tự động duyệt trong phạm vi workspace. Không còn action bị automatic approval từ chối/chặn.

## 7. Phát sinh và kiểm phạm vi

`scope.py --stage test` exit1 vì kiểm **toàn working tree chưa commit**, bao gồm12 path backend implement đã được duyệt:6 source,1 migration,1 fixture và4 unit. Đây là các thay đổi kế thừa được01/03/04 ghi nhận, không phải delta của lượt test. Không reset/commit ép hoặc sửa scope/gate để che exit. Snapshot253 hash source/unit/migration/input giữ nguyên, file fixture không được sửa, integration/workbook thuộc đúng bảng03. Phạm vi sửa thực tế lượt này:1 integration +1 workbook tổng +work task, không có file sản phẩm mới ngoài plan.

Không sửa01/03/04/06 hoặc tự approve. Gate cuối lưu tại `test-refresh-gate-final.log`. Các gitlink api_contract/backend/docs/frontend/tests khác sẵn được giữ nguyên. Không tạo PR/commit/push trong lượt test.

## Bước tiếp theo

- P9–P11 hoàn tất; chờ người duyệt đọc05/diff/evidence và tự duyệt test theo AGENTS.md/wf-test. Không còn câu hỏi nghiệp vụ hoặc test case Pending của task.

```powershell
& 'C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe' .agents/scripts/gate.py approve 4.12-ocr-text-normalization-catalog-index test
```

- Gate cuối xác nhận01/03/04 approved,05 draft và06 draft. Không cần reopen review thêm; sau khi duyệt test mới được bắt đầu review.
- Sau duyệt, lượt riêng dùng wf-next để review độc lập. Cần ít nhất một người khác approve PR theo DoD, không suy từ task testcase Pass rằng toàn backend đã xanh.
- Đề xuất commit/push artifact+evidence khi người dùng yêu cầu để máy khác tiếp tục được; không stage scratch. Backend/docs commit và push trước; superproject chỉ bump tới SHA đã push. Hiện chưa commit backend integration/workbook và code task kế thừa; work bị ignore cần add -f có chọn lọc:

```powershell
git add -f -- work/4.12-ocr-text-normalization-catalog-index/05-test-report.md work/4.12-ocr-text-normalization-catalog-index/testcases.json work/4.12-ocr-text-normalization-catalog-index/testcases.xlsx work/4.12-ocr-text-normalization-catalog-index/evidence/
git diff --cached --stat
git commit -m 'test(catalog): record refreshed OCR retrieval test evidence'
```

- Cập nhật lần cuối:2026-10-30, Codex.
