---
task: 4.14-ocr-unit-tests
title: Unit tests with real OCR output (PB31)
type: feature
stage: requirement
size: S
contract_change: no
affected: [backend]
status: approved
approved_by: Duc1445
approved_at: 2026-11-11 16:53 +0700
content_hash: sha256:c2de613be77ae8ff
---

# 4.14 · Unit tests with real OCR output (PB31)

## 1. Mục tiêu

Xây dựng bộ unit test tự động kiểm thử module chuẩn hóa chuỗi và bóc tách đặc trưng văn bản OCR (`normalize_ocr.py`) dựa trên tập dữ liệu văn bản thô thực tế trích xuất từ 49 ảnh bao bì vỉ và hộp thuốc Việt Nam (`datasets/results/pilot-002/raw`), đảm bảo thuật toán nhận diện ổn định trước các dạng nhiễu thực tế (mất dấu tiếng Việt, khoảng trắng bất thường, nhầm ký tự số O/0, I/1, số đăng ký VD/VN).

## 2. Phạm vi

### Trong phạm vi

- Kiểm thử các hàm cốt lõi của `normalize_ocr.py`: `normalize_clean`, `normalize_key`, `normalize_ocr_text`, `_parse_strength`, nhận diện hàm lượng và dòng tên thuốc.
- Sử dụng ít nhất 10 mẫu văn bản OCR thô thực tế đại diện cho cả dạng hộp (box) và dạng vỉ (blister) từ `datasets/results/pilot-002/raw`.
- Kiểm thử các ca biên có nhiễu thực tế:
  1. Nhầm ký tự số và chữ: `5o0mg`, `50Omg`, `8mg`, `l0` (chữ o/l nhầm với số 0/1).
  2. Số đăng ký thuốc: `SDK: VD-13882-11`, `SEK: VD-13882-11`, `SDK VD-1388-11` (không bị nhận diện nhầm thành hàm lượng thuốc).
  3. Dấu tiếng Việt bị lỗi/mất dấu/bỏ dấu phân rã NFD: `R THUOC Kt 0ON`, `HỘP 3 VỈ x 10 VIÊN`, `CÔNG TY CPDP TIPHARCO`.
  4. Khoảng trắng lạ hoặc xuống dòng tùy tiện của OCR scanner: `Metformin 500mg`, `Metformin.HCI 5o0mg`, `4AL FDO`.
  5. Cặp hàm lượng kép / phối hợp: `ACANDESARTAN HTZ 32-25`, `Bisoprolol 2.5`.
- Đặt file test tại: `backend/tests/unit/test_ocr_real_output.py`.

### Ngoài phạm vi

- Không thay đổi mã nguồn logic nghiệp vụ hay API contract trong backend hoặc client.
- Không huấn luyện lại mô hình ML Kit hay thay đổi engine OCR trên thiết bị di động.
- Không đánh giá tỷ lệ matching toàn bộ catalog (nhiệm vụ của Task 4.17).

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `datasets/results/pilot-002/raw/*.json` | Chứa 49 file JSON kết quả chạy ML Kit OCR thực tế từ bao bì thuốc Việt Nam, bao gồm `rawText`, `imageId`, `elapsedMs`. |
| `backend/src/drugtime/modules/catalog/application/normalize_ocr.py` | Cài đặt logic chuẩn hóa văn bản, tách dòng, phát hiện hàm lượng (`_parse_strength`, `_AMOUNT_LIKE`), xử lý phân tách dấu NFD/NFC. |
| `backend/tests/unit/test_catalog_ocr_normalization.py` | Bộ test tổng hợp giả lập (synthetic) hiện tại cho bộ chuẩn hóa OCR; cần bổ sung bộ test trên dữ liệu thực tế. |
| `PLAN_TIEN_DO_DUCNT.md` | Đặc tả mục tiêu Task 4.14 (PB31), yêu cầu kiểm thử bộ chuẩn hóa với ≥ 10 mẫu OCR thực tế có nhiễu. |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `backend` | Có | Thêm file unit test `tests/unit/test_ocr_real_output.py`. |
| `frontend` | Không | Không thay đổi code mobile app trong task này. |
| `api_contract` | Không | Không đổi schema API. |
| `tests` | Không | Đây là unit test nội bộ backend. |
| `docs` | Không | Không cập nhật tài liệu chính thức. |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: Task hoàn toàn là unit test nội bộ cho module chuẩn hóa backend, không thay đổi bất kỳ endpoint hay cấu trúc dữ liệu giao tiếp nào.
- Endpoint liên quan: Không có.

