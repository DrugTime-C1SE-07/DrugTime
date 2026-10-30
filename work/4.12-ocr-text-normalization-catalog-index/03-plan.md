---
task: 4.12-ocr-text-normalization-catalog-index
stage: plan
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-30 09:46 +0700
content_hash: sha256:1561587391291ad5
inputs:
  01-requirement.md: sha256:af09eb8e3be07716
---

# 4.12 · Plan giữ dòng OCR, gom cụm và index danh mục PostgreSQL

## 1. Giải pháp

Đầu vào: 01 đã duyệt ngày 30/10/2026, size L, contract_change no. Gate plan cho phép bắt đầu. Bản này thay thiết kế gộp text và dựng map Python toàn catalog; snapshot plan cũ ở `evidence/plan-refresh-20261030-before.md`. Chỉ đổi interface nội bộ catalog, không HTTP mới.

### 1a. Luồng, DTO và facade

`raw string → tách dòng → clean/key → trích hàm lượng → lọc khóa tên → eligibility → gom cụm → tổng hợp bằng chứng → query DB`.

- `normalize_ocr_text(text: str) -> NormalizedOcrText` là hàm thuần, từ chối non-string bằng TypeError cố định, không echo dữ liệu. DTO mới giữ raw_text, lines, clusters và strength_evidence. Chuỗi rỗng trả các collection rỗng, không default.
- `OcrLine`: line_id từ 1, raw, raw_start/raw_end, line_ending, clean, key, name_key, strengths, unparsed_strengths, removed_spans, query_eligible/eligibility_reason. Tách LF/CRLF/CR trước normalize, giữ dòng rỗng/cuối và thứ tự. `"\n"` truy được hai dòng trống. Không nối dòng hoặc suy hình học.
- clean là NFC/lowercase/trim/gộp whitespace nhưng còn dấu/ký hiệu; key bỏ dấu từ clean, đ→d. Khoảng trích/lọc thuộc key, không dùng offset sau bỏ dấu để cắt raw; raw nguyên gốc và line_id cho truy nguồn. Idempotence áp dụng riêng clean/key từng dòng.
- `StrengthOccurrence`: line_id, source_text/key span, canonical, parts theo thứ tự và trạng thái. Nhóm chưa hiểu giữ text/span/lý do riêng. `StrengthEvidence`: canonical, count dòng nguồn khác nhau, occurrences; cờ has_conflict/has_unparsed/has_ambiguous_line độc lập.
- `OcrCluster`: cluster_id từ dòng đầu, member_line_ids, count dòng khác nhau, representative_line_id/name_key, query eligibility và strength evidence của thành viên. Dòng strength-only giữ ở document, không gán tên theo thứ tự. DTO frozen/tuple, không field confidence thuốc/selected ID/tên đã xác minh.
- Facade mới `lookup_ocr_candidates(uow, normalized) -> OcrCatalogLookup`; application nhận reader Protocol, facade ghép SqlCatalog. Hai caller mô phỏng 4.13/4.15 dùng cùng DTO/quy tắc và UoW đọc mới mỗi lượt. Không tự mở transaction lồng.
- Xóa builder/loader toàn catalog và export CatalogIndex/IndexedMedication/build_catalog_index/load_catalog_index; bỏ SqlCatalog.list_for_index. Khảo sát caller chỉ thấy catalog và test task, chưa consumer sản phẩm ngoài module. Implement phải rg lại; có caller ngoài phạm vi thì báo trước sửa, không để wrapper tiếp tục normalize toàn catalog.

### 1b. Parser và tổng hợp hàm lượng

Tái dùng token/span detector/grammar hiện tại, đổi orchestration sang từng dòng/từng nhóm. Grammar đúng 01 mục 7a: mg/g/mcg, mg/ml, mg/<số>ml, phối hợp mg qua `+`, phần trăm; Decimal dương, chuẩn dấu phẩy/chấm và biểu diễn số tương đương (`500.0`→`500`), không quy đổi đơn vị. `0.5 g` và `500 mg` giữ riêng; không tự thêm mẫu số để gộp `5 mg/ml` với `5 mg/1 ml`.

Giữ hồi quy O.5g/l0mg/5OOmg, số âm/0, đơn vị ngoài MVP, phân nhóm nghìn và dang dở. `/`/`+` liên kết thành cả nhóm: `500mg + 5OOmg` chưa hiểu, không lấy 500mg làm phiếu. `500mg 250mg` giữ hai occurrence và cờ mơ hồ trong dòng. Nhóm hợp lệ độc lập cạnh nhóm sai vẫn giữ bằng chứng hợp lệ và has_unparsed, không coi chắc chắn.

Chỉ span hợp lệ được tách khỏi bản dẫn xuất tên; phần chưa hiểu giữ trong name_key theo hướng bảo thủ. Mỗi canonical nhận tối đa một phiếu mỗi line_id, song mọi occurrence vẫn giữ. Hai dòng 500mg count2; 4/1 hoặc hòa vẫn trả mọi giá trị/count/nguồn. Sort count giảm rồi canonical tăng, không xuất winner. Conflict là nhiều canonical khác nhau; has_unparsed độc lập ngay cả chỉ có một canonical. Không suy hàm lượng từ catalog hoặc gán dòng hàm lượng rời cho tên.

