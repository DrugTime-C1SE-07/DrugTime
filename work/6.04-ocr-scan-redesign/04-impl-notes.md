---
task: 6.04-ocr-scan-redesign
stage: implement
owner: Duc1445
started_at: 2026-11-26 14:11
status: approved
approved_by: Duc1445
approved_at: 2026-11-26 14:52 +0700
content_hash: sha256:f7b8be27654869ca
inputs:
  01-requirement.md: sha256:645fefcac97207fa
  03-plan.md: sha256:966b0ff836e39e0a
---

# 6.04-ocr-scan-redesign · Implement

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `flutter test test/features/medication_capture/ocr_controller_test.dart` → 8 pass, 0 fail | `evidence/implement-P1.log` |
| P2 | xong | `flutter test test/features/medication_capture/scan_medication_screen_test.dart` → 32 pass, 0 fail (scrim + corners + beam + pill đúng `computeScanFrameRect`, 0 overflow ở `360×640 1.3x`) | `evidence/implement-P2.log` |
| P3 | xong | `flutter test test/features/medication_capture/recognition_steps_test.dart` → 5 pass, 0 fail (`AppColors.brand` `#01554F`, `17px`) | `evidence/implement-P3.log` |
| P4 | xong | `flutter test test/features/medication_capture/ocr_single_result_card_test.dart` → 6 pass, 0 fail (pill `matched`/`low_confidence` `#92400E`, `score == 0`, `AppShadows.cardElevation`) | `evidence/implement-P4.log` |
| P5 | xong | `flutter test test/features/medication_capture/scan_medication_screen_test.dart` → 32 pass, 0 fail (`ScanFailureBody` & `ScanFailureActions`) | `evidence/implement-P5.log` |
| P6 | xong | `flutter test test/features/medication_capture/scan_medication_screen_test.dart` → 32 pass, 0 fail; `flutter analyze lib/features/medication_capture test/features/medication_capture` → 0 issues | `evidence/implement-P6.log`, `evidence/implement-analyze.log` |
| P7 | xong | `flutter test test/features/medication_capture/ocr_controller_test.dart` → 8 pass, 0 fail (`canRetry` cho `network`/`server`/`unavailable`/`recognition` vs hết hạn 24h/`closed`/`noText`) | `evidence/implement-P7.log` |
| P8 | xong | `flutter test test/features/medication_capture/ocr_single_result_card_test.dart` → 6 pass, 0 fail | `evidence/implement-P8.log` |
| P9 | xong | `flutter test test/features/medication_capture/recognition_steps_test.dart` → 5 pass, 0 fail | `evidence/implement-P9.log` |
| P10 | xong | `flutter test test/features/medication_capture/scan_medication_screen_test.dart` → 32 pass, 0 fail; `flutter test test/features/medication_capture/` → 115 pass, 0 fail, 1 skip; `flutter test test/features/medication/scanned_schedule_test.dart` → 2 pass, 0 fail; `flutter analyze` → 0 issues | `evidence/implement-P10.log`, `evidence/implement-medication-capture.log`, `evidence/implement-scanned-schedule.log`, `evidence/implement-analyze.log` |

### Đối chiếu quyết định nghiệp vụ (`QD-39`) & AC

- **`QD-39` (dòng 68, ✅ — kiểm tra tên/hàm lượng/đơn vị/liều/giờ trước khi tạo lịch)**: Đã thực hiện ở `P4`, `P6`, `P8`, `P10`; kiểm chứng bằng `ocr_single_result_card_test.dart` (6 pass), `scan_medication_screen_test.dart` (`matched`, `low_confidence`, `strength_unverified`) và `scanned_schedule_test.dart` (2 pass, chặn lưu thuốc thiếu hàm lượng).
- **`QD-39` (dòng 69, ✅ — chỉ tạo lịch thuốc trong danh mục, không gán thuốc gần giống)**: Đã thực hiện ở `P4`, `P5`, `P6`, `P10`; `no_match` / `noText` không hiển thị thuốc nào và không tự mở tìm thủ công, `low_confidence` bắt buộc người dùng đối chiếu và xác nhận thủ công.
- **`QD-39` (dòng 70, ✅ — ảnh và text OCR lưu mã hóa tối đa 24h, xóa ngay khi xác nhận/hủy)**: Đã thực hiện ở `P1`, `P5`, `P6`, `P7`, `P10`; `OcrController.canRetry` kiểm tra hạn 24h + trạng thái `isReleased`, `_onOcrChanged()` xóa RAM (`_clearImage`) khi `expiredImage`/`cleanup`, `unauthorized` (401) gọi ngay `_closeOcr()` + `_clearImage()` và khóa UI fail-closed.

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| frontend | `feat/6.04-ocr-scan-redesign` | `mobile/lib/features/medication_capture/presentation/state/ocr_controller.dart` (sửa) |
| frontend | `feat/6.04-ocr-scan-redesign` | `mobile/lib/features/medication_capture/presentation/widgets/scan_camera_overlay.dart` (thêm) |
| frontend | `feat/6.04-ocr-scan-redesign` | `mobile/lib/features/medication_capture/presentation/widgets/scan_failure_view.dart` (thêm) |
| frontend | `feat/6.04-ocr-scan-redesign` | `mobile/lib/features/medication_capture/presentation/widgets/recognition_steps.dart` (sửa) |
| frontend | `feat/6.04-ocr-scan-redesign` | `mobile/lib/features/medication_capture/presentation/widgets/ocr_single_result_card.dart` (sửa) |
| frontend | `feat/6.04-ocr-scan-redesign` | `mobile/lib/features/medication_capture/presentation/screens/scan_medication_screen.dart` (sửa) |
| frontend | `feat/6.04-ocr-scan-redesign` | `mobile/test/features/medication_capture/ocr_controller_test.dart` (sửa) |
| frontend | `feat/6.04-ocr-scan-redesign` | `mobile/test/features/medication_capture/ocr_single_result_card_test.dart` (sửa) |
| frontend | `feat/6.04-ocr-scan-redesign` | `mobile/test/features/medication_capture/recognition_steps_test.dart` (sửa) |
| frontend | `feat/6.04-ocr-scan-redesign` | `mobile/test/features/medication_capture/scan_medication_screen_test.dart` (sửa) |

