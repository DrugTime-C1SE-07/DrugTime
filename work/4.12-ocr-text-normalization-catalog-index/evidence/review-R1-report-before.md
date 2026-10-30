---
task: 4.12-ocr-text-normalization-catalog-index
stage: review
status: draft
---

# 4.12 · Review chuẩn hóa OCR và index catalog

## 1. Kết luận

**Chưa đạt** — 0 Critical, **1 High**, 0 Medium, 0 Low. R1 vi phạm AC6 và quy tắc parser bảo thủ ở 03 mục 1c. Không sửa source/test sản phẩm hoặc artifact approved trong lượt review.

Đã chạy lại 156 unit/architecture và 48 integration catalog: đều pass, không skip. Bốn ca bổ sung độc lập trong scratch đều fail và cùng chứng minh R1; các test đang có chưa phủ lỗi OCR ở ký tự đầu phần số của nhóm cạnh tranh.

## 2. Phạm vi đã review

| Submodule | Phạm vi/lệnh đối chiếu |
|---|---|
| backend | `git diff main...HEAD`, `git diff origin/main...HEAD`, `git diff HEAD -- src/drugtime/modules/catalog/api.py src/drugtime/modules/catalog/adapters/outbound/sql_catalog.py tests/unit/test_catalog_sync.py`; đọc toàn bộ 6 file untracked (3 source, 2 unit, 1 integration) của task. |
| docs | `git diff --numstat main...HEAD`, `git diff --numstat origin/main...HEAD`, workbook working tree so với snapshot trước test; kiểm giá trị/công thức/style/chiều rộng/cao/merge/freeze/chart/validation và spec. |
| superproject | `git status --short --branch`, `git diff --stat origin/main...HEAD`; đọc 01/03 và đối chiếu 04/05/evidence. |

Task chưa commit: diff nhánh riêng lẻ không chứa code 4.12; phải đọc cả working tree/untracked. `backend/main` local cũ nên `main...HEAD` hiện các thay đổi family của task 3.26. `origin/main...HEAD` backend rỗng (HEAD 2439aa6 đã nằm trong lịch sử origin/main fa64ce2); không quy các thay đổi family đó thành 4.12. Docs HEAD 73590c1 kế thừa hai commit test case 4.16 so origin/main 1e42083, đã được 05 ghi nhận; cần phân biệt khi chuẩn bị PR sau này. Không đổi branch/base trong lượt này.

Kết quả `scope.py --stage implement`: **exit 1**, 9 file OK, duy nhất `backend/tests/integration/test_catalog_index.py` bị báo NGOÀI do luật implement loại integration. File này nằm trong bảng 10 file đã approved của 03 và thuộc bước P8/test đã approved trong 05; không phải phát sinh ngoài plan. Không gọi raw scope là pass và không sửa công cụ để né lỗi. Log: `evidence/review-scope.log`.

Kiểm bổ sung `scratch/audit_test_stage.py verify-stage`: exit 0, 8/8 file implement giữ nguyên hash so trước test; delta chỉ gồm integration test và workbook, đều thuộc plan. Ngoại lệ scope test giữ 8 file implement đã được người dùng chấp nhận và 05 ghi lại. Không cần xin lại quyền cho những file đã được duyệt. Log: `evidence/review-stage-delta.log`.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1–AC5, AC7–AC14 có code/test phù hợp; AC6 chưa đạt ở R1. Truy vết chi tiết bên dưới. |
| Phạm vi | Đủ 9 file backend + 1 workbook trong 03. Không sửa router, writer, migration, grant, contract, frontend hoặc module khác của task. Giới hạn công cụ scope nêu ở mục 2. |
| Contract | Không thay HTTP request/response/mã lỗi. SQL diff chỉ thêm reader; 43 integration search và unit search/CRUD/ingest đều pass trong lượt review. |
| Bất biến kiến trúc | Code mới nằm trong catalog; 15 architecture test pass. Không thêm dependency liên module, client Supabase, patient endpoint, consent, dose hoặc interaction engine. Không áp dụng health-endpoint/db-migration vì không sửa các vùng tương ứng. |
| Bảo mật | Hàm thuần không ghi OCR ra log/storage/mạng; lỗi TypeError cố định không echo đầu vào; SQL reader tĩnh, không nối input OCR vào SQL. Test mới dùng dữ liệu tổng hợp, không thêm credential sản phẩm. Không phát hiện secret thật trong diff/evidence đã đọc; đây không phải kiểm toán toàn repo. |
| Xử lý lỗi | Reader/loader truyền lỗi, không fallback snapshot cũ/rỗng. Unit kiểm cả iterable lỗi giữa chừng; integration ngắt đúng PID connection riêng và assert DBAPIError. R1 nằm ở phân loại parser, không phải lỗi DB bị nuốt. |
| Hiệu năng | Một SELECT toàn active, EXISTS mapping có khóa theo medication_id, không vòng lặp truy vấn theo thuốc. Sort O(N log N), chuẩn hóa/bộ nhớ theo toàn catalog là lựa chọn không cache đã duyệt; chưa có benchmark/SLO dữ liệu thật, không tuyên bố đáp ứng latency production. |
| Chất lượng test | 97 normalizer + 12 index và hồi quy có assertion thực; integration dùng PostgreSQL/api_role, kiểm đủ tập ID >50, add/update/remove/restore, rỗng rollback, lỗi đọc thật. Không skip test mới. Thiếu biên ký tự đầu số sai dẫn đến R1. |
| Dễ đọc và nhất quán | DTO frozen, tuple/mapping copy bảo vệ snapshot; Protocol/application không import SQL adapter, facade ghép adapter, giữ pattern UoW sẵn có. Không thêm debug/TODO hoặc writer. |
| Đối chiếu 04/05 với evidence | Số test/failed/skipped và tập nodeid baseline khớp log/XML/JSON. Không phát hiện báo cáo pass giả. Các test case Pass hiện tại truy được bằng chứng, nhưng chưa thể dùng chúng để khẳng định AC6 đủ phủ sau R1. |