### 1c. Whitelist và eligibility

Chỉ lọc name_key sau parser: `vien nen`, `vien sui`, `sui`, `siro`; `hop <số> vi`, `<số> vien`; VD-/VN-<digits>-<digits> có thể kèm SĐK/SDK và `:`; ®/™/• thành khoảng trắng. So không dấu/hoa thường, khớp cụm dài trước, ranh giới token/cả mẫu. raw/clean/key trước lọc còn nguyên. Không thêm noise ngoài 01, không field/lookup SĐK. Test bảo vệ Sirolex/Vienna/VD-X, prefix lạ, số lô/HSD chưa khớp.

Eligibility phát triển ban đầu, phải đối chiếu raw AC23:

1. Rỗng/chỉ dấu/chỉ số/chỉ strength hoặc metadata whitelist → không query, reason cụ thể.
2. Có ít nhất một token chứa ≥4 chữ cái liên tiếp và không chỉ là một token cắt dở kết thúc `.` → query. Giữ nguyên token có số: Vitamin B12/D3 đủ thông tin, không xóa chữ số.
3. Met. không query độc lập/không mở rộng. B12/D3 đứng riêng giữ reason insufficient_context; trong tên đủ thông tin vẫn giữ. 5mg qua parser trước bước này. Không xóa token chỉ vì ngắn; tên thật ngắn ngoài quy tắc là giới hạn cần raw đánh giá.
4. Dòng không eligible vẫn giữ và chỉ có thể làm thành viên cụm theo điều kiện mảnh ở 1d; không tự query bằng mảnh đó.

### 1d. Clustering xác định và chọn đại diện

Dùng thư viện chuẩn `difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()` trên name_key, không dependency mới. Ngưỡng kỹ thuật khởi điểm T=0.86, **chưa được chọn bằng raw thật**. P5 thử tập hữu hạn 0.80/0.83/0.86/0.89/0.92, ghi ngưỡng cuối, nhãn, kết quả/ca sai; chưa có raw thì AC23 Pending. Trong tập có nhãn, ưu tiên ngưỡng không gom nhầm ca phải giữ riêng, rồi số ca gom đúng lớn nhất, hòa chọn T lớn hơn. Nếu không ngưỡng nào thỏa nhãn thì báo ca sai/quy tắc cần làm rõ, không sửa nhãn hoặc giả đã đạt. Đây là calibration tập nhỏ, không là độ chính xác matching ngoài tập.

- Signature là tập distinct canonical hợp lệ của dòng. Các signature có giá trị khác nhau không nhập nhau, kể cả tên giống; dòng có nhiều giá trị là signature riêng. Token có chữ số khác nhau (B12/D3, 16/160) cũng chặn nhập chỉ nhờ ratio.
- Trong mỗi signature có giá trị, gom exact key rồi duyệt nhóm theo count giảm/key tăng/line_id đầu tăng. Nhập nhóm vào cụm chỉ khi mọi cặp khác key đạt T (complete-link). Chọn cụm có min-ratio lớn nhất, hòa theo line_id đầu. Không single-link để A-B/B-C nối A-C dưới T.
- Nhóm signature rỗng xử lý sau: chỉ gắn vào cụm có strength khi khớp duy nhất một cụm qua complete-link. Cùng tên nhưng khớp cả cụm 16mg và 160mg thì giữ nhóm thiếu strength riêng. Các nhóm rỗng chưa gắn gom với nhau bằng cùng thuật toán exact/complete-link và tie-break trên; chúng không được dùng để nhập hay nối lại các cụm có strength. Dòng chưa hiểu không tạo phiếu hàm lượng.
- Mảnh cắt dở chỉ xét một token chữ có `.` cuối, phần trước chấm là tiền tố tại đầu token, dài ≥3 và ≥65% token tương ứng của dòng đầy đủ, vẫn đạt T sau bỏ chấm cuối và không mâu thuẫn số/strength. Phải có dòng eligible làm neo, không nối mảnh qua mảnh. Met. so Metformin thiếu cả tỷ lệ/ratio; formin không là tiền tố. Chỉ bỏ chấm để so, không sửa raw/clean/key. Substring đơn thuần không đủ.
- Dòng tên rỗng không tạo cụm tên; mỗi dòng thuộc tối đa một cụm, giữ singleton/cụm không query. Count là số line_id, không nhân vì nhiều strength hoặc query.
- Đại diện là member eligible có số phiếu exact-key lớn nhất, rồi tổng ratio tới thành viên lớn nhất, độ dài key lớn nhất, line_id nhỏ nhất. Cụm không eligible dùng cùng tie-break nhưng vẫn không query. Không dựng tên mới. Nếu Metformin/Metformin/Metformin bydrock. cùng cụm thì hai phiếu exact thắng dòng dài; nếu ratio không đủ thì dòng dài ở singleton, không thay đại diện chuẩn.
- Sort cụm count giảm/line_id đầu tăng/key đại diện tăng, giữ cả cụm nhỏ. Tính ratio cặp một lần trong bộ nhớ request; chi phí theo số dòng/độ dài, không theo toàn catalog. Không âm thầm cắt dòng/cụm.

### 1e. Tra cứu ứng viên DB

