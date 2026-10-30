---
task: 4.12-ocr-text-normalization-catalog-index
stage: test
status: draft
---

# 4.12 · Test tích hợp chuẩn hóa OCR và index danh mục

## 1. Môi trường

- Gate test exit 0, đầu vào `01`, `03`, `04` vẫn approved. Không sửa các artifact đầu vào hoặc code sản phẩm.
- Nhánh superproject/backend/docs: `feat/4.12-ocr-text-normalization-catalog-index`. Backend HEAD `2439aa66c914809d08c017f09379e03d0144da83`.
- Backend: `.venv/Scripts/python.exe`, Python 3.14.7, pytest 9.1.1, SQLAlchemy/psycopg sẵn có. Workflow/Excel dùng Python bundled tuyệt đối đã ghi trong 03; Python WindowsApps không chạy được.
- Supabase CLI 2.120.0 sẵn có tại `C:/Users/admin/AppData/Local/npm-cache/_npx/aa8e5c70f9d8d161/node_modules/@supabase/cli-windows-x64/bin/supabase.exe`; Docker local, PostgreSQL 17 ở `127.0.0.1:54322`, reader đăng nhập `api_role`.
- Đã chạy `supabase start`, `supabase db reset --local`, exit 0; migration sạch áp dụng đến `20261021115000_access_logs_admin_self_denied.sql`. CLI cảnh báo không có `supabase/seed.sql`; các test tự dựng dữ liệu tổng hợp. Log: `evidence/test-supabase-start.log`, `evidence/test-db-reset.log`. Credential local do CLI tự in đã được che trong log start.
- Full suite lần đầu dừng do Kong/Mailpit/PostgREST đang tắt, `API_URL` trống khi test Auth đọc status. Đã khởi động đúng ba container local có sẵn, thêm thư mục CLI vào PATH riêng của process và kiểm host API là `127.0.0.1`; không đổi file cấu hình/môi trường deploy. Log: `evidence/test-additional-local-services.log`.
- Mỗi lệnh pytest/lint/scope/Excel lưu output bằng `2>&1 | Tee-Object`; kiểm exit code. XML pytest giữ nodeid/kết quả để truy vết test case.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Test thực tế | Kết quả phiên này |
|---|---|---|
| AC1 | Unit normalizer: NFC/NFD, hoa/thường, đ/Đ; index/query cùng quy tắc | Pass |
| AC2 | Unit noise, multiline, khoảng trắng, idempotence | Pass |
| AC3 | Unit B12/D3 và ký tự O/0/l/1 được giữ | Pass |
| AC4 | Unit toàn bộ format đơn MVP/spacing/decimal, không quy đổi | Pass |
| AC5 | Unit nồng độ/phối hợp/phần trăm giữ cấu trúc và thứ tự | Pass |
| AC6 | Unit 0/âm/nhóm sai/cạnh tranh/ngoài MVP, metadata/quy cách được giữ | Pass |
| AC7 | Unit rỗng/noise/non-string, TypeError không echo dữ liệu | Pass |
| AC8 | Unit raw/null/DTO/khóa nguồn và integration I1 map toàn bộ source row | Pass |
| AC9 | Unit bucket trùng khóa giữ mọi ID/hàm lượng/dạng, collection bất biến | Pass |
| AC10 | I1 `test_loads_all_active_medications_above_search_limit__AC10`; I2 `test_empty_catalog_is_a_successful_empty_index__AC10`; I5 lỗi đọc PostgreSQL thật | Pass: toàn bộ active, 60 fixture active và 1 deleted, null/source mapping; rỗng thành công khác lỗi đọc |
| AC11 | I3 `test_committed_catalog_changes_are_visible_next_call__AC11`; I4 `test_same_snapshot_has_stable_order_and_old_index_is_unchanged__AC11`; I5 `test_real_read_error_after_success_is_not_empty_or_cached__AC10_AC11` | Pass: thêm/sửa/gỡ/khôi phục đã commit thấy ở giao dịch đọc mới trong cùng process; snapshot A bất biến; thứ tự ổn định; lỗi đọc không fallback |
| AC12 | Unit ingest/search/CRUD + 15 architecture; 43 invocation integration search cả hai route | Pass phần hồi quy catalog; giới hạn full suite ngoài task ghi ở mục 4/5b |
| AC13 | Unit guard file/mạng/writer và caplog/capsys; đường loader chỉ SELECT | Pass; không nghiệm thu cơ chế lưu OCR hoặc dữ liệu patient ngoài phạm vi |
| AC14 | Hai consumer tổng hợp qua facade, UoW riêng | Pass; chưa tích hợp endpoint/UI thật 4.13/4.15 |

