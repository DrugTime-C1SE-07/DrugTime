---
task: 6.04-ocr-scan-redesign
stage: test
status: approved
approved_by: Duc1445
approved_at: 2026-11-26 15:07 +0700
content_hash: sha256:aad584b061591005
inputs:
  01-requirement.md: sha256:645fefcac97207fa
  03-plan.md: sha256:966b0ff836e39e0a
  04-impl-notes.md: sha256:f7b8be27654869ca
---

# 6.04-ocr-scan-redesign · Test tích hợp

## 1. Môi trường

- Lệnh chuẩn bị (reset DB, khởi động service): Không áp dụng reset DB hay khởi động backend/Supabase vì task thuần Mobile UI (`contract_change: no`, `affected: [frontend]`, không có AC mức `integration` backend/DB; dùng lại hoàn toàn `POST /catalog/medications/match` và `GET /catalog/medications` hiện có). Kiểm thử chạy trên môi trường Flutter test (`flutter test`, `frontend/mobile`) và gộp bộ test case Excel qua `testcase_xlsx.py` (Python + `openpyxl`).
- Nhánh của vùng test tích hợp / tài liệu:
  - `frontend`: `feat/6.04-ocr-scan-redesign` (không chỉnh sửa thêm code sản phẩm hay test trong giai đoạn `test`)
  - `docs`: `feat/6.04-ocr-scan-redesign` (chỉ cập nhật `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` qua `testcase_xlsx.py merge`)

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Test | Kết quả |
|---|---|---|
| AC1 | `scan_medication_screen_test.dart`: `camera renders 4-side cameraScrim aligned with crop frame, guide pill below frame, no overflow at 360x640 1.3x (AC1)`; `scan beam sweeps down to bottom...`; `scan beam stays still when disableAnimations is true...`; `camera capture passes scan frame crop while gallery pick passes null crop` | pass |
| AC2 | `scan_medication_screen_test.dart`: `denied, permanentlyDenied, and camera error show elderly guidance and hide overlay without allow button (AC2)`; `permanent camera denial opens app settings...`; `camera requests permission automatically on open...` | pass |
| AC3 | `recognition_steps_test.dart` (5 tests: màu `AppColors.brand` `#01554F`, chữ `17px`, tiến trình theo `OcrStage`); `scan_medication_screen_test.dart`: `recognizing sheet shows 14px privacy banner, brand progress, no overflow at 360x640 1.3x, and cancelling resets stale _nameMissed (AC3)` | pass |
| AC4 | `ocr_single_result_card_test.dart` (6 tests: pill `'Đã nhận diện · 82% khớp'`, `score == 0`, thiếu trường, `strength_unverified`, `AppShadows.cardElevation`); `scan_medication_screen_test.dart`: `matched shows one large medicine...`, `matched and low_confidence result sheets show status pills without overflow at 360x640 1.3x (AC4, AC5)`; `ocr_models_test.dart` (score ngoài `[0, 1]`) | pass |
| AC5 | `ocr_single_result_card_test.dart` (`low confidence shows caution pill with cautionText (#92400E)...`); `scan_medication_screen_test.dart` (`low confidence shows the first medicine...`, `low confidence "not this medicine" searches the read name`, `matched and low_confidence... 360x640 1.3x`); `scanned_schedule_test.dart` (chặn lưu thuốc thiếu hàm lượng theo `QD-39`) | pass |
| AC6 | `scan_medication_screen_test.dart`: `no_match failure uses AppColors.brand header, 160x160 illus, 40x40 tips badges 17px, no Retry, no overflow at 360x640 1.3x (AC6)`; `no match asks to retake...`; `no match without a name...`; `no text twice in a row...` | pass |
| AC7 | `scan_medication_screen_test.dart`: `blurred and invalidImage failures offer manual search, gallery, retake without Retry (AC7)`; `a blurred photo says why and offers a retake`; `gallery can retry after an image processing error` | pass |
| AC8 | `ocr_controller_test.dart` (`canRetry is true for retryable failures while lease is valid`, `canRetry is false when expired or on non-retryable failure`); `scan_medication_screen_test.dart`: `network and recognition failures show Retry that re-runs OcrController.start() without retaking (AC8)`; `expiring encrypted image on failure screen hides Retry...` | pass |
| AC9 | `scan_medication_screen_test.dart`: `unauthorized (401) and cleanup failure release/lock UI fail-closed without Retry/Manual/Gallery/Retake (AC9)`; `expiring encrypted image on failure screen...`; `revoking consent during recognition clears the pending result`; `ocr_controller_test.dart` (hết hạn 24h, cancel, session switch, cleanup retry) | pass |
| AC10 | Kiểm thử thủ công trên thiết bị Android thật (`TC-OCRUI-21`, `TC-OCRUI-22` trong `testcases.xlsx`) | pending (manual — cần thiết bị Android thật và vỉ thuốc vật lý) |

## 3. Kịch bản chất lượng đã phủ

Task chỉ sửa giao diện Mobile (`frontend/mobile/lib/features/medication_capture/`) và không chạm endpoint dữ liệu sức khỏe, phân quyền người thân, đồng bộ liều hay engine tương tác thuốc. Các kịch bản chất lượng bảo mật/an toàn dùng thuốc áp dụng cho vùng OCR (`PB31`, `QD-39`, `QD-35`):