Retrieval MVP dùng chứa literal bỏ dấu: `catalog_search_key(column) LIKE :pattern ESCAPE '\'`, reuse hai expression GIN pg_trgm hiện có và helper escape_like. Query đại diện trước và mọi name_key eligible khác nhau của từng cụm (count hỗ trợ giảm/key tăng); exact key lặp query một lần rồi gắn lại nguồn, không nhân count. Giới hạn recall: typo không còn chuỗi khớp có thể không tìm ra; ratio ở đây gom dòng, không scoring/confidence thuốc của 4.13. Không hứa fuzzy matching catalog trong task này.

Ba nhánh parameterized độc lập: name, raw_active_ingredient, ingredient_alias. Nhánh alias bắt đầu từ alias_text có expression GIN mới, join medication_active_ingredients theo active_ingredient_id rồi medications theo ID; dùng index FK hoạt chất và unique liên kết đã có. Không suy link từ raw hoặc thêm lookup tên chuẩn hoạt chất ngoài phạm vi. Mọi nhánh lọc deleted_at IS NULL và giữ CatalogMedication raw/null/strength/form/has_active_ingredients.

Match source giữ query_key/cluster_id/line_id, loại name/raw_active_ingredient/ingredient_alias; alias có alias_id/alias_text/active_ingredient_id. Hợp nhất payload theo **ID**, union mọi nguồn; không gộp ID cùng tên hoặc loại theo strength. Không normalize catalog, không gọi list_active/search limit50.

Giới hạn kỹ thuật: 200 **distinct medication ID cho mỗi (query_key, source)**, lấy 201 để phát hiện truncated, order m.id tăng. Alias limit theo distinct ID trước rồi lấy đủ alias hit cho ID được chọn. Trả truncated từng query/source; không coi không thấy sau limit là không tồn tại. Không global cap làm cụm lớn chiếm cụm nhỏ. Đầu ra group theo cụm, ID tăng; top-N UI thuộc consumer. Test 199/200/201 và >50.

Không eligible → 0 lệnh đọc catalog, kết quả rỗng có cấu trúc. Lỗi bất kỳ nhánh/iterator truyền lên toàn lượt, không partial/cũ/giả rỗng thành công. UoW mới sau writer commit; không snapshot xuyên request/TTL/job rebuild/materialized view. Freshness tại giao dịch đọc, không khóa tới xác nhận.

## 2. Khảo sát

| File đã đọc trong lượt này | Điều rút ra |
|---|---|
| 01-requirement.md toàn bộ, mục 7/7a/7b/8/9 | 23 AC mới, L, raw thật cần provenance/nhãn; không HTTP mới. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, quy ước trạng thái, mục 2/3/14/16 | Nguồn 3.1, baseline QD-2026-10-03-v1; QD-36/38/39/45 ✅ là chốt baseline, chưa xác nhận triển khai/chữ ký Mentor. BQ-042 ❓ vẫn mở. Không phát hiện mâu thuẫn buộc đổi 01/contract. |
| `backend/src/drugtime/modules/catalog/application/normalize_ocr.py`, toàn file | Reuse detector bảo thủ; orchestration đang gộp newline/mất nhóm cạnh tranh cần thay. |
| `catalog/domain/catalog_index.py`, `application/build_catalog_index.py`, `api.py`, toàn file | Snapshot Python phải bỏ; rg backend/src và tests chỉ thấy caller trong catalog/test task. |
| `catalog/adapters/outbound/sql_catalog.py`, `sql_active_ingredients.py` | Reader cũ đọc toàn active; search cũ limit/thứ tự riêng. Alias hiện ILIKE qua hoạt chất. Thêm đường riêng, không sửa search/CRUD. |
| `catalog/application/search_medications.py`, `normalize.py`, `backend/pyproject.toml` | Reuse escape_like; ingest NFC/dấu/hoa thường. Python ≥3.12, đủ difflib/Decimal. |
| `backend/supabase/migrations/20261002101033_catalog_search_unaccent.sql`, toàn file | IMMUTABLE catalog_search_key, pg_trgm/unaccent, hai expression GIN, api_role có quyền hàm/extensions. |
| `20260927082912_rebuild_schema_v11.sql`, bảng/index/grant liên quan | Alias chỉ B-tree lower; có index FK hoạt chất và unique link, quyền/RLS đã có. Chỉ thêm GIN alias. |
| Unit/integration `test_catalog_index.py`, setup và các test đầu; rg caller | Test builder cũ phải đổi; giữ hồi quy còn đúng, không coi pass cũ là nghiệm thu mới. |
| `backend/tests/integration/conftest.py`, `tests/architecture/test_module_dependencies.py` | DB local/api_role, dữ liệu chung, admin AUTOCOMMIT/thiếu DB có thể skip. Catalog chỉ phụ thuộc identity. |
| wf-plan/wf-db-migration/wf-git, template 03, scope.py | Plan chỉ ghi work; implement không viết integration. Scope xét cả code cũ, không chỉ diff của lượt. |
| `rg --files work backend/tests frontend/mobile` lọc OCR/MLKit/raw/4.08/4.09 | Chưa thấy raw có nhãn trong vùng rà. Lần glob Windows đầu lỗi, đã rà lại bằng danh sách file. |
| Git status superproject/backend/docs, origin/main cục bộ | Cả ba feat/4.12-ocr-text-normalization-catalog-index. Backend 9 file và docs workbook cũ chưa commit; 5 gitlink khác sẵn. HEAD superproject bằng origin/main cục bộ, chưa fetch. |

