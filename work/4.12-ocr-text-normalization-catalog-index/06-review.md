---
task: 4.12-ocr-text-normalization-catalog-index
stage: review
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-30 14:22 +0700
content_hash: sha256:69a3cca64ea10b0a
inputs:
  01-requirement.md: sha256:af09eb8e3be07716
  03-plan.md: sha256:1561587391291ad5
  04-impl-notes.md: sha256:524fa01907d961a8
  05-test-report.md: sha256:15eccd7a8701fba2
---

# 4.12 · Review lại sau sửa R1

## 1. Kết luận

**Đạt** trong phạm vi task — **0 Critical, 0 High, 0 Medium, 0 Low đang mở**. R1/High của review trước đã được sửa và kiểm chứng lại; không phát hiện lỗi mới qua diff và các kiểm tra dưới đây. Kết luận này không có nghĩa toàn bộ backend đã xanh hoặc thay thế người khác approve PR theo DoD.

Lượt này đã thực thi **184 unit/architecture + 60 integration catalog + 4 probe review độc lập: đều pass, 0 skip**. 39 test case khớp evidence và workbook. Full suite ở bước test vẫn có **30 lỗi unit, 18 lỗi integration và 31 lỗi lint nền**; đã đối chiếu chính xác tập nodeid với lần chạy baseline được lưu, không chạy lại full suite/baseline trong review này.

Snapshot review trước sửa được giữ nguyên ở `evidence/review-R1-report-before.md`; log review cũ vẫn giữ. Chỉ cập nhật 06 và ghi evidence/scratch của lượt review; không sửa source, test sản phẩm, workbook hay 01/03/04/05 đã approved.

## 2. Phạm vi đã review

| Submodule | Đối chiếu |
|---|---|
| backend | `git diff --stat main...HEAD`, `git diff --stat origin/main...HEAD`, toàn bộ `git diff HEAD -- src/drugtime/modules/catalog/api.py src/drugtime/modules/catalog/adapters/outbound/sql_catalog.py tests/unit/test_catalog_sync.py`; đọc đầy đủ 6 file untracked của task (3 source, 2 unit, 1 integration). |
| docs | `git diff --stat origin/main...HEAD`, `git diff --numstat main...HEAD`, `git log --oneline origin/main..HEAD`; kiểm workbook working tree/spec và so 24 sheet khác với snapshot trước test. |
| superproject | `git status --short --branch`, 01/03/bảng 10 file, 04/05 và log/XML/JSON evidence. |

Backend HEAD `2439aa66c914809d08c017f09379e03d0144da83`; origin/main `fa64ce2`. Task chưa commit nên diff nhánh không chứa code 4.12: phải đọc cả working tree/untracked. Diff main local cũ (`33867bf`) tới HEAD là thay đổi family kế thừa, không thuộc 4.12. Docs HEAD `73590c1`, origin/main `1e42083`; hai commit kế thừa là `da3f624 test(medication): update selection confirmation cases` và `73590c1 chore: merge main and preserve task 4.16 test cases`. Khi mở PR cần kiểm base/commit để không lẫn thay đổi 4.16. Không đổi nhánh/base trong review.

`scope.py <task> --stage implement` **exit 1**: 9 file OK, duy nhất integration test bị báo NGOÀI vì luật stage implement loại integration. File này đã nằm trong bảng 03, thuộc P8/test đã approved; giới hạn này và ngoại lệ giữ 8 file implement ở stage test đã được chấp nhận từ lượt trước. Không phát sinh file sản phẩm mới ngoài plan; không gọi raw scope là pass hoặc sửa scope/gate. Log: `evidence/review-R1-scope.log`.