Test mới duy nhất: `backend/tests/integration/test_catalog_index.py` gồm 5 test I1–I5. Không sửa conftest, test cũ, source, API contract, migration hoặc grant.

- Targeted: từ backend, `python -m pytest tests/integration/test_catalog_index.py tests/integration/test_catalog_search.py --junitxml=../work/4.12-ocr-text-normalization-catalog-index/evidence/test-catalog-integration.xml` → **48 passed, 0 failed, 0 skipped**, 1 warning, 7.94 giây, exit 0. Log: `evidence/test-catalog-integration.log`.
- Unit/architecture: `python -m pytest tests/unit tests/architecture --junitxml=../work/4.12-ocr-text-normalization-catalog-index/evidence/test-unit-architecture.xml` → **1466 passed, 30 failed, 0 skipped**, 8 warnings, 77.31 giây, exit 1. Toàn bộ 156 invocation thuộc nhóm normalizer/index/ingest/search/CRUD/architecture pass; XML/log: `evidence/test-unit-architecture.xml`, `evidence/test-unit-architecture.log`.
- Đã chạy lại 6 file unit lỗi bằng source HEAD nguyên bản trích riêng vào scratch, ép import từ source đó và xác nhận chưa có `list_for_index`: **86 passed, 30 failed**, 18.25 giây. Tập nodeid fail trùng hoàn toàn unit suite phiên này, **0 lỗi mới**; log `evidence/test-baseline-unit.log`, đối chiếu `evidence/test-stage-delta.log`. Không gọi toàn bộ unit suite là pass.

## 3. Kịch bản chất lượng đã phủ

| Kịch bản áp dụng | Test | Kết quả |
|---|---|---|
| Catalog hiện tại, không tái sử dụng index giữa các lượt | I3: A → commit thêm/sửa/gỡ → B → restore → C, UoW mới từng lần | Pass |
| Phân biệt catalog rỗng với nguồn đọc lỗi | I2 rollback transaction, I5 ngắt đúng PID của connection api_role riêng/NullPool, assert DBAPIError | Pass |
| Bảo toàn ID/raw/null và snapshot cũ | I1/I3/I4 và unit index | Pass |
| Ranh giới module/search/ingest không đổi | 15 architecture, unit catalog và 43 integration search | Pass |
| Text OCR không log/lưu/gọi dịch vụ ngoài | Unit guard/caplog/capsys tổng hợp | Pass |

Không thêm test cross-patient/rút consent/dose idempotency/race/golden interaction cho 4.12 vì không sửa dữ liệu patient, engine tương tác, endpoint hoặc schema. Các test hồi quy sẵn có vẫn được đưa vào full integration suite; không suy kết quả toàn suite từ bảng trên.

## 4. Toàn bộ bộ test tích hợp

