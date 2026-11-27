---
task: 6.04-ocr-scan-redesign
stage: plan
status: approved
approved_by: Duc1445
approved_at: 2026-11-26 14:10 +0700
content_hash: sha256:966b0ff836e39e0a
inputs:
  01-requirement.md: sha256:645fefcac97207fa
---

# 6.04-ocr-scan-redesign · Plan

## 1. Giải pháp

### Kiến trúc & luồng dữ liệu

Giữ nguyên toàn bộ luồng dữ liệu on-device OCR và hợp đồng API (`CaptureController` → `EncryptedCaptureStore` → `OcrController` → `MlKitOcrReader` → `POST /catalog/medications/match` → `AddMedicationScreen` / `showDrugCatalogSheet`), không thêm dependency ngoài và không chạm `backend` hay `api_contract`. Thực hiện nâng cấp tập trung ở tầng trình bày (`presentation/`) và bổ sung 1 getter chỉ đọc ở `OcrController`:

1. **Một nguồn sự thật duy nhất cho khung quét và lớp phủ scrim (`scan_camera_overlay.dart`)**:
   - Tạo hàm thuần `computeScanFrameRect(Size viewport)` tính `Rect` của khung cắt với lề ngang `36dp`, lề trên tối thiểu `12dp`, và chừa sẵn vùng đệm đáy `64dp` cho `ScanGuidePill` (`frameH = min(220, max(0, vh - 12 - 64))`, căn giữa trong phần `vh - 64` và đảm bảo `top >= 12`) cùng `toCaptureCropRect(Rect frame, Size viewport)` chuyển sang `CaptureCropRect`.
   - Cả 4 thành phần — **lớp phủ tối 4 phía** (`CustomPainter` vẽ `PathFillType.evenOdd` với `AppColors.cameraScrim`), **4 góc khung 28px** (`AppColors.cameraAccent`), **tia quét lặp hữu hạn** (`ScanBeam`, co theo đúng `frameRect.height`), và **`CaptureCropRect`** gửi cho `camera.takePhoto(crop: ...)` — dùng chung cùng một `Rect` này.
   - **Pill hướng dẫn (`ScanGuidePill`)**: luôn đặt ngay dưới `frameRect.bottom` (trong vùng đệm `64dp` đã chừa sẵn, khoảng cách `12–16dp`), bảo đảm không bao giờ đè lên mép dưới khung cắt hay tràn biên kể cả trên màn hình thấp `360×640` với `textScaler = 1.3`.
2. **Phân tách token nền tối vs nền sáng & bỏ chiều cao cứng ở header (`scan_medication_screen.dart`)**:
   - Bỏ `SizedBox(height: 112)` cố định ở header; dùng `Column(mainAxisSize: MainAxisSize.min)` với nút đóng `×` dạng tròn `48×48` (`AppColors.brandTint` / `AppColors.brand`) cân đối với `SizedBox(width: 48)` bên trái và `Expanded` cho tiêu đề để không overflow ở `360×640` + `textScaler = 1.3`.
   - Áp dụng nghiêm ngặt 2 bộ token từ `app_theme.dart`: nền tối (`cameraCanvas`, `cameraScrim`, `cameraSurface`, `cameraControl`, `cameraAccent`, `onCamera`, `cameraMuted`, `cameraOutline`) cho `camera`/`recognizing`/`result`, và nền sáng (`canvas`, `surface`, `surfaceMuted`, `brand`, `brandTint`, `ink`, `inkMuted`, `border`, `safe*`, `caution*`) cho `failure` và nội dung bottom sheet.
   - **Điều kiện hiển thị thẻ hướng dẫn quyền/lỗi camera vs `ScanCameraOverlay`**: định nghĩa `showCameraIssue = camera != null && (camera.permissionStatus == CapturePermission.denied || camera.permissionStatus == CapturePermission.permanentlyDenied || camera.error != null)`. Chỉ khi `showCameraIssue == true` mới ẩn `ScanCameraOverlay` và hiển thị thẻ hướng dẫn nền tối (`AppColors.cameraSurface` + viền `AppColors.cameraOutline`, icon camera-off, gợi ý dùng `Thư viện` hoặc `Nhập tay`, và duy nhất 1 nút `Mở cài đặt` khi `permanentlyDenied`, không thêm `'Cho phép camera'`). Khi `showCameraIssue == false` (bao gồm trạng thái khởi tạo ban đầu trước khi `camera.start()` hoàn tất và khi camera sẵn sàng), giữ `ScanCameraOverlay` hiển thị để không làm vỡ 2 test `scan-beam` hiện có và không chồng đè UI.
