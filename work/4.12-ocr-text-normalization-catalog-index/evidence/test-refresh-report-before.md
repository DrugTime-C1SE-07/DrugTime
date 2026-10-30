---
task: 4.12-ocr-text-normalization-catalog-index
stage: test
status: draft
---

# 4.12 · Test lại sau sửa R1

Kết quả dưới đây thuộc **lượt test sau reopen implement/test ngày 28/10/2026**. Bản 05 trước sửa được giữ ở `evidence/test-R1-report-before.md`; các log cũ vẫn giữ nguyên. Chỉ 05, test integration trong plan, spec/workbook và evidence/scratch được cập nhật. Không sửa 01/03/04 đã approved hoặc kết luận review cũ trong 06.

## 1. Môi trường

- Gate test exit 0: `evidence/test-R1-gate.log`. Đầu vào 01/03/04 approved; người dùng đã reopen test trước lượt này.
- Superproject/backend/docs ở `feat/4.12-ocr-text-normalization-catalog-index`. Backend HEAD `2439aa66c914809d08c017f09379e03d0144da83`; giữ base và ngoại lệ scope đã xác nhận từ lượt trước.
- Backend Python `.venv/Scripts/python.exe` 3.14.7, pytest 9.1.1, Ruff 0.16.10. Workflow dùng Python tuyệt đối `C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe`; Excel/QA dùng runtime bundled theo loader. Alias WindowsApps không hoạt động.
- Supabase CLI 2.120.0 ở `C:/Users/admin/AppData/Local/npm-cache/_npx/aa8e5c70f9d8d161/node_modules/@supabase/cli-windows-x64/bin/supabase.exe`. Đã chạy `supabase start`, `supabase db reset --local` từ backend, cả hai exit 0, chỉ Supabase local `DrugTime-backend`/PostgreSQL `127.0.0.1:54322`; fixtures vẫn có local-host guard. Logs: `test-R1-supabase-start.log`, `test-R1-db-reset.log` trong evidence.
- Migration sạch tới `20261021115000_access_logs_admin_self_denied.sql`; CLI cảnh báo thiếu seed.sql, test tự tạo fixture. Dòng status chứa credential được che trước khi ghi log. Không đổi schema, grant, service config hoặc dữ liệu deploy.
- Mọi lệnh dưới đã chạy trong lượt này; output lưu bằng `2>&1 | Tee-Object`, kiểm exit code; XML ghi invocation để truy vết. Thư mục log là `work/4.12-ocr-text-normalization-catalog-index/evidence/`.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Kiểm chứng thực tế | Kết quả |
|---|---|---|
| AC1 | Unit normalizer/index NFC/NFD, đ/Đ, hoa/thường | Pass |
| AC2 | Unit multiline/noise/whitespace/idempotence | Pass |
| AC3 | B12/D3/O0l1 và 6 ca bảo vệ Long/Log/Ong + metadata sau sửa detector | Pass |
| AC4 | Unit format đơn MVP, dấu phẩy/chấm, spacing; không quy đổi | Pass |
| AC5 | Unit nồng độ/phối hợp/phần trăm giữ cấu trúc và thứ tự | Pass |
| AC6 | 18 ca R1 normalizer + 4 unit index + 12 integration nguồn DB; 0/âm/ngoài MVP/nhóm cạnh tranh vẫn giữ toàn text | Pass |
| AC7 | Rỗng/noise/non-string, TypeError cố định không echo input | Pass |
| AC8 | Raw/null/ID/mapping, cùng quy tắc normalize; R1 qua cả ba trường name/ingredient/strength từ PostgreSQL | Pass |
| AC9 | ID trùng khóa được giữ; sort và collection/DTO bất biến | Pass |
| AC10 | I1 >50 active và deleted, I2 catalog rỗng rollback, I5 lỗi PostgreSQL thật | Pass |
| AC11 | I3 thay đổi đã commit/khôi phục thấy ở UoW mới cùng process; I4 snapshot ổn định; I5 lỗi không fallback | Pass |
| AC12 | Ingest/search/CRUD + 15 architecture; 43 search integration trên hai route | Pass phần catalog; full suite ngoài task có lỗi nền như mục 4 |
| AC13 | Unit guard I/O/writer/caplog/capsys; loader chỉ SELECT | Pass; không nghiệm thu lưu ảnh/OCR thật hoặc dữ liệu patient ngoài phạm vi |
| AC14 | Hai consumer tổng hợp dùng cùng facade, UoW riêng | Pass; chưa tích hợp endpoint/UI thật 4.13/4.15 |

