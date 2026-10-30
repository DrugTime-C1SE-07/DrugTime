---
task: 4.12-ocr-text-normalization-catalog-index
stage: implement
owner: phucnguyenngoc
started_at: 2026-10-28 12:53
status: draft
---

# 4.12 · Implement

**Cập nhật sau mở lại implement:** mục 1–6 bên dưới giữ lịch sử lượt implement đầu (13:03). Kết quả thực thi mới, sửa R1/High từ review và trạng thái bàn giao hiện tại nằm ở mục 7 và “Bước tiếp theo”. Những câu “trong phiên này” ở mục lịch sử chỉ lượt đầu, không phải lượt sửa R1.

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | DTO frozen, tuple, mapping chỉ đọc; unit index 12 passed | `evidence/implement-P4-P6.log` |
| P2 | xong | Subset ký tự/noise/tên số/metadata/blank/type/I/O: 24 passed, 57 deselected tại lượt đầu; toàn bộ ca cuối nằm trong 97 test normalizer pass | `evidence/implement-P2.log`, `evidence/implement-catalog-targeted.log` |
| P3 | xong | Full normalizer cuối: 97 passed; grammar MVP bảo thủ, giữ nhóm sai/không rõ, dấu âm tách và nhóm cạnh tranh có dấu câu | `evidence/implement-P3.log`, `evidence/implement-catalog-targeted.log` |
| P4 | xong | Builder/loader giữ raw/null/ID, thứ tự ổn định, đọc mới và truyền lỗi; unit index 12 passed | `evidence/implement-P4-P6.log` |
| P5 | xong mức implement | Một SELECT toàn bộ active, map DTO; unit adapter trong 12 passed. PostgreSQL thật chờ P8 | `evidence/implement-P4-P6.log` |
| P6 | xong | Facade và hai consumer tổng hợp với hai UoW; unit index 12 passed | `evidence/implement-P4-P6.log` |
| P7 | xong | Catalog + architecture 156 passed; toàn bộ unit/architecture 1466 passed, 30 failed có sẵn; lint 31 lỗi có sẵn, 0 mới; scope exit 0 | `evidence/implement-catalog-targeted.log`, `evidence/implement-final-backend.log`, `evidence/implement-lint-baseline.log`, `evidence/implement-scope.log` |
| P8 | chưa làm — giai đoạn test | PostgreSQL thật sau duyệt implement | |
| P9 | chưa làm — giai đoạn test | Excel test case sau duyệt implement | |

## 2. File đã thay đổi

8/8 file backend thuộc phạm vi implement đã duyệt; cùng nhánh `feat/4.12-ocr-text-normalization-catalog-index` ở superproject và backend. Chưa commit/push.

| Submodule | File | Thay đổi |
|---|---|---|
| backend | `src/drugtime/modules/catalog/domain/catalog_index.py` | Thêm DTO frozen/enum; tuple và copy mapping chỉ đọc bảo vệ snapshot. |
| backend | `src/drugtime/modules/catalog/application/normalize_ocr.py` | Thêm normalizer ký tự và parser toàn biểu thức theo grammar MVP. |
| backend | `src/drugtime/modules/catalog/application/build_catalog_index.py` | Thêm builder/port/loader; sort ID, giữ raw/null, đọc mới mỗi lần và truyền lỗi. |
| backend | `src/drugtime/modules/catalog/adapters/outbound/sql_catalog.py` | Chỉ thêm `list_for_index`: một SELECT toàn bộ active, ORDER BY ID, giữ EXISTS ánh xạ. |
| backend | `src/drugtime/modules/catalog/api.py` | Export DTO/normalizer/builder/loader; ghi trách nhiệm giao dịch mới của caller. |
| backend | `tests/unit/test_catalog_ocr_normalization.py` | Thêm 97 ca tổng hợp; Unicode/noise/số/grammar/unsupported/malformed/idempotence/I/O. |
| backend | `tests/unit/test_catalog_index.py` | Thêm 12 test snapshot/raw/null/ID/trùng khóa/bất biến/đọc mới/lỗi/2 consumer/adapter/no I/O. |
| backend | `tests/unit/test_catalog_sync.py` | Thêm 1 regression ingest NFD → NFC, giữ dấu/hoa thường tên/hoạt chất. |

