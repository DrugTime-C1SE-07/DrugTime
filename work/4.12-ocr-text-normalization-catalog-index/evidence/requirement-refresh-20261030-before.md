---
task: 4.12-ocr-text-normalization-catalog-index
title: OCR text normalization + catalog index
type: feature
stage: requirement
size: M
contract_change: no
affected: [backend]
status: draft
---

# 4.12 · Chuẩn hóa văn bản OCR và index danh mục thuốc

## 1. Mục tiêu

Cung cấp bộ chuẩn hóa text OCR và index danh mục dùng chung cho task 4.13 (matching/scoring) và 4.15 (search/autocomplete). Giữ đúng tên, hàm lượng và định danh catalog để các task sau tạo ứng viên cho người dùng kiểm tra.

Người dùng đã chốt ngày 28/10/2026: OCR vỏ thuốc, mỗi lần một thuốc; chạy normalize/index ở backend; giữ ký tự nghi ngờ, không tự đoán; không cache index. Không còn câu hỏi chặn requirement.

## 2. Phạm vi

### Trong phạm vi

- Xử lý text của một vỏ thuốc/một thuốc mỗi lần gọi; có thể có nhiều dòng, không đồng nhất nhiều dòng với nhiều thuốc.
- Bỏ dấu tiếng Việt, kể cả `đ/Đ` → `d`, viết thường, gộp khoảng trắng và lọc nhiễu đã đặc tả. NFC/NFD cho cùng khóa so khớp.
- Tách hàm lượng nhận diện được khỏi chuỗi phục vụ so khớp; giữ chữ số thuộc tên như `B12`, `D3`. Chuỗi còn lại chưa được khẳng định là tên chuẩn trong catalog. Phân biệt hàm lượng với số lượng dùng/quy cách đóng gói.
- MVP lọc nhiễu ký tự/whitespace đã liệt kê; số lô, hạn dùng, nhà sản xuất và metadata chưa nhận diện vẫn được giữ trong text chuẩn hóa, không suy chúng thành hàm lượng. Không tuyên bố đã trích xuất được riêng tên thuốc từ mọi bố cục vỏ.
- Dùng cùng quy tắc chuẩn hóa cho text truy vấn và dữ liệu index từ tên/hoạt chất thô của catalog. Giữ nguyên dữ liệu gốc phục vụ hiển thị, không ghi đè tên có dấu.
- Xây index từ toàn bộ thuốc catalog còn được chọn mới; giữ ID, tên, hoạt chất thô, `strength_text`, `dosage_form` và khóa chuẩn hóa tương ứng khi có dữ liệu. Không gộp các ID chỉ vì trùng khóa tên.
- Giao diện nội bộ cho các consumer 4.13/4.15, tuân thủ facade/ranh giới module hiện có; chưa tích hợp endpoint/UI của các task đó.
- Cung cấp hàm nạp catalog hiện tại và dựng/dựng lại index cho từng lượt gọi, không tái sử dụng snapshot qua các lượt gọi. Khi tích hợp 4.13/4.15, mỗi lượt dùng lấy catalog mới; dữ liệu index chỉ dùng trong lượt xử lý đó.
- Unit test normalize/index; test tích hợp nguồn đọc catalog thật và dựng lại sau khi dữ liệu thay đổi trong cùng tiến trình. Không cần cơ chế thông báo thay đổi hoặc làm mới cache.

### Ngoài phạm vi

