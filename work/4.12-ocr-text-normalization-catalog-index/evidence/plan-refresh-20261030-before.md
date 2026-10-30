---
task: 4.12-ocr-text-normalization-catalog-index
stage: plan
status: draft
---

# 4.12 · Plan chuẩn hóa văn bản OCR và index danh mục thuốc

## 1. Giải pháp

Đầu vào đã duyệt: `01-requirement.md`, size M, `contract_change: no`. Gate plan cho phép bắt đầu; không có giai đoạn contract. Thực hiện trong module `catalog` của backend, dùng thư viện chuẩn Python; không tạo module OCR hoặc dependency liên module mới.

### 1a. Luồng và giao diện nội bộ

1. `normalize_ocr_text(text: str) -> NormalizedOcrText` là hàm thuần cho một vỏ thuốc, kể cả nhiều dòng. Chỉ nhận `str`; kiểu khác phát sinh `TypeError` với thông báo cố định không chứa đầu vào.
2. `build_catalog_index(medications: Iterable[CatalogMedication]) -> CatalogIndex` là builder thuần. Dùng cùng normalizer cho tên và hoạt chất thô, giữ nguyên DTO nguồn. Dựng lại bằng cách gọi lại builder với dữ liệu mới; không có state hoặc thao tác refresh riêng.
3. Application có port `CatalogIndexReader.list_for_index(uow)` và use case `load_catalog_index(uow, reader)`: đọc toàn bộ catalog active rồi gọi builder, mỗi invocation đều đọc lại. Facade `catalog.api.load_catalog_index(uow)` lắp `SqlCatalog` vào port; export DTO và hai hàm thuần qua facade để 4.13/4.15 dùng chung.
4. Consumer mở UoW/giao dịch đọc mới cho mỗi lượt bằng pattern `shared.db.unit_of_work()`, gọi loader một lần, dùng index trong lượt đó rồi bỏ. Loader không giữ snapshot trong module, singleton, closure, Redis hoặc file. Engine/connection pool hiện có không phải cache nội dung catalog.
5. SQL reader mới thực hiện một `SELECT` lấy đủ trường của `CatalogMedication`, `WHERE m.deleted_at IS NULL ORDER BY m.id`; giữ cách tính `has_active_ingredients` bằng `EXISTS` hiện có. Không dùng search, phân trang Admin hoặc vòng lặp nhiều trang: tránh giới hạn 50 và tránh ghép nhiều snapshot. Lỗi DB truyền lên caller; chỉ truy vấn thành công có 0 dòng mới trả index rỗng.

Facade nhận UoW theo pattern hiện hữu; không tự mở transaction lồng bên trong. Docstring phải nêu trách nhiệm tạo giao dịch mới của caller. Tính mới được bảo đảm tại lần đọc, không khóa catalog đến lúc người dùng xác nhận. Khi tích hợp 4.13/4.15, phải gọi đường loader này cho mỗi lượt; đối chiếu lại ID/trạng thái trước xác nhận thuộc task tích hợp.

### 1b. DTO và cấu trúc index

- `NormalizedOcrText`: `normalized_text` chứa toàn bộ text sau lọc nhiễu, `name_key` chứa phần còn lại phục vụ so khớp, `strength_text: str | None`, `strength_parts: tuple[str, ...]`, `strength_status` thuộc `absent`, `parsed`, `unparsed`, `ambiguous`.
- `parsed` chỉ nghĩa là nhận diện format MVP, không có nghĩa hàm lượng hoặc tên thuốc đã được xác minh. `unparsed` biểu thị có dấu hiệu hàm lượng chưa hiểu; `ambiguous` biểu thị nhiều nhóm cạnh tranh không có quan hệ rõ. Hai trạng thái này không trả một hàm lượng được chọn tùy tiện; giữ nguyên phần nghi ngờ trong `name_key`/`normalized_text`, `strength_text=None`, `strength_parts=()`.
- `IndexedMedication`: giữ `CatalogMedication` gốc cùng kết quả normalize tên/hoạt chất, khóa hàm lượng và dạng bào chế nếu nguồn có dữ liệu. `active_ingredient` trên DTO nguồn chính là `medications.raw_active_ingredient`, không phải ánh xạ hoạt chất đã xác minh. Trường tùy chọn thiếu giữ `None`; không điền hoạt chất/hàm lượng nguồn từ suy luận trên tên.
- `CatalogIndex`: `entries` là tuple theo ID tăng dần; `name_to_ids` và `ingredient_to_ids` là mapping khóa không rỗng → tuple ID theo thứ tự tăng dần. Mapping chỉ đọc, DTO frozen và các collection lồng dùng tuple để caller không làm biến đổi index của lượt khác. Chỉ gom ID vào bucket, không gộp bản ghi. Chuỗi tùy chọn có mặt nhưng chỉ whitespace cho khóa rỗng và không tạo bucket rỗng.
- Khóa tên/hoạt chất dùng `name_key` của cùng normalizer. Khóa `strength_text` dùng biểu diễn hàm lượng khi parse được, nếu chưa hiểu giữ khóa text đã chuẩn hóa; luôn giữ trạng thái parse và text gốc để không coi khóa đó là dữ liệu xác minh. Khóa dạng bào chế chỉ áp dụng bước chuẩn hóa ký tự/whitespace. Không mở rộng alias, token scoring hoặc fuzzy matching.