Không sửa integration test, workbook, HTTP router, migration, writer hoặc import liên module. `scope.py --stage implement` cuối exit 0, không có `[NGOÀI]`; log `evidence/implement-scope.log`. `[CHƯA SỬA]` workbook thuộc P9, đúng ranh giới giai đoạn.

## 3. Kết quả test cuối

Tất cả lệnh dưới đã chạy trong phiên này. Backend dùng `backend/.venv/Scripts/python.exe` (Python 3.14.7; pytest 9.1.1, Ruff 0.16.10). Lệnh backend chạy từ `backend`; output thô lưu bằng `2>&1 | Tee-Object` và kiểm exit code.

| Lệnh | Kết quả thực tế | Log |
|---|---|---|
| `python -m pytest tests/unit/test_catalog_ocr_normalization.py tests/unit/test_catalog_index.py tests/unit/test_catalog_sync.py tests/unit/test_catalog_search.py tests/unit/test_catalog_crud.py tests/architecture` | exit 0: **156 passed**, 1 warning, 0 skipped; gồm 97 normalizer + 12 index + 3 ingest + 10 search + 19 CRUD + 15 architecture | `evidence/implement-catalog-targeted.log` |
| `python -m pytest tests/unit tests/architecture` (cuối) | exit 1: **1466 passed, 30 failed**, 8 warnings, 0 skipped; toàn bộ 15 architecture pass | `evidence/implement-final-backend.log` |
| Cùng bộ unit/architecture, lượt trước hoàn thiện thêm 16 biên parser | exit 1: 1450 passed, cùng 30 failed, 8 warnings | `evidence/implement-unit-architecture.log` |
| Chạy 6 file test bị lỗi với source nguyên bản backend HEAD `2439aa66`, import từ bản trích xuất riêng trong scratch | exit 1: **86 passed, 30 failed**, 1 warning; tập nodeid fail trùng hoàn toàn full suite, **0 lỗi mới** | `evidence/implement-baseline-unit.log` |
| `python -m ruff check .` | exit 1: **31 lỗi** ở 11 file; tất cả có sẵn tại HEAD, không có lỗi lint mới | `evidence/implement-lint.log` |
| `python work/.../scratch/compare_lint_baseline.py` (từ gốc bằng backend Python) | exit 0: current 31 / baseline 31 / introduced 0, so code + message + dòng nguồn từ `git show HEAD:<file>` | `evidence/implement-lint-baseline.log` |
| `python -m ruff check` với 7 file mới/sửa (trừ SQL adapter có 2 E501 baseline) | exit 0: All checks passed | `evidence/implement-lint-changed.log` |
| `ruff format` với 7 file mới/sửa trên | Đã format; SQL adapter chỉ giữ hunk thêm reader, không để format lan vào search/CRUD cũ | `evidence/implement-format-final.log` |
| Runtime workflow tuyệt đối + `.agents/scripts/scope.py 4.12-ocr-text-normalization-catalog-index --stage implement` | exit 0: 8 file backend đúng phạm vi | `evidence/implement-scope.log` |

30 lỗi nền gồm 24 ca contract thiếu path/khác semantics trong checkout `api_contract` hiện tại và 6 ca invalid-auth profile mong 401 nhưng nhận 422. Đã chạy lại bằng source HEAD chưa có `list_for_index`, cùng dependencies và cùng contract hiện tại; không suy baseline chỉ từ tên test. Script tái hiện và JSON outcome nằm trong scratch, không đề xuất commit. Danh sách nodeid và traceback trong log baseline/full; không sửa source/test cũ/contract để làm xanh các lỗi ngoài phạm vi.

Các warning là Starlette TestClient deprecation và JWT HMAC ngắn trong fixture unit auth hiện hữu; không chứa credential thật. Không gọi full suite là pass. Integration PostgreSQL, DB reset và Excel chưa chạy ở implement; AC10/AC11 mức DB và AC12 search integration chờ P8.