Người dùng xác nhận raw ở repo cha, chưa kéo và yêu cầu lệnh. Đã đưa `git -c submodule.recurse=false pull --ff-only origin main` tại gốc; agent chưa chạy pull. Sau khi có dữ liệu phải kiểm vị trí/provenance/nhãn; không tự coi screenshot/text không nhãn là ground truth.

### Quyết định nghiệp vụ áp dụng

| Mã / mục / nội dung nguồn / trạng thái | AC | Bước | Test |
|---|---|---|---|
| QD-36 / mục 2 / giữ ID, ngừng chọn mới thuốc gỡ, không xóa lịch sử / ✅ | AC17, AC18, AC19 | P6, P7, P9 | U8–U10, I2–I4 |
| QD-38 / mục 2 / giá trị dương, hàm lượng khác lượng dùng, không tự quy đổi / ✅ | AC3, AC4, AC5, AC6, AC12, AC13, AC14 | P1, P3, P4 | U3/U6 |
| BQ-042 / mục 2 còn mở / đơn vị/dạng/quy đổi chưa chốt / ❓ | AC4, AC5, AC6 | P3 | U3, chỉ grammar 01 mục 7a |
| QD-39 / mục 3 / kiểm tra trước tạo lịch, chỉ catalog, không gán gần giống vượt chặn / ✅ | AC9, AC10, AC11, AC12, AC13, AC14, AC17, AC21 | P4, P6, P7 | U5/U6/U8/U11, I2 |
| QD-39 / mục 3 / OCR mã hóa tối đa24h/xóa khi xác nhận-hủy / ✅; 4.12 chỉ bộ nhớ | AC21, AC23 | P2, P5, P8 | U11/U12/I6, fixture bao bì không cá nhân, không log raw thực |
| QD-39 / mục 3 / bỏ Admin duyệt scan không khớp / ✅ | AC21 | P7, P8 | U11, review diff không route/Admin/writer |
| QD-45 / mục14/16 / contract/backlog chuẩn/truy vết kiểm thử / ✅ | AC20, AC22 | P7, P8, P10, P11 | U10/R1–R3/I5, workbook bằng kết quả mới |
| Requirement 30/10 mục2/7/7b/9 / giữ dòng, whitelist, cụm bảo vệ, DB index, không cache | AC1, AC2, AC7, AC8, AC15, AC16, AC18, AC19, AC23 | P1, P2, P4, P5, P6, P9 | U1/U4/U5/U7/U9/U12/I1/I3/I4 |

PB31/TC-04 theo truy vết của 01; không đọc lại DOCX hoặc xác minh ảnh thiết bị trong lượt này. Không patient endpoint, không áp dụng wf-health-endpoint/cross-patient/consent/dose race. Không thêm dependency liên module/C4/ma trận import; architecture regression vẫn chạy.

## 3. File sẽ thay đổi (ranh giới phạm vi)

15 mục: backend14 (7 source gồm 1 xóa, 1 migration, 4 unit, 1 fixture, 1 integration), docs1 workbook. Đường dẫn từ gốc submodule. Các file uncommitted vòng cũ ghi sửa/xóa, không tính là kết quả mới. Artifact/evidence chỉ ở work task.

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| backend | `src/drugtime/modules/catalog/domain/catalog_index.py` | Sửa | DTO dòng/cụm/strength/candidate/nguồn, bỏ map DTO. |
| backend | `src/drugtime/modules/catalog/application/normalize_ocr.py` | Sửa | Dòng/clean/key/parser/whitelist/eligibility/tổng hợp. |
| backend | `src/drugtime/modules/catalog/application/cluster_ocr_lines.py` | Thêm | Ratio/complete-link/strength bridge/đại diện. |
| backend | `src/drugtime/modules/catalog/application/build_catalog_index.py` | Xóa | Bỏ builder/loader toàn catalog. |
| backend | `src/drugtime/modules/catalog/application/lookup_ocr_candidates.py` | Thêm | Protocol/lookup mọi cụm/union nguồn/truncated. |
| backend | `src/drugtime/modules/catalog/adapters/outbound/sql_catalog.py` | Sửa | Bỏ list_for_index, thêm 3 nhánh indexed, giữ search/CRUD. |
| backend | `src/drugtime/modules/catalog/api.py` | Sửa | Ghép/export facade mới, bỏ interface map cũ. |
| backend | `supabase/migrations/*_catalog_ingredient_alias_search.sql` | Thêm | Một migration timestamp CLI thêm alias expression GIN. |
| backend | `tests/unit/test_catalog_ocr_normalization.py` | Sửa | Dòng/Unicode/grammar/lọc/eligibility/vote/hồi quy. |
| backend | `tests/unit/test_catalog_ocr_clusters.py` | Thêm | Cụm/bridge/đại diện/raw và biên cutoff. |
| backend | `tests/unit/test_catalog_index.py` | Sửa | Thay test builder bằng query/facade/nguồn/limit/lỗi. |
| backend | `tests/unit/test_catalog_sync.py` | Sửa | Giữ regression NFC/dấu/hoa thường vòng cũ. |
| backend | `tests/fixtures/catalog_ocr_clustering.json` | Thêm | Raw có provenance/nhãn và synthetic tách loại rõ. |
| backend | `tests/integration/test_catalog_index.py` | Sửa, giai đoạn test | Migration/index/query/alias/quyền/freshness/lỗi/limit. |
| docs | `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` | Sửa, giai đoạn test | 23 AC, Bug/Test Report, giữ chức năng khác. |