- Lệnh cuối từ backend: thêm thư mục Supabase CLI vào PATH riêng của process, rồi `python -m pytest tests/integration --junitxml=../work/4.12-ocr-text-normalization-catalog-index/evidence/test-integration.xml`.
- Kết quả cuối: **1101 passed, 18 failed, 1 xpassed, 0 skipped**, 5859 warnings, **496.54 giây (8 phút 16 giây)**, exit 1. Đã chạy đủ 1120 invocation. Toàn bộ 5 test index và 43 search pass cả trong lần targeted và full suite; không gọi full suite là pass.
- Log/XML: `evidence/test-integration.log`, `evidence/test-integration.xml`.
- Baseline integration: chạy đúng 18 nodeid fail bằng `backend/.venv/Scripts/python.exe -X utf8 work/4.12-ocr-text-normalization-catalog-index/scratch/run_baseline_integration_tests.py --failed-only`, import source HEAD nguyên bản chưa có reader 4.12 → **18 failed**, 7.38 giây, exit 1; tập fail trùng hoàn toàn full suite, **0 lỗi mới**. Log: `evidence/test-baseline-integration.log`; XML: `evidence/test-baseline-integration.xml`. Không chạy toàn bộ baseline 1115 test cũ; chỉ tái hiện đúng tập lỗi cần đối chiếu.
- Lượt đầu trước khi phục hồi các service local: **92 passed, 3 failed**, 44.60 giây, exit 2 do guard Auth `API_URL` trống; chỉ chạy được một phần. Giữ log/XML ở `evidence/test-integration-first.log`, `evidence/test-integration-first.xml`.
- Ruff test mới cuối: `python -m ruff check --no-cache tests/integration/test_catalog_index.py` và `python -m ruff format --no-cache --check tests/integration/test_catalog_index.py` → exit 0, `evidence/test-index-lint.log`.
- Ruff toàn backend: script đối chiếu source HEAD chạy lại trong phiên này → current 31 / baseline 31 / introduced 0, exit 0 của kiểm tra đối chiếu; bản thân `ruff check .` exit 1. Log: `evidence/test-lint-baseline.log`.
- Scope raw: `scope.py 4.12-ocr-text-normalization-catalog-index --stage test` **exit 1**, báo 2 file mới `[OK]` và 8 file implement từ giai đoạn trước `[NGOÀI]`; không gọi raw scope là pass. Log: `evidence/test-scope.log`.
- Kiểm tra bổ sung: hash cả **8/8 file implement không đổi** so đầu phiên; loại riêng đúng các file đã có này để kiểm delta thì chỉ còn integration test + workbook, đều có trong 03. Kiểm cả tập implement thuộc plan và tập nodeid fail unit bằng baseline chạy lại → exit 0; `evidence/test-stage-delta.log`. Đây là bằng chứng riêng, không sửa hoặc thay thế kết quả raw scope.
- Người dùng đã xác nhận trong phiên: **“Chấp nhận ngoại lệ, giữ nguyên 8 file implement”**. Ghi nhận ngoại lệ công cụ này cho bàn giao, không đổi scope.py/gate/approval hoặc giấu file thay đổi.

## 5. Bộ test case Excel