### Truy vết AC

| AC | Đối chiếu thực tế |
|---|---|
| AC1–AC2 | NFD/bỏ dấu/đ/chữ thường, thay đúng 3 noise bằng khoảng trắng; unit NFC/NFD và idempotence pass. |
| AC3 | Không sửa O/0/l/1; B12/D3/chữ số tên được giữ. R1 không yêu cầu biến đổi các ký tự nghi ngờ. |
| AC4–AC5 | Grammar đóng, Decimal dương; đơn/nồng độ/phối hợp/% nhận toàn nhóm, không quy đổi và giữ thứ tự. Unit pass. |
| AC6 | **R1**: nhóm lỗi OCR có số bắt đầu bằng O/l bị detector bỏ sót, dẫn đến chọn một nhóm hợp lệ còn lại. Các ca âm/0/dang dở/metadata đang có vẫn pass. |
| AC7 | Empty/noise thành rỗng; non-string TypeError thông báo cố định, unit pass. |
| AC8–AC9 | Giữ CatalogMedication raw/null/ID, không suy nguồn strength từ tên; buckets giữ mọi ID, frozen/tuple/mapping proxy và copy mapping; unit pass. |
| AC10–AC11 | SELECT đầy đủ active không LIMIT, ổn định theo ID; loader đọc mỗi lần. 5 integration test index pass: đầy đủ/null/mapping, rỗng rollback, cập nhật đã commit + phục hồi, snapshot ổn định, lỗi đọc không fallback. |
| AC12 | Ingest giữ dấu/hoa thường/NFC; unit search/CRUD/architecture và integration hai route search pass. Không đổi behavior route. Full suite vẫn có lỗi nền đã được chứng minh, xem mục bằng chứng. |
| AC13 | Unit guard/caplog/capsys + review đường gọi chỉ SELECT; không lưu/log OCR hay tự chọn thuốc. Không nghiệm thu camera, lưu OCR hoặc patient flow. |
| AC14 | Hai caller tổng hợp dùng cùng facade/quy tắc, UoW riêng; chưa tích hợp consumer thực 4.13/4.15, đúng phạm vi. |

### Bằng chứng review thực thi trong lượt này

Lệnh từ backend dùng `backend/.venv/Scripts/python.exe`; workflow/Excel dùng `C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` vì Python WindowsApps không chạy được. Output thô lưu bằng Tee-Object và kiểm exit code.