## 3b. Bộ test case Excel

Task M: làm ở giai đoạn test (P9).

## 4. Migration

Không có.

## 5. Ghi chú cho người review

- Đã đối chiếu trực tiếp QD-36/38/39/45 và BQ-042 trong tài liệu quyết định với 01/03: không phát hiện mâu thuẫn; giữ format MVP đã duyệt, không tự quy đổi hoặc xác nhận thuốc.
- Gate implement cho phép bắt đầu; 01 và 03 còn hiệu lực. Python mặc định WindowsApps không chạy; workflow dùng runtime tuyệt đối đã ghi trong 03.
- Hai repo đang trên nhánh local `feat/4.12-ocr-text-normalization-catalog-index`, chưa commit/push. Backend HEAD ban đầu `2439aa66`, khác main local `33867bff`; giữ base đã khảo sát trong plan. Superproject đã tách base về `origin/main` (`a6d2f88`) theo xác nhận trực tiếp của người dùng. Con trỏ api_contract/backend/frontend/tests đã khác từ đầu; docs khác thêm do đổi gitlink base, không sửa nội dung submodule này.
- `parsed` chỉ nói nhận diện cú pháp; không xác minh dược, không tự sửa O/0/l/1, không suy ánh xạ hoạt chất hoặc hàm lượng nguồn từ tên. Tách toàn nhóm đơn/nồng độ/phối hợp/phần trăm trong MVP; IU/UI/µg/μg và dạng ngoài danh sách vẫn chưa phân tích.
- `normalized_text` giữ toàn bộ text đã chuẩn hóa; chỉ `name_key` bỏ span hàm lượng hợp lệ. Token có dấu câu/dấu âm/quan hệ dang dở vẫn chặn việc lấy một nhóm hợp lệ khác. Đây là giữ tín hiệu chưa chắc chắn, không mở rộng grammar nhận hàm lượng.
- Index không cache nội dung; caller 4.13/4.15 phải tạo UoW/giao dịch mới mỗi lượt. Snapshot chỉ mới tại SELECT; đối chiếu lại ID/trạng thái khi xác nhận thuộc task tích hợp.

### Truy vết nghiệp vụ → AC → kiểm chứng

| Quy tắc nguồn (giữ trạng thái như 01/03) | AC / bước | Bằng chứng implement / giới hạn |
|---|---|---|
| QD-36 ✅: giữ ID, ngừng chọn mới thuốc đã gỡ; người dùng chốt không cache | AC8–AC11 / P1,P4–P6 | Unit giữ mọi ID, raw/null, bất biến, sort, reader được gọi mỗi lần và lỗi không fallback; SQL lọc deleted. DB thật P8 chưa nghiệm thu. |
| QD-38 ✅ và BQ-042 ❓: hàm lượng khác lượng dùng, dương, không tự quy đổi; dùng format task đã duyệt | AC3–AC6 / P2,P3 | 97 ca normalizer bao gồm 0/âm/đơn vị ngoài MVP/lỗi OCR/nhóm cạnh tranh; metadata, B12/D3 và quy cách còn nguyên. |
| QD-39 ✅: người dùng kiểm tra, chỉ catalog, không tự chọn/khôi phục Admin đối soát | AC8,AC13,AC14 / P1–P6 | DTO không có confidence/chọn thuốc; giữ nguồn và has_active_ingredients; facade chung, không endpoint/writer/UI mới. |
| QD-39 ✅: nếu lưu OCR phải mã hóa/xóa; task không lưu | AC13 / P2–P6 | Guard file/mạng/writer, caplog/capsys không chứa marker; source hàm thuần, loader chỉ SELECT. Không triển khai hoặc tuyên bố nghiệm thu cơ chế lưu OCR. |
| QD-45 ✅: contract/backlog chuẩn | AC12,AC14 / P6,P7 | Regression ingest/search/CRUD và architecture pass, SQL diff chỉ thêm reader; API HTTP không sửa. 30 lỗi contract/profile nền đã chứng minh; integration search chờ P8. |