### 1c. Chuẩn hóa và parser bảo thủ

Thứ tự: thay `•`, `®`, `™` bằng khoảng trắng → Unicode NFD/bỏ dấu kết hợp tiếng Việt và ánh xạ `đ/Đ` → chữ thường → gộp whitespace/trim → nhận diện cả biểu thức hàm lượng → chỉ tách span đã nhận diện trọn vẹn → gộp khoảng trắng của phần còn lại. Không dùng NFKC để tự biến đổi ký tự nghi ngờ hoặc đơn vị ngoài phạm vi. Giữ các dấu `/`, `+`, `%`, dấu thập phân và ký tự chưa được đặc tả; không xóa toàn bộ dấu câu hay chữ số. `normalized_text` không mất hàm lượng; chuẩn hóa khóa có tính idempotent.

Parser dùng grammar tường minh, kiểm biên token và tính dương của chuỗi số bằng `Decimal`, không dùng float hoặc phép quy đổi. Dấu phẩy thập phân được đổi thành chấm, không đổi độ lớn. Nhận cả viết liền/cách đơn vị, hoa/thường và whitespace quanh `/`/`+` sau bước chuẩn hóa:

Tập format MVP đóng theo bảng 7a: đơn vị đơn là `mg`, `g`, `mcg`; nồng độ là `mg/ml` hoặc `mg/<số dương>ml`; phối hợp là các thành phần `mg` nối bằng `+`; phần trăm là số dương với `%`. Chưa mở rộng nồng độ sang `g/ml`, `mcg/ml`, `mg/g` hoặc phối hợp đơn vị khác. Số gồm chữ số ASCII, có thể có một dấu thập phân giữa các chữ số; không nhận dấu âm/dương hoặc scientific notation. Cả tử và mẫu có số đều phải dương.

| Nhóm | Format MVP | Kết quả kỹ thuật |
|---|---|---|
| Đơn | `500MG`, `0,5 g`, `0.5 g`, `25 mcg` | `500 mg`, `0.5 g`, `0.5 g`, `25 mcg`; một phần |
| Nồng độ | `5 mg/ml`, `250mg/5ml` | `5 mg/ml`, `250 mg/5 ml`; giữ cả tử/mẫu; không thêm hệ số hoặc đổi đơn vị |
| Phối hợp | `500mg + 65mg` | `500 mg + 65 mg`; parts `("500 mg", "65 mg")` theo thứ tự; không lấy phần đầu |
| Phần trăm | `0,9%` | `0.9 %`; không đổi sang mg/ml |

Chỉ tách khi toàn nhóm là format hợp lệ và không có nhóm hàm lượng cạnh tranh/chưa hiểu khiến việc chọn không rõ. Ký tự dấu âm, số 0, phần số lỗi OCR, đơn vị không hỗ trợ, dấu quan hệ bị thiếu hoặc dang dở không được bỏ qua để parse một chuỗi con hợp lệ. Ví dụ `-500mg`, `0mg`, `5OOmg`, `500mg +`, `500mg + 5OOmg`, `500/65mg` giữ chưa phân tích; `500mg 250mg` là `ambiguous`, không chọn 500 hoặc 250.

Giữ `Vitamin B12`, `Vitamin D3`, tên chứa số, `O/0`, `l/1`, `20 viên`, `Số lô AB12, HSD 10/2027` trong text còn lại. Không suy metadata hoặc số lượng thành hàm lượng. Với `Thuốc Mẫu 500mg 20 viên`, chỉ phần `500mg` có thể tách; `20 vien` còn trong `name_key`. Chuỗi sau tách không được quảng bá là tên thuốc chuẩn trong catalog.

IU/UI, `µg`/`μg`, phối hợp viết tắt và dấu phân nhóm hàng nghìn nằm ngoài MVP. Trước khi parse số, coi token có phần đầu 1–3 chữ số không bắt đầu bằng 0, tiếp theo là một hoặc nhiều nhóm dấu chấm/phẩy + đúng 3 chữ số, là có nguy cơ phân nhóm và giữ `unparsed`; ví dụ `1,000 mg`/`1.000 mg` không suy thành 1000 mg. `0,5`/`0.5` không thuộc nhánh này. Chuỗi có nhiều dấu phân cách còn lại cũng không được parse một phần. Đây là quy tắc bảo thủ cho text chưa chắc chắn, không thiết lập giới hạn hàm lượng hoặc chuẩn đơn vị mới. Chỉ mở rộng grammar khi có quyết định/mẫu rõ; không dùng kế hoạch để tự chốt BQ-042.