Audit SHA256 độc lập xác nhận **10/10 file code/workbook hiện tại bằng snapshot cuối test đã approved**, gồm 9 backend + 1 docs. Review không sửa chúng. Log: `evidence/review-R1-evidence-audit-final.log`.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1–AC14 có triển khai và bằng chứng phù hợp. R1/AC6 đã khắc phục; chi tiết truy vết bên dưới. |
| Phạm vi | Đúng 10 file trong 03; artifact ở work. Không sửa endpoint, writer, migration, contract hoặc consumer 4.13/4.15. Raw scope có giới hạn đã nêu. |
| Contract | API HTTP và search cũ giữ nguyên. Diff SQL chỉ thêm reader; 43 integration search trên hai route và unit search/CRUD/ingest pass trong review. |
| Bất biến kiến trúc | 15 architecture test pass. Code mới trong catalog, application dùng port, facade ghép adapter. Không thêm import liên module, patient endpoint, client Supabase, consent/dose/interaction/schema. Không cần wf-health-endpoint hoặc wf-db-migration cho thay đổi này. |
| Bảo mật | Normalizer/builder thuần, không log/lưu/gửi OCR; TypeError cố định không echo đầu vào. Reader SQL tĩnh, không đưa text OCR vào câu lệnh; dữ liệu test tổng hợp. Không phát hiện secret mới trong phần thay đổi đã đọc; không tuyên bố đã audit toàn repo/evidence về bí mật. |
| Xử lý lỗi | Reader/loader truyền lỗi lên, không trả snapshot cũ/rỗng hoặc kết quả một phần. Unit kiểm lỗi iterator giữa chừng; integration kiểm DBAPIError từ connection PostgreSQL riêng bị ngắt. |
| Hiệu năng | Reader một SELECT toàn active, EXISTS theo medication_id; không N+1/LIMIT/phân trang. Sort O(N log N), chi phí/bộ nhớ theo toàn catalog là lựa chọn không cache đã duyệt; chưa đo SLO/latency dữ liệu thật. |
| Chất lượng test | Expected regression rõ ràng, không mock normalizer để tạo đáp án. 121 normalizer + 16 index, hồi quy cũ và 17 index DB/43 search DB pass. Có biên không chắc chắn, raw/null/mapping, >50, rỗng rollback, thay đổi commit và lỗi đọc; 0 skip. |
| Dễ đọc và nhất quán | Grammar parse tách khỏi detector nghi ngờ; Decimal, frozen DTO, tuple/mapping proxy copy; giữ pattern UoW/facade và CatalogMedication hiện có. Không thêm debug/TODO/writer/cache. |
| Đối chiếu 04/05 với log | Số test và tập lỗi baseline khớp XML/JSON/log; cả 22 ca fail trước sửa có invocation pass trong lượt này. 39 ca Excel Pass truy được tới test pass. Không gọi full suite là pass. |

### Truy vết tiêu chí chấp nhận

| AC | Code / bằng chứng và giới hạn |
|---|---|
| AC1–AC2 | NFD/bỏ dấu/đ/chữ thường và đúng ba noise, gộp whitespace; test NFC/NFD/idempotence/multiline pass. Không tự phân đoạn nhiều thuốc. |
| AC3 | Không thay O/0/l/1; giữ B12/D3/tên số, thêm ca Long/Log/Ong/O0l1 kèm metadata. Detector chỉ nhận tín hiệu khi có chữ số thực, không nới grammar parse. |
| AC4–AC5 | Grammar đóng cho đơn/nồng độ/phối hợp/% của MVP; Decimal dương, giữ thứ tự/tử/mẫu, không đổi đơn vị/độ lớn. |
| AC6 | R1: `_AMOUNT_LIKE` nhận tiền tố O/l kèm số, dùng chung cho attached/spaced detector. Nhóm lỗi và nhóm hợp lệ cạnh tranh giữ toàn text, unparsed, strength None/parts rỗng. Biên âm/0/ngoài MVP/dang dở/metadata/ambiguous cũ vẫn pass. |
| AC7 | Empty/noise trả rỗng/absent; non-string TypeError cố định. |
| AC8–AC9 | Builder giữ DTO raw/null/ID/mapping, không suy strength nguồn từ tên; bucket giữ mọi ID, sort ổn định, collection bất biến. 12 integration R1 kiểm độc lập trên name/ingredient/strength từ DB. |
| AC10–AC11 | SELECT toàn active có ORDER BY ID, loader đọc mỗi invocation; không giữ snapshot trong state. 5 integration gốc kiểm >50/rỗng/add-update-remove-restore/snapshot/lỗi thật. Caller chịu trách nhiệm mở UoW mới mỗi lượt; freshness tại SELECT. |
| AC12 | Ingest vẫn NFC và giữ dấu/hoa thường. Hồi quy search/CRUD/architecture và 43 search integration pass; contract không đổi. Lỗi toàn suite có sẵn được tách riêng bên dưới. |
| AC13 | Review đường gọi + guard I/O/writer/caplog/capsys: chỉ xử lý bộ nhớ, reader SELECT, không tự chọn thuốc. Chưa nghiệm thu camera/OCR ảnh/lưu trữ/patient flow ngoài phạm vi. |
| AC14 | Hai caller tổng hợp dùng chung facade/DTO, UoW riêng. Chưa tích hợp endpoint/UI thật của 4.13/4.15, đúng phạm vi. |