- ML Kit/camera/nhận dạng ảnh, upload hoặc lưu ảnh/text OCR; phân đoạn đơn nhiều thuốc.
- Fuzzy matching, sửa tên theo catalog, scoring/confidence/threshold/top-N (4.13); bộ fixture OCR thực tế đầy đủ (4.14). 4.12 vẫn có unit test tổng hợp của riêng mình.
- Endpoint tìm kiếm/autocomplete (4.15), màn chọn/xác nhận (4.16); không thay hành vi search hiện tại.
- Tự sửa `O/0`, `l/1` trong tên/số; suy ra hàm lượng/hoạt chất không chắc chắn; quy đổi đơn vị hoặc tính liều.
- Mở rộng alias hoạt chất thành tên thuốc hoặc sửa bảng ánh xạ hoạt chất đã xác minh.
- Tạo lịch, thêm thuốc người dùng, lưu nháp, gửi yêu cầu bổ sung catalog, Admin duyệt OCR không khớp.
- Cache index xuyên lượt gọi, TTL/revision/invalidation, index lưu trên Redis/file, job hoặc hook cập nhật catalog. Không thêm migration/schema hoặc sửa writer DAV/Admin cho vòng đời index.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| Yêu cầu và trả lời của người dùng, 28/10/2026 | Chuẩn hóa/tách hàm lượng; index từ catalog dùng chung 4.13/4.15; một vỏ thuốc/một thuốc; backend; không tự sửa ký tự nghi ngờ. Sau trao đổi về vòng đời index, người dùng chốt “không cache”. |
| `AGENTS.md`; `.agents/skills/wf-next/SKILL.md`; `.agents/skills/wf-requirement/SKILL.md`; `.agents/skills/wf-git/SKILL.md` | Lập và duyệt requirement trước code; chỉ ghi artifact task trong giai đoạn này, không tự duyệt hoặc commit/push. |
| `docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx`, `Sprint 4 Backlog!B19:G19`, hàng 20–23 | 4.12 thuộc PB31, 11 giờ, Nguyen; 4.13 matching/scoring, 4.14 test OCR thực, 4.15 search/autocomplete, 4.16 chọn/xác nhận. Không coi trạng thái workbook là bằng chứng implementation. |
| Cùng workbook, `Product Backlog`, hàng 38 | PB31 quét vỉ thuốc bằng ML Kit trên thiết bị, ảnh không rời thiết bị; không khớp/confidence thấp thì tìm thủ công. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, quy ước trạng thái và mục 2/3/14/16 | QD-36/38/39/45; danh sách đơn vị/quy đổi chưa được chốt đầy đủ. Truy vết ở mục 3a. |
| `docs/Team1_DTU/03_Design/Architecture/DrugTime_Architecture.docx`, table 25, TC-04 | ML Kit trên thiết bị rồi matching catalog, ảnh không rời thiết bị; nguồn chưa xác định vị trí index. Người dùng đã chọn backend. |
| `docs/Team1_DTU/02_Requirements/Software Requirements Specification/DrugTime_SRS.docx`, FR1.2, BR-11, BR-12/UC.06 | Quét vỉ thuốc, kiểm tra thủ công và fallback catalog. Phần Admin nhận scan không khớp mâu thuẫn QD-39; loại khỏi task. |
| `backend/src/drugtime/modules/catalog/normalize.py`; `backend/tests/unit/test_catalog_sync.py` | Normalize ingest hiện chỉ NFC/gộp whitespace; không được đổi nó thành hàm làm mất dấu/chữ thường của dữ liệu hiển thị. |
| `backend/src/drugtime/modules/catalog/domain/medication.py`; `catalog/parsers/dav_drugbank.py`; `catalog/repository.py` | Có ID/tên/hoạt chất thô/hàm lượng/dạng bào chế. Sync có upsert, soft-delete và phục hồi thuốc, nên index có thể cũ sau sync. |
| `backend/src/drugtime/modules/catalog/service.py`; `catalog/application/service.py`; `catalog/adapters/outbound/sql_catalog.py`; `catalog/api.py` | Catalog thay đổi từ cả DAV sync và Admin CRUD. Search bỏ soft-delete; liên module qua facade. Chỉ refresh tại sync không bao phủ Admin CRUD. |
| `backend/supabase/migrations/20261002101033_catalog_search_unaccent.sql` | Đã có SQL `catalog_search_key()` và hai GIN trigram index tên/hoạt chất. Chưa có tách hàm lượng/index OCR nội bộ. |
| `backend/supabase/migrations/20260927082912_rebuild_schema_v11.sql`, `medications`/`medication_active_ingredients` | `strength_text` thô khác hàm lượng theo ánh xạ hoạt chất đã xác minh; task không ghi đè ánh xạ. |
| `api_contract/openapi.json`, `GET /catalog/medications`; `backend/tests/unit/test_catalog_search.py` | q/limit và substring tên/hoạt chất không dấu/chữ thường; giữ khoảng trắng bên trong q. Normalize OCR mạnh hơn không được âm thầm đổi semantics này. |
| `backend/tests/architecture/test_module_dependencies.py` | Chưa có module OCR trong ma trận; không tự thêm dependency mới. |
| `work/4.16-selection-confirmation-screen/01-requirement.md`, mục 2/3/9; `03-plan.md` | 4.16 dùng ứng viên mock, chưa định nghĩa API OCR thật, chờ 4.13/4.15. DTO mock không phải API chuẩn. |