Lựa chọn này tách normalize OCR khỏi `catalog/normalize.py` vốn phục vụ ingest giữ dấu/hoa thường. Reader riêng giữ nguyên semantics của search và chỉ tạo một snapshot DB cho mỗi lần đọc. Không cần sửa DAV sync, Admin writer, SQL function/index hoặc cơ chế invalidation.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `work/4.12-ocr-text-normalization-catalog-index/01-requirement.md`, đặc biệt mục 7/7a/8a | 14 AC, bảng format MVP và quyết định không cache đã được duyệt; không có endpoint mới. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, quy ước trạng thái; mục 2/3/14/16 | Đã đọc lại nguồn trực tiếp. Nguồn từ hồ sơ bản 3.1, baseline `QD-2026-10-03-v1` ngày 03/10/2026. QD-36/38/39/45 là ✅; nghĩa là chốt baseline, chưa xác nhận triển khai/chưa có chữ ký Mentor. BQ-042 vẫn ❓. Không phát hiện thay đổi cần reopen 01. |
| `backend/src/drugtime/modules/catalog/normalize.py`; `backend/tests/unit/test_catalog_sync.py` | Ingest NFC/gộp whitespace, nhận object; test hiện có chỉ dùng tên tiếng Anh. Cần thêm regression tiếng Việt; OCR phải có hàm riêng từ chối non-string. |
| `backend/src/drugtime/modules/catalog/domain/medication.py` | Tái dùng `CatalogMedication` frozen, có đủ ID/tên/hoạt chất thô/hàm lượng/dạng bào chế. Không sửa DTO/response search cũ. |
| `backend/src/drugtime/modules/catalog/application/search_medications.py`; `backend/src/drugtime/shared/uow.py` | Pattern application nhận Protocol/reader và UoW, không phụ thuộc SQLAlchemy. |
| `backend/src/drugtime/modules/catalog/adapters/outbound/sql_catalog.py` | Search có limit/thứ tự riêng; Admin list có phân trang và COUNT. Thêm method đọc toàn catalog, không sửa phương thức cũ. |
| `backend/src/drugtime/modules/catalog/api.py`; `backend/src/drugtime/shared/db.py` | Facade ghép adapter; UoW hiện có tạo transaction cho mỗi lần gọi. Export nội bộ không đồng nghĩa HTTP API mới. |
| `backend/tests/unit/test_catalog_search.py`; `backend/tests/integration/test_catalog_search.py` | Hồi quy sẵn có phủ trim/wildcard/q/limit, Unicode không dấu, prefix-first/name order, giữ whitespace bên trong q và alias search. |
| `backend/tests/integration/conftest.py` | DB thật local, app dùng `api_role`; fixture catalog ghi dữ liệu dùng chung và không dọn. Không được giả định catalog chỉ có fixture của test. Có thể dùng SQL cục bộ trong file test mới thay vì sửa factory vốn cố định strength. |
| `backend/tests/architecture/test_module_dependencies.py` | `catalog` chỉ phụ thuộc `identity`; giải pháp mới ở trong catalog nên không sửa matrix hoặc C4. |
| `backend/supabase/migrations/20260927082912_rebuild_schema_v11.sql`, bảng medications/grants | `deleted_at` là dấu ngừng chọn; `api_role` đã có quyền SELECT. Reader không cần migration/grant mới. |
| `backend/pyproject.toml`; `.agents/scripts/scope.py`; `.agents/skills/wf-git/SKILL.md`; `.agents/skills/wf-test/SKILL.md`; `.agents/skills/wf-testcase/SKILL.md` | Python ≥3.12; unit ở implement, integration ở test; scope chặn ghi integration tại implement. File Excel tổng được xử lý cuối test bằng script dự án. |

### Quyết định nghiệp vụ áp dụng

Các mục nguồn bên dưới thuộc cùng file quyết định đã ghi ở bảng trên. Quyết định không cache là trả lời người dùng ngày 28/10/2026 trong 01 mục 8a, không gán thành nội dung QD-36 gốc. Các test U/I được định nghĩa ở mục 5.

| Quy tắc + mục/nội dung nguồn + trạng thái | AC | Bước | Test/bằng chứng |
|---|---|---|---|
| QD-36, mục 2: giữ ID, ngừng chọn thuốc đã gỡ, không sửa lịch sử; ✅ | AC8–AC11 | P1, P4, P5, P8 | U8–U11; I1–I5 |
| QD-38, mục 2: hàm lượng khác lượng dùng, giá trị dương, không tự quy đổi; ✅ | AC3–AC6, AC13 | P2, P3 | U3–U7 |
| BQ-042, mục 2/Còn mở: danh sách đơn vị/phép quy đổi còn ❓; dùng format task đã duyệt ở 01 mục 7a, không tự nâng thành QD đã chốt | AC4–AC6 | P3 | U4–U7, gồm unsupported/ambiguous và không quy đổi |
| QD-39, mục 3: người dùng phải kiểm tra; chỉ chọn từ catalog; không gán thuốc gần giống để vượt chặn; ✅ | AC8, AC13, AC14 | P1, P4, P6 | U8, U12, U13; review không có matching/tự xác nhận |
| QD-39, mục 3: lưu OCR phải mã hóa/tối đa 24 giờ/xóa khi xác nhận hoặc hủy; ✅. 4.12 không triển khai lưu OCR | AC13 | P2–P6 | U12; kiểm đường gọi chỉ xử lý bộ nhớ, không log/storage text |
| QD-39, mục 3: không khôi phục Admin duyệt OCR không khớp; ✅ | AC13/phạm vi | P6, P7 | U12; scope/diff không có endpoint, writer hoặc Admin mới |
| QD-45, mục 14 và mục 16: contract/backlog chuẩn, không tự chốt phần còn mở; ✅ | AC12, AC14 | P6, P7, P8 | U13, R1–R3, I6; không sửa router/OpenAPI/semantics search |
| Người dùng 28/10/2026, 01 mục 8a: không cache; đọc và dựng mới mỗi lượt, dữ liệu hiện tại tại thời điểm đọc | AC10, AC11 | P4–P6, P8 | U10–U11; I1–I5; lỗi đọc không trả snapshot cũ |