Glob migration chỉ một file suffix trên. Không sửa migration cũ/route/contract/conftest/dependency/writer/ma trận/frontend/schema docs. Test search/architecture cũ chỉ chạy. Ngoài bảng phải ghi Phát sinh trước sửa.

## 4. Checklist

- [ ] P1 [backend] Đổi DTO nguồn/dòng/cụm/strength/candidate, immutable, bỏ map DTO — file: domain/catalog_index.py — AC: AC1, AC4, AC5, AC9, AC12, AC13, AC14, AC17, AC22 — xong khi: U1/U3/U6/U8/U10 giữ nguồn/raw/ID/null, không chọn thuốc/confidence.
- [ ] P2 [backend] Tách dòng, clean/key, lọc đúng whitelist sau parser, eligibility có reason — file: application/normalize_ocr.py, tests/unit/test_catalog_ocr_normalization.py — AC: AC1, AC2, AC3, AC7, AC8, AC15, AC21 — xong khi: U1/U2/U4/U7/U11 pass, không query rỗng hoặc xóa số tên.
- [ ] P3 [backend] Parser từng nhóm/span, Decimal canonical, distinct vote/count/conflict/unknown — file: như P2 — AC: AC3, AC4, AC5, AC6, AC12, AC13, AC14 — xong khi: U3/U6 pass lặp/đa số/hòa/hỏng/strength rời, không sửa ký tự/nhân phiếu.
- [ ] P4 [backend] Clustering 1d và test bridge/đại diện/thứ tự/mảnh — file: application/cluster_ocr_lines.py, tests/unit/test_catalog_ocr_clusters.py — AC: AC8, AC9, AC10, AC11, AC12, AC13, AC14 — xong khi: U5/U6 pass, mỗi dòng tối đa một cụm, không nối signature khác qua dòng thiếu strength.
- [ ] P5 [backend] Đọc raw người dùng kéo về, kiểm provenance/nhãn/không cá nhân, thử tập T và ghi lựa chọn/ca sai — file: tests/fixtures/catalog_ocr_clustering.json, test_catalog_ocr_clusters.py — AC: AC10, AC11, AC23 — xong khi: U12 chạy raw có nhãn, ngưỡng cuối trong 04; thiếu raw thì Pending AC23, không thay bằng synthetic.
- [ ] P6 [backend] CLI tạo migration alias GIN; query 3 nguồn bind/escape/active/distinct ID/probe201, bỏ list_for_index — file: migration đã liệt kê, sql_catalog.py — AC: AC16, AC17, AC18, AC19, AC21 — xong khi: U8/U9/U11 pass và diff không mở quyền; I1–I4/I6 phải kiểm DB thật ở test.
- [ ] P7 [backend] Thay builder bằng lookup application/facade, union nguồn và lỗi toàn lượt/UoW mới — file: build_catalog_index.py xóa, lookup_ocr_candidates.py, api.py, test_catalog_index.py — AC: AC15, AC17, AC18, AC19, AC20, AC21, AC22 — xong khi: U7–U11 pass, rg source không còn đường index cũ, không normalize catalog/fallback.
- [ ] P8 [backend] Giữ ingest regression, chạy unit/architecture/lint/scope, ghi 04 mới — file: test_catalog_sync.py và các unit đã khai báo — AC: AC2, AC3, AC6, AC20, AC21, AC22, AC23 — xong khi: R1–R3/log mới, lỗi nền/skip/Pending rõ; chỉ sửa 04 sau reopen nếu còn approved rồi draft/chờ duyệt.
- [ ] P9 [backend, test] Reset local sạch, kiểm upgrade/index/quyền/data preservation/alias/commit/error/limit — file: tests/integration/test_catalog_index.py — AC: AC16, AC17, AC18, AC19, AC21 — xong khi: I1–I4/I6 DB thật api_role không skip, log reset/EXPLAIN/test, không sửa code implement ở test.
- [ ] P10 [backend, test] Chạy integration search cũ và toàn suite sau migration; phân biệt lỗi task/baseline bằng thực thi — file: chỉ integration đã khai báo nếu thêm case trong phạm vi, regression cũ chỉ chạy — AC: AC20 — xong khi: I5 và full checks có pass/fail/skip thật, không đổi expected HTTP cũ.
- [ ] P11 [docs, test] Theo wf-testcase ghi spec/workbook EP/BVA/bảng quyết định, Bug/Test Report — file: workbook tổng, spec/workbook riêng task trong work — AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18, AC19, AC20, AC21, AC22, AC23 — xong khi: validate/build/merge có log, giữ sheet khác, raw thiếu thì AC23 Pending; 05 draft sau reopen nếu cần rồi dừng.