### 3a. Quyết định nghiệp vụ áp dụng

Nguồn quyết định chính tổng hợp từ hồ sơ bản 3.1, baseline `QD-2026-10-03-v1`. ✅ nghĩa là đã chốt baseline, chưa xác nhận triển khai/chưa có chữ ký Mentor. Ví dụ parser ở mục 7a là đề xuất mới của task, không phải nội dung đã chốt trong QD-38.

| Quyết định, mục, trạng thái | Quy tắc trong phạm vi | AC / giới hạn |
|---|---|---|
| QD-36, mục 2, giữ ID/ngừng chọn mới, ✅ | Không gộp ID; mỗi lần nạp/dựng lại đọc catalog hiện tại và loại thuốc đã gỡ trước thời điểm đọc. | AC8–AC11; không cache giữa các lượt, không sửa lịch sử. |
| QD-38, mục 2, hàm lượng/đơn vị, ✅ | Hàm lượng khác lượng dùng; không tự suy ra/quy đổi đơn vị khi thiếu xác minh. | AC3–AC6/AC13; format hỗ trợ phải được chỉ rõ. |
| QD-39, mục 3, kiểm tra/chỉ thuốc trong catalog, ✅ | Normalize/index không tự chọn/xác nhận thuốc, không tạo thuốc ngoài catalog. | AC8/AC13; matching/xác nhận ở task sau. |
| QD-39, mục 3, ảnh/văn bản OCR, ✅ | Không thêm log/storage OCR. Nếu sau này lưu phải mã hóa, tối đa 24 giờ, xóa khi xác nhận/hủy. | AC13; task này không nghiệm thu cơ chế lưu/xóa OCR thật. |
| QD-39, mục 3, bỏ Admin duyệt OCR không khớp, ✅ | Không xây luồng đối soát Admin theo SRS cũ. | Ngoài phạm vi; mục 10 ghi mâu thuẫn. |
| QD-45, mục 14/16, ✅ | Dùng backlog/contract chuẩn; không tự đặt endpoint OCR hoặc đổi search. | AC12. |
| PB31; Architecture TC-04 | Ảnh không rời thiết bị. | 4.12 không nhận ảnh; xử lý text nội bộ backend theo trả lời người dùng. |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| backend | Có | Normalize/index, nguồn đọc catalog mới mỗi lượt, unit/integration test. Không sửa các writer hoặc thêm migration. |
| frontend | Không | Chưa tích hợp ML Kit, API truyền text, autocomplete hoặc UI. |
| api_contract | Không | Không thêm/sửa giao tiếp HTTP. |
| tests | Không dự kiến | Test DB/catalog nằm trong backend; chưa có E2E app–OCR. |
| docs | Không đối với chức năng | Chỉ đọc nguồn. Excel test case tổng xử lý cuối wf-test; khai báo file cụ thể khi lập plan. |
| .agents | Không | Không thay quy trình. |

## 5. Thay đổi API contract

- `contract_change`: no. Phạm vi là bộ xử lý/index nội bộ; không thêm endpoint OCR/index/rebuild hoặc trường confidence.
- Endpoint tham chiếu: `GET /catalog/medications`; không thay method/path/q/limit/response/thứ tự/semantics của nó.
- Việc tích hợp consumer và thay API nếu cần thuộc requirement/contract được duyệt của task tương ứng. Nếu trao đổi tiếp dẫn tới API mới trong 4.12, phải đánh giá lại frontmatter/AC trước duyệt.

## 6. Vùng rủi ro và bất biến bị chạm

- Đúng tên/hàm lượng ở đầu vào chọn thuốc: giữ chữ số thuộc tên, dữ liệu chưa chắc chắn, ID và trường gốc; không tự xác minh thuốc hoặc khuyến nghị liều.
- Text OCR có thể nhạy cảm: chỉ xử lý giá trị trong bộ nhớ, không mở endpoint đọc dữ liệu bệnh nhân, không thêm log/storage/gửi ra ngoài. Không thay PEP/consent/access log.
- Không thay schema, sync, CRUD hoặc job. Quyết định không cache không cần cơ chế version/invalidation cho catalog.
- Không sửa liều/lịch hoặc engine tương tác; không thêm test cross-patient/chạy đua liều không liên quan.
- Không thêm import liên module ngoài ma trận. Nếu plan cần dependency mới, cập nhật C4 theo quy trình trước khi code.

