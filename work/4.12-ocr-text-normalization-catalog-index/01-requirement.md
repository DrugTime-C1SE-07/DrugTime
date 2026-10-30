---
task: 4.12-ocr-text-normalization-catalog-index
title: OCR line normalization, clustering and database catalog indexes
type: feature
stage: requirement
size: L
contract_change: no
affected: [backend]
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-30 09:18 +0700
content_hash: sha256:af09eb8e3be07716
---

# 4.12 · Chuẩn hóa dòng OCR, gom cụm và index danh mục trong DB

## 1. Mục tiêu

Biến text raw nhiều dòng của một vỏ thuốc thành các dòng chuẩn hóa, cụm thông tin lặp và hàm lượng có nguồn truy vết để 4.13 matching/voting. Tra cứu catalog bằng index PostgreSQL, không đọc toàn catalog rồi dựng map Python mỗi lượt. Giữ bất định và xung đột để người dùng kiểm tra ở luồng xác nhận; không tự chọn thuốc hoặc coi đa số là kết quả đã xác minh.

Bản sửa sau khi người dùng mở lại requirement ngày 30/10/2026. Phạm vi là sáu việc người dùng chốt trong hội thoại và các điều chỉnh về mảnh ngắn, đại diện cụm, bảo toàn xung đột đã được đồng ý bằng “ok. cứ làm như bạn sửa”. Thay thế yêu cầu cũ về gộp toàn text, giữ mọi metadata trong khóa tên và dựng index Python mỗi lượt; tiếp tục không sửa ký tự OCR nghi ngờ.

## 2. Phạm vi

### Trong phạm vi

1. **Giữ dòng.** Đầu vào nội bộ là string raw có xuống dòng từ 4.11. Tách dòng trước normalize, giữ raw, thứ tự/định danh dòng nguồn; dòng trống/bị lọc vẫn có thể truy vết. Gộp whitespace trong từng dòng, không nối các dòng thành một tên hoặc tự suy bố cục vỉ.
2. **Hai biểu diễn.** Mỗi dòng có `clean`: NFC, lowercase, trim, gộp whitespace, còn dấu; `key`: bản bỏ dấu của clean, kể cả `đ/Đ` thành `d`. Giữ raw để đối chiếu; NFC/NFD cho cùng clean/key, không xóa số thuộc tên hoặc tự sửa ký tự nghi ngờ.
3. **Trích trước lọc.** Trích hàm lượng theo grammar 7a trước khi bỏ từ nhiễu/mảnh ngắn. Giữ nguồn của từng biểu thức và phần chưa hiểu; bảo toàn nồng độ/phối hợp. Không tự ghép một dòng hàm lượng rời vào tên khác chỉ dựa trên thứ tự dòng.
4. **Khóa tên tìm kiếm.** Dẫn xuất từ key sau trích hàm lượng, lọc theo whitelist 7b; giữ clean/key trước lọc. Không xóa mọi chữ số/từ lạ hoặc coi phần còn lại là tên chuẩn đã xác minh.
5. **Mảnh ngắn.** Không xóa mọi mảnh dưới 3–4 ký tự. Giữ `B12`, `D3`, `5mg`; mảnh cắt dở ít thông tin không thành truy vấn độc lập chỉ vì còn text. Không mở rộng `Met.` thành `Metformin`. Quy tắc đủ thông tin phải được ghi/test ở plan.
6. **Gom cụm.** So khóa tên theo độ giống kiểu `ratio()` kết hợp tín hiệu mảnh cắt dở; chuỗi con không là điều kiện đủ. Giữ thành viên, count và dòng nguồn, không mất bằng chứng lặp hoặc nhân phiếu do xử lý nội bộ. Không gom các dòng có hàm lượng đã nhận diện khác nhau chỉ vì tên giống; dòng thiếu hàm lượng không được nối gián tiếp hai cụm xung đột.
7. **Đại diện cụm.** Chọn dòng được thành viên hỗ trợ tốt nhất, không mặc định dòng dài nhất; độ dài chỉ là tiêu chí phụ. Sắp cụm theo count, hòa có thứ tự ổn định được plan ghi rõ. Giữ cả cụm nhỏ cho 4.13, không coi count là confidence thuốc.
8. **Tổng hợp hàm lượng.** Gộp các biểu diễn hợp lệ tương đương theo grammar, giữ count/nguồn. Trả mọi giá trị khác nhau và cờ xung đột; có thể ưu tiên đa số nhưng không xóa thiểu số hoặc trả một kết quả chắc chắn khi hòa. Phần OCR sai/chưa hiểu giữ riêng, không sửa rồi tính phiếu cho giá trị đoán.
9. **Tra cứu DB.** Tái sử dụng pg_trgm/index bỏ dấu trên medications.name/raw_active_ingredient; thêm trigram bỏ dấu cho ingredient_aliases bằng migration mới. Cung cấp tra cứu nội bộ bằng khóa tên đủ thông tin của các cụm, ưu tiên cụm lớn nhưng không bỏ các cụm khác. Giữ ID, tên, hoạt chất, hàm lượng, dạng bào chế gốc và nguồn khớp. Không gộp ID trùng tên; alias dẫn tới thuốc qua liên kết thuốc–hoạt chất đã có, không tự tạo ánh xạ.
10. **Vòng đời index.** Dựng index qua migration; DB duy trì theo INSERT/UPDATE/DELETE của DAV/Admin. Runtime chỉ normalize request và truy vấn ứng viên; bỏ đường dựng map/normalize toàn catalog mỗi lần gọi loader. Không thêm snapshot ứng dụng xuyên request, TTL, job rebuild hoặc materialized view.
11. **Kiểm chứng.** Unit cho dòng/khóa/lọc/cụm/hàm lượng và hồi quy; integration cho DB/alias/dữ liệu mới sau commit/lỗi đọc/migration. Chọn và ghi ngưỡng gom cụm bằng raw OCR thật có nhãn gom/giữ riêng, cố định thành regression. Không coi test tổng hợp là bằng chứng độ chính xác trên ảnh thật.