Danh mục dùng chung và text nội bộ không đọc/ghi patient; không phát sinh endpoint dữ liệu sức khỏe. Không áp dụng `wf-health-endpoint` hoặc `wf-db-migration`. Các kịch bản cross-patient, rút consent, dose idempotency/race, golden interaction không có thay đổi liên quan để bổ sung test riêng trong task này. Hồi quy architecture vẫn bắt buộc.

## 3. File sẽ thay đổi (ranh giới phạm vi)

Đường dẫn tính từ gốc submodule. Tổng 10 file: backend 9 (5 source, 3 unit test, 1 integration test); docs 1 workbook ở cuối giai đoạn test. Artifact/evidence/spec Excel riêng của task chỉ ở `work/4.12-ocr-text-normalization-catalog-index/`.

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| backend | `src/drugtime/modules/catalog/domain/catalog_index.py` | Thêm | DTO normalize/entry/index và trạng thái parser; giữ dữ liệu nguồn, collection bất biến. |
| backend | `src/drugtime/modules/catalog/application/normalize_ocr.py` | Thêm | Chuẩn hóa khóa OCR và parser format MVP thuần, bảo thủ. |
| backend | `src/drugtime/modules/catalog/application/build_catalog_index.py` | Thêm | Builder, port đọc catalog và use case đọc mới mỗi invocation. |
| backend | `src/drugtime/modules/catalog/adapters/outbound/sql_catalog.py` | Sửa | Chỉ thêm `list_for_index`, đọc toàn bộ active một SELECT với thứ tự ID. |
| backend | `src/drugtime/modules/catalog/api.py` | Sửa | Export DTO/normalizer/builder/loader nội bộ và ghép reader. |
| backend | `tests/unit/test_catalog_ocr_normalization.py` | Thêm | Ma trận Unicode/nhiễu/tên số/grammar hợp lệ và chưa hiểu, kiểu đầu vào, không tác dụng phụ. |
| backend | `tests/unit/test_catalog_index.py` | Thêm | Giữ raw/ID/null, bucket trùng khóa, tính ổn định, gọi reader mới, lỗi đọc, hai caller dùng facade. |
| backend | `tests/unit/test_catalog_sync.py` | Sửa | Hồi quy ingest vẫn giữ dấu/hoa thường và NFC cho tên/hoạt chất. |
| backend | `tests/integration/test_catalog_index.py` | Thêm, giai đoạn test | Reader/loader với PostgreSQL thật bằng api_role, >50 active, rỗng, thay đổi đã commit và lỗi đọc. |
| docs | `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` | Sửa, giai đoạn test | Gộp test case/báo cáo bằng `testcase_xlsx.py`; giữ chức năng khác và kết quả đã có. |

Các test hồi quy search/architecture có sẵn chỉ chạy, không dự kiến sửa. Nếu phát hiện cần sửa ngoài bảng: ghi Phát sinh và làm rõ phạm vi trước khi sửa. Không sửa `01` đã approved.

## 4. Checklist