3. **Chuẩn hóa sheet đang nhận diện (`S07-O2`) & sửa rò trạng thái hủy**:
   - `recognition_steps.dart`: xóa các hằng màu cục bộ (`_brand = 0xFF00534D`...), dùng `AppColors.brand` (`#01554F`), `AppColors.brandTint`, `AppColors.border`, `AppColors.ink`, `AppColors.inkMuted`; thống nhất cỡ chữ `17px` qua `AppTextStyles.body.copyWith(fontSize: 17, ...)` với bước active dùng `AppColors.brand` + `FontWeight.w700`.
   - `scan_medication_screen.dart`: nâng banner `'Ảnh chỉ xử lý trên máy, không gửi đi'` lên `14px Medium` (`AppColors.surfaceMuted`, viền `AppColors.border`, icon `AppColors.brand`); trong `_failDuringRecognition()` đặt lại `_nameMissed = false` để không dính trạng thái từ lần quét trước.
4. **Chuẩn hóa thẻ kết quả `S07-O2r` (`ocr_single_result_card.dart`)**:
   - **Thay thế** (loại bỏ) badge `% khớp` góc phải tên thuốc hiện tại (`ocr_single_result_card.dart:53-68`) bằng `Key('ocr-status-pill')` đặt phía trên tên thuốc (tránh lặp `% khớp` 2 lần):
     - `matched` (`!checkReminder`): nền `AppColors.safeBg`, icon check `AppColors.safe`, chữ `AppColors.safe` Bold 14px `'Đã nhận diện · XX% khớp'` (hoặc `'Đã nhận diện'` khi `score <= 0`).
     - `low_confidence` (`checkReminder`): nền `AppColors.cautionBg`, icon cảnh báo `AppColors.caution`, chữ `AppColors.cautionText` (`#92400E`, đạt tương phản ≥ 4.5:1) Bold 14px `'Cần đối chiếu · XX% khớp'` (hoặc `'Cần đối chiếu'` khi `score <= 0`).
   - Bổ sung `AppShadows.cardElevation` cho thẻ, giữ nguyên 3 dòng `OcrInfoRow`, banner cảnh báo (`low_confidence`/`strength_unverified`) và `OcrResultActions` ghim đáy.
5. **Tách màn lỗi `S07-O3e` (`scan_failure_view.dart`), luồng `Thử lại` reactive & dọn ảnh fail-closed (`ocr_controller.dart`, `scan_medication_screen.dart`)**:
   - Thêm getter `bool get canRetry` trên `OcrController`: chỉ `true` khi `!_closed && !_disposed && !image.isReleased && _clock().isBefore(image.expiresAt) && (failure?.canRetry ?? false)`.
   - Quản lý vòng đời listener `_onOcrChanged` an toàn trên `_ScanMedicationScreenState`:
     - Gắn listener khi tạo `_ocr` và **gỡ listener `ocr.removeListener(_onOcrChanged)` TRƯỚC khi gọi `await ocr.close()`** trong `_closeOcr()` (và trong `dispose()`).
     - Trong `_onOcrChanged()`, chỉ xử lý khi `mounted && _screen == _Screen.failure && identical(_ocr, ocr) && ocr.stage == OcrStage.failure`:
       - Nếu `ocr.failure?.kind == OcrFailureKind.expiredImage`: gọi ngay `_clearImage()`, cập nhật `_failureTitle = 'Ảnh đã hết hạn'`, `_failure = ocr.failure!.message` (ẩn nút `Thử lại`, vẫn cho `Chụp lại`/`Chọn ảnh khác`/`Tìm thuốc thủ công`).
       - Nếu `ocr.failure?.kind == OcrFailureKind.cleanup`: gọi ngay `_clearImage()`, đặt `_lockedFailure = true`, `_cleanupPending = true`, cập nhật `_failureTitle = 'Chưa dọn được ảnh tạm'`, `_failure = ocr.failure!.message`.
   - Tách hàm dùng chung `_applyOcrOutcome(int generation)` cho cả `_capture()` và `_retryOcr()`:
     - Khi `failure?.kind == OcrFailureKind.unauthorized`: đặt ngay `_lockedFailure = true`, `_nameMissed = false`, gọi `await _closeOcr()` + `_clearImage()` để giải phóng ngay ảnh tạm mã hóa và RAM (nếu `_closeOcr()` trả `false` thì đặt `_cleanupPending = true` và báo lỗi dọn ảnh).
     - Khi `failure?.kind == OcrFailureKind.cleanup`: đặt `_lockedFailure = true`, `_cleanupPending = true`, gọi `_clearImage()`.
     - Khi người dùng bấm `Thử lại` (`_retryOcr()`): nếu `_busy || _invalidated || _lockedFailure` thì bỏ qua; nếu `ocr == null || !ocr.canRetry` thì gọi `_clearImage()`, cập nhật `_failureTitle = 'Ảnh đã hết hạn'`, `_failure = 'Ảnh không còn khả dụng. Hãy chụp lại.'` (không return im lặng); ngược lại chuyển sang `_Screen.recognizing` và gọi `ocr.start()`.
   - Tách `ScanFailureBody` (vòng minh họa `160×160` `AppColors.cautionBg`, tiêu đề `20px Bold`, mô tả `17px Regular`, thẻ gợi ý viền `AppColors.border` + `AppShadows.cardElevation` với 2 huy hiệu icon `40×40` `AppSizes.iconTile` và chữ `17px Medium`) và `ScanFailureActions` (thanh đáy nền `AppColors.surface` có viền trên `AppColors.border`):
     - Khi `isLockedFailure` (`_invalidated || _lockedFailure || _cleanupPending`): ẩn hoàn toàn `Thử lại`, `Tìm thuốc thủ công`, `Chọn ảnh khác` và `Chụp lại`; chỉ hiển thị duy nhất nút thoát an toàn gọi `_exit()` (nhãn `'Thử dọn lại'` khi `_cleanupPending`, hoặc `'Đóng'` khi đã dọn sạch như 401 `unauthorized`, không mở lại camera).
     - Khi `!isLockedFailure`: hiển thị `Thử lại` (chỉ khi `_ocr?.canRetry ?? false`), `Tìm thuốc thủ công`, `Chọn ảnh khác`, `Chụp lại`.