P1–P8 implement; P9–P11 sau gate test/04 duyệt. Không đánh dấu hoàn tất bằng evidence cũ. Thiếu raw không chặn bước độc lập nhưng không được kết luận đủ AC23/P5.

## 5. Test

### Unit

| Mã / test dự kiến và dữ liệu | AC | Submodule / file |
|---|---|---|
| U1 test_line_sources_and_clean_key: LF/CRLF/CR/trống cuối/lặp/NFC/NFD/đ/raw offset/order/idempotence | AC1, AC2 | backend: tests/unit/test_catalog_ocr_normalization.py |
| U2 test_names_and_confusables: B12/D3/O0l1/Metforrnin, Met. không mở rộng, 5mg trích trước lọc | AC3 | Cùng U1 |
| U3 test_strength_whole_spans: toàn 7a/Decimal/mg-g không quy đổi/nồng độ/phối hợp/%; âm/0/5OO/O.5/l0/unsupported/grouping/dang dở/nhiều nhóm/metadata | AC4, AC5, AC6 | Cùng U1 |
| U4 test_whitelist_and_eligibility: mẫu 01, SDK riêng dòng, siro/sủi, Sirolex/Vienna/VD-X/số lô/HSD, tên đủ/ngắn/noise và reason | AC7, AC8 | Cùng U1 |
| U5 test_clusters_no_bridge_and_stable_representative: lặp; dưới/bằng/trên T; prefix 65%; substring/suffix; A-B/B-C nhưng A-C fail; token số; Candesartan Krka16/160mg; thiếu strength với thứ tự hoán vị; exact-support thắng dài; cụm nhỏ giữ | AC9, AC10, AC11 | backend: tests/unit/test_catalog_ocr_clusters.py |
| U6 test_evidence_retains_minority_and_unknown: 2 dòng500, 4/1, hòa, lặp trong dòng một phiếu/đủ occurrence, 500 vs5OO, nhiều nhóm/nhóm hỏng/strength rời | AC12, AC13, AC14 | U1 và U5 |
| U7 test_empty_and_ineligible_no_read: empty/whitespace/noise/non-string, lỗi không echo, fake reader không gọi | AC15 | U1 và tests/unit/test_catalog_index.py |
| U8 test_candidate_mapping_and_sources: 3 nhánh/escape/alias join/raw/null/ID cùng tên/nguồn đầy đủ | AC17, AC21 | backend: tests/unit/test_catalog_index.py; không gọi unit là bằng chứng index |
| U9 test_independent_query_source_budget: 199/200/201 distinct ID/alias duplicates, lớn-nhỏ/biến thể, query dedup không đổi count, truncated, không builder toàn catalog | AC18 | Cùng U8 |
| U10 test_two_facade_callers_and_fresh_reader: UoW tách, DTO/rules chung, kết quả đổi giữa lượt; exception/iterator lỗi không partial/cũ/rỗng | AC19, AC22 | Cùng U8 |
| U11 test_no_ocr_io_log_or_writes: caplog/capsys marker tổng hợp, guard I/O normalizer/cluster, guard writer và review đường query; không OCR/LLM/tự chọn | AC21 | U1/U5/U8 |
| U12 test_labelled_real_raw_regression: provenance/sample ID/nhãn gom-giữ riêng, tập T/đại diện/mảnh, expected cố định và số mẫu/ca sai/giới hạn; synthetic ghi loại riêng | AC23 | U5 và tests/fixtures/catalog_ocr_clustering.json; thiếu raw Pending, không skip rồi gọi pass |
| R1 ingest tiếng Việt NFC/dấu/hoa thường; R2 unit search/CRUD/sync; R3 toàn architecture | AC20 | backend: test_catalog_sync.py và test sẵn có chỉ chạy |

### Tích hợp

Ca mới ở backend/tests/integration/test_catalog_index.py, SQL fixture local ngay file, không sửa conftest hoặc giả catalog chỉ có test data.

| Mã / test dự kiến | AC / kịch bản | Kiểm chứng |
|---|---|---|
| I1 test_alias_index_migration_preserves_data_and_plan | AC16 | Reset toàn migration sạch; thêm lượt apply file mới trên DB baseline có alias tổng hợp, so payload/hash migration cũ/ACL/RLS; pg_get_indexdef và valid/ready; EXPLAIN JSON từng nhánh. Bảng nhỏ không bắt planner tự chọn index; probe enable_seqscan=off chỉ trong transaction rollback để kiểm khả năng dùng, không là benchmark. |
| I2 test_name_ingredient_alias_preserve_ids_and_sources | AC17 | Unicode bỏ dấu, null, nhiều ID cùng tên khác strength/form, soft-delete, alias không link/link nhiều thuốc/nhiều alias; giữ raw/nguồn, không suy link/chọn strength. |
| I3 test_clusters_and_budget_above_old_limit | AC18 | ≥60 match; biên199/200/201 distinct ID từng nhánh, alias duplicates, cụm lớn/nhỏ; 201→truncated; query events không SELECT toàn catalog+builder. |
| I4 test_committed_medication_alias_link_changes_and_read_error | AC19 | Đọc A rồi writer commit thêm/sửa/soft-delete/restore thuốc, thêm/sửa/xóa alias, thêm/gỡ link; UoW mới cùng process thấy B/C không restart/TTL. A là object bất biến. Sau thành công ngắt đúng PID connection riêng local, đọc phải DBAPIError; nhánh sau lỗi không partial. |
| I5 toàn tests/integration/test_catalog_search.py hiện hữu | AC20 | Cả route hiện có/q/limit/Unicode/wildcard/whitespace/thứ tự/shape/active, không đổi expected. |
| I6 test_api_role_path_and_client_privileges_unchanged | AC21 | Query qua api_role chỉ đọc; so ACL/RLS/EXECUTE trước-sau, anon/authenticated không mở quyền/worker không thêm grant. Không bảng/log mới nên không có ràng buộc/append-only trigger mới để test. |