| Kiểm tra | Kết quả | Evidence |
|---|---|---|
| `gate.py <task> review` | exit 0, cho bắt đầu | `review-gate.log` |
| `python -m pytest -p no:cacheprovider tests/unit/test_catalog_ocr_normalization.py tests/unit/test_catalog_index.py tests/unit/test_catalog_sync.py tests/unit/test_catalog_search.py tests/unit/test_catalog_crud.py tests/architecture` | exit 0: **156 passed**, 1 warning, 0 skip | `review-targeted.log`, `review-targeted.xml` |
| `python -m pytest -p no:cacheprovider tests/integration/test_catalog_index.py tests/integration/test_catalog_search.py` | exit 0: **48 passed**, 1 warning, 0 skip, PostgreSQL local đang chạy; không reset DB trong review | `review-catalog-integration.log`, `.xml` |
| `python -m pytest -p no:cacheprovider work/<task>/scratch/test_review_regression.py` với PYTHONPATH backend/src | exit 1: **4 failed**, đủ 4 ca tái hiện R1, 0 skip | `review-parser-regression.log`, `.xml`; probe bổ sung `review-parser-probes.log` |
| `testcase_xlsx.py validate <task>` | exit 0: OCRNORM 19 Pass, CATINDEX 16 Pass | `review-testcase-validate.log` |
| `scratch/audit_testcase_traceability.py` | exit 0: 35 ca liên kết tới invocation pass trong XML, phủ khai báo AC1–AC14, 17 lớp EP/8 rule; không đồng nghĩa mọi biên AC đã phủ | `review-testcase-traceability.log` |
| `scratch/audit_test_stage.py verify-book` | exit 0: giữ 24 sheet cũ; hai sheet mới khớp ID/actual/status/spec và công thức không REF lỗi | `review-workbook.log` |
| `scratch/audit_test_stage.py verify-stage` | exit 0: hash 8/8 giữ nguyên; tập delta thuộc plan; tập lỗi baseline khớp | `review-stage-delta.log` |
| Đọc XML/JSON độc lập bằng ElementTree, so tập failure và SHA256 10 file | exit 0 | `review-evidence-audit-final.log` |

Đối chiếu báo cáo trước: unit **1466 pass/30 fail/0 skip**; integration **1101 pass/18 fail/1 XPASS/0 skip**; targeted 48 pass. Baseline unit dùng JSON thực thi kèm log (không có XML baseline unit); baseline integration có XML đủ 18 fail. Đã kiểm tập fail bằng nhau, không chỉ số lượng. Không chạy lại full suite hoặc baseline toàn bộ trong lượt review; đây là đối chiếu evidence giai đoạn test đã approved. Full suite không xanh; việc khớp baseline không phủ nhận lỗi mới ở R1 vì trước đó chưa có test cho biên này.

Ruff trước đó 31 lỗi hiện tại/31 baseline/0 introduced, khớp log `test-lint-baseline.log`; chưa chạy lại toàn Ruff trong review. Hai nhóm warning targeted là Starlette TestClient deprecation sẵn có. Workbook được kiểm dữ liệu; không render hoặc kiểm trực tiếp Microsoft Excel lại trong review, 05 giữ bằng chứng hiển thị trước đó.

## 4. Phát hiện

| ID / Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| **R1 / High (P1)** | `backend/src/drugtime/modules/catalog/application/normalize_ocr.py:19–22`, sử dụng trong `_groups` dòng 79–96 | `_NUMBER_LIKE` và `_ATTACHED_AMOUNT` bắt buộc ký tự số đầu là `[0-9]`. Nhóm như `O.5g`, `O.5 g`, `l0mg`, `l0 mg` không được ghi nhận là nhóm nghi ngờ. Với `Thuoc 500mg O.5g`, kết quả là `name_key='thuoc o.5g'`, `strength_text='500 mg'`, status `parsed`. Nhóm 500mg bị tách/chọn trong khi có hàm lượng chưa hiểu cạnh tranh; vi phạm AC6/03 mục 1c. Builder cũng dùng chính normalizer nên chịu cùng sai phân loại. | Mở lại implement; mở rộng **nhận diện tín hiệu nghi ngờ** để giữ nguyên cả text/unparsed, strength None/parts rỗng khi có nhóm cạnh tranh dạng này. Không biến O/l thành số, không nới grammar parse và không gán mọi tên chứa số thành hàm lượng. Thêm regression attached/spaced/hoa thường + nhóm hợp lệ trước/sau, giữ các ca B12/D3/tên và metadata. Chạy lại targeted và cập nhật test case/Bug Report trong giai đoạn test sau sửa. |

Bằng chứng tối thiểu tái chạy từ gốc:

```powershell
$env:PYTHONPATH = 'D:/DrugTime/source/DrugTime/backend/src'
& backend/.venv/Scripts/python.exe -m pytest -p no:cacheprovider work/4.12-ocr-text-normalization-catalog-index/scratch/test_review_regression.py
```

Scratch chỉ là bằng chứng review, không đề xuất commit. Để evidence vẫn hữu dụng sau bỏ scratch, 4 input/expected/actual đều có trong log/XML và bảng trên. Chưa sửa testcases.json/workbook hoặc 05 đã approved; 35 kết quả Pass vẫn phản ánh các ca đã chạy, cần bổ sung ca lỗi và Bug Report khi reopen test.

## 5. Mô tả PR