AC1/AC2/AC7 được kiểm trong normalizer (Unicode/noise/rỗng/non-string với lỗi cố định không echo dữ liệu). Không áp dụng PEP/consent/dose race hoặc schema migration vì chỉ catalog/text nội bộ, không truy cập patient, không đổi engine tương tác.

## 6. Phát sinh

- Sandbox không cho tạo lock nhánh ở lần đầu; thao tác tạo nhánh local được auto-review cho phép khi chạy lại với quyền phù hợp. Không thay cấu hình quyền.
- Scope lần đầu báo 179 artifact 4.16 ngoài phạm vi vì nhánh mới kế thừa commit superproject `cf7ba94`. Đã dừng mutation, fetch xác minh commit chưa vào origin/main, hỏi và nhận xác nhận “Cho phép tách base về origin/main”. Chuyển riêng nhánh superproject chưa có commit mới về `a6d2f88`; giữ nhánh 4.16 tại `cf7ba94`, toàn bộ work/4.12 và source backend. Scope sau đổi base exit 0, đủ 8 file backend trong plan. Log: `evidence/implement-scope-before.log` (exit 1), `evidence/implement-scope-base.log` (exit 0). Không sửa artifact approved hoặc thêm phạm vi.
- Ruff phát hiện 31 lỗi có sẵn (gồm 2 E501 SQL Admin CRUD, nay dòng 104/106 sau thêm reader); toàn bộ đã đối chiếu với source HEAD, 0 lỗi mới. Không sửa file ngoài phạm vi để dọn lint.
- Kiểm độc lập đã phát hiện và sửa trong phạm vi parser hai biên: dấu âm tách whitespace và nhóm cạnh tranh bị che bởi dấu câu (`500mg 250mg,`, `500mg 25mcg.`)/biểu thức thiếu đơn vị (`500mg 5/ml`). Tất cả giữ unparsed/toàn text, không chọn nhóm đầu; test hồi quy có trong 97 ca cuối. Các ca này làm rõ yêu cầu bảo thủ đã duyệt, không thêm đơn vị hoặc đổi nghiệp vụ.
- Toàn bộ unit/architecture không xanh vì 30 lỗi nền đã tái hiện trên source HEAD; không phải regression của 4.12. Giới hạn này cần reviewer biết trước bước test, không che bằng skip/đổi expected.

## 7. Sửa R1 sau review — 28/10/2026

### Phạm vi và kết quả

- Người dùng thông báo đã reopen implement vì lỗi phát hiện ở review. Gate với ID đầy đủ cho phép bắt đầu, owner vẫn là `phucnguyenngoc`; không có contract stage. Đọc lại 01/03/04/06 và QD-36/38/39/45, BQ-042 trong nguồn nghiệp vụ. Không có thay đổi nghiệp vụ hoặc phạm vi cần sửa plan.
- R1: detector cũ chỉ nhận số bắt đầu bằng chữ số, nên bỏ qua `O.5g`, `O.5 g`, `l0mg`, `l0 mg`, rồi tách nhầm `500mg` còn lại. Bổ sung 28 regression/ca bảo vệ và chạy trước khi sửa: 22 fail đúng nguyên nhân, 6 pass.
- Sửa riêng tín hiệu nhận diện: nhánh tiền tố `o/l` chỉ gồm ký tự số/nghi ngờ/dấu phân cách và phải chứa ít nhất một chữ số thật, theo sau là đơn vị. Quy tắc này nhận nhóm nghi ngờ để trả `unparsed`, giữ toàn text, `strength_text=None`, parts rỗng; không thay O/l, không đổi `_NUMBER` hoặc grammar parse. Điều kiện chữ số tránh bắt các từ `Long`, `Log`, `Ong` như hàm lượng.
- Chỉ sửa **3 file backend** ở bảng 03: `application/normalize_ocr.py`, `tests/unit/test_catalog_ocr_normalization.py`, `tests/unit/test_catalog_index.py`. Test mới phủ viết liền/cách đơn vị, hoa/thường, dấu chấm/phẩy, nhóm nghi ngờ đứng riêng/trước/sau nhóm hợp lệ, giữ B12/D3/tên/metadata và lan truyền đúng vào khóa tên/hoạt chất/hàm lượng của index.
- Truy vết: QD-38 ✅ + BQ-042 ❓ → AC3/AC6/AC8 → P3/P4/P7 → 28 ca mới. Không mở rộng đơn vị/quy đổi hay tự xác minh thuốc; không ghi/log OCR. P1–P7 giữ hoàn tất, bổ sung sửa R1 đã xong **3/3 công việc** (regression trước sửa, detector/test, kiểm chứng cuối).