## 7. Tiêu chí chấp nhận

`unit` không cần DB/mạng. `integration` dùng PostgreSQL thật và dữ liệu catalog tổng hợp. Mỗi lượt nạp/dựng index đọc catalog hiện tại trong lượt đó; không bảo đảm catalog không đổi sau thời điểm đọc.

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given text tiếng Việt NFC/NFD, hoa/thường, có `đ/Đ`, When normalize, Then cùng khóa bỏ dấu/chữ thường; `THUỐC ĐỎ` và `thuốc đỏ` → `thuoc do`. | unit |
| AC2 | Given text một vỏ thuốc có whitespace/tab/xuống dòng/bullet `•`/dấu `®`/`™`, When normalize, Then gộp khoảng trắng và bỏ nhiễu đã liệt kê, không dính hai từ; chạy lại chuẩn hóa khóa cho cùng kết quả. Không tự tách thành nhiều thuốc. | unit |
| AC3 | Given `Vitamin B12`, `Vitamin D3`, tên chứa số hoặc ký tự nghi ngờ `O/0`, `l/1`, When normalize, Then giữ chữ số/ký tự thuộc tên; không tự thay ký tự hoặc tạo hàm lượng chỉ từ số trong tên. | unit |
| AC4 | Given hàm lượng đơn trong mục 7a, When normalize, Then tách tên/hàm lượng; cách viết liền/cách đơn vị, dấu phẩy/chấm thập phân cho biểu diễn theo bảng, không đổi độ lớn hoặc quy đổi đơn vị. | unit |
| AC5 | Given nồng độ/phối hợp trong mục 7a, When normalize, Then giữ đủ tử/mẫu và mọi thành phần theo thứ tự, không chỉ lấy số đầu hoặc bỏ quan hệ `/`/`+`. | unit |
| AC6 | Given `20 viên`, số âm/0, `5OOmg`, hàm lượng thiếu/sai hoặc `Thuốc Mẫu 500mg 250mg` không có dấu phối hợp/quan hệ rõ, When normalize, Then không đoán thành một hàm lượng dương đã xác minh; phần chưa hiểu vẫn phân biệt được với phần tách hợp lệ, không chọn tùy tiện một giá trị. Metadata `Số lô AB12, HSD 10/2027` không trở thành hàm lượng và không bị xóa tùy tiện. | unit |
| AC7 | Given chuỗi rỗng/whitespace/chỉ nhiễu đã liệt kê, When normalize, Then kết quả rỗng, không tạo tên/hàm lượng mặc định; đầu vào không phải chuỗi bị từ chối rõ ràng. | unit |
| AC8 | Given catalog có trường tùy chọn thiếu, When build index, Then dùng cùng quy tắc chuẩn hóa với text truy vấn, giữ đúng ID/dữ liệu gốc, không crash hoặc tự suy ra hoạt chất/hàm lượng đã xác minh. | unit |
| AC9 | Given các ID có cùng tên chuẩn hóa nhưng khác hàm lượng/dạng bào chế, When build, Then giữ mọi ID cùng dữ liệu riêng; không ghi đè/gộp theo tên. | unit |
| AC10 | Given catalog DB gồm active/soft-delete, When build từ catalog thật, Then có đủ active và không có soft-delete; kiểm tập lớn hơn 50 kết quả của search hiện tại, catalog rỗng và lỗi đọc DB không bị coi là catalog rỗng thành công. | integration |
| AC11 | Given một lượt gọi đã dựng index A, sau đó catalog thêm/sửa/gỡ thành B và commit, When gọi lại hàm nạp/dựng index trong cùng tiến trình với giao dịch đọc mới, Then đọc DB và phản ánh B, không dùng lại A hoặc chờ restart/TTL; cùng snapshot cho nội dung/thứ tự ổn định. Nếu đọc mới lỗi thì báo lỗi, không trả snapshot cũ như kết quả thành công. | integration |
| AC12 | Given normalize/index mới, When chạy hồi quy ingest/search/architecture, Then dữ liệu hiển thị vẫn giữ dấu/hoa thường; search q/limit/wildcard/khoảng trắng bên trong và thứ tự giữ đúng contract; không phát sinh import sai ranh giới. | unit + integration |
| AC13 | Given fixture tổng hợp, When gọi normalize/build, Then không lưu/log text OCR, không gọi dịch vụ ngoài, không sửa catalog/ánh xạ/liều/lịch hoặc tự chọn/xác nhận thuốc. | unit |
| AC14 | Given hai caller nội bộ mô phỏng 4.13 và 4.15, When sử dụng bộ normalize/index, Then cùng interface/quy tắc và không phụ thuộc implementation riêng của consumer hoặc endpoint/UI chưa có. | unit |