### Lệnh và bằng chứng thực thi trong lượt review này

Backend dùng `.venv/Scripts/python.exe` từ backend; workflow dùng Python tuyệt đối `C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe`; Excel/audit dùng runtime bundled `C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`. Alias WindowsApps không chạy được. Output kiểm tra lưu bằng `2>&1 | Tee-Object`; các log dưới nằm trong `evidence/`.

| Kiểm tra | Kết quả | Log / XML |
|---|---|---|
| `gate.py 4.12-ocr-text-normalization-catalog-index review` | exit 0 | `review-R1-gate.log` |
| `python -m pytest -p no:cacheprovider tests/unit/test_catalog_ocr_normalization.py tests/unit/test_catalog_index.py tests/unit/test_catalog_sync.py tests/unit/test_catalog_search.py tests/unit/test_catalog_crud.py tests/architecture --junitxml=...` | exit 0: **184 passed**, 1 warning, 0 skip | `review-R1-targeted.log/.xml` |
| `python -m pytest -p no:cacheprovider tests/integration/test_catalog_index.py tests/integration/test_catalog_search.py --junitxml=...` | exit 0: **60 passed**, 1 warning, 0 skip; PostgreSQL local thật, không reset DB trong review | `review-R1-integration.log/.xml` |
| Từ gốc, PYTHONPATH=backend/src, `python -m pytest -p no:cacheprovider work/<task>/scratch/test_review_regression.py --junitxml=...` | exit 0: **4 passed**, 0 skip; đúng 4 probe từng fail ở review trước | `review-R1-original-probe.log/.xml` |
| `testcase_xlsx.py validate <task>` | exit 0: OCRNORM 21/21, CATINDEX 18/18 Pass | `review-R1-testcase-validate.log` |
| `scratch/audit_testcase_traceability.py` | exit 0: 39 case có evidence/node mapping pass, AC1–AC14, 17 lớp EP/8 rule và BVA search | `review-R1-traceability.log` |
| `scratch/verify_test_R1.py workbook` | exit 0: giữ 24 sheet khác; hai workbook khớp 39 ID/actual/status và công thức không REF lỗi | `review-R1-workbook.log` |
| `scratch/audit_review_R1.py` lượt cuối | exit 0: 10/10 hash giữ nguyên; 184+60+4 pass; 22 fail trước sửa → pass; tập lỗi baseline khớp | `review-R1-evidence-audit-final.log` |

Hai warning targeted/integration là Starlette TestClient deprecation có sẵn. Không tăng retry, đổi expected hay bỏ test. Không chạy lại toàn Ruff hoặc render/Excel native trong review; dùng bằng chứng lint/render đã approved của 05, kiểm lại workbook ở mức dữ liệu/công thức/style/dimensions/merge/freeze/chart/validation.

### Evidence đã approved được đối chiếu, không phải lần chạy full mới

- `test-R1-unit-architecture.log/.xml`: **30 failed, 1494 passed**, 1524 invocation, 0 skip. `test-R1-baseline-unit-results.json` + log ghi source HEAD nguyên bản trong scratch: **86 passed, 30 failed**. Audit review so trực tiếp 30 nodeid fail bằng nhau.
- `test-R1-integration.log/.xml`: **18 failed, 1113 passed, 1 XPASS**, 1132 invocation, 0 skip. Baseline failed-only có **18 failed**, khớp trực tiếp tập nodeid; không phải toàn bộ baseline integration. XPASS là marker xfail cũ của auth doses, không sửa ở task này.
- `test-R1-lint-baseline.log`: **current=31, existing baseline=31, introduced=0**; bản thân Ruff exit 1, audit baseline exit 0.
- Lỗi nền gồm contract/auth profile ở unit; alert dispatch/dose timestamp/notification schema/mobile login/profile schema ở integration. Không phát hiện sai lệch mới qua đối chiếu này; khớp baseline không chứng minh mọi biên chưa test đều đúng.

