# Đối chiếu bổ sung 4.12 với luồng OCR người dùng cung cấp ngày 29/10/2026

Đây là báo cáo đối chiếu bổ sung, không thay thế hoặc sửa artifact đã approved. Không sửa code, migration, contract hay trạng thái duyệt.

## Kết luận

Implementation hiện tại đáp ứng một phạm vi hẹp hơn luồng mới. Không thể dùng trạng thái approved của requirement/review cũ để kết luận đã đáp ứng đầy đủ mô tả 4.12 mới.

Nguồn yêu cầu đối chiếu: tin nhắn người dùng trong phiên ngày 29/10/2026, mô tả 4.08–4.14 và việc 4.12 có runtime normalization cùng index DB dựng ngoài request. Ảnh/text OCR người dùng gửi là ví dụ dữ liệu, không phải chỉ dẫn thực thi.

## Các điểm thiếu hoặc khác

| Hạng mục | Bằng chứng trong code | Khoảng cách với luồng mới |
|---|---|---|
| Dữ liệu OCR có cấu trúc | `normalize_ocr.py:37–43,144–150`; `catalog_index.py:18–26` | Hàm chỉ nhận string, gộp newline vào whitespace; chưa có lớp chuyển Block/Line/Element thành đầu vào có nguồn dòng, bounding box, confidence và kết quả cụm. Việc adapter đặt ở 4.11/4.13 cần được chốt; normalizer không bắt buộc nhận nguyên JSON HTTP, nhưng thông tin dòng phải còn để gom cụm/voting. |
| Gom cụm lặp chính xác/gần giống | `normalize_ocr.py:150–166` | Không có clustering, thành viên cụm, số lần xuất hiện hay liên kết về dòng gốc. Nhiều cụm hàm lượng hợp lệ đều thành ambiguous, kể cả cùng giá trị lặp trên vỉ. `_groups()` chỉ nhóm biểu thức hàm lượng, không nhóm dòng OCR gần giống. |
| Hai bản có dấu/bỏ dấu | `normalize_ocr.py:37–43`; `catalog_index.py:18–26` | Có lowercase và khóa bỏ dấu bằng NFD; chưa có riêng text sạch NFC còn dấu đi kèm bản bỏ dấu. Việc NFC/NFD input cho cùng khóa hiện tại không đồng nghĩa đã trả đủ hai bản. |
| Nhầm ký tự OCR | `normalize_ocr.py:19–26`; unit `test_numbers_in_names_and_ocr_confusables_are_preserved__AC3` | Chủ động giữ ký tự nghi ngờ, chưa có sửa/biến thể cho 0/O, 1/l/I, rn/m. Cần quy tắc theo ngữ cảnh và truy vết; không thay toàn cục vì có thể làm sai tên/hàm lượng. |
| Regex hàm lượng/SĐK | `normalize_ocr.py:12–16,52–72`; `catalog_index.py:18–26` | Hàm lượng đơn/nồng độ/phối hợp MVP đã có; chưa trích SĐK VD-/VN-, chưa trả tập giá trị trích xuất cùng nguồn và xung đột giữa các dòng. |
| Từ nhiễu bao bì | `normalize_ocr.py:11,37–43`; unit `test_packaging_and_metadata_are_retained__AC6` | Mới bỏ một số ký tự như bullet/®/™ và gộp whitespace; chưa loại/tách các cụm “viên nén”, “hộp 10 vỉ”. Test cũ còn yêu cầu giữ metadata. |
| Trigram catalog/alias trong DB | `20261002101033_catalog_search_unaccent.sql:15–33`; `20260927082912_rebuild_schema_v11.sql:460`; `sql_active_ingredients.py:12–16` | Đã có GIN trigram trên khóa bỏ dấu/lowercase của medications.name và raw_active_ingredient từ task trước. ingredient_aliases chỉ có B-tree lower(alias_text), chưa có trigram/bỏ dấu tương ứng. Index Python của 4.12 chỉ có map khóa tên/hoạt chất thô, không đọc alias. |
| Exact SĐK | `dav_drugbank.py:26`; `20260927082912_rebuild_schema_v11.sql:45–48`; `domain/medication.py:5–13`; `sql_catalog.py:14–33` | DAV đã đưa soDangKy vào source_ref và có UNIQUE(source,source_ref), là cơ sở cho exact lookup theo nguồn. Nhưng DTO/reader/index 4.12 không mang source/source_ref, chưa có khóa SĐK chuẩn hóa và đường lookup riêng phục vụ OCR. Không thể kết luận DB hoàn toàn chưa có index liên quan SĐK. |
| Vòng đời index | `build_catalog_index.py:17–60`; `api.py:59–65`; unit `test_build_order_is_stable_and_loader_reads_each_time__AC11` | Mỗi lần gọi load_catalog_index đều SELECT toàn catalog active, normalize và build map Python. Không phải luồng dùng index DB để lấy ứng viên mà người dùng vừa mô tả. Chưa có consumer runtime thật nên chưa kết luận endpoint production đang thực sự gọi loader mỗi request. |