### Ngoài phạm vi

- Chụp/crop/xoay/tiền xử lý ảnh, gọi ML Kit, OCR lại, upload/lưu ảnh (4.10/4.11). Không dùng vấn đề hướng in trên ảnh để thiết kế lại OCR trong task chuẩn hóa.
- Nhận nguyên JSON Block/Line/Element, bounding box/confidence hoặc tạo đầu vào trung gian client; chỉ string có xuống dòng. Không suy vị trí/hướng/confidence không có trong input.
- Trích SĐK thành trường, sửa/xác minh/exact lookup/index SĐK. Chỉ nhận diện mẫu 7b để lọc khóa tên; raw/clean/key trước lọc vẫn giữ SĐK.
- Sửa/tạo biến thể `0/O`, `1/l/I`, `rn/m`, suy tên/hàm lượng theo catalog hoặc mở rộng từ cắt dở; quy đổi đơn vị/tính liều.
- Scoring thuốc từ tên/hàm lượng/hoạt chất/vote, confidence cao/trung bình/thấp, LASA và quyết định top-N UI (4.13). Ngưỡng gom dòng khác ngưỡng confidence thuốc.
- API matching/search mới (4.13/4.15), render/chọn/xác nhận (4.11/4.16); không đổi HTTP hiện hữu.
- Bộ ảnh/nhãn 4.08, go/no-go và đo ML Kit 4.09, bộ fixture thật đầy đủ và đánh giá matching toàn luồng 4.14. Tập raw thật nhỏ chọn ngưỡng gom cụm là kiểm chứng 4.12, không thay thế các task đó.
- Sửa sync/CRUD, dữ liệu catalog/alias/ánh xạ đã xác minh, thêm thuốc ngoài catalog, tạo lịch/liều, gửi yêu cầu bổ sung catalog hoặc Admin duyệt OCR không khớp.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn | Điều rút ra |
|---|---|
| Hội thoại người dùng 29–30/10/2026: luồng 4.08–4.14, sáu việc 4.12, các điều chỉnh đã đồng ý và thông báo reopened | Nguồn phạm vi mới: text giữ dòng; hai bản; trích trước lọc; gom có bảo vệ; giữ thiểu số; DB index; không SĐK lookup/sửa ký tự/JSON cấu trúc. |
| Ảnh vỉ Metformin và raw ML Kit người dùng gửi | Ví dụ lặp tên/biến thể, hàm lượng và metadata. Screenshot chưa là file raw fixture máy đọc được/ground truth đã đối chiếu; không tuyên bố đã chạy OCR trên ảnh. |
| `evidence/requirement-refresh-20261030-before.md`; `evidence/review-flow-gap-20261029.md` | Lưu requirement trước sửa và đối chiếu code. Probe/test ngày 29/10 là lịch sử, không nghiệm thu implementation mới. |
| `AGENTS.md`; `.agents/templates/01-requirement.md`; skills `wf-requirement`, `wf-git`, `wf-db-migration` | Chỉ sửa work ở requirement; có migration là size L; migration mới/DB sạch/quyền tối thiểu; không tự approve hoặc sửa artifact approved sau. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, quy ước trạng thái và mục 2/3/14/16 | Đọc lại quy tắc nguồn; trạng thái/baseline và AC ở 3a. |
| `backend/src/drugtime/modules/catalog/application/normalize_ocr.py`; `domain/catalog_index.py`; `application/build_catalog_index.py`; `api.py` | Cũ: gộp newline, chỉ khóa bỏ dấu, không cụm; hàm lượng lặp thành ambiguous, loader dựng map toàn catalog mỗi lần. Cần đổi interface/test nội bộ. |
| `catalog/adapters/outbound/sql_catalog.py`; `sql_active_ingredients.py`; `domain/medication.py`; `normalize.py`; `parsers/dav_drugbank.py` | Search/raw hiện hữu; alias qua liên kết hoạt chất; DAV có SĐK ở source_ref nhưng lookup SĐK nay ngoài phạm vi. |
| `backend/supabase/migrations/20261002101033_catalog_search_unaccent.sql`; `20260927082912_rebuild_schema_v11.sql` | Có pg_trgm/bỏ dấu trên tên/hoạt chất thô; alias mới B-tree lower(alias_text). DB index không phải snapshot ứng dụng hoặc job rebuild. |
| `backend/tests/unit/test_catalog_ocr_normalization.py`; `test_catalog_index.py`; `backend/tests/integration/test_catalog_index.py` | Test cũ bảo vệ giữ metadata/dựng map mỗi lần; cần thay theo AC mới, không dùng pass cũ để kết luận đầy đủ. |
| `api_contract/openapi.json`, GET /catalog/medications; `backend/tests/unit/test_catalog_search.py`; `backend/tests/architecture/test_module_dependencies.py` | HTTP/search cũ giữ nguyên; facade catalog tuân thủ ma trận module. |
| Backlog `docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx`, Sprint 4 Backlog B19:G19/hàng 20–23, Product Backlog hàng 38 | Truy vết từ vòng requirement trước: 4.12 PB31, 4.13 scoring, 4.14 fixture thật, 4.15 search. Hội thoại mới ưu tiên; không đọc lại workbook ở vòng này. |
| Architecture `DrugTime_Architecture.docx`, table 25 TC-04; SRS `DrugTime_SRS.docx` FR1.2/BR-11/BR-12/UC.06; `work/4.16-selection-confirmation-screen/01-requirement.md`, `03-plan.md` | Nguồn đã đọc ở vòng trước: ảnh ở thiết bị, người dùng kiểm tra; màn chọn mock; mâu thuẫn Admin OCR ở mục 10. Không đọc lại DOCX/sửa 4.16 trong vòng này. |