Trong `backend/tests/integration/test_catalog_index.py`, bổ sung **1 test parametrized, 12 invocation**: `test_corrupted_strength_from_database_stays_unparsed__AC6_AC8`. Sáu dạng `O.5g`, `o,5 G`, `O.5 g`, `l0mg`, `L0 MG`, `l0 mg` đứng trước/sau `500mg`. Tạo catalog tổng hợp và đọc qua api_role; đối chiếu raw/ID/mapping và khóa/status/None/parts rỗng trên tên, hoạt chất, hàm lượng. Expected được viết độc lập, không gọi normalizer sản phẩm để tạo expected. Giữ nguyên 5 test integration đã có, fixture chung và mọi file sản phẩm/unit.

- Targeted: `python -m pytest -p no:cacheprovider tests/integration/test_catalog_index.py tests/integration/test_catalog_search.py --junitxml=../work/4.12-ocr-text-normalization-catalog-index/evidence/test-R1-catalog-integration.xml` → **60 passed, 1 warning in 13.20s**, exit 0. Có 17 index + 43 search; 0 skip. Log/XML cùng prefix `test-R1-catalog-integration`.
- Unit/architecture: `python -m pytest -p no:cacheprovider tests/unit tests/architecture --junitxml=../work/4.12-ocr-text-normalization-catalog-index/evidence/test-R1-unit-architecture.xml` → **30 failed, 1494 passed, 8 warnings in 64.86s (0:01:04)**, exit 1. Toàn bộ 184 invocation thuộc nhóm normalizer/index/ingest/search/CRUD/architecture pass, gồm 28 regression/ca bảo vệ R1; 0 skip. Log/XML cùng prefix `test-R1-unit-architecture`.
- Unit baseline: chạy `backend/.venv/Scripts/python.exe -X utf8 work/.../scratch/run_baseline_contract_tests.py` với source HEAD nguyên bản trích vào scratch; kiểm import đúng nguồn và chưa có reader 4.12 → **86 passed, 30 failed**, 1 warning, 16.24 giây, exit 1. **Tập nodeid 30 fail trùng hoàn toàn** lượt unit hiện tại, 0 introduced/0 baseline-only. Log `test-R1-baseline-unit.log`, JSON outcome `test-R1-baseline-unit-results.json`. Không suy baseline chỉ từ số lượng.

## 3. Kịch bản chất lượng đã phủ

| Kịch bản áp dụng | Kiểm chứng | Kết quả |
|---|---|---|
| Không tái sử dụng snapshot giữa lượt | I3 A → commit thêm/sửa/gỡ → B → restore → C; UoW mới mỗi lần | Pass |
| Rỗng khác nguồn lỗi, không fallback snapshot cũ | I2 rollback và I5 ngắt đúng connection api_role riêng/NullPool | Pass |
| Giữ raw/ID/null, nhóm OCR chưa chắc chắn | I1/I3/I4, unit index và 12 ca DB R1 | Pass |
| Không tự biến O/l thành số hoặc chọn một nhóm hợp lệ khác | 18 unit normalizer, 4 unit index, 12 DB và 6 ca bảo vệ tên/metadata | Pass |
| Ranh giới module và search/ingest giữ nguyên | 15 architecture, unit catalog, 43 search integration | Pass |
| Không log/lưu/gọi dịch vụ ngoài với OCR | Guard I/O/writer + caplog/capsys từ fixture tổng hợp | Pass |

Không áp dụng PEP/consent/cross-patient/dose race/golden interaction riêng cho 4.12: không sửa endpoint patient, liều, engine tương tác hoặc schema. Full integration vẫn chạy các test sẵn có tương ứng, không suy pass từ bảng này.

## 4. Toàn bộ bộ test tích hợp và kiểm tra phạm vi