## 4. Phát hiện

Không còn phát hiện mở trong phạm vi task.

| ID / mức trước sửa | Vị trí hiện tại | Trạng thái và bằng chứng |
|---|---|---|
| R1 / High | `backend/src/drugtime/modules/catalog/application/normalize_ocr.py:19–28`, dùng trong `_groups`; test normalizer/index/integration | **Đã khắc phục, review lại pass**. `_AMOUNT_LIKE` mở rộng detector cho O/l kèm chữ số, không thay `_NUMBER`/grammar hợp lệ và không sửa ký tự OCR. 18 unit normalizer + 4 unit index từng fail trước sửa đều pass; 6 ca bảo vệ tên pass; 12 regression DB pass trên ba trường; 4 probe độc lập ban đầu đều pass. |

Các input ban đầu `Thuoc 500mg O.5g`, `O.5 g`, `l0mg`, `l0 mg` nay giữ toàn text trong name_key/normalized_text, status unparsed, strength None/parts rỗng. Test mới còn phủ nhóm sai trước/sau nhóm hợp lệ, dấu phẩy/chấm, hoa/thường và dạng đứng riêng. Không dùng kết quả này để mở rộng format ngoài MVP hoặc tuyên bố dữ liệu dược đã được xác minh.

## 5. Mô tả PR

Chỉ soạn mô tả, **chưa tạo PR/commit/push/merge hoặc bump gitlink**. Khi được yêu cầu mở PR, điền URL thật liên kết PR backend ↔ docs ↔ superproject; kiểm lại base docs đang kế thừa 4.16 và stage đúng bảng 03. Không đưa các gitlink api_contract/frontend/tests đang khác từ trước vào task này.

### Backend

Title: `feat(catalog): normalize OCR text and build fresh catalog indexes`

Task 4.12 bổ sung chuẩn hóa OCR dùng chung cho 4.13/4.15 và index catalog dựng mới mỗi lượt. Hàm thuần giữ raw/ID/null, tách hàm lượng đúng grammar MVP, giữ toàn text khi chưa chắc chắn; ví dụ `Thuoc 500mg O.5g` giữ unparsed, không chọn 500mg. Reader đọc toàn catalog active bằng một SELECT, lỗi truyền lên và không trả snapshot cũ. Facade nêu caller mở giao dịch mới mỗi lượt; HTTP/search không đổi.

Validation: 184 unit/architecture, 60 integration catalog và 4 probe review pass; 39 test case truy được evidence. Full suite test: 1494 pass/30 fail unit, 1113 pass/18 fail/1 XPASS integration; các tập fail trùng baseline đã thực thi, 31 lỗi lint nền/0 mới. AC1–AC14 được đối chiếu trong 06. Không có AC manual; có thể chạy lại hai lệnh pytest targeted ở mục 3 trên Supabase local.

Rủi ro/giới hạn: chi phí đọc/normalize toàn catalog mỗi lượt; chưa benchmark production. Grammar MVP không sửa lỗi OCR/quy đổi/xác minh thuốc; consumer thật phải mở UoW mới và đối chiếu catalog lại trước xác nhận. Liên kết PR docs/superproject sẽ điền khi tạo.

### Docs

Title: `test(catalog): document OCR normalization and catalog index cases`

Task 4.12 cập nhật hai chức năng OCRNORM/CATINDEX trong Test_Cases.xlsx: 39 ca Pass, thêm regression R1, giữ ID cũ và 24 sheet chức năng khác. Bug R1 đã retest/review pass, không còn lỗi mở trong task.