Chưa soạn mô tả PR sẵn để mở vì còn High; wf-review chỉ yêu cầu phần này khi Đạt/Đạt kèm lưu ý. Chưa mở PR, commit/push, merge hay bump gitlink. Sau sửa và review lại: PR backend, docs workbook và superproject artifact/gitlink; merge backend/docs trước superproject, chỉ bump SHA đã push. Kiểm lại base docs đang chứa test case 4.16 trước khi mở PR.

## 6. Ghi chú cho quy trình / phát sinh

- Khi xác định giai đoạn, agent đã đọc 04/05 trước khi nạp wf-review. Vì vậy không đánh dấu đã tuân thủ yêu cầu đọc diff trước tự thuật. Đã bù bằng đối chiếu code/01/03, probe độc lập, rerun 156+48 test và kiểm evidence; không coi đó là thay thế một người review PR khác theo DoD.
- Scope implement ở cuối review sẽ báo integration test đã duyệt của giai đoạn test là NGOÀI; scope test sẽ báo 8 file implement giữ lại. Cần phân biệt phạm vi toàn task với phạm vi ghi mới của từng giai đoạn. Chỉ ghi sự thật và ngoại lệ đã chấp nhận, không thay tool/gate/approval.
- Kiểm evidence lượt đầu giả định có test-baseline-unit.xml và dừng với FileNotFoundError; giữ `review-evidence-audit.log` lỗi này, không dùng làm bằng chứng pass. Lượt cuối đọc đúng JSON unit + XML integration, exit 0 tại `review-evidence-audit-final.log`.
- Sandbox lần đầu chặn ghi review-gate.log; lần chạy lại được auto-review cho phép, gate exit 0. Không đổi quyền hay cấu hình sandbox.
- Handoff theo wf-handoff: review đã hoàn thành, sửa R1 chưa bắt đầu. Source backend/test sản phẩm/workbook không bị sửa bởi lượt review. Evidence ghi SHA256; hash implement vẫn 8/8 như trước test.

## Bước tiếp theo

- Đang chờ người dùng mở lại implement để sửa R1, theo AGENTS.md và wf-review: agent review không sửa code và không tự reopen/approve.
- Lệnh cần chạy trong terminal của người duyệt:

```powershell
& 'C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' .agents/scripts/gate.py reopen 4.12-ocr-text-normalization-catalog-index implement
```

- Sau đó gửi `tiếp tục 4.12`: agent kiểm gate implement, sửa detector/test thuộc plan; không sửa requirement/plan approved. Sau duyệt implement cần test/review lại theo gate, gồm bổ sung test case/Bug Report và chạy hồi quy. Approval downstream có thể hết hiệu lực theo nội dung đầu vào.
- Nếu muốn duyệt riêng **báo cáo review với kết luận Chưa đạt**, người duyệt có thể chạy `gate.py approve 4.12-ocr-text-normalization-catalog-index review`; việc đó không khắc phục R1 hoặc đủ điều kiện merge. Không cần duyệt review để mở lại implement.
- Chưa commit: backend gồm đúng 9 file ở bảng 03 (5 source, 3 unit, 1 integration); docs 1 workbook; superproject có gitlink api_contract/backend/docs/frontend/tests khác checkout gốc và work/4.12 đang ignore. Không stage các gitlink ngoài task. Không có sửa code dở thêm từ review.
- Lệnh lưu artifact, **chỉ chạy khi người dùng yêu cầu commit**; không stage scratch:

```powershell
git add -f -- work/4.12-ocr-text-normalization-catalog-index/01-requirement.md work/4.12-ocr-text-normalization-catalog-index/03-plan.md work/4.12-ocr-text-normalization-catalog-index/04-impl-notes.md work/4.12-ocr-text-normalization-catalog-index/05-test-report.md work/4.12-ocr-text-normalization-catalog-index/06-review.md work/4.12-ocr-text-normalization-catalog-index/testcases.json work/4.12-ocr-text-normalization-catalog-index/testcases.xlsx work/4.12-ocr-text-normalization-catalog-index/evidence/
git diff --cached --stat
git commit -m 'docs(ocr): record 4.12 review and parser finding'
git push -u origin feat/4.12-ocr-text-normalization-catalog-index
```

- Code backend/workbook giữ chưa commit đến khi sửa/kiểm R1 hoặc người dùng yêu cầu lưu WIP; trước commit stage đúng từng file trong 03, review staged diff, push backend/docs trước bump superproject theo wf-git. Không chạy các lệnh commit/push trong lượt này.
- Cập nhật lần cuối: 2026-10-28 13:30 +0700, Codex.