| Công việc | Trạng thái | Bằng chứng |
|---|---|---|
| R1-1: viết regression và chứng minh lỗi trước sửa | xong | `implement-R1-before.log/.xml`: 22 failed, 6 passed, 109 deselected |
| R1-2: sửa detector trong P3, kiểm normalizer/index/hồi quy | xong | `implement-R1-targeted.log/.xml`: 184 passed, gồm 121 normalizer + 16 index + 3 ingest + 10 search + 19 CRUD + 15 architecture |
| R1-3: toàn unit/architecture, lint/format, đối chiếu phạm vi | xong với giới hạn lỗi nền/scope giữ lại | Log và audit bên dưới |

### Kiểm tra thực thi trong lượt sửa

Lệnh backend chạy từ `backend`, dùng `.venv/Scripts/python.exe`, output lưu bằng `2>&1 | Tee-Object`; không skip test. Mọi log bên dưới nằm trong `work/4.12-ocr-text-normalization-catalog-index/evidence/`.

| Lệnh / kiểm tra | Kết quả | Log |
|---|---|---|
| Python tuyệt đối + `gate.py 4.12-ocr-text-normalization-catalog-index implement` | exit 0, cho bắt đầu | `implement-R1-gate.log` |
| `python -m pytest -p no:cacheprovider tests/unit/test_catalog_ocr_normalization.py tests/unit/test_catalog_index.py -k 'ocr_corrupted_leading_digit or corrupted_competing_strength or names_do_not' --junitxml=...` trước sửa source | exit 1: **22 failed, 6 passed**, 109 deselected | `implement-R1-before.log`, `.xml` |
| `python -m pytest -p no:cacheprovider tests/unit/test_catalog_ocr_normalization.py tests/unit/test_catalog_index.py tests/unit/test_catalog_sync.py tests/unit/test_catalog_search.py tests/unit/test_catalog_crud.py tests/architecture --junitxml=...` | exit 0: **184 passed**, 1 warning; toàn bộ 22 ca từng fail đã pass | `implement-R1-targeted.log`, `.xml` |
| `python -m pytest -p no:cacheprovider tests/unit tests/architecture --junitxml=...` | exit 1: **1494 passed, 30 failed**, 8 warnings, 0 skip | `implement-R1-final-backend.log`, `.xml` |
| `python -m ruff format --check` và `python -m ruff check` trên đúng 3 file sửa | cả hai exit 0: 3 files already formatted / All checks passed | `implement-R1-format.log`, `implement-R1-lint-changed.log` |
| `python -m ruff check .` | exit 1: 31 lỗi | `implement-R1-lint.log` |
| `python work/.../scratch/compare_lint_baseline.py` | exit 0: 31 hiện tại / 31 có sẵn ở HEAD / 0 mới | `implement-R1-lint-baseline.log` |
| `scope.py 4.12-ocr-text-normalization-catalog-index --stage implement` | **exit 1**: 9 OK, 1 NGOÀI là integration test từ P8; không gọi raw scope là pass | `implement-R1-scope.log` |
| `python work/.../scratch/audit_implement_R1.py` (từ gốc) | exit 0: tập 30 fail trùng XML giai đoạn test trước và JSON baseline HEAD; 3/3 file delta thuộc plan implement; 37/40 file snapshot giữ hash, gồm integration test/workbook | `implement-R1-evidence-delta-audit-final.log` |