| Kịch bản | Test | Kết quả |
|---|---|---|
| Ảnh chỉ xử lý OCR trên thiết bị, không tự chọn/tự lưu thuốc (`QD-39` dòng 68–69) | `ocr_single_result_card_test.dart`, `scan_medication_screen_test.dart` (`matched`, `low_confidence`, `no_match`), `scanned_schedule_test.dart` | pass |
| Xóa ngay ảnh tạm mã hóa & RAM khi xác nhận, hủy, hết hạn 24h, lỗi 401 hoặc thu hồi consent (`QD-39` dòng 70, `QD-35`) | `ocr_controller_test.dart`, `scan_medication_screen_test.dart` (`expiring encrypted image`, `unauthorized (401) and cleanup failure`, `revoking consent`) | pass |
| Khả dụng cho người lớn tuổi (độ tương phản `#01554F` / `#92400E`, cỡ chữ `17px`/`14px`, không overflow trên `360×640` với `textScaler = 1.3`) | `recognition_steps_test.dart`, `ocr_single_result_card_test.dart`, `scan_medication_screen_test.dart` (`AC1`, `AC3`, `AC4`, `AC5`, `AC6`) | pass |
| 5 kịch bản tích hợp backend trong `AGENTS.md` (truy cập chéo patient 403, rút consent API, trùng `client_uuid`, worker chạy đua `bo_lo`, golden scenarios tương tác) | Không áp dụng (không chạm `backend`, `api_contract` hay DB) | N/A |

## 4. Toàn bộ bộ test tích hợp

- Lệnh: `cd frontend/mobile && flutter test test/features/medication_capture/ test/features/medication/scanned_schedule_test.dart`
- Kết quả: **117 pass / 0 fail / 1 skip / 54 giây** (exit 0).
- Log: `evidence/test-integration.log`
- `scope.py --stage test`: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` là **`[OK]`**; script báo 114 file `[NGOÀI]` gồm đúng 10 file đã làm ở giai đoạn `implement` trong `frontend` (chưa commit theo quy trình chờ duyệt cuối) và 104 file tồn đọng sẵn trên workspace từ trước task (xem Mục 7) — log: `evidence/test-scope.log`.

## 5. Bộ test case Excel

- Spec: `work/6.04-ocr-scan-redesign/testcases.json` · File task: `work/6.04-ocr-scan-redesign/testcases.xlsx` · File tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (sheet `Quét vỉ & kết quả OCR`)
- Log: `evidence/testcase-xlsx.log` (`validate=0`, `build=0`, `merge=0`, không có cảnh báo xung đột sheet cũ)

| Chức năng (mã) | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| Hoàn thiện màn hình quét vỉ thuốc & kết quả OCR (`OCRUI`) | 22 | 20 | 0 | 2 |

- Test case `Pending` cần người chạy:
  - `TC-OCRUI-21` (`AC10` — manual): Quét vỉ thuốc thật trên điện thoại Android trong điều kiện ánh sáng thường, kiểm tra lớp phủ scrim 4 phía, ảnh cắt đúng khung, sheet nhận diện, pill kết quả và chuyển sang bước Lịch uống.
  - `TC-OCRUI-22` (`AC10` — manual): Quét vỉ thuốc trong ánh sáng yếu/loá với cỡ chữ hệ thống ~130%, kiểm tra độ tương phản màn lỗi S07-O3e (`#01554F`), thẻ gợi ý và nút `Thử lại` khi tắt/bật lại mạng trên thiết bị Android thật.
- Bug đã ghi vào Bug Report: Không có (`Fail = 0`).

## 5b. Lỗi sản phẩm tìm thấy

Không có. Toàn bộ 117 test tự động thuộc luồng OCR và chuyển bước lịch uống đều pass, không có lỗi mới phát hiện trong giai đoạn `test`.

## 6. Test không ổn định hoặc bị skip

- **1 test bị skip (sẵn có, không liên quan task)**: `frontend/mobile/test/features/medication_capture/ocr_web_id_test.dart` (`web accepts safe integer and rejects unsafe or nonpositive ID`, dòng 31: `skip: !kIsWeb`) — test chỉ chạy trên nền tảng Web để kiểm tra giới hạn số nguyên an toàn của JavaScript (`2^53 - 1`), nên tự động skip khi chạy `flutter test` trên VM/Windows.
- **Test không ổn định**: Không có (toàn bộ 117 test chạy ổn định trong cả giai đoạn `implement` và `test`, 0 flaky).

## 7. Phát sinh

- `scope.py --stage test` báo 114 file `[NGOÀI]`:
  - 10 file trong `frontend` thuộc bảng phạm vi giai đoạn `implement` của chính task `6.04-ocr-scan-redesign` (chưa commit theo quy tắc chờ người dùng yêu cầu).
  - 104 file tồn đọng sẵn trên workspace trước khi bắt đầu task (`100` file trong `DrugTime_Pilot_4.01/`, `1` file `execute_ducnt_plan/work/5.10-disclaimer-injection/01-requirement.md`, `3` file ở `backend/` trên nhánh `feat/5.10-disclaimer-injection`).
  - Trong phạm vi giai đoạn `test`, chỉ sửa duy nhất `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (trên nhánh mới `docs` `feat/6.04-ocr-scan-redesign`), được `scope.py` công nhận `[OK]`.

## Bước tiếp theo

- Đang chờ: người dùng duyệt giai đoạn `test` (phiên reviewer `3e2c9d0d-ffc3-4c37-b436-ba32311131a1` đã kiểm chứng độc lập vòng 2 kết luận **ĐẠT**).
- Việc cần làm: Người dùng chạy `python .agents/scripts/gate.py approve 6.04-ocr-scan-redesign test` (và có thể chạy bổ sung 2 test case thủ công `TC-OCRUI-21`, `TC-OCRUI-22` trên máy Android thật), sau đó tiếp tục giai đoạn 6 (`wf-review`).
- Cập nhật lần cuối: 2026-11-26 15:06, Antigravity