- [ ] P1 [backend] Định nghĩa DTO/enum kỹ thuật theo 1b; tái dùng CatalogMedication, tuple/mapping chỉ đọc và docstring phân biệt parsed với xác minh dược — file: `src/drugtime/modules/catalog/domain/catalog_index.py` — AC: AC6, AC8, AC9, AC14 — xong khi: DTO không chứa field confidence/chọn thuốc, giữ raw/null và test U8/U9 kiểm dữ liệu không mất.
- [ ] P2 [backend] Viết bước chuẩn hóa ký tự riêng, từ chối non-string, lọc đúng nhiễu quy định, giữ số và ký tự nghi ngờ — file: `src/drugtime/modules/catalog/application/normalize_ocr.py`, `tests/unit/test_catalog_ocr_normalization.py` — AC: AC1, AC2, AC3, AC7, AC13 — xong khi: U1–U3/U7/U12 pass, cùng khóa NFC/NFD, idempotent và không dính từ sau bỏ nhiễu.
- [ ] P3 [backend] Thêm parser toàn biểu thức theo 1c, chuẩn hóa đơn vị/decimal nhưng không quy đổi; chỉ tách span hợp lệ, trả unparsed/ambiguous khi cần — file: cùng hai file của P2 — AC: AC3, AC4, AC5, AC6, AC7, AC13 — xong khi: U3–U7 pass cho đơn/nồng độ/phối hợp/%, số âm/0, token số lỗi, nhóm dang dở và metadata; không parse lén chuỗi con.
- [ ] P4 [backend] Dựng index thuần và port/use case đọc mới; sort theo ID, bucket giữ mọi ID, giữ raw/null, truyền lỗi nguồn lên — file: `src/drugtime/modules/catalog/application/build_catalog_index.py`, `tests/unit/test_catalog_index.py` — AC: AC8, AC9, AC11, AC13, AC14 — xong khi: U8–U12 pass, đảo thứ tự đầu vào vẫn cho index tương đương và reader được gọi lại mỗi lần.
- [ ] P5 [backend] Thêm SQL reader đọc đủ active bằng một SELECT, tái dùng cách map CatalogMedication hiện hữu; không có LIMIT/count/phân trang hoặc write — file: `src/drugtime/modules/catalog/adapters/outbound/sql_catalog.py` — AC: AC10, AC11, AC12 — xong khi: diff chỉ thêm reader, use case/facade có thể ghép adapter; ghi rõ kiểm chứng DB thật I1–I5 ở P8 sau duyệt implement.
- [ ] P6 [backend] Ghép/export qua facade, ghi rõ caller tạo UoW mới mỗi lượt; hai caller tổng hợp dùng cùng facade, không import endpoint hoặc implementation consumer — file: `src/drugtime/modules/catalog/api.py`, `tests/unit/test_catalog_index.py` — AC: AC11, AC12, AC13, AC14 — xong khi: U10–U13 pass và architecture không phát sinh dependency mới.
- [ ] P7 [backend] Thêm hồi quy ingest tiếng Việt và chạy kiểm tra implement, lưu bằng chứng — file: `tests/unit/test_catalog_sync.py`; đọc/chạy các test hồi quy đã có — AC: AC1–AC9, AC12–AC14 — xong khi: unit/architecture và lint pass hoặc lỗi baseline được ghi đúng bằng chứng; `scope.py --stage implement` không có file ngoài phạm vi; ghi 04 rồi dừng chờ duyệt.
- [ ] P8 [backend, giai đoạn test] Viết và chạy I1–I6 trên Supabase local/DB sạch, reader dùng api_role; xác minh >50/rỗng/active/update/add/remove/restore/lỗi và bất biến snapshot cũ; chạy lại toàn bộ integration — file: `tests/integration/test_catalog_index.py` — AC: AC10, AC11, AC12 — xong khi: không skip thay bằng bằng chứng pass, không cần sửa fixture chung; đủ log test mới + toàn bộ suite. Lỗi sản phẩm đưa vào 05 để reopen implement, không sửa code sản phẩm ở test.
- [ ] P9 [docs, giai đoạn test] Theo wf-testcase viết spec test case với EP/BVA/bảng quyết định, bao phủ đủ 14 AC; validate/build/merge vào workbook tổng, ghi kết quả thật và Bug Report — file: `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`, artifact `work/4.12-ocr-text-normalization-catalog-index/testcases.json` và `testcases.xlsx` — AC: AC1–AC14 — xong khi: script exit 0, không ghi đè kết quả xung đột chưa được xử lý, scope test đúng, 05 có Pass/Fail/Pending và log tương ứng.

P1–P7 thuộc implement; P8–P9 chỉ bắt đầu sau gate test và 04 được duyệt. Test tích hợp và workbook được khai báo trước để đầy đủ ranh giới, không tạo/sửa chúng ở giai đoạn implement.

## 5. Test

### Unit

Tên dưới đây là dự kiến, có thể parametrized theo lớp dữ liệu; số hàng không phải số invocation pytest.