### Phương án đã cân nhắc & lý do chọn

- **Vẽ lớp phủ scrim 4 phía**: chọn `CustomPainter` vẽ `Path` với `PathFillType.evenOdd` (hình chữ nhật toàn viewport trừ `frameRect`) thay vì 4 `Positioned` container riêng lẻ. Lý do: ít node widget hơn, không bị hở khe sub-pixel 0.5px ở các cạnh trên màn hình mật độ điểm ảnh lẻ (`2.625x`, `2.75x`), và luôn dùng chung `frameRect` với `ScanCornersPainter`.
- **Tách widget vs sửa nguyên trong `scan_medication_screen.dart`**: chọn tách 2 file thuần giao diện (`scan_camera_overlay.dart`, `scan_failure_view.dart`) thay vì nhồi thêm vào file 919 dòng hiện tại. Lý do: `scan_medication_screen.dart` gọn xuống ~650 dòng, tách rõ ranh giới render vs điều phối vòng đời/dọn ảnh, và dễ kiểm chứng đơn vị hàm `computeScanFrameRect`.

### Đối chiếu bất biến kiến trúc & kỹ năng chuyên đề

- **Bất biến #1 (không truy cập Supabase từ client, ảnh OCR chỉ ở thiết bị)**: không thay đổi tầng mạng/lưu trữ; ảnh vẫn được mã hóa nội bộ và chỉ gửi chuỗi văn bản qua `POST /catalog/medications/match`.
- **An toàn dữ liệu tạm (`QD-39`)**: `_closeOcr()` và `_clearImage()` vẫn được gọi ở mọi nhánh xác nhận, chụp lại, thoát, Back, background, đổi phiên/rút consent và hết hạn 24h; listener `_onOcrChanged` đảm bảo UI fail-closed ngay khi hết hạn/lỗi cleanup.
- **`wf-db-migration` & `wf-health-endpoint`**: không áp dụng (không tạo/sửa migration hay endpoint backend; danh mục thuốc không phải dữ liệu sức khỏe).

## 1a. Quyết định nghiệp vụ áp dụng

- **Nguồn:** `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` (bản 3.1, baseline `QD-2026-10-03-v1`, Mục 3 "Nhập thuốc: OCR & nhập tay" và Mục 10 "Xóa tài khoản & lưu giữ dữ liệu").