Upgrade trên dữ liệu: dùng DB local riêng/disposable hoặc baseline local trước migration mới rồi áp dụng đúng file; không xóa migration history/rollback schema môi trường dùng chung. Reset/fixture không song song test khác. Connection admin AUTOCOMMIT cần transaction riêng READ COMMITTED khi cần rollback. Không ngắt connection ngoài PID của test. Tắt SQL echo/params, fixture DB tổng hợp.

### Lệnh và evidence dự kiến

Workflow dùng `C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe`; backend ưu tiên .venv/Scripts/python.exe -m pytest/-m ruff, kiểm dependencies lúc chạy. Log prefix mới để giữ evidence cũ.

| Giai đoạn | Lệnh / kiểm tra | Log trong evidence task |
|---|---|---|
| implement | pytest unit normalizer/clusters/index/sync/search/CRUD + tests/architecture | implement-refresh-targeted.log và XML |
| implement | U12, tập ngưỡng, provenance hash/kết quả từng sample ID, không raw thực | implement-refresh-cluster-calibration.log và JSON |
| implement | pytest tests/unit tests/architecture; ruff check .; scope.py <task> --stage implement | implement-refresh-unit-architecture.log, implement-refresh-lint.log, implement-refresh-scope.log |
| test | supabase start; supabase db reset sau kiểm local; upgrade/ACL/EXPLAIN | test-refresh-supabase-start.log, test-refresh-db-reset.log, test-refresh-migration-upgrade.log |
| test | pytest tests/integration/test_catalog_index.py tests/integration/test_catalog_search.py; pytest tests/integration; các kiểm tra wf-test yêu cầu | test-refresh-targeted.log, test-refresh-integration.log và XML |
| test | testcase_xlsx.py validate/build/merge <task>; scope.py <task> --stage test | test-refresh-testcase.log, test-refresh-scope.log |

Lưu output thô `2>&1 | Tee-Object`, kiểm exit từng lệnh. Skip/lỗi nền/Pending phải ghi đúng; không dùng pass184+60+4 cũ nghiệm thu AC mới. Test raw thật dùng sample ID cho param/assert, không dump raw/DTO trong failure; log chỉ thống kê và định danh tối thiểu, raw ở fixture bao bì được kiểm provenance.

## 6. Migration

Implement chạy `supabase migration new catalog_ingredient_alias_search`; một file mới BEGIN/COMMIT: `CREATE INDEX ingredient_aliases_search_idx ON public.ingredient_aliases USING gin (public.catalog_search_key(alias_text) extensions.gin_trgm_ops)`.

Reuse function/từ điển/extensions/index tên/hoạt chất/index join hiện có. Không đổi bảng/cột/constraint/enum/dữ liệu/function/grant/RLS. Không cấp quyền PUBLIC/anon/authenticated/API/worker mới; quyền đọc sẵn đủ. Không bảng sức khỏe/log mới nên không mở rộng policy/trigger ngoài phạm vi.

GIN build transactional trên bảng có dữ liệu có thể chặn writer và tăng disk: kiểm kích thước/lock, chọn cửa sổ bảo trì lúc triển khai. Không dùng CONCURRENTLY trong transaction, không hứa thời gian khi chưa benchmark. Reset sạch + upgrade có dữ liệu + định nghĩa/index eligibility/ACL preservation I1/I6, CRUD index maintenance I4. Nếu hủy về sau viết migration DROP INDEX mới, không sửa migration đã áp dụng. Schema docs/ERD không đổi vì chỉ index nội bộ; nếu cần thì khai báo phạm vi riêng.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| superproject | feat/4.12-ocr-text-normalization-catalog-index |
| backend | feat/4.12-ocr-text-normalization-catalog-index |
| docs, chỉ sửa workbook ở test | feat/4.12-ocr-text-normalization-catalog-index |

Theo wf-git, hiện ba repo đúng nhánh, không detached. Trước sửa lại kiểm status/base; code9 file/backend và workbook cũ chưa commit, không stash/reset/ghi đè thay đổi người khác. Gitlink khác sẵn không thuộc lượt plan. Agent chưa fetch/pull/checkout submodule; chỉ đưa user lệnh kéo repo cha không recurse. Commit/push/PR chỉ khi yêu cầu, backend/docs trước rồi pointer tới SHA đã push/đã merge thực. Đề xuất lưu03/evidence trên nhánh task, không stage scratch.

## 8. Rủi ro