- Spec: `testcases.json`; workbook task: `testcases.xlsx`; workbook tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`.
- `testcase_xlsx.py validate`, `build`, `merge` đã chạy exit 0 bằng script dự án. Không có cảnh báo xung đột kết quả. Log: `evidence/testcase-xlsx.log`.

| Chức năng (mã) | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| Chuẩn hóa OCR (OCRNORM) | 19 | 19 | 0 | 0 |
| Index danh mục (CATINDEX) | 16 | 16 | 0 | 0 |
| Tổng task 4.12 | 35 | 35 | 0 | 0 |

- Tất cả Pass truy được đến nodeid/parameter invocation thực tế trong XML của phiên này; đủ AC1–AC14, 17 lớp EP, 8 rule quyết định, biên q 0/1/100/101 và limit 0/1/50/51. Log: `evidence/test-testcase-traceability.log`.
- Không có Pending cần người chạy trong phạm vi API nội bộ 4.12; camera/ảnh thực/consumer thật thuộc task khác, không tính là đã kiểm.
- Không có Bug Report mới của 4.12; các lỗi hồi quy ngoài phạm vi được ghi riêng mục 5b, không thay kết quả/bug của chức năng khác trong workbook.
- Đã so trước/sau: **24 sheet chức năng cũ giữ nguyên** giá trị/công thức/style, chiều cao/rộng, merge, freeze, chart và validation; hai sheet mới khớp ID/actual/status của spec và có công thức tổng hợp hợp lệ. `Report` được script dựng lại theo thiết kế. Log: `evidence/test-workbook-qa.log`.
- Kiểm tra hiển thị: render read-only 8 vùng ảnh của hai sheet mới, EP/bảng quyết định và Report bằng artifact tool. Chữ tiếng Việt/wrap/row height đọc được, không thấy cắt nội dung; Report tính đúng 35/0/0 và 100% executed/passed, chart không chồng Bug Report. Preview bar chart hiện legend `Series1/2/3`; metadata XLSX gốc vẫn tham chiếu đúng `Report!D10/E10/F10` cho Executed/Passed/Failed, đây là giới hạn import/render. Không sửa workbook để né renderer; chưa kiểm trực tiếp bằng Microsoft Excel. Ảnh QA trong scratch không đề xuất commit.

## 5b. Lỗi sản phẩm tìm thấy

Chưa phát hiện lỗi sản phẩm mới trong phạm vi 4.12. I2 từng fail do giả định fixture về membership SET ROLE; đã sửa test, không sửa sản phẩm hoặc nới expected.

Lỗi nền unit tái hiện trên source HEAD: 24 ca contract thiếu path/khác semantics ở checkout `api_contract` hiện tại, 6 ca invalid-auth profile mong 401 nhưng nhận 422. Giữ nguyên contract/test/source cũ; không tự mở rộng 4.12 để xử lý chúng.

Full integration có 18 lỗi ngoài 4.12; **đã tái hiện cả 18 cùng nodeid bằng source HEAD nguyên bản**, không có lỗi mới do task trong tập đối chiếu. Nhóm lỗi quan sát được:

| Nhóm / số lỗi | Kỳ vọng / thực tế | Nhận định sau đối chiếu baseline |
|---|---|---|
| Alert dispatch / 3 | Test muốn 200, nhận 401 | Fixture override `identity.current_user`, nhưng route đi qua `notification_user` gọi identity trực tiếp; không có bearer token. |
| Dose confirmation / 1 | Timestamp cắt về phút, thực tế giữ `59.999000` giây | Source giữ timestamp đầu vào, khác expected cũ; không sửa expected trong 4.12. |
| Notification schema / 3 | Response khớp required trong contract, thực tế thêm `medication_name`/`scheduled_at` | Checkout contract hiện tại không cùng response backend. Bao gồm legacy-null snapshot và snapshot flow. |
| Mobile login / 10 | Chặn newline/Unicode phone, lưu NUL trong tên hoặc chặn độ dài/ngày sinh; thực tế khác expected | 2 newline phone, 4 Unicode phone, 1 tên chứa NUL và 3 giới hạn profile. Không có lỗi token rate limit trong danh sách cuối. |
| Profile API / 1 | Response đúng tập field cũ, thực tế có thêm `email` | Test/schema kỳ vọng khác response hiện tại. |

Danh sách nodeid/traceback ở `evidence/test-integration.log` và `evidence/test-baseline-integration.log`. Đây là lỗi đã có trên baseline của suite; việc phân loại từng mismatch ngoài task thành bug sản phẩm hay test/contract cũ cần xử lý trong phạm vi riêng. Không sửa source/test/contract cũ hoặc reopen implement của 4.12 để dọn các lỗi này.

## 6. Test không ổn định hoặc bị skip

- Test mới/targeted catalog: 0 skip/xfail/xpass. Không retry tự động, không sleep, không đổi expected để pass.
- Lượt targeted đầu: 47 passed, 1 failed vì `postgres` local không có quyền `SET LOCAL ROLE api_role`; transaction đã rollback. Sửa I2 dùng connection api_role trực tiếp, READ COMMITTED trước begin, UPDATE tạm và loader cùng connection, rollback finally rồi so toàn bộ `(id, deleted_at)` trước/sau. api_role đã có UPDATE medications, không cấp thêm quyền. Không đổi AC/grammar hoặc dùng mock để thay DB thật. Log/XML đầu: `evidence/test-catalog-integration-first.log`, `evidence/test-catalog-integration-first.xml`.
- Cảnh báo unit/integration là Starlette TestClient deprecation và HMAC key ngắn của fixture unit hiện hữu; không đưa credential thật vào log.
- Full suite 0 skip, 0 xfail, **1 XPASS** ở test có marker xfail từ trước: `test_post_doses_batch_requires_authentication__AC9`. Expected-failure cũ ghi phụ thuộc identity chưa sửa ở task 2.10; lần này assertion authentication pass. Giữ nguyên marker/test cũ; không tính XPASS này thành test mới của 4.12.
- Test mobile login hiện hữu có ngân sách 18 verify mỗi cửa sổ 300 giây; full run có chờ theo helper này. Không đổi budget, rate limit, retry hoặc assertion.

## 7. Phát sinh

- Correction I2 so với giả định plan: kết nối api_role trực tiếp thay admin connection + SET LOCAL ROLE vì PostgreSQL local không cấp membership cho postgres; giữ cùng transaction/rollback và các assertion. Không cần đổi code/grant/migration hoặc requirement/plan.
- Ngoại lệ scope đã được người dùng xác nhận, chi tiết mục 4. Không thay source/test unit ở giai đoạn test, có hash làm bằng chứng.
- Docs trước lượt này ở `feat/4.16-selection-confirmation-screen`, working tree sạch. Tạo nhánh task từ trạng thái đó để giữ test case 4.16 đã có; chỉ sửa workbook đã khai báo. Không switch/reset hoặc bỏ commit task cũ.
- Một log QA workbook đầu bị lỗi encoding CP1252 khi in tên sheet tiếng Việt; đã chạy lại với `-X utf8`, exit 0. Không đổi workbook để né lỗi encoding.
- Lần đầu runner baseline integration không collection được do thiếu đường import bare test và chuẩn hóa nhầm literal `\n` trong parameter ID; exit 4, không phải lỗi sản phẩm/bằng chứng regression. Đã sửa riêng script scratch và chạy lại thành công việc tái hiện 18 lỗi; log hạ tầng đầu lưu `evidence/test-baseline-integration-runner-first.log`. Kết luận baseline chỉ dùng lần sau đã thực thi đủ 18 nodeid.
- Sandbox chặn ghi evidence/Docker ở lần đầu; các lần chạy cần quyền phù hợp đã được auto-review cho phép. Không thay cấu hình sandbox hoặc dependency hệ thống.
- Chưa commit/push code hoặc artifact; không bump submodule. Scratch chứa runner/bản trích nguồn/ảnh QA, không đề xuất commit.

## Bước tiếp theo

- Đã xong P8/P9: 5 integration test mới + 43 search pass, full suite đã chạy đủ, 35 test case đã dựng/gộp; không còn câu hỏi chặn. Full unit/integration vẫn có lỗi nền đã tái hiện như mục 2/4/5b; ngoại lệ scope đã được người dùng xác nhận.
- Đang chờ: người duyệt đọc `05`, diff test/workbook, bằng chứng baseline và ngoại lệ scope; tự chạy `python .agents/scripts/gate.py approve 4.12-ocr-text-normalization-catalog-index test` nếu đồng ý. Python WindowsApps lỗi thì dùng `& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .agents/scripts/gate.py approve 4.12-ocr-text-normalization-catalog-index test`.
- Sau duyệt, ở lượt riêng dùng wf-review; agent không tự duyệt hoặc bắt đầu review trong lượt test.
- Đề xuất commit backend test trước, docs workbook và artifact/evidence task theo wf-git khi người dùng yêu cầu; không stage scratch.
- Cập nhật lần cuối: 2026-10-28 13:22 +0700, Codex.