| Mã & nội dung nguồn | Trạng thái | AC | Bước checklist | Test phủ |
|---|---|---|---|---|
| `QD-39` (dòng 68): Mọi kết quả OCR và nhập tay phải được người dùng kiểm tra tên thuốc, hàm lượng, đơn vị, liều và giờ trước khi tạo lịch. | ✅ | AC4, AC5 | P4, P6, P8, P10 | `ocr_single_result_card_test.dart`, `scan_medication_screen_test.dart` (`matched`, `low_confidence`, `strength_unverified`) |
| `QD-39` (dòng 69): Giai đoạn 1 chỉ tạo lịch cho thuốc đã có trong danh mục; không gán thuốc gần giống để vượt chặn. | ✅ | AC5, AC6 | P4, P5, P6, P10 | `scan_medication_screen_test.dart` (`low_confidence`, `no_match`, `noText`, manual fallback) |
| `QD-39` (dòng 70): Ảnh và văn bản OCR chỉ lưu mã hóa tối đa 24 giờ, xóa ngay khi xác nhận hoặc hủy; bản nháp chỉ giữ các trường người dùng đã kiểm tra. | ✅ | AC8, AC9 | P1, P5, P6, P7, P10 | `ocr_controller_test.dart` (`canRetry` vs `expiredImage`), `scan_medication_screen_test.dart` (`retry`, `expiredImage`, `unauthorized`, `cleanup`, `_invalidated`, cancel/exit) |
| `QD-39` (dòng 71): Không khôi phục màn hình Admin duyệt thuốc quét không khớp. | ✅ | Ngoài phạm vi | — | — |

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `work/6.04-ocr-scan-redesign/01-requirement.md` (`approved`) | Chốt `size: M`, `contract_change: no`, `affected: [frontend]`, 10 AC (`AC1–AC10`), các giả định Q1(A)/Q2(A)/Q3(A). |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` (bản 3.1, baseline `QD-2026-10-03-v1`, Mục 3 & 10) | Xác nhận 4 quy tắc `QD-39` (✅) và `QD-35` (✅) không đổi so với `01-requirement.md`. |
| `frontend/mobile/lib/app/theme/app_theme.dart` | Đầy đủ token nền tối (`cameraCanvas`, `cameraScrim`, `onCamera`, `cameraControl`, `cameraSurface`, `cameraAccent`, `onCameraAccent`, `cameraMuted`, `cameraOutline`), nền sáng/lâm sàng (`canvas`, `surface`, `surfaceMuted`, `brand`, `brandTint`, `ink`, `inkMuted`, `border`, `safe`/`safeBg`, `caution`/`cautionBg`/`cautionText`), `AppShadows.cardElevation`, `AppSizes.tapTarget = 48`, `AppSizes.primaryButton = 56`, `AppSizes.iconTile = 40`. `AppTextStyles` có thang 28/24/18/16/14 nên cỡ `17px` viết nhất quán bằng `AppTextStyles.body.copyWith(fontSize: 17, ...)`. |
| `frontend/mobile/lib/features/medication_capture/presentation/screens/scan_medication_screen.dart` | 919 dòng; chứa `_ScanCorners`, `_ScanBeam`, header `SizedBox(height: 112)` cố định, `_computeScanCropRect`, `_capture`, `_failDuringRecognition` (quên reset `_nameMissed = false`), `_failureBody`, `_resultSheet`, `_recognizingContent`. Chưa nghe listener từ `_ocr` khi đang ở `_Screen.failure`, chưa có `_retryOcr()`, ẩn `Tìm thuốc thủ công` khi lỗi ảnh/mạng/server. |
| `frontend/mobile/lib/features/medication_capture/presentation/state/ocr_controller.dart` | Đã giữ `_text` khi `failure.canRetry == true` để `start()` gọi lại đối chiếu (hoặc OCR lại nếu `recognition`). Cần thêm getter `canRetry` kiểm tra `!_closed && !_disposed && !image.isReleased && _clock().isBefore(image.expiresAt) && (failure?.canRetry ?? false)`. |
| `frontend/mobile/lib/features/medication_capture/presentation/widgets/ocr_single_result_card.dart` | Đang hiển thị badge `% khớp` màu `AppColors.brandTint`/`brand` ở góc phải tên thuốc, chưa có pill trạng thái phân biệt `matched` (`safeBg`/`safe`) vs `low_confidence` (`cautionBg`/`cautionText`) và chưa có `AppShadows.cardElevation`. |
| `frontend/mobile/lib/features/medication_capture/presentation/widgets/recognition_steps.dart` | Đang hardcode `_brand = 0xFF00534D` lệch `AppColors.brand = 0xFF01554F`, chữ chưa `17px`, bước active đang dùng `_ink` thay vì `AppColors.brand`. |
| `frontend/mobile/test/features/medication_capture/ocr_single_result_card_test.dart`, `recognition_steps_test.dart`, `scan_medication_screen_test.dart` | `ocr_single_result_card_test.dart:43` kiểm chuỗi chính xác `find.text('82% khớp')` (cần cập nhật sang `'Đã nhận diện · 82% khớp'`). `scan_medication_screen_test.dart` kiểm `Key('scan-beam')`, `Key('scan-preview')`, `Key('scan-frame')`, `Key('scan-hint')`, `Key('scan-recognizing')`, `Key('scan-result-sheet')`, `Key('scan-result-scroll')`, `Key('scan-progress')`, chuỗi `'Đặt tên thuốc vào trong khung'`, `'Mở cài đặt'`, `'Chụp lại'`, không có `'Cho phép camera'` — phải giữ nguyên toàn bộ các key & nhãn này. |

## 3. File sẽ thay đổi (ranh giới phạm vi)

<!-- scope.py đọc bảng này. Đường dẫn tính từ gốc submodule; được dùng glob, ví dụ `src/<module>/auth/**`. -->

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | `mobile/lib/features/medication_capture/presentation/state/ocr_controller.dart` | Sửa | Thêm getter `canRetry` kiểm tra phiên chưa đóng, ảnh chưa giải phóng/chưa hết hạn 24h và `failure?.canRetry == true`. |
| frontend | `mobile/lib/features/medication_capture/presentation/widgets/scan_camera_overlay.dart` | Thêm | Tách `computeScanFrameRect`, `toCaptureCropRect`, lớp phủ scrim 4 phía (`AppColors.cameraScrim`), 4 góc khung 28px, `ScanBeam` và `ScanGuidePill` (`S07-O1`). |
| frontend | `mobile/lib/features/medication_capture/presentation/widgets/scan_failure_view.dart` | Thêm | Tách `ScanFailureBody` (vòng tròn 160×160, thẻ gợi ý icon badge 40×40 chữ `17px Medium`) và `ScanFailureActions` (thanh đáy nền `AppColors.surface`, phân nhánh nút `Thử lại`/`Tìm thuốc thủ công`/`Chọn ảnh khác`/`Chụp lại`/fail-closed) cho `S07-O3e`. |
| frontend | `mobile/lib/features/medication_capture/presentation/widgets/recognition_steps.dart` | Sửa | Đồng bộ màu `AppColors` (`brand` `#01554F`, `brandTint`, `ink`, `inkMuted`, `border`), nâng cỡ chữ `17px` và màu `AppColors.brand` cho bước đang chạy (`S07-O2`). |
| frontend | `mobile/lib/features/medication_capture/presentation/widgets/ocr_single_result_card.dart` | Sửa | Bổ sung `Key('ocr-status-pill')` cho `matched` (`safeBg`/`safe`) và `low_confidence` (`cautionBg`/`cautionText` `#92400E`) cùng `AppShadows.cardElevation` (`S07-O2r`). |
| frontend | `mobile/lib/features/medication_capture/presentation/screens/scan_medication_screen.dart` | Sửa | Chuẩn hóa toàn bộ token nền tối/nền sáng, bỏ `SizedBox(height: 112)` cố định ở header, tích hợp `ScanCameraOverlay` & `ScanFailureView`, cải thiện UI khi chưa có quyền/lỗi camera, gắn listener `_ocr` theo dõi hết hạn 24h/cleanup, thêm `_retryOcr()`, reset `_nameMissed = false` trong `_failDuringRecognition()`. |
| frontend | `mobile/test/features/medication_capture/ocr_controller_test.dart` | Sửa | Bổ sung unit test cho `OcrController.canRetry` (lỗi thử lại được còn hạn vs hết hạn 24h/đã đóng vs lỗi không thử lại). |
| frontend | `mobile/test/features/medication_capture/ocr_single_result_card_test.dart` | Sửa | Cập nhật assertion pill mới (`'Đã nhận diện · 82% khớp'`) và bổ sung test cho pill `low_confidence` (`AppColors.cautionText`), `score <= 0`, và `AppShadows.cardElevation`. |
| frontend | `mobile/test/features/medication_capture/recognition_steps_test.dart` | Sửa | Bổ sung test màu `AppColors.brand` (`#01554F`) và cỡ chữ `17px` cho 3 trạng thái bước. |
| frontend | `mobile/test/features/medication_capture/scan_medication_screen_test.dart` | Sửa | Bổ sung widget test phủ `AC1–AC9` (scrim khớp khung cắt, pill hướng dẫn, quyền camera `denied`/`permanentlyDenied`/`camera.error`, `S07-O2` banner & reset `_nameMissed`, `S07-O3e` header `#01554F` & tips, lỗi ảnh, luồng `Thử lại` `canRetry` + biên hết hạn 24h, fail-closed `unauthorized`/`cleanup`/`_invalidated`, không overflow trên `360×640` với `textScaler = 1.3`). |

## 4. Checklist

- [ ] P1 [frontend] Thêm getter `canRetry` trên `OcrController` kiểm tra `!_closed && !_disposed && !image.isReleased && _clock().isBefore(image.expiresAt) && (failure?.canRetry ?? false)` — file: `mobile/lib/features/medication_capture/presentation/state/ocr_controller.dart` — AC: AC8, AC9 — xong khi: unit test `ocr_controller_test.dart` xác nhận `canRetry` đúng với cả `network`/`recognition` còn hạn, trả `false` khi `expiredImage`/`closed`/`noText`.
- [ ] P2 [frontend] Tạo `scan_camera_overlay.dart` gồm `computeScanFrameRect` (chừa sẵn `64dp` đáy cho guide pill và `12dp` trên, tự co `frameH` trên màn hình thấp), `toCaptureCropRect`, lớp phủ tối 4 phía `ScanScrimPainter` (`PathFillType.evenOdd`, `AppColors.cameraScrim`, `Key('scan-scrim')`), 4 góc 28px (`ScanCornersPainter`), `ScanBeam` (`Key('scan-beam')`, co theo `frameRect.height`, tôn trọng `disableAnimations`), và `ScanGuidePill` (`Key('scan-hint')`, icon quét màu mint, luôn đặt dưới `frameRect.bottom` không đè khung cắt) — file: `mobile/lib/features/medication_capture/presentation/widgets/scan_camera_overlay.dart` — AC: AC1 — xong khi: `computeScanFrameRect` khớp tuyệt đối giữa vùng khoét scrim, 4 góc và `CaptureCropRect` và `ScanGuidePill` không đè lên `frameRect` trên `360×640` + `textScaler = 1.3`.
- [ ] P3 [frontend] Cập nhật `recognition_steps.dart` dùng hoàn toàn token `AppColors` (`brand` `#01554F`, `brandTint`, `ink`, `inkMuted`, `border`), nâng chữ 3 bước lên `17px` qua `AppTextStyles.body.copyWith(fontSize: 17, ...)` với bước active tô `AppColors.brand` Bold — file: `mobile/lib/features/medication_capture/presentation/widgets/recognition_steps.dart` — AC: AC3 — xong khi: `recognition_steps_test.dart` pass và xác nhận đúng màu `#01554F` + cỡ chữ `17px`.
- [ ] P4 [frontend] Cập nhật `ocr_single_result_card.dart`: **loại bỏ** badge `% khớp` cũ ở góc phải tên thuốc và **thay thế** bằng `Key('ocr-status-pill')` phía trên tên thuốc cho `matched` (`AppColors.safeBg` + icon check + chữ `AppColors.safe` Bold `'Đã nhận diện · XX% khớp'` / `'Đã nhận diện'`) và `low_confidence` (`AppColors.cautionBg` + icon cảnh báo + chữ `AppColors.cautionText` `#92400E` Bold `'Cần đối chiếu · XX% khớp'` / `'Cần đối chiếu'`), bổ sung `AppShadows.cardElevation` — file: `mobile/lib/features/medication_capture/presentation/widgets/ocr_single_result_card.dart` — AC: AC4, AC5 — xong khi: `ocr_single_result_card_test.dart` pass với toàn bộ nhánh `matched`, `low_confidence`, `score <= 0`, `strengthUnverified` và không lặp `% khớp` 2 lần.
- [ ] P5 [frontend] Tạo `scan_failure_view.dart` gồm `ScanFailureBody` (vòng tròn `160×160` `AppColors.cautionBg`, tiêu đề `20px Bold`, mô tả `17px Regular`, thẻ gợi ý `Key('scan-failure-tips')` có viền `AppColors.border` + `AppShadows.cardElevation` + 2 huy hiệu icon `40×40` + chữ `17px Medium`) và `ScanFailureActions` (`Key('scan-failure-actions')`, nền `AppColors.surface`, viền trên `AppColors.border`): khi `isLockedFailure == true` chỉ hiển thị nút thoát an toàn `onExit` (`'Thử dọn lại'` khi `cleanupPending`, `'Đóng'` khi đã dọn sạch); khi `isLockedFailure == false` phân nhánh `Thử lại` (chỉ khi `canRetry`), `Tìm thuốc thủ công`, `Chọn ảnh khác`, `Chụp lại` — file: `mobile/lib/features/medication_capture/presentation/widgets/scan_failure_view.dart` — AC: AC6, AC7, AC8, AC9 — xong khi: widget test `S07-O3e` pass cho cả `no_match`, lỗi ảnh, `canRetry`, và `isLockedFailure`.
- [ ] P6 [frontend] Cập nhật `scan_medication_screen.dart`: bỏ `SizedBox(height: 112)` cố định ở header, chuẩn hóa toàn bộ màu/typography theo 2 bộ token nền tối vs nền sáng (header `S07-O3e` dùng `AppColors.brand` `#01554F`, nút đóng `×` tròn nền `AppColors.brandTint` icon `AppColors.brand`), tích hợp `ScanCameraOverlay` (chỉ ẩn và thay bằng thẻ hướng dẫn khi `denied`/`permanentlyDenied`/`camera.error`, giữ overlay lúc khởi tạo để không vỡ 2 test `scan-beam`; chỉ có duy nhất 1 nút `'Mở cài đặt'` khi `permanentlyDenied`, không thêm `'Cho phép camera'`), tích hợp `ScanFailureView`, nâng banner bảo mật `S07-O2` lên `14px Medium`, reset `_nameMissed = false` trong `_failDuringRecognition()`, gỡ listener `_onOcrChanged` **trước** `await ocr.close()` trong `_closeOcr()`, lọc chặt điều kiện trong `_onOcrChanged()` (gọi `_clearImage()` khi `expiredImage`/`cleanup` và đặt `_lockedFailure = _cleanupPending = true` khi `cleanup`), trong `_applyOcrOutcome()` đặt `_lockedFailure = true` + gọi ngay `_closeOcr()` + `_clearImage()` khi `unauthorized`, và bổ sung `_retryOcr()` — file: `mobile/lib/features/medication_capture/presentation/screens/scan_medication_screen.dart` — AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9 — xong khi: toàn bộ test cũ trong `test/features/medication_capture/` vẫn xanh.
- [ ] P7 [frontend] Bổ sung unit test cho `OcrController.canRetry` (nhánh `network`, `recognition`, `expiredImage`, `closed`, `noText`) — file: `mobile/test/features/medication_capture/ocr_controller_test.dart` — AC: AC8, AC9 — xong khi: `flutter test test/features/medication_capture/ocr_controller_test.dart` pass.
- [ ] P8 [frontend] Cập nhật và bổ sung widget test trong `ocr_single_result_card_test.dart` (pill `matched`, pill `low_confidence` với `AppColors.cautionText`, `score == 0`, `AppShadows.cardElevation`) — file: `mobile/test/features/medication_capture/ocr_single_result_card_test.dart` — AC: AC4, AC5 — xong khi: `flutter test test/features/medication_capture/ocr_single_result_card_test.dart` pass.
- [ ] P9 [frontend] Bổ sung widget test màu `AppColors.brand` (`#01554F`) và cỡ chữ `17px` trong `recognition_steps_test.dart` — file: `mobile/test/features/medication_capture/recognition_steps_test.dart` — AC: AC3 — xong khi: `flutter test test/features/medication_capture/recognition_steps_test.dart` pass.
- [ ] P10 [frontend] Bổ sung widget test toàn diện trong `scan_medication_screen_test.dart` phủ `AC1–AC9` (scrim 4 phía + pill dưới khung không đè `frameRect`, `denied`/`permanentlyDenied`/`camera.error` ẩn overlay và giữ 2 test `scan-beam` xanh, `S07-O2` banner `14px` & reset `_nameMissed` sau hủy giữa chừng với đúng bộ nút đáy, `S07-O3e` header `#01554F` + tips card, lỗi ảnh `blurred`/`invalidImage` có `Tìm thuốc thủ công` và không có `Thử lại`, bấm `Thử lại` cho `network` & `recognition`, biên ảnh hết hạn 24h dọn RAM + ẩn `Thử lại`, fail-closed giải phóng ảnh & RAM cho `unauthorized` (401)/`cleanup`/`_invalidated` chỉ cho thoát/thử dọn lại, và kiểm tra không overflow trên `Size(360, 640)` + `TextScaler.linear(1.3)` ở cả 4 trạng thái `_Screen`), rồi chạy toàn bộ `flutter test test/features/medication_capture/` và `flutter analyze` — file: `mobile/test/features/medication_capture/scan_medication_screen_test.dart` — AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9 — xong khi: toàn bộ test pass và `flutter analyze` không có lỗi mới.

## 5. Test

### Unit

| Test dự kiến | AC | Submodule |
|---|---|---|
| `ocr_controller_test.dart`: `canRetry is true for network/server/unavailable/recognition while lease valid` | AC8 | frontend |
| `ocr_controller_test.dart`: `canRetry becomes false after 24h expiry, close(), or non-retryable failure` | AC8, AC9 | frontend |
| `ocr_single_result_card_test.dart`: `matched shows green status pill "Đã nhận diện · 82% khớp" and card shadow` | AC4 | frontend |
| `ocr_single_result_card_test.dart`: `matched with score 0 shows "Đã nhận diện" without percentage` | AC4 | frontend |
| `ocr_single_result_card_test.dart`: `low_confidence shows caution pill with AppColors.cautionText (#92400E)` | AC5 | frontend |
| `recognition_steps_test.dart`: `active step uses AppColors.brand (#01554F) bold 17px, done uses ink 17px, pending uses inkMuted 17px` | AC3 | frontend |
| `scan_medication_screen_test.dart`: `camera renders 4-side cameraScrim aligned with crop frame, guide pill, dark tokens, no overflow at 360x640 textScaler 1.3` | AC1 | frontend |
| `scan_medication_screen_test.dart`: `denied, permanentlyDenied, and camera error show elderly guidance without allow button` | AC2 | frontend |
| `scan_medication_screen_test.dart`: `recognizing sheet shows 14px privacy banner, brand progress, and cancelling resets stale _nameMissed with no Retry button while keeping Manual/Gallery/Retake` | AC3 | frontend |
| `scan_medication_screen_test.dart`: `matched and low_confidence result sheets stay usable without overflow at 360x640 textScaler 1.3` | AC4, AC5 | frontend |
| `scan_medication_screen_test.dart`: `no_match failure header uses AppColors.brand (#01554F), tips card badges 40x40 17px, no retry button, no overflow at 360x640 textScaler 1.3` | AC6 | frontend |
| `scan_medication_screen_test.dart`: `blurred and invalidImage failures offer manual search, gallery, retake without retry button` | AC7 | frontend |
| `scan_medication_screen_test.dart`: `network and recognition failures show Retry button that re-runs OcrController.start() and succeeds without retaking` | AC8 | frontend |
| `scan_medication_screen_test.dart`: `expiring encrypted image while on failure screen clears RAM buffer, hides Retry and shows expired message cleanly` | AC8, AC9 | frontend |
| `scan_medication_screen_test.dart`: `unauthorized (401), cleanup failure, and invalidated session release temp image + RAM buffer, hide Retry/Manual/Gallery/Retake and only allow safe exit/cleanup retry` | AC9 | frontend |

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| Không có test tích hợp backend/DB mới | Không chạm endpoint dữ liệu sức khỏe, phân quyền người thân, đồng bộ liều hay tương tác thuốc (`contract_change: no`, chỉ sửa UI Mobile) | Kiểm chứng thủ công `AC10` trên thiết bị Android thật và chạy toàn bộ bộ test Mobile + `wf-testcase` ở giai đoạn `wf-test`. |

## 6. Migration

Không có. Task chỉ thay đổi tầng giao diện Mobile trong submodule `frontend`, không thêm/sửa bảng hay migration Supabase.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| superproject (`DrugTIme_main`) | `feat/6.04-ocr-scan-redesign` |
| `frontend` | `feat/6.04-ocr-scan-redesign` (tạo từ `main` đã fast-forward tại `442cb4e`, không chạm các submodule khác) |

## 8. Rủi ro

- **Dung lượng ổ `E:` (`E:\temp`, `errno = 112`)**: Reviewer ghi nhận lỗi thiếu dung lượng đĩa khi biên dịch `.dill` của `flutter test`. *Giảm thiểu*: kiểm tra dung lượng trống ổ `E:` (hoặc trỏ `TEMP`/`TMP` sang ổ còn dư dung lượng nếu người dùng cho phép) trước khi chạy `flutter test` ở giai đoạn `implement`; không tuyên bố pass nếu lệnh test không chạy thành công.
- **Lệch vùng cắt ảnh và scrim trên màn hình thấp (`360×640`, `textScaler = 1.3`)**: Bỏ `height: 112` cố định làm viewport camera co lại. *Giảm thiểu*: dùng duy nhất hàm `computeScanFrameRect(Size viewport)` sinh đồng thời vùng khoét scrim, 4 góc khung và `CaptureCropRect`, kèm test kích thước `360×640` + `textScaler = 1.3`.
- **Test cũ bị vỡ do đổi định dạng nhãn `% khớp` hoặc thứ tự nút**: `ocr_single_result_card_test.dart:43` tìm chuỗi chính xác `'82% khớp'`, và `scan_medication_screen_test.dart` tìm đúng các key/nhãn hiện hành. *Giảm thiểu*: giữ nguyên tất cả `Key(...)` và nhãn nút hiện hành (`'Đặt tên thuốc vào trong khung'`, `'Đúng thuốc này'`, `'Không phải thuốc này'`, `'Chụp lại'`, `'Mở cài đặt'`, `'Tìm thuốc thủ công'`, `'Chọn ảnh khác'`), chỉ cập nhật chủ đích `ocr_single_result_card_test.dart:43` theo P8.
- **Race condition khi bấm `Thử lại` sát thời điểm ảnh hết hạn 24h hoặc phiên bị hủy**: *Giảm thiểu*: kiểm tra `ocr.canRetry` trước khi chuyển `_Screen.recognizing`, lắng nghe `_onOcrChanged`, dùng biến `generation` chống phản hồi đến muộn và luôn gọi `_closeOcr()` khi thoát/hủy.

## 9. Câu hỏi mở

Không có. Các câu hỏi `Q1`, `Q2`, `Q3` đã được chốt theo giả định mặc định khi `01-requirement.md` được người dùng duyệt.

## 10. Phát sinh

- Workspace vẫn còn 104 file tồn đọng ngoài phạm vi từ trước (`100` file trong `DrugTime_Pilot_4.01/`, `1` file `execute_ducnt_plan/work/5.10-disclaimer-injection/01-requirement.md`, `3` file trong `backend/` ở nhánh `feat/5.10-disclaimer-injection`) và superproject `main` đang phân kỳ với `origin/main` (đã ghi ở `01-requirement.md` Mục 10). Khi bước vào giai đoạn `implement`, cần tách nhánh `feat/6.04-ocr-scan-redesign` sạch trên `frontend` (đang sạch tại `442cb4e`) và hỏi người dùng hướng xử lý file tồn đọng ở superproject/`backend` nếu muốn `scope.py` báo 0 file ngoài phạm vi.

## Bước tiếp theo

- Đang chờ: người dùng duyệt giai đoạn `plan` (phiên reviewer `3e2c9d0d-ffc3-4c37-b436-ba32311131a1` đã review độc lập vòng 2 kết luận ĐẠT).
- Việc cần làm: Người dùng chạy `python .agents/scripts/gate.py approve 6.04-ocr-scan-redesign plan`, sau đó bắt đầu giai đoạn `implement` (`wf-implement`).
- Cập nhật lần cuối: 2026-11-26 14:07, Antigravity