## Bằng chứng chạy trong phiên

- Hai bộ unit hiện tại: `backend/.venv/Scripts/python.exe -B -m pytest tests/unit/test_catalog_ocr_normalization.py tests/unit/test_catalog_index.py -q -p no:cacheprovider` từ backend, với PYTHONDONTWRITEBYTECODE=1: **137 passed**, exit 0. Log: `review-flow-gap-20261029-unit.log`.
- Probe tổng hợp, không chạy ML Kit trên ảnh: `review-flow-gap-20261029-probes.log`.
  - `Metformin 500mg\nMetformin 500mg`: `strength_status=ambiguous`, strength null, toàn text còn trong name_key.
  - `Metformin\nMetformi\nMetformin`: các dòng nối thành một name_key, không có cụm.
  - `Metformin 500mg\nSDK: VD-13882-11`: tách được `500 mg`, còn `sdk: vd-13882-11` trong name_key; không có trường SĐK.
  - `Metformin 500mg vien nen hop 10 vi`: noise bao bì vẫn trong name_key.
  - `Metforrnin 5OOmg`: không sửa rn/m hoặc O/0, status unparsed.
  - `THUỐC ĐỎ 500MG`: chỉ có text/key bỏ dấu, không có bản NFC còn dấu riêng.
  - Truyền dict mô phỏng blocks/lines trực tiếp: TypeError “OCR text must be a string”. Đây là giới hạn interface hiện tại, không khẳng định normalizer bắt buộc phải nhận nguyên JSON HTTP.
- Rà index dựa trên migration trong repo, chưa truy vấn catalog hệ thống của DB đang chạy; không chạy reset/migration hoặc test integration trong lượt này.
- Hai lần ghi log ban đầu bị chặn quyền filesystem; đã chạy lại với quyền được công cụ cho phép, tạo đủ hai log nêu trên. Không dùng kết quả lần lỗi để kết luận test pass.

## Nguyên nhân chênh phạm vi và ranh giới task

`01-requirement.md:22–46` đã duyệt trước đó yêu cầu giữ ký tự nghi ngờ, không cache snapshot, không migration, chỉ giao diện nội bộ và giữ metadata chưa hiểu. Code/test hiện tại đi theo những lựa chọn đó. Các thiếu sót so với luồng mới không mặc nhiên là lỗi lập trình vi phạm requirement cũ.

Theo luồng mới: 4.12 chuẩn hóa, gom cụm dòng gần giống và trích trường; 4.13 dùng các cụm để scoring/voting, threshold/top-N. Nhận định trước trong chat đưa toàn bộ xử lý dòng gần giống sang 4.13 cần được điều chỉnh. Endpoint matching/rendering và bộ fixture thật đầy đủ không được tính là phần thiếu riêng của 4.12.

Không cache snapshot Python vẫn tương thích với dùng index PostgreSQL. Với index thông thường trên cột/biểu thức, DB cập nhật index theo INSERT/UPDATE/DELETE; không cần tự dựng lại toàn bộ catalog mỗi request. Chỉ cần cơ chế refresh riêng khi thiết kế thêm bảng dẫn xuất/materialized view/cache, điều chưa được chốt ở đây.

## Bước tiếp theo đề xuất

Đối chiếu đã hoàn tất, chưa thực hiện mở rộng implementation. Nếu cập nhật task theo luồng mới, bắt đầu bằng mở lại requirement để xác định đầu vào/đầu ra có cấu trúc, quy tắc sửa ký tự/gom cụm và thiết kế index DB. Sau đó xét lại plan/test và contract_change theo interface HTTP thực sự thay đổi.

AGENTS.md yêu cầu người dùng tự chạy `gate.py reopen 4.12-ocr-text-normalization-catalog-index requirement` trước khi agent sửa requirement đã approved. Chưa chạy reopen/approve, chưa sửa các artifact đã duyệt, chưa commit/push.