| Mã / Test dự kiến | AC | Submodule / nơi chứa |
|---|---|---|
| U1 `test_vietnamese_nfc_nfd_case_and_d_share_key__AC1` | AC1 | backend: `tests/unit/test_catalog_ocr_normalization.py`; NFC/NFD, `THUỐC ĐỎ` → `thuoc do`. |
| U2 `test_noise_multiline_whitespace_and_key_idempotence__AC2` | AC2 | Cùng file U1; tab/xuống dòng/•/®/™, cả nhiễu giữa hai từ, một kết quả cho một vỏ. Kiểm lại normalized_text/name_key qua toàn bộ input chuỗi U1–U7: normalize lần hai từ normalized_text phải cho cùng hai khóa, kể cả parsed/unparsed/ambiguous; không đòi khôi phục strength từ name_key đã tách. |
| U3 `test_numbers_in_names_and_ocr_confusables_are_preserved__AC3` | AC3 | Cùng file U1; B12/D3, tên chứa số, O/0/l/1, không tự có strength. |
| U4 `test_simple_strength_spacing_units_and_decimal__AC4` | AC4 | Cùng file U1; toàn bộ mẫu đơn của 7a, chữ hoa, viết liền/cách, comma/dot; 0.5 g vẫn là g. |
| U5 `test_concentration_combination_and_percent_preserve_structure__AC5` | AC5 | Cùng file U1; `5 mg/ml`, `250mg/5ml`, `500mg + 65mg`, `0,9%`; kiểm cả text, parts, dấu quan hệ và thứ tự. |
| U6 `test_invalid_unsupported_and_competing_strengths_are_retained__AC6` | AC5, AC6 | Cùng file U1; `-5mg`, `0mg`, `5OOmg`, `500mg +`, `500mg + 5OOmg`, `500mg 250mg`, IU/UI/µg/μg, `500/65mg`, dấu phân nhóm; thêm `250mg/0ml`, `250mg/-5ml`, `250mg/5OOml`, `250mg/`, `5 g/ml`, `5 mcg/ml`, `5 mg/g`. Giữ cả nhóm chưa hiểu, không lấy riêng tử số hoặc một thành phần. |
| U7 `test_packaging_metadata_blank_and_wrong_input_types__AC6_AC7` | AC6, AC7 | Cùng file U1; `20 viên`, `Thuốc Mẫu 500mg 20 viên`, số lô/HSD giữ nguyên; rỗng/whitespace/chỉ nhiễu trả rỗng/absent; None/int/bytes/list → TypeError không echo dữ liệu. |
| U8 `test_index_preserves_original_fields_and_optional_values__AC8` | AC8 | backend: `tests/unit/test_catalog_index.py`; raw dấu/hoa thường, null/whitespace, đủ khóa khi có dữ liệu; query/catalog cùng normalize; không suy ánh xạ hoặc strength nguồn. |
| U9 `test_equal_keys_keep_all_ids_forms_and_strengths__AC9` | AC9 | Cùng file U8; tên/hoạt chất trùng khóa khác ID/hàm lượng/dạng; tuple/map bất biến; không ghi đè bucket. |
| U10 `test_build_order_is_stable_and_loader_reads_each_time__AC11` | AC11 | Cùng file U8; reader giả lần A/B khác dữ liệu, gọi hai lần đọc hai lần; input đảo thứ tự vẫn cùng index; A không bị đổi khi tạo B. |
| U11 `test_read_failure_after_success_propagates_without_fallback__AC11` | AC11 | Cùng file U8; sau A reader ném lỗi → cùng loại lỗi tới caller, không trả A hoặc index rỗng. |
| U12 `test_normalize_and_build_have_no_ocr_persistence_or_external_calls__AC13` | AC13 | Cả hai file U1/U8; marker tổng hợp trong caplog/capsys không xuất hiện, guard đường I/O file/mạng và writer; chỉ normalize/builder thuần chạy dưới guard. Không mock chính logic cần kiểm; review bổ sung đường gọi loader chỉ có SELECT. |
| U13 `test_two_consumers_share_catalog_facade_contract__AC14` | AC14 | Cùng file U8; hai caller tổng hợp 4.13/4.15 import DTO/hàm từ catalog.api; fake reader/SqlCatalog boundary cho loader, UoW tách biệt; không tạo module/route consumer thật. |
| R1 `test_ingest_preserves_vietnamese_case_accents_and_nfc__AC12` mới | AC12 | backend: `tests/unit/test_catalog_sync.py`; tên/hoạt chất NFD → NFC nhưng giữ dấu/hoa thường. |
| R2 bộ `test_catalog_search.py`, `test_catalog_sync.py`, `test_catalog_crud.py` hiện có | AC12 | backend: `tests/unit/`; giữ trim/escape/limit và ingest/Admin. Không đổi expected để hợp thức hóa semantics mới. |
| R3 toàn bộ architecture tests hiện có | AC12 | backend: `tests/architecture/`; import matrix, route enforcement. |

### Tích hợp

| Mã / Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| I1 `test_loads_all_active_medications_above_search_limit__AC10` | AC10 | `backend/tests/integration/test_catalog_index.py`: tạo ≥60 active và một deleted; truy vấn tập active hiện tại để đối chiếu đầy đủ ID/thứ tự/field, không chỉ assert count fixture; đọc qua api_role. |
| I2 `test_empty_catalog_is_a_successful_empty_index__AC10` | AC10 | Cùng file I1; fixture admin_engine là AUTOCOMMIT nên lấy connection quản trị riêng, đổi `execution_options(isolation_level="READ COMMITTED")` trước `begin()`. Trong transaction đó tạm soft-delete active, `SET LOCAL ROLE api_role`, gọi loader qua SqlUnitOfWork cùng connection; luôn rollback ở finally, kiểm ID/deleted_at khôi phục. Không DELETE/TRUNCATE hoặc commit việc làm rỗng catalog dùng chung. |
| I3 `test_committed_catalog_changes_are_visible_next_call__AC11` | AC11 | Cùng file I1; đọc A rồi đóng transaction; writer commit thêm/sửa tên/hoạt chất/strength/form và soft-delete; giao dịch api_role mới cùng process đọc B đúng thay đổi; restore rồi đọc C thấy lại ID. Không restart, sleep hoặc TTL. |
| I4 `test_same_snapshot_has_stable_order_and_old_index_is_unchanged__AC11` | AC11 | Cùng file I1; đọc lặp trong cùng transaction/snapshot không có writer, đối chiếu nội dung/thứ tự; A bất biến sau các lượt B/C. |
| I5 `test_real_read_error_after_success_is_not_empty_or_cached__AC10_AC11` | AC10, AC11 | Cùng file I1; sau loader thành công, mở connection api_role riêng trên local, lấy `pg_backend_pid()`, admin connection gọi `pg_terminate_backend` đúng PID vừa tạo; loader dùng chính connection bị ngắt phải truyền lỗi DBAPI/OperationalError, không trả snapshot cũ/index rỗng. Chỉ ngắt connection riêng của test; luôn đóng/dispose ở finally. Connection SQLAlchemy đã close đơn thuần không đủ bằng chứng lỗi đọc PostgreSQL. Không đưa OCR text vào SQL/log. |
| I6 bộ `tests/integration/test_catalog_search.py` hiện có | AC12 | backend; chạy cả hai route hiện hữu. Đủ q/limit 1–50/Unicode/wildcard/whitespace bên trong/prefix-name-order/null/soft-delete; không đổi contract/expected. |