Không chạy lại baseline unit trên source HEAD trong lượt này: audit chỉ đối chiếu chính xác nodeid với evidence trước, không suy từ số lượng. Ruff baseline đã thực thi lại trong lượt này. Không chạy integration/DB reset, không dựng lại Excel ở implement; cần thực hiện sau duyệt implement trong giai đoạn test.

### Phát sinh và giới hạn bàn giao

- Raw scope báo `backend/tests/integration/test_catalog_index.py` vì file P8 còn chưa commit từ giai đoạn test đã approved trước khi reopen; đúng giới hạn đã ghi ở 06 mục 2/6. File nằm trong 03 nhưng bị loại ở stage implement. Hash trước/sau chứng minh không sửa file này, workbook cũng giữ nguyên. Delta thực tế chỉ 3 file hợp lệ trong plan, không thêm file sản phẩm ngoài phạm vi và không sửa scope/gate để né lỗi.
- Sandbox chặn ghi log/snapshot lần đầu; lần chạy với escalation được auto-review cho phép. Không thay quyền/cấu hình. Alias WindowsApps `python` không chạy được, nên workflow dùng Python tuyệt đối.
- Audit scratch lần đầu truyền thiếu bảng plan vào `scope.evaluate`, exit 1 sau khi kiểm xong test; đã sửa script audit để truyền `scope.plan_entries(TASK)` và chạy lại thành công. Giữ `implement-R1-evidence-delta-audit.log` lỗi đầu, chỉ dùng log `...-final.log` làm bằng chứng kết luận.
- 30 test fail và 31 lỗi lint nền vẫn còn; không tuyên bố toàn suite xanh. R1 đã sửa theo regression, nhưng chưa có test/review mới nghiệm thu sau sửa; không đổi kết luận `Chưa đạt` trong 06.
- Không sửa 01/03/05 đã approved, testcases.json/workbook hoặc artifact review. Các hash code ở 05/06 là snapshot trước sửa R1, phải cập nhật ở giai đoạn tương ứng sau khi người dùng reopen theo gate.

## Bước tiếp theo

- Đã xong **7/7 bước implement và 3/3 công việc sửa R1**. Đang chờ người duyệt đọc mục 7, diff 3 file và evidence, rồi duyệt lại implement. Không còn câu hỏi nghiệp vụ chặn trong phạm vi sửa này.
- Người duyệt tự chạy trong terminal (agent không chạy lệnh duyệt):

```powershell
python .agents/scripts/gate.py approve 4.12-ocr-text-normalization-catalog-index implement
```

- Nếu alias Python WindowsApps lỗi, thay `python` bằng `& 'C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe'`.
- Sau duyệt, ở lượt riêng dùng wf-next/gate để xác định trạng thái test. 05 cũ còn approved nhưng input implement thay đổi sẽ làm approval cũ hết hiệu lực; người duyệt reopen test khi gate yêu cầu, rồi chạy lại integration/hồi quy và bổ sung ca R1 + Bug Report trước review lại. Không coi 35 ca Excel cũ là phủ regression mới.
- Chưa commit/push. Backend vẫn có 9 file task chưa commit; docs có workbook P9 cũ; superproject có các gitlink khác từ trước và work/4.12 đang ignore. Lượt này chỉ đổi 3 file backend cùng 04/evidence/scratch của task; không stage scratch hoặc gitlink ngoài task.
- Khi người dùng yêu cầu lưu code/artifact: commit và push backend trước; chọn 8 file implement + integration đã làm ở 03 sau kiểm staged diff. Commit docs workbook ở repo docs khi xử lý test. Superproject chỉ bump đến SHA đã push, rồi stage artifact không gồm scratch, ví dụ `git add -f -- work/4.12-ocr-text-normalization-catalog-index/04-impl-notes.md work/4.12-ocr-text-normalization-catalog-index/evidence/`; commit Conventional Commits và push nhánh task theo wf-git.
- Cập nhật lần cuối: 2026-10-28 13:55 +0700, Codex.