- Từ backend, thêm thư mục CLI vào PATH riêng process; `python -m pytest -p no:cacheprovider tests/integration --junitxml=../work/4.12-ocr-text-normalization-catalog-index/evidence/test-R1-integration.xml`.
- Kết quả: **18 failed, 1113 passed, 1 xpassed, 5860 warnings in 459.81s (0:07:39)**, exit 1; đã chạy đủ **1132 invocation**, 0 skipped. Log/XML: `test-R1-integration.log/.xml`. Cả 60 invocation index/search pass trong targeted và full suite. Không gọi toàn suite là pass.
- Tái hiện đúng tập fail integration bằng source HEAD nguyên bản: `backend/.venv/Scripts/python.exe -X utf8 work/.../scratch/run_baseline_integration_tests.py --failed-only` → **18 failed**, exit 1. Tập nodeid trùng hoàn toàn lượt full hiện tại, 0 introduced/0 baseline-only; không chạy toàn bộ baseline integration. Log/XML `test-R1-baseline-integration.log/.xml`, outcome `test-R1-baseline-integration-results.json`.
- Lint/format đúng test integration sửa: `python -m ruff check --no-cache tests/integration/test_catalog_index.py`; `python -m ruff format --no-cache --check tests/integration/test_catalog_index.py` → cả hai exit 0. Log `test-R1-index-lint.log`.
- Chạy Ruff toàn backend và so source HEAD bằng `scratch/compare_lint_baseline.py` → current 31 / baseline 31 / introduced 0; audit exit 0, bản thân Ruff exit 1. Log `test-R1-lint-baseline.log`.
- `scope.py 4.12-ocr-text-normalization-catalog-index --stage test` **exit 1**: integration test + workbook `[OK]`, 8 file implement chưa commit từ trước `[NGOÀI]`. Giữ nguyên ngoại lệ người dùng đã xác nhận: **“Chấp nhận ngoại lệ, giữ nguyên 8 file implement”**. Không sửa tool, giấu file hoặc gọi raw scope là pass. Log `test-R1-scope.log`.
- Audit SHA256 xác nhận **8/8 file implement không đổi** trong lượt test; loại đúng tập đã có để kiểm delta thì chỉ có integration test + workbook, đều trong bảng 03 và stage test. Audit `scratch/verify_test_R1.py stage` exit 0; log `test-R1-stage-delta.log`. Hash đầu `test-R1-implementation-before.json`, hash cuối 10 file code/workbook `test-R1-final-hashes.json`. 01/03/04 không sửa.

## 5. Bộ test case Excel

- Spec `testcases.json`; file task `testcases.xlsx`; file tổng `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`. Chỉ script dự án `testcase_xlsx.py` author XLSX; artifact tool dùng read-only để QA.
- `validate`, `build`, `merge` lượt cuối đều exit 0, không có cảnh báo xung đột kết quả. Log `test-R1-testcase-xlsx-final.log`. Mọi actual/status được cập nhật từ XML lượt test này, không giữ Pass chỉ dựa vào kết quả cũ.

| Chức năng | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| OCRNORM | 21 | 21 | 0 | 0 |
| CATINDEX | 18 | 18 | 0 | 0 |
| Tổng task | 39 | 39 | 0 | 0 |

- Giữ 35 ID cũ; thêm `TC-OCRNORM-20/21`, `TC-CATINDEX-17/18` cho R1. Đủ AC1–AC14, 17 lớp EP và 8 rule quyết định; BVA q 0/1/100/101, limit 0/1/50/51. Audit nodeid/XML exit 0: `test-R1-traceability-final.log`.
- **R1/High: retest pass, chờ review lại.** Lịch sử fail trước sửa ở 06 và `implement-R1-before.log` (giai đoạn implement trước, không phải lượt này); nguyên nhân detector bỏ sót tiền tố O/l được ghi trong comments và Report remarks. Bug Report hiện có **0 lỗi mở trong phạm vi task**, khớp 0 case Fail. Không chuyển 06 sang Đạt ở giai đoạn test. Lỗi nền ngoài task giữ riêng ở mục 5b, không đổi bug/kết quả của chức năng khác.
- Không có Pending cần người chạy trong phạm vi task. Camera/ảnh thật/matching/UI thuộc task khác và chưa được nghiệm thu tại đây.
- So trước/sau xác nhận **24 sheet chức năng khác giữ nguyên** giá trị/công thức/style/chiều cao/rộng/merge/freeze/chart/validation; không thêm/xóa sheet ngoài hai chức năng có sẵn. Hai workbook khớp 39 ID/actual/status và công thức không REF lỗi. `Report` tổng được dựng lại theo thiết kế script. Log `test-R1-workbook-qa-final.log`.
- Render các dòng R1/tổng/Report, xem ảnh thực tế; wrap và row height đọc được, điều kiện chuẩn bị test DB đúng. Artifact recalculation cho tổng **39/0/0**, executed/passed 100%, không tìm thấy lỗi công thức trong lượt scan. Log `test-R1-render-final.log`; ảnh ở scratch, không đề xuất commit. Không kiểm lại Microsoft Excel native; chart không được chỉnh, giới hạn preview Series1/2/3 đã ghi ở báo cáo trước vẫn giữ.

## 5b. Lỗi sản phẩm và giới hạn

Không phát hiện lỗi sản phẩm mới của 4.12 trong các ca đã chạy. R1 đã qua retest; việc xác nhận kết luận review thuộc giai đoạn review kế tiếp.