### 3a. Quyết định nghiệp vụ áp dụng

Nguồn QD: `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, bản nguồn 3.1, baseline `QD-2026-10-03-v1`. ✅ là chốt baseline, chưa xác nhận đã triển khai/chưa có chữ ký Mentor. Quy tắc gom cụm mới là quyết định người dùng trong hội thoại, không tự coi ngưỡng gom là quyết định dược đã xác minh.

| Mã / mục / trạng thái nguồn | Quy tắc áp dụng | AC |
|---|---|---|
| QD-36 / mục 2 / ✅ | Giữ ID, thuốc gỡ ngừng chọn mới, không gộp ID theo tên; lượt đọc mới sau commit phản ánh catalog. | AC17–AC19 |
| QD-38 / mục 2 / ✅ | Hàm lượng khác lượng dùng; giá trị hợp lệ dương, không tự quy đổi; parser/vote không là xác minh dược. | AC3–AC6, AC12–AC14 |
| QD-39 / mục 3 / ✅: người dùng kiểm tra tên/hàm lượng/đơn vị/liều/giờ, chỉ thuốc catalog | Không tự chọn/xác nhận hoặc gán thuốc gần giống; đa số không che xung đột. Xác nhận ở task sau. | AC9–AC14, AC17, AC21 |
| QD-39 / mục 3 / ✅: lưu OCR mã hóa tối đa 24 giờ, xóa khi xác nhận/hủy | 4.12 chỉ xử lý trong bộ nhớ, không log/lưu raw/clean/cụm/request; fixture bao bì kiểm tra không có dữ liệu cá nhân. Không nghiệm thu lưu/xóa OCR thật. | AC21, AC23 |
| QD-39 / mục 3 / ✅: bỏ Admin duyệt scan không khớp | Không khôi phục luồng Admin đối soát OCR. | AC21; ngoài phạm vi |
| QD-45 / mục 14,16 / ✅ | API/backlog chuẩn theo nguồn; không tự thêm endpoint/đổi search/sửa sổ quyết định. | AC20, AC22 |
| PB31 / Architecture TC-04, truy vết vòng trước | Ảnh không rời thiết bị; 4.12 nhận text nội bộ backend, không nhận/gửi ảnh. | AC21 |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| backend | Có | Normalize dòng, kiểu kết quả/cụm, parser/tổng hợp hàm lượng, facade/query SQL, migration alias và unit/integration. |
| frontend | Không | Không đổi ML Kit/camera/JSON hoặc màn xác nhận. |
| api_contract | Không | Không đổi giao tiếp HTTP; interface mới chỉ nội bộ. |
| tests | Không dự kiến | Integration catalog nằm trong backend, chưa E2E app–OCR. |
| docs | Không với chức năng | Chỉ đọc nguồn. Cuối wf-test cập nhật workbook theo wf-testcase nếu plan liệt kê đúng file testcase-book; không sửa schema/sổ quyết định trong requirement. |
| .agents | Không | Không đổi quy trình, gate hoặc scope. |

## 5. Thay đổi API contract

- `contract_change`: no. String nhiều dòng và kết quả dòng/cụm/hàm lượng là interface nội bộ cho 4.13/4.15; không tạo endpoint OCR/matching/cluster/rebuild.
- GET /catalog/medications giữ method/path, q/limit, response, wildcard/whitespace bên trong q, thứ tự và semantics. Query pg_trgm mới không âm thầm thay endpoint cũ.
- API matching thật/request giữ newline do 4.11/4.13 định nghĩa qua contract riêng; không giả định ML Kit luôn có confidence hoặc JSON hình học.
- Nếu plan đòi đổi HTTP phải xét lại contract_change trước code; không gọi thay đổi API là “chỉ backend” để bỏ qua contract.

## 6. Vùng rủi ro và bất biến bị chạm

- **Đúng dữ liệu chọn thuốc:** tránh xóa số/mảnh tên, gom sai tên/hàm lượng; giữ raw/nguồn/chưa hiểu/xung đột. Đại diện/vote/trigram không xác minh thuốc hoặc liều.
- **Schema/index:** migration mới, không sửa migration đã áp dụng; kiểm reset sạch, định nghĩa/index sử dụng được, quyền và dữ liệu cũ theo wf-db-migration. Không thêm bảng OCR hoặc mở quyền client. Kế hoạch SQL cụ thể ở plan.
- **Ranh giới module:** qua facade catalog, không import ngoài ma trận; dependency liên module mới cần C4 trước code. Không sửa engine tương tác tất định.
- **Bí mật/OCR:** không credential/log/storage/gửi OCR ra ngoài. Không endpoint dữ liệu patient, không thay PEP/consent/liều/lịch hoặc thêm test cross-patient không liên quan.
- **Catalog cập nhật:** giao dịch đọc mới sau commit phản ánh thay đổi; lỗi DB không trả snapshot cũ; không cam kết catalog bất biến tới lúc xác nhận. Consumer xác nhận phải đối chiếu ID ở task tích hợp.

## 7. Tiêu chí chấp nhận

Unit không cần DB/mạng; integration dùng PostgreSQL thật và catalog tổng hợp. Raw thật dùng làm fixture phải có provenance/nhãn và không có dữ liệu cá nhân. Evidence không chứa nội dung request OCR thực.

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given LF/CRLF, dòng trống/tab/dòng trùng, When normalize, Then còn thứ tự/nguồn từng dòng, raw không đổi, không nối dòng; dòng không query vẫn truy vết được. | unit |
| AC2 | Given `THUỐC ĐỎ` NFC/NFD/whitespace khác nhau, When normalize, Then clean NFC `thuốc đỏ`, key `thuoc do`, còn dấu ở clean, quy tắc clean/key idempotent, `đ/Đ` đúng. | unit |
| AC3 | Given `Vitamin B12`, `Vitamin D3`, `5mg`, `O0l1`, `Metforrnin`, `5OOmg`, When trích/lọc, Then giữ số/ký tự, trích 5mg trước lọc mảnh ngắn, không sửa ký tự hoặc mở rộng `Met.`. | unit |
| AC4 | Given 7a, When trích, Then `500MG`/`500 mg` cùng `500 mg`, `0,5 g`/`0.5g` cùng `0.5 g`, không quy đổi; mỗi biểu thức có nguồn dòng. | unit |
| AC5 | Given `5mg/ml`, `250mg/5ml`, `500mg + 65mg`, `0,9%`, When trích/tổng hợp, Then giữ tử/mẫu/thứ tự phối hợp, không đếm thành phần thành các hàm lượng cạnh tranh. | unit |
| AC6 | Given âm/0, `5OOmg`, `500mg + 5OOmg`, `500mg 250mg`, số lô/HSD/quy cách, When trích, Then không chọn phần đầu của biểu thức hỏng hoặc đoán số; giữ chưa hiểu/nhiều giá trị/nguồn; metadata không thành hàm lượng. | unit |
| AC7 | Given `Metformin 500mg viên nén hộp 10 vỉ` hoặc `Metformin 500mg\nSDK: VD-13882-11`, When trích rồi lọc 7b, Then khóa tên dòng tên là `metformin`, dòng chỉ SĐK không query tên, clean/key trước lọc giữ thông tin, 500mg đã trích; không có field/lookup SĐK. | unit |
| AC8 | Given dòng chỉ quy cách/ký hiệu, mảnh cắt dở ít thông tin và tên có B12/D3, When quyết định query độc lập, Then không query rỗng/rộng, không xóa mảnh khỏi raw/clean/key hoặc hỏng tên; eligibility có fixture dương/âm/lý do. | unit |
| AC9 | Given `Metformin` lặp/hoa thường/whitespace, When cluster, Then cùng cụm, đúng count dòng nguồn, giữ mọi thành viên, không nhân phiếu do xử lý nội bộ. | unit |
| AC10 | Given fixture gán nhãn gom/giữ riêng và mảnh cắt dở, When cluster với ngưỡng đã ghi, Then đúng nhãn; substring không đủ. `Candesartan Krka 16mg` và `Candesartan Krka 160mg` giữ riêng; dòng thiếu hàm lượng không nối gián tiếp hai cụm. | unit |
| AC11 | Given `Metformin`, `Metformin`, `Metformin bydrock.`, When chọn đại diện, Then nếu cùng cụm thì đại diện `metformin`, không lấy dòng dài lỗi; cụm xếp theo count, hòa ổn định, giữ cả cụm nhỏ. | unit |
| AC12 | Given hai dòng `Metformin 500mg`, When trích/tổng hợp, Then giá trị `500 mg` count 2 với hai nguồn, không ambiguous chỉ vì lặp; cụm tên nếu gom vẫn có hai thành viên. | unit |
| AC13 | Given 500mg 4 lần/850mg 1 lần hoặc hai giá trị hòa, When tổng hợp, Then giữ cả giá trị/count/nguồn/cờ xung đột, không trả duy nhất hàm lượng chắc chắn theo đa số; không tự gán dòng hàm lượng rời cho tên. | unit |
| AC14 | Given dòng `Metformin 500mg` và dòng `Metformin 5OOmg`, When xử lý, Then giữ hợp lệ dòng đầu/bất định dòng sau, không sửa O/0, tính dòng sai thành phiếu 500mg hoặc che phần chưa hiểu. | unit |
| AC15 | Given rỗng/whitespace/chỉ nhiễu, When normalize/query, Then kết quả rỗng/không đủ thông tin có cấu trúc, không tên/hàm lượng mặc định/query toàn catalog; non-string bị từ chối rõ, không echo raw vào lỗi/log. | unit |
| AC16 | Given migration mới/DB có dữ liệu, When reset sạch rồi áp dụng, Then có trigram alias bỏ dấu, tái dùng index tên/hoạt chất, không sửa migration cũ/dữ liệu gốc hoặc mở quyền client. Kiểm định nghĩa và khả năng query dùng index, không ép planner chọn index trên bảng nhỏ. | integration |
| AC17 | Given tên/hoạt chất/alias có dấu, nhiều ID trùng tên khác strength/form và active/soft-delete, When query DB, Then đúng fixture qua tên/hoạt chất/alias bỏ dấu, giữ ID/raw/nguồn khớp, không soft-delete; alias chỉ qua liên kết đã có. | integration |
| AC18 | Given nhiều cụm/count và catalog lớn hơn giới hạn search cũ, When gọi interface mới, Then ưu tiên cụm lớn nhưng giữ nguồn ứng viên cụm khác; không dựng map/normalize toàn catalog hoặc ngầm kế thừa limit 50. Giới hạn kỹ thuật nếu có ghi/test trong plan; consumer quyết top-N cuối. | unit + integration |
| AC19 | Given đã query rồi catalog/alias/ánh xạ thêm/sửa/gỡ và commit, When query giao dịch đọc mới cùng tiến trình, Then dữ liệu mới không restart/TTL/rebuild Python; lỗi đọc truyền lên, không snapshot cũ/giả rỗng thành công. | integration |
| AC20 | Given normalize/index mới, When hồi quy ingest/search/architecture, Then raw hiển thị giữ dấu/hoa thường; endpoint cũ không đổi q/limit/wildcard/whitespace/thứ tự/shape; không import sai/đổi engine tương tác. | unit + integration |
| AC21 | Given fixture, When normalize/cluster/query, Then không log/lưu/gửi OCR ra ngoài/gọi OCR hoặc LLM/ghi catalog/alias/ánh xạ/liều/lịch/tự chọn thuốc; quyền DB mới không cấp anon/authenticated. | unit + integration |
| AC22 | Given hai caller nội bộ mô phỏng 4.13/4.15, When dùng facade, Then nhận dòng/cụm/hàm lượng/count/nguồn/xung đột và ứng viên cùng quy tắc, không cần JSON client/HTTP mới hoặc confidence thuốc/top-N UI. | unit |
| AC23 | Given tập raw thật nhỏ có provenance/nhãn gom-giữ riêng và fixture biên tổng hợp, When chọn ngưỡng và chạy regression, Then ghi ngưỡng/quy tắc đại diện/mảnh cắt dở, expected cố định, kết quả/ca sai/giới hạn rõ. Không có raw thật thì không đánh dấu Pass chỉ bằng screenshot/test tổng hợp. | unit |

### 7a. Grammar hàm lượng MVP tiếp tục hỗ trợ

Đây là nhận diện cú pháp, không xác minh dược hoặc quy đổi. Biểu thức ngoài bảng/ký tự OCR sai giữ chưa hiểu. Nhiều nhóm cùng dòng không liên kết rõ phải giữ nhiều giá trị/bất định; nhiều dòng cùng giá trị là bằng chứng lặp theo AC12.

| Đầu vào | Biểu diễn |
|---|---|
| `500MG`, `500 mg` | `500 mg` |
| `0,5 g`, `0.5g` | `0.5 g` |
| `25 mcg` | `25 mcg` |
| `5 mg/ml` | `5 mg/ml` |
| `250mg/5ml` | `250 mg/5 ml` |
| `500mg + 65mg` | `500 mg + 65 mg`, giữ thứ tự thành phần |
| `0,9%` | `0.9 %` |
| `Vitamin B12`, `Vitamin D3` | Không trích số thuộc tên thành hàm lượng |

Không tự hỗ trợ thêm IU/UI, µg/μg, `500/65mg`, phân nhóm hàng nghìn, lỗi OCR số/đơn vị hoặc quy đổi g↔mg. Danh sách đơn vị còn mở ở QD-38 không được coi đã chốt đầy đủ.

### 7b. Lọc khóa tên và mảnh ngắn

- Whitelist MVP: cụm `viên nén`, `viên sủi`, `sủi`, `siro`; quy cách `hộp <số> vỉ`, `<số> viên`; SĐK dạng `VD-<chữ số>-<chữ số>`/`VN-<chữ số>-<chữ số>` có thể kèm nhãn SĐK/SDK; ký hiệu ®/™/•. So không phân biệt hoa thường/dấu, khớp ranh giới từ/cả mẫu; không xóa một phần tên chỉ vì chứa chuỗi giống noise.
- `SDK: VD-13882-11` minh họa từ raw người dùng, không phải yêu cầu xác minh SĐK. Prefix/metadata chưa khớp được giữ; không mở regex tùy ý để xóa mọi text lỗi.
- Chỉ lọc khóa tên; raw/clean/key trước lọc còn nguyên thông tin để đối chiếu. Mẫu thêm ở plan phải có ví dụ bảo vệ xóa nhầm.
- Không có quy tắc “ngắn hơn 3–4 ký tự thì xóa”. B12/D3 thuộc tên được giữ; 5mg qua parser trước lọc. Met. không tự mở rộng/truy vấn độc lập khi thiếu thông tin; eligibility/containment phải được plan ghi và test.

## 8. Câu hỏi mở

Không còn câu hỏi chặn requirement; không hỏi lại sáu việc/các điều chỉnh đã được đồng ý.

Phụ thuộc kiểm chứng: chưa thấy file raw ML Kit thật có nhãn 4.08/4.09 trong các vùng đã rà; ảnh raw hội thoại là screenshot. Plan cần xác định tập raw thật nhỏ/provenance để chọn ngưỡng; khi thiếu thì ghi rõ và chưa đánh dấu AC23 Pass. Không bịa confidence/nhãn hoặc tuyên bố đã đo accuracy.

## 9. Giả định và điểm đã xác nhận

- Một lần một vỏ/một thuốc; nhiều dòng/bản in lặp, có thể phối hợp. Nhiều hàm lượng không mặc nhiên nhiều thuốc.
- Tách dòng → clean/key → trích hàm lượng → lọc khóa tên → gom có bảo vệ → trả cụm/hàm lượng/xung đột và tra cứu DB. Không có hình học để ghép các dòng thành một lần in.
- Không cache là không giữ snapshot ứng dụng xuyên request; không cấm index PostgreSQL. DB duy trì index theo dữ liệu, không cần job rebuild sau mỗi CRUD.
- ratio()/containment chỉ nhóm dòng; 4.13 chấm điểm/confidence/voting cuối. Count chỉ số lần xuất hiện quan sát được, không khẳng định các lần đọc độc lập.
- Ngưỡng, đại diện, eligibility, tie-break và limit query kỹ thuật được plan ghi/test; không tự đặt top-N hoặc SLO/accuracy. Không cam kết ví dụ top-3 ≥90% của task 4.09.
- Catalog là nguồn sự thật; không gộp ID/sửa alias/suy ánh xạ. Consumer đối chiếu trạng thái thuốc trước xác nhận ở task tích hợp, không sửa 4.16 tại đây.

## 10. Phát sinh

- 03-plan/04-impl-notes/05-test-report/06-review còn approval/nội dung phạm vi cũ. Không sửa trong lượt này. Sau duyệt requirement cần mở lại/cập nhật các giai đoạn tương ứng; pass cũ không nghiệm thu AC mới.
- Trước lượt này đã có 9 file backend và workbook docs chưa commit; gitlink backend/frontend/api_contract/tests/docs cũng khác từ trước. Snapshot trước/sau ở evidence bảo vệ nội dung đang có; không stage/revert/commit/sửa chúng trong requirement.
- Scope kiểm toàn working tree/commit task nên báo thay đổi cũ ngoài phạm vi requirement. Giữ raw kết quả, so hash trước/sau; không báo scope pass hoặc sửa script/reset code để làm sạch. User đã cho phép cập nhật requirement này, không yêu cầu can thiệp các thay đổi cũ.
- SRS cũ có Admin xử lý OCR không khớp, mâu thuẫn QD-39; tiếp tục ngoài phạm vi. Không đưa Cloud Vision/gửi ảnh ra ngoài vào task chuẩn hóa.
- Alias python WindowsApps không chạy trong môi trường agent; dùng `C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe`, không đổi cài đặt máy.

### Bằng chứng vòng sửa requirement

- Gate đầu lượt: requirement draft/được bắt đầu; `evidence/requirement-refresh-20261030-gate-start.log`.
- Bản trước sửa: `evidence/requirement-refresh-20261030-before.md`; snapshot `...-before.json/.log`. Script audit trong scratch/requirement-refresh-20261030-audit.py chỉ kiểm phạm vi, không code sản phẩm/không đề xuất commit scratch.
- Scope: chạy runtime trên với `.agents/scripts/scope.py 4.12-ocr-text-normalization-catalog-index --stage requirement` → **exit 1**, báo 10 file backend/docs đã thay đổi từ trước; raw tại `evidence/requirement-refresh-20261030-scope.log`. Không gọi đây là scope pass.
- Audit: chạy runtime trên với `work/4.12-ocr-text-normalization-catalog-index/scratch/requirement-refresh-20261030-audit.py after` → **exit 0**; tập/hash 10 file ngoài work, hash 03–06 và trạng thái git các repo không đổi so với snapshot trước. Log `evidence/requirement-refresh-20261030-audit.log`, dữ liệu `...-before.json`/`...-after.json`. Vì lượt này chỉ cập nhật requirement đã được người dùng cho phép, không cần yêu cầu lại quyền sửa các file cũ mà thực tế chưa đụng tới.
- Gate sau sửa: chạy runtime trên với `.agents/scripts/gate.py 4.12-ocr-text-normalization-catalog-index` → **exit 0**, requirement draft, size L/contract_change no; 03–06 approved nhưng ĐÃ CŨ do đầu vào thay đổi. Log `evidence/requirement-refresh-20261030-gate-final.log`.
- Không chạy test chức năng hoặc migration ở lượt chỉ sửa requirement; không dùng kết quả unit ngày 29/10 để khẳng định tính năng mới pass.

## 11. Size

- `size`: L vì cần migration index alias, theo wf-requirement. Thêm dòng/cụm/vote/xung đột và thay query cần unit/integration; không thuộc S dù một submodule chức năng.
- `contract_change`: no vì chưa đổi HTTP; có migration không mặc nhiên đổi API. Bảng file/checklist ở plan sau duyệt, không đặt ở requirement L.

## Bước tiếp theo

- Đang chờ: người duyệt đọc/duyệt requirement mới; không còn câu hỏi nghiệp vụ chặn. Raw thật cho AC23 là phụ thuộc kiểm chứng cần plan xử lý.
- Người duyệt tự chạy: `& 'C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe' .agents/scripts/gate.py approve 4.12-ocr-text-normalization-catalog-index requirement`.
- Sau duyệt: mở lại plan cũ, cập nhật theo bản này ở lượt riêng qua wf-next/wf-plan; approval cũ không đủ để code tiếp. Người dùng tự chạy reopen khi cần; agent không thay trạng thái duyệt hoặc viết approval.
- Chỉ sửa requirement/evidence/scratch task; chưa plan/code/migration/contract. Đề xuất lưu artifact/evidence trên nhánh task khi người dùng yêu cầu commit; không stage scratch.
- Cập nhật lần cuối: 2026-10-30, Codex.