Kết quả `python .agents/scripts/scope.py 6.04-ocr-scan-redesign --stage implement`: **0 file ngoài phạm vi trong `frontend`** (khớp chính xác 10/10 file trong `03-plan.md`); tổng báo 104 file `[NGOÀI]` đều là file tồn đọng sẵn trên workspace từ trước khi bắt đầu task (xem Mục 6) — log: `evidence/implement-scope.log`.

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| frontend | `flutter analyze lib/features/medication_capture test/features/medication_capture` | 0 issues (exit 0) | `evidence/implement-analyze.log` |
| frontend | `flutter test test/features/medication_capture/` | 115 pass / 0 fail / 1 skip (exit 0) | `evidence/implement-medication-capture.log` |
| frontend | `flutter test test/features/medication/scanned_schedule_test.dart` | 2 pass / 0 fail / 0 skip (exit 0) | `evidence/implement-scanned-schedule.log` |
| frontend | `flutter test` (toàn bộ mobile) | 1787 pass / 15 fail / 2 skip (15 ca fail thuộc các module khác sẵn có trên `frontend/main`, 0 ca thuộc `medication_capture`, xem Mục 6) | `evidence/implement-final-frontend.log` |

## 3b. Bộ test case Excel (chỉ task size S)

Làm ở giai đoạn test (task size M).

## 4. Migration

Không có.

## 5. Ghi chú cho người review

- **Thay đổi trong phạm vi 10/10 file đã duyệt** trên nhánh `frontend` `feat/6.04-ocr-scan-redesign` (tạo từ `main` `442cb4e`).
- **Tối ưu thêm sau khi chạy test & analyzer trong chính các file của plan**:
  1. `_resultSheet` áp dụng `BoxConstraints(maxHeight: maxHeight)` cho cả `_Screen.recognizing` lẫn `_Screen.result`, đồng thời thêm `maxLines: 1, overflow: TextOverflow.ellipsis` cho `Key('scan-step-label')` để giữ `frame.top` ổn định và `frame.bottom < sheet.top` trên cả 2 trạng thái.
  2. `_cameraActions()` bọc 2 cột `Thư viện` và `Nhập tay` bằng `Expanded` để loại bỏ lỗi overflow ngang 55px trên màn hình nhỏ `360×640` với `TextScaler.linear(1.3)`.
  3. Loại bỏ trường `_nameMissed` đã không còn sử dụng trong `scan_medication_screen.dart` (vì `ScanFailureActions` đã hiển thị `Tìm thuốc thủ công` thống nhất trên mọi lỗi không bị khóa fail-closed, đồng thời loại bỏ hoàn toàn nguy cơ dính trạng thái `_nameMissed` cũ và đạt 0 warning `flutter analyze`).
- **Chưa commit / chưa push** theo đúng quy trình.

## 6. Phát sinh

- **104 file `[NGOÀI]` trong `scope.py --stage implement`**: hoàn toàn là file tồn đọng sẵn trên workspace trước khi bắt đầu task 6.04 (`100` file untracked trong `DrugTime_Pilot_4.01/`, `1` file untracked `execute_ducnt_plan/work/5.10-disclaimer-injection/01-requirement.md`, và `3` file modified/untracked ở `backend/` trên nhánh `feat/5.10-disclaimer-injection`). Trong submodule `frontend`, 10/10 file thay đổi khớp hoàn toàn với `03-plan.md`.
- **15 ca test fail sẵn có trong `flutter test` toàn bộ `frontend/mobile`** (không liên quan tới 10 file trong `medication_capture` và không chạm các module này):
  - `test/app/adherence_demo_bootstrap_test.dart` (1 ca)
  - `test/features/drug_food_warning/food_warning_flow_test.dart` (2 ca)
  - `test/features/interaction_check/interaction_flow_test.dart` (5 ca)
  - `test/features/family_link/patient_switcher_home_entry_test.dart` (2 ca)
  - `test/features/medication/medication_screens_test.dart` (1 ca)
  - `test/shared/widgets/mascot/mascot_artwork_test.dart` (2 ca)
  - `test/features/profile/profile_layout_test.dart` (2 ca)

## Bước tiếp theo

- Đang chờ: người dùng duyệt giai đoạn `implement` (phiên reviewer `3e2c9d0d-ffc3-4c37-b436-ba32311131a1` đã review độc lập code/test/Figma kết luận **ĐẠT**, kèm 3 lưu ý Low không chặn có thể cân nhắc bổ sung ở giai đoạn `test`: kiểm `scrimPainter.cutout.size == cornersRect.size`, kiểm tap `'Đóng'` ở ca 401, và dùng `scorePercent > 0`).
- Việc cần làm: Người dùng chạy `python .agents/scripts/gate.py approve 6.04-ocr-scan-redesign implement`, sau đó tiếp tục giai đoạn 5 (`wf-test` + `wf-testcase`).
- Cập nhật lần cuối: 2026-11-26 14:44, Antigravity