### 7a. Format hàm lượng MVP đề xuất

Đây là chuẩn hóa cách viết text, không quy đổi giá trị giữa đơn vị và không xác nhận dữ liệu dược. Bảng cần được người duyệt đọc cùng requirement; các format ngoài bảng giữ là chưa phân tích, không tự đoán.

| Đầu vào tổng hợp | Tên chuẩn hóa | Hàm lượng |
|---|---|---|
| `• Thuốc Mẫu 500MG` | `thuoc mau` | `500 mg` |
| `Thuốc Mẫu 0,5 g` / `Thuốc Mẫu 0.5 g` | `thuoc mau` | `0.5 g` |
| `Thuốc Mẫu 25 mcg` | `thuoc mau` | `25 mcg` |
| `Thuốc Mẫu 5 mg/ml` | `thuoc mau` | `5 mg/ml` |
| `Thuốc Mẫu 250mg/5ml` | `thuoc mau` | `250 mg/5 ml` |
| `Thuốc Mẫu 500mg + 65mg` | `thuoc mau` | Hai thành phần `500 mg`, `65 mg`, giữ thứ tự/phối hợp |
| `Thuốc Mẫu 0,9%` | `thuoc mau` | `0.9 %`, không đổi sang mg/ml |
| `Vitamin B12` | `vitamin b12` | Không có |

Chưa chốt/hỗ trợ: IU/UI, `µg`/`μg` và quan hệ cách viết với mcg, phối hợp viết tắt `500/65mg`, dấu phân nhóm hàng nghìn hoặc lỗi OCR trong số/đơn vị. Có thể bổ sung sau khi có mẫu và quyết định rõ; QD-38 chưa cung cấp danh sách cụ thể. Text toàn vỏ có thể chứa ngày/số lô/số lượng: không được coi mọi số là hàm lượng hoặc xóa toàn bộ chữ số để loại nhiễu.

## 8. Câu hỏi mở

Không còn câu hỏi chặn. Q1 về vòng đời index đã được trả lời “không cache” ngày 28/10/2026; quyết định được chuyển sang phạm vi, AC11 và mục 9.

Q2 [không chặn] Cần thêm/bớt format hàm lượng nào trong bảng 7a để phù hợp các vỏ thuốc mục tiêu?
- Ảnh hưởng: phạm vi parser/unit test; không đổi phần bỏ dấu/index.
- Lựa chọn: dùng bảng MVP / bổ sung mẫu cụ thể đã bỏ thông tin cá nhân.
- Giả định mặc định: dùng bảng 7a; ngoài danh sách trả trạng thái chưa phân tích, không tự quy đổi.

### 8a. Vòng đời index đã chốt

Mỗi lượt tiêu thụ: đọc catalog active hiện tại → chuẩn hóa → dựng index → dùng trong lượt đó. Không giữ index để phục vụ lượt sau; không có TTL, revision, invalidation hoặc refresh ở startup/worker. 4.12 cung cấp builder/rebuilder và hàm nạp từ catalog; tích hợp 4.13/4.15 phải gọi đường nạp mới này thay vì tự giữ snapshot xuyên lượt.

Lý do: catalog có cả writer DAV và Admin, chạy ở các tiến trình khác nhau. Đọc mới mỗi lượt tránh phải đồng bộ cache giữa các writer/process. Đánh đổi đã giải thích với người dùng là lặp lại đọc/chuẩn hóa toàn catalog mỗi lượt; đo hiệu năng khi tích hợp, không thêm cache trong task này.