- **30 lỗi unit nền** đã tái hiện tại HEAD: 24 contract thiếu path/khác semantics của checkout api_contract hiện tại và 6 invalid-auth profile mong 401, thực tế 422.
- **18 lỗi integration nền** đã tái hiện tại HEAD: alert dispatch 3 (200/401), dose timestamp 1 (cắt phút/giữ giây), notification schema 3, mobile login 10 (newline/Unicode phone/NUL/profile boundaries), profile schema thêm email 1. Tập nodeid và traceback nằm trong log full/baseline lượt này; audit đối chiếu tập chính xác.
- **31 lỗi lint nền** giữ nguyên. Không sửa code/test/contract cũ để dọn các lỗi ngoài phạm vi. Việc khớp baseline chỉ chứng minh tập fail hiện tại có sẵn, không chứng minh mọi biên chưa viết test đều đúng.

## 6. Test không ổn định hoặc bị skip

- Targeted/unit/integration lượt cuối 0 skip, không tăng retry/timeout, không nới expected hoặc dùng mock thay DB thật. 1 XPASS từ marker xfail có sẵn ở `test_post_doses_batch_requires_authentication__AC9`; giữ nguyên marker/test cũ và không coi là test mới của task.
- Full mobile-login dùng helper rate-limit 18 verify/300 giây vốn có; không bỏ cơ chế chờ. Warning Starlette/TestClient, JWT fixture unit và warning của test tích hợp hiện hữu nằm trong logs; không dùng warning để che fail.

## 7. Phát sinh

- Ngoại lệ raw scope giữ từ lượt trước; kiểm hash/delta mới xác nhận chỉ sửa hai file sản phẩm được phép ở stage test (integration test và workbook). Không commit/push hoặc bump gitlink.
- Sandbox chặn ghi snapshot/evidence và Docker lần đầu; lần chạy escalation được auto-review cho phép. Không đổi quyền, config hoặc dependency hệ thống.
- Audit workbook đầu fail do so datetime của openpyxl với chuỗi trong snapshot JSON; đã sửa **script scratch kiểm tra** chuẩn hóa JSON datetime, chạy lại exit 0; giữ `test-R1-workbook-qa.log` lỗi đầu, dùng `...-final.log` làm kết luận.
- QA nội dung phát hiện TC-CATINDEX-18 kế thừa nhầm điều kiện chuẩn bị unit. Đã sửa spec sang Supabase local và validate/build/merge/render lại; không thay test tự động, actual/status hoặc sản phẩm. Log lượt đầu/final đều giữ.

## Bước tiếp theo

- **P8/P9 hoàn tất sau sửa R1**: 60 targeted integration pass, full unit/integration đã chạy đủ và so tập lỗi nền bằng lần thực thi HEAD mới; 39 test case được dựng/gộp, không câu hỏi nghiệp vụ chặn.
- Đang chờ người duyệt đọc 05/diff integration/workbook/evidence và tự chạy:

```powershell
& 'C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe' .agents/scripts/gate.py approve 4.12-ocr-text-normalization-catalog-index test
```

- Sau duyệt, ở lượt riêng dùng wf-next/gate → wf-review để review lại R1 và cập nhật 06; **06 hiện vẫn Chưa đạt theo snapshot trước sửa**, không dùng làm kết luận hiện tại. Agent không tự duyệt hoặc bắt đầu review trong lượt này.
- Chưa commit: backend 9 file trong bảng 03 (5 source, 3 unit, 1 integration), docs 1 workbook; superproject gitlink api_contract/backend/docs/frontend/tests khác checkout base từ trước, work/4.12 đang ignore. Lượt test chỉ sửa integration + workbook + 05/spec/evidence/scratch; không stage gitlink ngoài task hoặc scratch.
- Khi được yêu cầu lưu: commit/push backend và docs trên nhánh task trước; superproject chỉ bump SHA đã push. Lệnh artifact đã soạn, **chỉ chạy khi người dùng yêu cầu**:

```powershell
git add -f -- work/4.12-ocr-text-normalization-catalog-index/05-test-report.md work/4.12-ocr-text-normalization-catalog-index/testcases.json work/4.12-ocr-text-normalization-catalog-index/testcases.xlsx work/4.12-ocr-text-normalization-catalog-index/evidence/
git diff --cached --stat
git commit -m 'docs(ocr): record 4.12 regression retest evidence'
git push -u origin feat/4.12-ocr-text-normalization-catalog-index
```

- Cập nhật lần cuối: 2026-10-28 22:21 +0700, Codex.