| Rủi ro | Phát hiện/giảm thiểu |
|---|---|
| Raw có nhãn chưa ở checkout | User đang kéo repo cha; P5/U12 rõ phụ thuộc. T0.86 chưa AC23/accuracy; không bịa nhãn/screenshot thay raw. |
| Gom sai/strength bridge hoặc phiếu nhân | Signature/complete-link/số/unique attachment, count line_id và occurrence riêng; U5/U6/raw negatives. |
| Eligibility bỏ tên ngắn, retrieval literal bỏ typo | Giữ dòng không query/reason, fixture dương-âm/raw; ghi giới hạn recall, không tự sửa tên/đơn vị. |
| Alias limit mất nguồn/ID trùng tên | Limit distinct ID trước, union nguồn/ID, U8/U9/I2/I3. |
| Consumer coi kết quả bị cắt là đầy đủ | truncated từng query/source, không global cap, biên199/200/201 và >50. |
| Index lock/disk/planner bảng nhỏ | Migration chỉ index, maintenance window, EXPLAIN eligibility khác benchmark. |
| Catalog đổi/lỗi DB | UoW mới, không fallback/partial/cache, I4; task tích hợp kiểm lại ID khi xác nhận. |
| Raw cá nhân/lộ evidence | Bao bì/provenance/nhãn được kiểm, log sample ID/aggregate, không echo SQL params hoặc dump DTO. |
| Approval/evidence cũ stale và scope file cũ | Không sửa01/04–06 approved, reopen đúng lúc; snapshot trước-sau, không reset/sửa scope để có pass. |

## 9. Câu hỏi mở

Q1 là phụ thuộc kiểm chứng: user xác nhận raw ở repo cha, chưa kéo; đã đưa lệnh pull không recurse. Sau kéo cần vị trí/provenance/nhãn gom-giữ riêng và kiểm không cá nhân. Thiếu nhãn phải nhờ chủ dữ liệu xác nhận, không tự chốt để hết cảnh báo. Tiếp tục bước độc lập được, P5/AC23 chưa thể kết luận đạt.

Không còn câu hỏi nghiệp vụ khác chặn thiết kế; grammar01/BQ-042 giữ trạng thái nguồn. Threshold/eligibility/limit là kỹ thuật, không xác minh dược.

## 10. Phát sinh

- Chỉ sửa03/evidence/scratch trong work, không source/test/migration/workbook hoặc artifact approved. 04–06 cũ giữ để gate nhận biết input stale.
- WindowsApps python không chạy, dùng runtime tuyệt đối mục5. Sandbox chặn ghi evidence ban đầu, retry được phê duyệt tự động trong đúng work; không đổi quyền/cấu hình máy.
- Scope plan còn có thể báo10 file cũ backend/docs; phải ghi raw exit, không gọi pass. User pull trong lúc audit phải tách thay đổi external, không khôi phục code/pointer của họ.

### Bằng chứng plan mới

- Gate đầu: runtime mục5 + gate.py task plan → exit0; `evidence/plan-refresh-20261030-gate-start.log`.
- Snapshot before → exit0: 14 hash được bảo vệ (10 file sản phẩm cũ +01/04/05/06), status7 repo; `evidence/plan-refresh-20261030-before.json/.md/.log`.
- Cấu trúc/truy vết: `scratch/plan_refresh_20261030.py validate` → exit0, parser scope đọc đúng15 file duy nhất, P1–P11 và bảng test phủ AC1–AC23; log `evidence/plan-refresh-20261030-validation.log`. Đây là kiểm artifact, không test sản phẩm.
- Scope: runtime mục5 + `scope.py 4.12-ocr-text-normalization-catalog-index --stage plan` → **exit1**, 10 file backend/docs ngoài stage plan đúng các thay đổi đã có; raw log `evidence/plan-refresh-20261030-scope.log`. Không gọi là scope pass. Theo phạm vi user đã cho cập nhật plan và audit dưới đây, không cần xin lại quyền cho code cũ thực tế không sửa.
- Audit after → exit0: toàn14 hash được bảo vệ và status7 repo bằng snapshot đầu lượt; `evidence/plan-refresh-20261030-after.json`, `...-audit.log`. 01 và04–06 không đổi, code9 file/backend và workbook không đổi. Không reset/stage/sửa script scope.
- Gate cuối → exit0: 01 approved, 03 draft, 04–06 approved nhưng ĐÃ CŨ vì đầu vào thay đổi; giai đoạn cần làm/chờ duyệt là plan. Log `evidence/plan-refresh-20261030-gate-final.log`. Không tự đổi approval.
- Chưa chạy test sản phẩm/lint/OCR/migration/accuracy raw trong lượt plan.

## Bước tiếp theo

- Chờ người duyệt đọc03; phụ thuộc Q1 và ngưỡng cuối ghi rõ, không tự coi đã giải quyết.
- Người duyệt tự chạy: `& 'C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe' .agents/scripts/gate.py approve 4.12-ocr-text-normalization-catalog-index plan`.
- Cổng duyệt bắt buộc theo AGENTS.md §2 và wf-plan bước10; agent không approve. Dừng plan lượt này. Sau duyệt gate implement ở lượt riêng; 04 cũ còn approved thì user reopen trước khi cập nhật, không ghi đè.
- Đề xuất commit03/evidence khi user yêu cầu để tool/máy khác tiếp tục, không stage scratch/gitlink cũ.
- Cập nhật lần cuối: 2026-10-30, Codex.