Fixture rỗng ở I2 không chạy đồng thời với writer test khác. Kiểm độc lập với dữ liệu seed/test cũ; trường thiếu/strength khác dựng bằng SQL ngay trong file I1, không sửa conftest. SQL dựng fixture không phải migration và chỉ dùng DB local. Đây là test reader + nguồn PostgreSQL thật, không thay bằng mock DB.

### Lệnh dự kiến và evidence

Chạy từ `backend` bằng môi trường backend có dependencies (ưu tiên `.venv` sẵn có); không dùng việc có runtime app làm bằng chứng môi trường test backend đã đủ. `python` WindowsApps hiện không chạy được trong môi trường agent; các lệnh workflow dùng runtime tuyệt đối bên dưới. Chưa chạy các test chức năng ở giai đoạn plan.

| Giai đoạn | Lệnh dự kiến | Log trong `work/4.12-ocr-text-normalization-catalog-index/evidence/` |
|---|---|---|
| implement | `pytest tests/unit/test_catalog_ocr_normalization.py tests/unit/test_catalog_index.py tests/unit/test_catalog_sync.py tests/unit/test_catalog_search.py tests/unit/test_catalog_crud.py` | `implement-catalog-targeted.log` |
| implement | `pytest tests/unit tests/architecture` | `implement-unit-architecture.log` |
| implement | `ruff check .` | `implement-lint.log` |
| implement | Từ gốc: `python .agents/scripts/scope.py 4.12-ocr-text-normalization-catalog-index --stage implement` | `implement-scope.log` |
| test | `supabase start`, sau đó `supabase db reset` trên local đã kiểm tra | `test-supabase-start.log`, `test-db-reset.log` |
| test | `pytest tests/integration/test_catalog_index.py tests/integration/test_catalog_search.py` | `test-catalog-integration.log` |
| test | `pytest tests/integration` | `test-integration.log` |
| test | Từ gốc: `python .agents/scripts/testcase_xlsx.py validate 4.12-ocr-text-normalization-catalog-index`, rồi `build`, rồi `merge` cùng task ID | `testcase-xlsx.log` (append theo thứ tự) |
| test | Từ gốc: `python .agents/scripts/scope.py 4.12-ocr-text-normalization-catalog-index --stage test` | `test-scope.log` |

Lưu output thô bằng `2>&1 | Tee-Object` (đường dẫn log từ backend là `../work/...`), kiểm exit code của từng lệnh. Thiếu môi trường hoặc suite có skip phải ghi rõ, không gọi là AC đã pass.

## 6. Migration

Không có. Không sửa bảng/index/SQL function/grant/RLS, không thay DB reader search đang dùng `catalog_search_key()`. Reset DB ở giai đoạn test là chuẩn bị môi trường hồi quy, không tạo migration mới.

## 7. Nhánh git

Áp dụng wf-git; tên task thống nhất theo quy ước dự án. Đây là kế hoạch nhánh, chưa switch/create/commit/push trong lượt plan.

| Submodule | Nhánh |
|---|---|
| superproject | `feat/4.12-ocr-text-normalization-catalog-index` |
| backend | `feat/4.12-ocr-text-normalization-catalog-index` |
| docs, chỉ trước giai đoạn test/merge workbook | `feat/4.12-ocr-text-normalization-catalog-index` |

Khảo sát hiện tại: superproject/docs ở `feat/4.16-selection-confirmation-screen`, backend ở `feat-3.26`; working tree backend/docs không có file sửa chưa commit theo status đã đọc. Superproject có con trỏ `backend`, `frontend`, `api_contract`, `tests` khác commit được ghi; đã có ở requirement, không gán cho task 4.12. Trước implement/test kiểm tra lại status/HEAD/base và chuẩn bị nhánh theo wf-git, không đem thay đổi task khác vào commit 4.12. Không ghi đè, stash hoặc sửa các thay đổi có sẵn của người khác. Chỉ commit/push khi người dùng yêu cầu; artifact/evidence được đề xuất commit trên nhánh task sau mỗi giai đoạn.

## 8. Rủi ro