Validation: validate/traceability/workbook audit exit 0, 39 actual/status khớp test evidence; build/merge/render nằm trong 05 đã approved. Review không dựng lại workbook hoặc kiểm Excel native. Kiểm PR base/commit để chỉ đưa thay đổi 4.12, giữ nội dung 4.16 đã có. Liên kết PR backend/superproject sẽ điền khi tạo.

### Superproject

Title: `chore(catalog): record task 4.12 evidence and update submodules`

Lưu 01/03/04/05/06, testcases.json/xlsx và evidence của task 4.12; chỉ bump backend/docs tới SHA đã push. Không stage scratch hoặc các gitlink ngoài task. Gate test hợp lệ, review Đạt với R1 đã khắc phục; toàn suite còn lỗi nền được nêu rõ trong báo cáo.

Validation: gate, scope với giới hạn đã chấp nhận, 10-file hash audit, targeted 184+60+4 pass và 39 test case. Liên kết PR backend/docs và SHA cuối sẽ điền sau khi tạo/push. Thứ tự merge: **backend và docs trước, superproject sau**. Sau squash/rebase merge phải cập nhật gitlink tới commit đã merge thực tế trước merge superproject, theo wf-git.

## 6. Ghi chú cho quy trình / phát sinh

- Trong bước điều phối, đã đọc 05 để lấy trạng thái/bước tiếp theo trước khi nạp wf-review. Vì vậy không đánh dấu tuân thủ tuyệt đối yêu cầu đọc diff trước tự thuật. Đã đọc lại 01/03, toàn bộ phần code task, đối chiếu evidence độc lập và rerun test/probe; vẫn cần người khác approve PR theo DoD.
- Scope implement loại integration đã approved ở test, dù file thuộc plan; giữ đúng raw exit 1 và ngoại lệ đã được chấp nhận, không xin lại ngoại lệ hoặc sửa công cụ.
- Audit review đầu fail do script scratch thay backslash trong cả nodeid parametrized (làm đổi escape trong dữ liệu test). So trực tiếp JSON cho thấy tập nodeid bằng nhau; đã sửa chỉ script audit, rerun exit 0. Giữ `review-R1-evidence-audit.log` lần đầu, chỉ dùng `...-final.log` để kết luận. Không sửa evidence test hoặc expected sản phẩm.
- Sandbox ban đầu chặn ghi snapshot/log; retry escalation được auto-review cho phép. Không đổi quyền/cấu hình máy.

## Bước tiếp theo

- Review lại hoàn tất, **R1 đóng sau kiểm chứng**; đang chờ người duyệt đọc 06/diff/evidence và tự duyệt review theo AGENTS.md/wf-review. Agent không tự approve hoặc mở PR trong lượt review.

```powershell
& 'C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe' .agents/scripts/gate.py approve 4.12-ocr-text-normalization-catalog-index review
```

- Sau duyệt: khi người dùng yêu cầu, commit/push backend và docs trước; kiểm base docs và staged diff, dùng mô tả PR mục 5. Superproject chỉ bump SHA đã push/đã merge phù hợp. DoD còn cần ít nhất một người khác approve PR.
- Chưa commit: backend 9 file đúng bảng 03, docs 1 workbook; superproject có gitlink api_contract/backend/docs/frontend/tests khác từ trước và work task đang ignore. Review chỉ cập nhật 06/evidence/scratch, không thêm code dở.
- Đề xuất lưu artifact/evidence khi người dùng yêu cầu; không chạy commit/push hoặc stage scratch trong lượt này:

```powershell
git add -f -- work/4.12-ocr-text-normalization-catalog-index/01-requirement.md work/4.12-ocr-text-normalization-catalog-index/03-plan.md work/4.12-ocr-text-normalization-catalog-index/04-impl-notes.md work/4.12-ocr-text-normalization-catalog-index/05-test-report.md work/4.12-ocr-text-normalization-catalog-index/06-review.md work/4.12-ocr-text-normalization-catalog-index/testcases.json work/4.12-ocr-text-normalization-catalog-index/testcases.xlsx work/4.12-ocr-text-normalization-catalog-index/evidence/
git diff --cached --stat
git commit -m 'docs(ocr): record task 4.12 review after regression fix'
```

- Cập nhật lần cuối: 2026-10-28, Codex.