Trước xác nhận thuốc ở luồng tích hợp phải đối chiếu lại ID/trạng thái/dữ liệu hiện tại vì catalog có thể thay đổi sau lúc dựng index. Đây là yêu cầu đưa vào task tích hợp, không sửa artifact 4.16 đã duyệt trong phiên này.

## 9. Giả định và điểm đã xác nhận

- Đã xác nhận bởi người dùng 28/10/2026: mỗi lần OCR vỏ thuốc là một thuốc; không tự sửa ký tự nghi ngờ; normalize/index ở backend; không cache.
- Một thuốc có thể có nhiều dòng và là thuốc phối hợp nhiều thành phần; không mặc định nhiều hàm lượng nghĩa là nhiều thuốc.
- Index dựa trên tên và hoạt chất thô; chưa mở rộng alias hoặc suy ra quan hệ thuốc–hoạt chất.
- Catalog là nguồn sự thật; index dựng mới từ dữ liệu vừa nạp cho mỗi lượt sử dụng. Cấu trúc dữ liệu/thuật toán dựng index được quyết định ở plan; không mở lại lựa chọn cache đã chốt.
- Không tự đặt SLO dung lượng/độ trễ khi chưa có số đo/yêu cầu; bắt buộc đọc đủ catalog thay vì cắt theo search limit.

## 10. Phát sinh

- SRS BR-12/UC.06 còn mô tả Admin xử lý OCR không khớp, mâu thuẫn QD-39. Loại khỏi 4.12; chủ tài liệu xử lý riêng.
- Nhánh hiện tại `feat/4.16-selection-confirmation-screen`; gate báo task 4.16 đã xong quy trình. Có con trỏ submodule thay đổi tại backend/frontend/api_contract/tests từ trước. Không sửa hoặc quy chúng cho 4.12; trước implement phải chuẩn bị nhánh và kiểm tra lại theo wf-git.
- `python` mặc định trỏ WindowsApps và không chạy được trong môi trường agent. Dùng Python runtime do app cung cấp; không sửa cài đặt máy.
- Chưa chạy test chức năng và chưa sửa code 4.12 trong giai đoạn requirement. Không coi bảng OCR trong README backend là bằng chứng implementation.
- `User_Stories.xlsx` không đọc được bằng openpyxl (`BadZipFile`); không dùng file này làm nguồn kết luận. Đã đọc backlog chuẩn và nguồn quyết định.

### Bằng chứng kiểm tra requirement

- Lệnh gate: `& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .agents/scripts/gate.py 4.12-ocr-text-normalization-catalog-index requirement` — cho phép bắt đầu requirement; output: `evidence/requirement-gate.log`.
- Lệnh scope: cùng runtime, `.agents/scripts/scope.py 4.12-ocr-text-normalization-catalog-index --stage requirement` — exit 0, không có thay đổi nào ngoài work; output: `evidence/requirement-scope.log`.
- Đây là kiểm tra gate/phạm vi, không phải kết quả test normalize/index; chưa có implementation mới để chạy.

## 11. Size

- `size`: M; một submodule chức năng, parser hàm lượng/nồng độ/phối hợp và nguồn catalog cần unit/integration test, vượt giới hạn khoảng 3 file/50 dòng của S. Cần kiểm soát đúng tên/hàm lượng trong luồng chọn thuốc.
- Không cần schema/cơ chế cập nhật cache. Không có bảng file/checklist implement ở requirement M; lập ở giai đoạn plan sau duyệt.

## Bước tiếp theo

- Đang chờ: người duyệt requirement. Không còn câu hỏi chặn; Q2 về format là tùy chọn, mặc định theo bảng 7a.
- Việc cần làm: người duyệt đọc bản yêu cầu đã chốt không cache và tự chạy `python .agents/scripts/gate.py approve 4.12-ocr-text-normalization-catalog-index requirement` trong terminal; nếu alias Python lỗi, dùng runtime tuyệt đối ghi trong evidence. Đề xuất commit artifact/evidence task trên nhánh task của superproject khi được yêu cầu để tiếp tục ở máy/tool khác.
- Giai đoạn kế tiếp sau duyệt: plan qua wf-next/wf-plan ở lượt riêng. Không tự duyệt hoặc bắt đầu plan/code trong lượt requirement.
- Cập nhật lần cuối: 28/10/2026, Codex.