## 6. Vùng rủi ro và bất biến bị chạm

- Vùng rủi ro: Không chạm vùng rủi ro nào của dự án (không động đến dữ liệu sức khỏe, phân quyền, consent, dose log, schema hay secret).
- Bất biến: Không vi phạm bất biến nào.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | **Given** 10 mẫu raw OCR thực tế từ `datasets/results/pilot-002/raw`, **When** đưa qua `normalize_ocr_text()`, **Then** trả về đối tượng `NormalizedOcrText` có đầy đủ các dòng, không ném exception và giữ nguyên tính toàn vẹn ký tự gốc. | unit |
| AC2 | **Given** mẫu OCR có chứa chuỗi số đăng ký như `SDK: VD-13882-11`, **When** phân tích hàm lượng (`strengths`), **Then** chuỗi số đăng ký tuyệt đối không bị parse sai thành hàm lượng thuốc hợp lệ (`canonical`). | unit |
| AC3 | **Given** các mẫu OCR chứa hàm lượng chuẩn và hàm lượng có nhiễu (ví dụ `500mg`, `10 mg`, `32-25`), **When** phân tích cấu trúc hàm lượng, **Then** bộ trích xuất nhận diện đúng các hàm lượng chuẩn hợp lệ và gắn cờ hoặc loại bỏ các chuỗi nhiễu không hợp lệ. | unit |
| AC4 | **Given** các chuỗi văn bản tiếng Việt bị lỗi font/dấu từ scanner (ví dụ `R THUOC Kt 0ON`, `HỘP 3 VỈ`), **When** gọi `normalize_key()`, **Then** loại bỏ dấu tiếng Việt chuẩn xác (ASCII lowercase) để phục vụ tra cứu đánh chỉ mục mà không làm sập tiến trình. | unit |
| AC5 | **Given** toàn bộ bộ test `test_ocr_real_output.py`, **When** chạy bằng lệnh `pytest backend/tests/unit/test_ocr_real_output.py`, **Then** 100% test case pass thành công. | unit |

## 8. Câu hỏi mở

Không có.

## 9. Giả định

- Dữ liệu thô trong `datasets/results/pilot-002/raw/*.json` là dữ liệu chuẩn thực tế thu thập từ đợt chạy Pilot-002 của dự án.
- Các hàm parser của `normalize_ocr.py` được thiết kế theo nguyên tắc "conservative" (thận trọng, không tự ý sửa đổi bừa bãi khi không chắc chắn).

## 10. Phát sinh

Không có.

## 11. Size

- `size`: S
- Lý do: Task chỉ thêm 01 file unit test trong submodule `backend`, không chạm vùng rủi ro, không thay đổi API contract, không sửa đổi migration hay logic production.

## 12. File sẽ thay đổi (chỉ task S)

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| `backend` | `tests/unit/test_ocr_real_output.py` | Thêm | Bộ unit test kiểm thử bộ chuẩn hóa OCR trên dữ liệu bao bì thực tế (≥ 10 mẫu) |

## 13. Checklist (chỉ task S)

- [ ] P1 [backend] Tạo file `tests/unit/test_ocr_real_output.py` với fixture trích xuất 10+ mẫu raw text thực tế và các test case kiểm tra AC1–AC4.
- [ ] P2 [backend] Chạy `pytest backend/tests/unit/test_ocr_real_output.py` xác minh AC5 và ghi log bằng chứng vào `work/4.14-ocr-unit-tests/evidence/test-run.log`.

## Bước tiếp theo

- Đang chờ: người duyệt duyệt `01-requirement.md`
- Việc cần làm: Người dùng chạy lệnh `python .agents/scripts/gate.py approve 4.14-ocr-unit-tests requirement` để phê duyệt.
- Cập nhật lần cuối: 2026-11-11 14:30, Antigravity