| Rủi ro | Phát hiện/giảm thiểu |
|---|---|
| Regex nhận một phần của số âm, số OCR lỗi, phối hợp thiếu hoặc nhiều nhóm | Kiểm cả grammar/biên token trước khi tách; U6/U7 bắt buộc; giữ unparsed/ambiguous và text, không chọn giá trị. |
| Mất số trong tên, metadata, dấu quan hệ hoặc mất dữ liệu hiển thị | Normalizer riêng; U2/U3/U5/U7/U8/R1; không sửa ingest/search/raw catalog. |
| Đọc thiếu do tái dùng search limit hoặc pagination | Reader một SELECT không LIMIT; I1 >50 và đối chiếu toàn tập active. |
| Snapshot cũ khi consumer giữ index/UoW giữa nhiều lượt | Không state nội dung trong loader; docstring facade nêu transaction mới; U10/U11/I3–I5 kiểm cùng process. Tích hợp 4.13/4.15 phải tuân theo đường loader. |
| Catalog đổi sau lúc đọc | Không hứa tính mới qua thời điểm đọc; task tích hợp phải xác minh lại ID/trạng thái trước xác nhận, không thêm lock/cache/hook vào 4.12. |
| Chi phí đọc và chuẩn hóa toàn catalog mỗi lượt | Dựng O(N + tổng độ dài text), sort O(N log N), bộ nhớ theo catalog/khóa; không thêm SLO/benchmark hoặc cache khi chưa có yêu cầu. Đo với dữ liệu thật khi tích hợp. |
| Lộ OCR qua log/exception hoặc thêm storage ngoài ý muốn | Hàm thuần, lỗi kiểu đầu vào không echo text, U12 và review đường gọi; chỉ fixture tổng hợp trong log test. |
| Test rỗng sai do seed/dữ liệu dùng chung hoặc AUTOCOMMIT | I2 connection riêng chuyển READ COMMITTED trước begin, rollback finally và kiểm phục hồi; I1 so ID toàn bộ; không chạy I2 cùng writer song song. I5 chỉ ngắt đúng connection riêng do test vừa mở. |
| Môi trường DB/backend thiếu khiến test skip | Kiểm runtime/service ở giai đoạn tương ứng; lưu pass/fail/skip thực tế, không suy pass từ code. |
| Workbook tổng có kết quả tester khác | Đọc mã sheet hiện tại, giữ ID test case, dùng script merge; nếu script báo xung đột kết quả thì xử lý với người dùng theo wf-testcase, không tự ghi đè. |

## 9. Câu hỏi mở

Không có câu hỏi chặn plan. Q2 tùy chọn của 01 về format hàm lượng giữ mặc định bảng 7a. Đơn vị/format ngoài MVP giữ chưa phân tích; không chờ BQ-042 để triển khai phạm vi đã duyệt. Nếu muốn mở rộng phạm vi hoặc đổi AC, người dùng reopen requirement trước.

## 10. Phát sinh

- Không sửa code, integration test, workbook hoặc artifact đã approved trong lượt plan; chưa chạy test chức năng, lint hoặc reset DB.
- Python mặc định trỏ WindowsApps không chạy được. Workflow dùng `C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`; không sửa cài đặt máy.
- Sandbox từ chối ghi log ban đầu dù nằm trong workspace; đã lưu log bằng thao tác được phê duyệt tự động trong đúng thư mục evidence. Không thay quyền file hoặc cấu hình sandbox.
- SRS cũ còn Admin xử lý OCR không khớp đã được 01 loại khỏi phạm vi theo QD-39; không tạo công việc sửa tài liệu nguồn trong task này.

### Bằng chứng kiểm tra plan

- Gate: runtime tuyệt đối nêu trên + `.agents/scripts/gate.py 4.12-ocr-text-normalization-catalog-index plan` → exit 0, cho phép bắt đầu. Output: `evidence/plan-gate.log`.
- Scope đầu phiên: cùng runtime + `.agents/scripts/scope.py 4.12-ocr-text-normalization-catalog-index --stage plan` → exit 0, không có thay đổi ngoài work. Output: `evidence/plan-scope-before.log`.
- Scope cuối: cùng runtime + `.agents/scripts/scope.py 4.12-ocr-text-normalization-catalog-index --stage plan` → exit 0, không có thay đổi ngoài work. Output: `evidence/plan-scope.log`.
- Cấu trúc/truy vết: cùng runtime + `work/4.12-ocr-text-normalization-catalog-index/scratch/validate_plan.py` → exit 0; frontmatter draft, approval requirement còn hiệu lực, parser scope đọc đúng 10 file, checklist P1–P9 và các hàng test phủ AC1–AC14. Output: `evidence/plan-validation.log`. Script thử ở scratch không đề xuất commit. Đây là kiểm tra artifact/phạm vi, không phải test sản phẩm.

## Bước tiếp theo

- Đang chờ: người duyệt đọc và duyệt `03-plan.md`; không có câu hỏi chặn.
- Việc cần làm: tự chạy `python .agents/scripts/gate.py approve 4.12-ocr-text-normalization-catalog-index plan` trong terminal của người duyệt. Nếu alias lỗi, dùng `& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .agents/scripts/gate.py approve 4.12-ocr-text-normalization-catalog-index plan`.
- Sau duyệt: ở lượt riêng chạy gate implement, kiểm tra git/nhánh theo mục 7 rồi thực hiện P1–P7; P8–P9 thuộc giai đoạn test. Agent không tự duyệt hoặc bắt đầu code trong lượt plan.
- Đề xuất commit artifact/evidence của task trên nhánh task của superproject khi người dùng yêu cầu, để tool/máy khác tiếp tục được.
- Cập nhật lần cuối: 2026-10-28, Codex.
