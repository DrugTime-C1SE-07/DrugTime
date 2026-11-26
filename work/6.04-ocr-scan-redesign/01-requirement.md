---
task: 6.04-ocr-scan-redesign
title: Mobile redesign & complete Blister Pack Scan (OCR) & medication recognition result screens
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: Duc1445
approved_at: 2026-11-26 13:58 +0700
content_hash: sha256:645fefcac97207fa
---

# 6.04-ocr-scan-redesign · Mobile: Redesign & complete Blister Pack Scan (OCR) & medication recognition result screens

## 1. Mục tiêu

Hoàn thiện và căn chỉnh toàn bộ giao diện luồng quét vỉ/hộp thuốc bằng OCR trên ứng dụng Flutter Mobile (`ScanMedicationScreen`: `S07-O1` camera, `S07-O2` đang nhận diện, `S07-O2r` kết quả nhận diện và `S07-O3e` không nhận diện được / lỗi) theo thiết kế Figma `Prototype_DrugTime` (`453:2216`, `453:2422`, `453:2817`, `453:2589`) và hệ thống design token `AppColors` / `AppTextStyles` / `AppSpacing` / `AppRadius` / `AppSizes` của DrugTime. Đảm bảo độ tương phản và cỡ chữ tối ưu cho người lớn tuổi (không tràn chữ khi `textScaler = 1.3`), giữ đầy đủ quy tắc an toàn dùng thuốc và dữ liệu tạm OCR (`QD-39`, hợp đồng `POST /catalog/medications/match`), và hoàn thiện mọi nhánh lỗi/thử lại (`Thử lại` khi `canRetry`, `Tìm thuốc thủ công`, `Chọn ảnh khác`, `Chụp lại`).

## 2. Phạm vi

### Trong phạm vi

- **Phân tách và chuẩn hóa Design Token nền tối vs nền sáng**:
  - **Nhóm nền tối** (header & khung camera ở `S07-O1`, `S07-O2`, `S07-O2r`): chỉ dùng `AppColors.cameraCanvas`, `AppColors.cameraScrim`, `AppColors.cameraSurface`, `AppColors.cameraControl`, `AppColors.cameraAccent`, `AppColors.onCamera`, `AppColors.cameraMuted`, `AppColors.cameraOutline` (loại bỏ các mã màu cứng `0xFF101111`, `0xFF171A19`, `0xFF303030`, `0xFF505454`, v.v.).
  - **Nhóm nền sáng** (màn lỗi `S07-O3e` và nội dung sheet trắng ở `S07-O2`, `S07-O2r`): chỉ dùng `AppColors.canvas`, `AppColors.surface`, `AppColors.surfaceMuted`, `AppColors.brand`, `AppColors.brandTint`, `AppColors.ink`, `AppColors.inkMuted`, `AppColors.border`, `AppColors.safe`/`safeBg`, `AppColors.caution`/`cautionBg`/`cautionText`, `AppShadows.cardElevation` (không dùng màu sáng của nền tối lên nền sáng).
  - **Bố cục header linh hoạt**: thay `SizedBox(height: 112)` cố định ở header của `ScanMedicationScreen` bằng bố cục tự giãn theo chiều cao nội dung để không overflow trên màn hình nhỏ (`360×640`) hoặc cỡ chữ lớn (`textScaler = 1.3`) ở cả 4 trạng thái `_Screen`.
- **Màn hình Camera quét vỉ thuốc (`S07-O1` · `453:2216`)**:
  - Bổ sung **lớp phủ tối 4 phía ngoài khung quét** (`dim/t`, `dim/b`, `dim/l`, `dim/r` trên Figma `453:2216`) bằng `AppColors.cameraScrim`, khoét sáng đúng vùng khung cắt với kích thước `frameW × frameH` từ `_computeScanCropRect` (không dùng margin dọc cứng làm lệch vùng cắt/scrim trên màn hình thấp).
  - Chuẩn hóa 4 góc khung quét (dài 28px, bo tròn đầu nét) và tia quét lặp hữu hạn (đứng yên khi `disableAnimations = true`).
  - Nâng cấp dòng hướng dẫn `'Đặt tên thuốc vào trong khung'` thành dạng **pill tối mờ bo tròn (`border-radius: 999`) có icon quét màu mint** đặt phía dưới khung quét (theo `guide` trong Figma `453:2250`, giữ nguyên văn bản `'Đặt tên thuốc vào trong khung'` khớp test hồi quy AC9).
  - Chuẩn hóa nút đóng `×` dạng tròn nền xanh nhạt (`AppColors.brandTint`) icon tối (`AppColors.brand`) đồng bộ ở cả nền tối và nền sáng như Figma `S07-O1/O3e`, thanh điều khiển đáy (`Thư viện` 56×56, nút chụp 80×80, `Nhập tay` 56×56, nhãn chữ `14px Medium`, thông điệp riêng tư `'Ảnh chỉ xử lý trên điện thoại của bạn'` `14px` đúng Figma `453:2267`).
  - Cải thiện hiển thị trạng thái chưa có quyền camera hoặc lỗi camera (`denied`, `permanentlyDenied`, `camera.error`): hiển thị khung/hướng dẫn dễ hiểu cho người lớn tuổi (gợi ý dùng `Thư viện` hoặc `Nhập tay`; thêm nút `Mở cài đặt` khi `permanentlyDenied`), vẫn giữ hành vi tự động xin quyền khi mở và không thêm nút `'Cho phép camera'`.
- **Màn hình Đang nhận diện (`S07-O2` · `453:2422`)**:
  - Giữ nguyên `ScanningMascot` và `RecognitionSteps` 3 bước gắn `OcrStage` thật (đã chốt ở `adhoc-20261120`), đồng thời căn chỉnh theo Figma `453:2422`:
    - Đồng bộ màu `AppColors.brand` (`#01554F`), `AppColors.brandTint` (`#E7F3F1`), `AppColors.ink` (`#211D1D`), `AppColors.inkMuted` (`#5B6169`) trong `recognition_steps.dart` (thay hằng số cục bộ `_brand = 0xFF00534D` lệch token).
    - Nâng chữ 3 bước trong `RecognitionSteps` lên `17px` (active: `AppColors.brand` Bold; done: `AppColors.ink` Medium; pending: `AppColors.inkMuted` Regular) đúng Figma `453:2510/2515/2520`.
    - Nâng banner bảo mật `'Ảnh chỉ xử lý trên máy, không gửi đi'` (đúng Figma `453:2524`) lên `14px Medium` với icon khiên `AppColors.brand`.
  - Rà soát thao tác hủy giữa lúc đang nhận diện (`_failDuringRecognition`): reset `_nameMissed = false` (tránh dính trạng thái lần quét trước), dọn ảnh tạm mã hóa ngay và bỏ qua phản hồi đến muộn.
- **Màn hình Kết quả nhận diện (`S07-O2r` · `453:2817` kết hợp `OcrSingleResultCard`)**:
  - Giữ bố cục 1 thẻ chi tiết `OcrSingleResultCard` (tên thuốc lớn, 3 dòng `Hàm lượng` / `Dạng bào chế` / `Hoạt chất` hiển thị `'Chưa có thông tin'` khi trống, banner cảnh báo `low_confidence` hoặc `strength_unverified`) và 3 nút hành động ghim đáy (`Đúng thuốc này`, `Không phải thuốc này`, `Chụp lại`) theo `QD-39` và `POST /catalog/medications/match`.
  - Bổ sung từ Figma `S07-O2r` (`453:2926`):
    - **Pill trạng thái nhận diện** phía trên tên thuốc trong `OcrSingleResultCard`:
      - `matched`: nền `AppColors.safeBg` (`#E8F7EE`), icon check `AppColors.safe` (`#15803D`), chữ `AppColors.safe` Bold 14px `'Đã nhận diện · XX% khớp'` (hoặc `'Đã nhận diện'` khi `score <= 0`).
      - `low_confidence`: nền `AppColors.cautionBg` (`#FEF3E2`), icon cảnh báo `AppColors.caution`, chữ `AppColors.cautionText` (`#92400E`, đạt tương phản ≥ 4.5:1) Bold 14px `'Cần đối chiếu · XX% khớp'` (hoặc `'Cần đối chiếu'` khi `score <= 0`).
    - Áp dụng `AppShadows.cardElevation` cho thẻ kết quả và bảo đảm không tràn bố cục trên màn hình `360×640` hoặc `textScaler = 1.3`. (Lưu ý: cập nhật assertion `find.text('82% khớp')` trong `ocr_single_result_card_test.dart` sang định dạng pill mới.)
- **Màn hình Không nhận diện được / Lỗi (`S07-O3e` · `453:2589`)**:
  - **Sửa lỗi tương phản header**: dòng `'Bước 1/3 · Chưa đọc được'` dùng `AppColors.brand` (`#01554F`, 14px SemiBold) đúng Figma `I492:8426;492:7286` (thay cho `#70D9CC` tương phản kém trên nền sáng).
  - Chuẩn hóa vòng tròn minh họa `160×160` nền `AppColors.cautionBg` (`#FEF3E2`) với icon `scanLine` màu `AppColors.caution`, tiêu đề `20px Bold #211D1D`, mô tả `17px Regular #5B6169`.
  - Nâng cấp thẻ gợi ý (`tips` theo Figma `453:2610`): nền `AppColors.surface`, viền `AppColors.border`, đổ bóng `AppShadows.cardElevation`, bo góc 16; mỗi dòng có **huy hiệu icon 40×40 bo tròn** (ánh sáng: nền `AppColors.cautionBg`, icon nắng `AppColors.caution`; khung quét: nền `AppColors.brandTint`, icon quét `AppColors.brand`) kèm chữ **`17px Medium #211D1D`**.
  - Chuẩn hóa **thanh hành động đáy (`bottom-bar`)** nền `AppColors.surface` có viền trên `AppColors.border`, phân nhánh rõ theo loại lỗi:
    - `no_match` / `noText`: hiển thị `'Tìm thuốc thủ công'` (điền sẵn `suggested_query` nếu có), `'Chọn ảnh khác'`, `'Chụp lại'` (có icon `LucideIcons.scanLine`); **không** hiện `'Thử lại'`, **không** tự mở tìm thủ công.
    - Lỗi ảnh / không thử lại được (`blurred`, `dark`, `invalidImage`, `textTooLong`, `validation`, `unsupported`): hiển thị lý do cụ thể kèm `'Tìm thuốc thủ công'`, `'Chọn ảnh khác'`, `'Chụp lại'`; **không** hiện `'Thử lại'`.
    - Lỗi tạm thời có thể thử lại (`OcrFailure.canRetry == true`: `network`, `server`, `unavailable`, `recognition`): khi `_ocr` còn mở và ảnh chưa hết hạn 24h và `!_invalidated`, hiển thị nút **`Thử lại`** (chuyển lại `_Screen.recognizing` và gọi lại `OcrController.start()` dùng lại `_text` hoặc ảnh mã hóa còn hạn, không bắt chụp lại) cùng `'Tìm thuốc thủ công'`, `'Chọn ảnh khác'`, `'Chụp lại'`. Nếu `_ocr` bị đóng hoặc ảnh hết hạn 24h trong lúc đang ở màn lỗi thì ẩn nút `'Thử lại'` (hiện thông báo hết hạn mời chụp lại, không return im lặng).
    - Lỗi phiên/bảo mật/dọn ảnh (`_invalidated`, `OcrFailureKind.unauthorized`, `OcrFailureKind.cleanup`): ẩn `'Thử lại'`, `'Tìm thuốc thủ công'`, `'Chọn ảnh khác'` (fail-closed, chỉ cho thoát hoặc thử dọn lại/chụp lại an toàn).
- **Kiểm thử tự động**:
  - Cập nhật và bổ sung widget test trong `frontend/mobile/test/features/medication_capture/` phủ toàn bộ `AC1–AC9` mà không làm hỏng bộ test hiện có.

### Ngoài phạm vi

- Không thay đổi backend OCR matching engine (`backend`) hay hợp đồng API `POST /catalog/medications/match` (`api_contract`).
- Không thay đổi logic mã hóa/giải mã ảnh nội bộ (`EncryptedCaptureStore`, `CaptureCryptoWorker`) hay thư viện ML Kit OCR nền trừ khi cần sửa lỗi liên quan trực tiếp đến UI.
- Không khôi phục màn hình Admin duyệt thuốc quét không khớp (`QD-39`).
- Không thay đổi bước 2 và bước 3 của `AddMedicationScreen` (`S07-O4` / `S07-M2` / `S07-M3` / `S07-M4`) ngoài điểm nhận `scannedDrug` hiện có.
- Không hỗ trợ nhận nhiều thuốc trong 1 ảnh (hợp đồng hiện tại chỉ quét 1 vỉ/hộp thuốc mỗi lần).

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| Figma `Prototype_DrugTime` (`453:2216` `S07-O1`, `453:2319` `S07-O1b`, `453:2422` `S07-O2`, `453:2817` `S07-O2r`, `453:2589` `S07-O3e`) qua `figma-ui` MCP (`scan_design`) và đối chiếu ảnh trực tiếp trên tab Figma | Đã kiểm chứng cả dữ liệu node (`scan_design`) lẫn giao diện trực quan 5 frame (`S07-O1` → `S07-O3e`): `S07-O1` có 4 khối scrim `dim/t,b,l,r` khoét khung 220px, góc 28px `#7FD8C9`, pill hướng dẫn nền tối bo tròn đặt ngay dưới khung kèm icon quét màu mint, nút đóng `×` tròn nền nhạt, 3 nút đáy + dòng `'Ảnh chỉ xử lý trên điện thoại của bạn'` `14px`; `S07-O2` có 3 bước `17px` (active `#01554F` Bold) + banner `'Ảnh chỉ xử lý trên máy, không gửi đi'` `14px Medium`; `S07-O2r` có pill xanh lá `"Đã nhận diện · khớp XX%"` `#15803D`/`#E8F7EE`; `S07-O3e` có header `'Bước 1/3 · Chưa đọc được'` màu `#01554F`, vòng minh họa `160×160` `#FDF0E1`, thẻ tips có icon badge `40×40` + chữ `17px Medium`, thanh đáy nền trắng. |
| `docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx` (`Product Backlog`, `Sprint 6 Backlog`) & `docs/DrugTime_Sprint_Backlog_Task_Descriptions (1).md` | `PB31` (Scan blister pack): OCR trên thiết bị bằng ML Kit, không gửi ảnh ra ngoài, fallback tìm thủ công. **Điểm lệch mã backlog**: bản `.xlsx` cũ trong `docs/` đang ghi mã `6.04` là `PB33 · Simple Mode toggle`, trong khi người dùng giao task mới ở Sprint 6 với mã `6.04 · PB31` (ghi nhận tại Q3). |
| `docs/Team1_DTU/02_Requirements/Software Requirements Specification/DrugTime_SRS.docx` (`UC 06` cập nhật 17/11/2026 & `UC 07` cập nhật 18/11/2026) | `UC 06` mô tả luồng quét vỏ thuốc, chụp lại/chọn ảnh khác, lỗi ảnh/nhận diện và chuyển sang `UC 05` sau khi xác nhận; `UC 07` yêu cầu người dùng luôn kiểm tra và xác nhận rõ ràng trước khi điền vào form thêm thuốc. **Điểm không nhất quán**: `UC 06` Alternative Flow 2 còn câu cũ *"For a low-confidence result, System opens catalogue search automatically..."* mâu thuẫn với `openapi.json` (`POST /catalog/medications/match`) và `QD-39`. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` (bản 3.1, baseline `QD-2026-10-03-v1`, Mục 3 & Mục 10) | `QD-39` (4 quy tắc ✅): bắt buộc người dùng kiểm tra tên/hàm lượng/đơn vị/liều/giờ trước khi tạo lịch; chỉ tạo lịch cho thuốc trong danh mục, không gán thuốc gần giống; ảnh/text OCR lưu mã hóa tối đa 24h và xóa ngay khi xác nhận/hủy; không khôi phục màn Admin duyệt thuốc không khớp. `QD-35` (✅): dọn ảnh OCR khi hủy/xóa. |
| `api_contract/openapi.json` (`POST /catalog/medications/match`, `GET /catalog/medications`) | Đặc tả 3 trạng thái `matched`, `low_confidence`, `no_match`; client không tự suy trạng thái từ `score`; `matched` và `low_confidence` đều hiển thị 1 thẻ `items[0]` (`low_confidence` thêm lời nhắc đối chiếu tên & hàm lượng; `matched` + `strength_unverified` thêm lời nhắc đối chiếu hàm lượng); `no_match` mời chụp lại hoặc người dùng tự chọn tìm thủ công với `suggested_query` (không tự mở tìm thủ công). |
| `frontend/mobile/lib/features/medication_capture/presentation/screens/scan_medication_screen.dart` | Đã có 4 trạng thái `_Screen`, khung cắt `CaptureCropRect`, tia quét lặp, `ScanningMascot`, `RecognitionSteps`, `OcrSingleResultCard`, dọn ảnh khi thoát/background/đổi phiên/rút consent. Các điểm cần hoàn thiện: mã màu cứng thay vì `AppColors`, `SizedBox(height: 112)` cố định ở header, thiếu scrim 4 phía, thiếu pill hướng dẫn, header `S07-O3e` dùng `#70D9CC`, thẻ tips thiếu icon badge `40×40` & chữ `17px`, thiếu nút `Thử lại` khi `canRetry`, ẩn `Tìm thuốc thủ công` khi lỗi ảnh/mạng/server, `_failDuringRecognition` chưa reset `_nameMissed`. |
| `frontend/mobile/lib/features/medication_capture/presentation/widgets/ocr_single_result_card.dart` & `recognition_steps.dart` | `OcrSingleResultCard` chưa có pill trạng thái phân biệt `matched` (`safeBg`/`safe`) vs `low_confidence` (`cautionBg`/`caution`) và chưa có `AppShadows.cardElevation`. `recognition_steps.dart` dùng `_brand = 0xFF00534D` lệch `AppColors.brand = 0xFF01554F`, chữ chưa `17px` và bước active chưa dùng `AppColors.brand`. |
| `frontend/mobile/lib/features/medication_capture/domain/capture_ports.dart`, `presentation/state/capture_controller.dart`, `presentation/state/ocr_controller.dart` | `CaptureSource` và `CaptureController` **đã cài sẵn** `flashAvailable`, `flashOn` và `toggleFlash()` (chỉ chưa có nút UI trên `ScanMedicationScreen`). `OcrController` đã lưu tạm `_text` khi `failure.canRetry == true` để `start()` gọi lại đối chiếu không cần chạy lại OCR, nhưng `start()` sẽ return im lặng nếu `_closed == true` (khi ảnh hết hạn 24h hoặc đã đóng). |
| `frontend/mobile/lib/app/theme/app_theme.dart` | Đã có đủ bộ token camera nền tối (`cameraCanvas`, `cameraScrim`, `onCamera`, `cameraControl`, `cameraSurface`, `cameraAccent`, `onCameraAccent`, `cameraMuted`, `cameraOutline`), token nền sáng/lâm sàng (`canvas`, `surface`, `brand`, `brandTint`, `safe*`, `caution*`), `AppShadows.cardElevation` và `AppSizes`. |
| Bộ test hiện hành: `scan_medication_screen_test.dart`, `ocr_single_result_card_test.dart`, `recognition_steps_test.dart`, `scanning_mascot_test.dart`, `ocr_controller_test.dart`, `capture_controller_test.dart`, `add_medication_entry_test.dart`, `medication/scanned_schedule_test.dart` | Bảo vệ các hành vi đang chạy: tự xin quyền camera (không có nút `'Cho phép camera'`), cắt theo khung, `matched`/`low_confidence`/`strength_unverified`/`no_match`/`noText`, ảnh mờ, hủy khi đang nhận diện, dọn ảnh tạm, ghim nút đáy và nối sang `AddMedicationScreen`. |

## 3a. Quyết định nghiệp vụ áp dụng

- **Nguồn:** `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` (bản 3.1, baseline `QD-2026-10-03-v1`, Mục 3 "Nhập thuốc: OCR & nhập tay" và Mục 10 "Xóa tài khoản & lưu giữ dữ liệu").

| Mã | Mục / nội dung quy tắc | Trạng thái nguồn | AC tương ứng |
|---|---|---|---|
| `QD-39` (dòng 68) | Mọi kết quả OCR **và** nhập tay phải được người dùng kiểm tra tên thuốc, hàm lượng, đơn vị, liều và giờ trước khi tạo lịch. | ✅ | AC4, AC5 |
| `QD-39` (dòng 69) | Giai đoạn 1 chỉ tạo lịch cho thuốc đã có trong danh mục; không gán thuốc gần giống để vượt chặn. | ✅ | AC5, AC6 |
| `QD-39` (dòng 70) | Ảnh và văn bản OCR chỉ lưu mã hóa tối đa 24 giờ, xóa ngay khi xác nhận hoặc hủy; bản nháp chỉ giữ các trường người dùng đã kiểm tra. | ✅ | AC8, AC9 |
| `QD-39` (dòng 71) | Không khôi phục màn hình Admin duyệt thuốc quét không khớp. | ✅ | Ngoài phạm vi |

*Điểm không nhất quán phát hiện khi đối chiếu tài liệu:*
1. **`Product Backlog PB31` và `DrugTime_SRS.docx` (`UC 06` Alternative Flow 2)** ghi cũ là tự động mở tìm thủ công khi `low_confidence`, mâu thuẫn với hợp đồng API hiện hành `api_contract/openapi.json` (`POST /catalog/medications/match`) và `QD-39`: `low_confidence` hiển thị 1 thẻ `items[0]` kèm lời nhắc đối chiếu tên & hàm lượng (không tự chọn/không tự mở tìm thủ công); `no_match` không hiển thị thuốc nào, mời chụp lại hoặc người dùng tự bấm `Tìm thuốc thủ công` với `suggested_query`. Task này tuân theo `openapi.json` hiện hành và `QD-39`.
2. **Figma `S07-O2r` (`453:2817`) vs `OcrSingleResultCard` (PR `b6f9b6d`)**: Figma vẽ thẻ gọn 2 dòng (`Paracetamol 500mg` / `Paracetamol · Viên nén`) kèm nút `Đổi` và 2 nút ngang; code hiện tại đã mở rộng thành 3 dòng nhãn rõ (`Hàm lượng`, `Dạng bào chế`, `Hoạt chất`) + banner cảnh báo + 3 nút dọc ghim đáy để dễ đối chiếu theo `QD-39` (chốt ở Q1).
3. **Mã backlog `6.04`**: `Product-and-Sprint-backlog-DrugTime.xlsx` trong `docs/` đang ghi `6.04 = PB33 (Simple Mode toggle)`, trong khi người dùng giao `6.04 = PB31 (Mobile: Redesign & complete Blister Pack Scan & recognition result screens)` (chốt ở Q3).

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `frontend` | Có | Cập nhật UI và widget test trong `frontend/mobile/lib/features/medication_capture/` và `frontend/mobile/test/features/medication_capture/`. |
| `backend` | Không | Dùng nguyên endpoint `POST /catalog/medications/match` và `GET /catalog/medications` hiện có. |
| `api_contract` | Không | Không thêm/sửa/xóa endpoint hay schema request/response. |
| `tests` | Không | Kiểm thử tự động nằm trong `frontend/mobile/test/features/medication_capture/`. |
| `docs` | Không (ở giai đoạn implement) | Cập nhật `Test_Cases.xlsx` thực hiện ở giai đoạn `wf-test` / `wf-testcase`. |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: Mọi thay đổi chỉ nằm ở giao diện và quản lý trạng thái hiển thị phía Mobile; hình dạng request/response, mã trạng thái và ý nghĩa `status`/`reasons`/`suggested_query` giữ nguyên 100%.
- Endpoint liên quan (chỉ dùng):
  - `POST /catalog/medications/match`
  - `GET /catalog/medications`

## 6. Vùng rủi ro và bất biến bị chạm

- **Bất biến kiến trúc #1**: Mobile App chỉ gọi Backend API, không truy cập Supabase trực tiếp; ảnh vỉ thuốc chỉ xử lý OCR trên thiết bị bằng ML Kit, không gửi ảnh ra ngoài thiết bị (PB31, QD-39).
- **Quyền riêng tư & dữ liệu tạm OCR (QD-39)**: Ảnh và văn bản OCR chỉ lưu mã hóa tối đa 24h; mọi hành động xác nhận (`Đúng thuốc này`), tìm thủ công, chụp lại, thoát màn hình, ẩn ứng dụng xuống nền, hết hạn 24h hoặc rút consent/đổi phiên đều phải giải phóng và xóa sạch ảnh tạm mã hóa (`_closeOcr()` + xóa buffer bộ nhớ `_clearImage()`).
- **An toàn dùng thuốc (QD-39)**: Tuyệt đối không tự động xác nhận hay bỏ qua bước người dùng kiểm tra tên thuốc, hàm lượng, đơn vị, liều và giờ trước khi tạo lịch.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given màn hình `ScanMedicationScreen` mở ở trạng thái camera (`S07-O1`) có quyền camera, When render trên `375×812` và trên màn hình nhỏ/chữ lớn (`360×640`, `textScaler = 1.3`), Then dùng bộ token nền tối (`AppColors.cameraCanvas`/`cameraScrim`/`cameraControl`/`cameraAccent`), hiển thị lớp phủ tối `AppColors.cameraScrim` 4 phía ngoài khung cắt (khoét sáng đúng vùng khung), 4 góc khung 28px, pill hướng dẫn `'Đặt tên thuốc vào trong khung'` có icon, tia quét lặp hữu hạn (đứng yên khi `disableAnimations = true`), bộ 3 nút `Thư viện` / `Chụp ảnh` / `Nhập tay` ≥ 48dp (nhãn `14px`), dòng `'Ảnh chỉ xử lý trên điện thoại của bạn'` (`14px`), và không overflow header/body. | unit (widget) |
| AC2 | Given màn hình camera mở khi quyền camera là `denied`, `permanentlyDenied`, hoặc `camera.error != null`, When render xong, Then không có nút `'Cho phép camera'` (giữ cơ chế tự xin quyền khi mở), hiển thị khung hướng dẫn rõ ràng gợi ý dùng `Thư viện` hoặc `Nhập tay`; riêng `permanentlyDenied` hiển thị thêm nút `Mở cài đặt` gọi `openSettings()`. | unit (widget) |
| AC3 | Given người dùng vừa chụp/chọn ảnh và màn hình đang ở trạng thái nhận diện (`S07-O2`), When `OcrStage` chạy qua `recognizing` → `matching` (kể cả khi `textScaler = 1.3`), Then không overflow header/sheet, `RecognitionSteps` dùng màu `AppColors.brand` (`#01554F`) và cỡ chữ `17px` cho bước đang chạy, thanh tiến trình tăng theo `OcrStage` thật (`1/3` → `2/3`), banner `'Ảnh chỉ xử lý trên máy, không gửi đi'` hiển thị `14px Medium`; When người dùng chạm hủy giữa chừng (`_failDuringRecognition`), Then đặt lại `_nameMissed = false`, dọn ảnh tạm mã hóa, chuyển sang `_Screen.failure` và bỏ qua phản hồi đến muộn. | unit (widget) |
| AC4 | Given `POST /catalog/medications/match` trả `status: matched` với `items[0]`, When màn hình kết quả (`S07-O2r`) hiển thị, Then chỉ hiển thị 1 thẻ `OcrSingleResultCard` (có `AppShadows.cardElevation`) kèm pill trạng thái màu xanh lá (`AppColors.safeBg`/`AppColors.safe`, icon check, `'Đã nhận diện · XX% khớp'` hoặc `'Đã nhận diện'` khi `score <= 0`), tên thuốc và 3 dòng `Hàm lượng` / `Dạng bào chế` / `Hoạt chất`; nếu `reasons` có `strength_unverified` thì hiển thị cảnh báo `'Hãy xem số mg trên vỏ hộp'`; các nút `Đúng thuốc này`, `Không phải thuốc này`, `Chụp lại` ghim đáy và bấm được không tràn trên `360×640` và `textScaler = 1.3`; bấm `Đúng thuốc này` dọn ảnh tạm và mở `AddMedicationScreen(scannedDrug: ...)` để kiểm tra liều/giờ (`QD-39`). | unit (widget) |
| AC5 | Given `POST /catalog/medications/match` trả `status: low_confidence` với nhiều ứng viên và `suggested_query`, When màn hình kết quả hiển thị, Then chỉ hiển thị 1 thẻ `items[0]` có pill trạng thái màu hổ phách (`AppColors.cautionBg`/`AppColors.cautionText`, icon cảnh báo, `'Cần đối chiếu · XX% khớp'`) kèm banner `'Hãy đối chiếu tên và số mg với vỏ hộp'`, không tự mở tìm thủ công; When bấm `Đúng thuốc này`, Then dọn ảnh tạm rồi chuyển sang `AddMedicationScreen` (giữ nguyên bước kiểm tra tên/hàm lượng/đơn vị/liều/giờ trước khi lưu theo `QD-39`); When bấm `Không phải thuốc này`, Then mở sheet tìm thủ công điền sẵn `suggested_query`. | unit (widget) |
| AC6 | Given `POST /catalog/medications/match` trả `status: no_match` hoặc ML Kit không đọc được chữ (`noText`), When màn hình lỗi (`S07-O3e`) hiển thị (kể cả trên `360×640` với `textScaler = 1.3`), Then dùng bộ token nền sáng, header `'Bước 1/3 · Chưa đọc được'` dùng màu `AppColors.brand` (`#01554F`, không dùng `#70D9CC`, không overflow), hiển thị vòng minh họa `160×160` (`AppColors.cautionBg`), thẻ gợi ý có 2 huy hiệu icon `40×40` và chữ `17px Medium`, không hiện thẻ thuốc, không tự mở tìm thủ công; thanh đáy nền `AppColors.surface` cung cấp `Tìm thuốc thủ công` (điền sẵn `suggested_query` nếu có), `Chọn ảnh khác`, `Chụp lại`, và **không** hiện nút `Thử lại`. | unit (widget) |
| AC7 | Given chụp/chọn ảnh gặp lỗi không thể thử lại (`CaptureWarning.blurred`/`dark`, `OcrFailureKind.invalidImage`, `textTooLong`, `validation`, `unsupported`), When màn hình lỗi (`S07-O3e`) hiển thị và `!_invalidated`, Then hiển thị đúng tiêu đề/lý do lỗi, thanh đáy cung cấp `Tìm thuốc thủ công`, `Chọn ảnh khác`, `Chụp lại`, và **không** hiện nút `Thử lại`. | unit (widget) |
| AC8 | Given bước nhận diện/đối chiếu gặp lỗi tạm thời có thể thử lại (`OcrFailureKind.network`, `server`, `unavailable`, `recognition` với `canRetry == true`), When màn hình lỗi hiển thị trong khi `_ocr` còn mở và ảnh chưa hết hạn 24h (`!_invalidated`), Then thanh đáy hiển thị nút `Thử lại` cùng `Tìm thuốc thủ công`, `Chọn ảnh khác`, `Chụp lại`; When bấm `Thử lại`, Then chuyển về `_Screen.recognizing`, gọi lại `OcrController.start()` (tận dụng `_text` đã đọc hoặc giải mã lại ảnh từ `lease` khi lỗi `recognition`) và hiện kết quả nếu thành công; When ảnh hết hạn 24h hoặc `_ocr` đã đóng trước khi/trong khi bấm `Thử lại`, Then ẩn `Thử lại` hoặc hiển thị thông báo ảnh hết hạn mời chụp lại (không return im lặng). | unit (widget) |
| AC9 | Given ảnh tạm mã hóa đang được giữ ở trạng thái nhận diện, kết quả hoặc lỗi, When người dùng bấm `Đúng thuốc này`, `Chụp lại`, `Đóng`, nhấn Back, đưa app xuống nền, ảnh quá hạn 24h (`OcrFailureKind.expiredImage`), hoặc phiên/consent bị thu hồi (`_invalidated` / `OcrFailureKind.unauthorized` / `cleanup`), Then ảnh tạm mã hóa (`release`) và buffer RAM (`_clearImage`) được xóa sạch, phản hồi đến muộn bị bỏ qua; riêng khi `_invalidated`, `unauthorized` hoặc `cleanup` thì không hiển thị nút `Thử lại`, `Tìm thuốc thủ công`, `Chọn ảnh khác` (fail-closed). | unit (widget) |
| AC10 | Given thiết bị thật có camera (Android), When người dùng chụp vỉ thuốc thật ở ánh sáng thường và ánh sáng yếu, Then lớp phủ tối khung quét rõ nét, ảnh cắt đúng khung, chuyển mượt qua sheet nhận diện và màn kết quả/lỗi mà không giật hoặc tràn bố cục. | manual (cần thiết bị thật và vỉ thuốc vật lý) |

## 8. Câu hỏi mở

Q1 [không chặn] Bố cục thẻ kết quả `S07-O2r` — giữ thẻ chi tiết 3 dòng + 3 nút ghim đáy hay thu gọn theo Figma `453:2817`?
- Ảnh hưởng: Figma `453:2817` vẽ thẻ kết quả rút gọn 2 dòng (`Paracetamol 500mg` / `Paracetamol · Viên nén`, nút `Đổi`, 2 nút ngang `Quét lại` / `Đúng thuốc này`), trong khi `frontend/main` (`OcrSingleResultCard`, PR `b6f9b6d`) đang dùng thẻ chi tiết 3 dòng nhãn rõ (`Hàm lượng`, `Dạng bào chế`, `Hoạt chất`) + banner cảnh báo `low_confidence`/`strength_unverified` + 3 nút dọc ghim đáy (`Đúng thuốc này`, `Không phải thuốc này`, `Chụp lại`).
- Lựa chọn: (A) Giữ thẻ chi tiết 3 dòng & 3 nút ghim đáy (tuân thủ `QD-39` và giữ xanh bộ test hiện có) đồng thời bổ sung pill trạng thái xanh/hổ phách & shadow từ Figma `S07-O2r` / (B) Đổi sang bố cục rút gọn 2 dòng & 2 nút ngang đúng nguyên mẫu Figma `453:2817`.
- Giả định mặc định: (A) Giữ thẻ chi tiết 3 dòng & 3 nút ghim đáy kết hợp pill trạng thái & token từ Figma `S07-O2r`.

Q2 [không chặn] Nút bật/tắt đèn flash (torch) trên màn hình camera (`S07-O1`): Figma `453:2216` không có nút flash, nhưng tầng dưới (`CaptureSource`, `SystemCaptureSource`, `CaptureController.toggleFlash()`) đã cài sẵn. Có cần thêm nút UI bật/tắt flash trên `ScanMedicationScreen` trong task 6.04 không?
- Ảnh hưởng: Nếu chọn (B), chỉ cần thêm nút icon bật/tắt đèn flash trên `ScanMedicationScreen` (hiển thị khi `flashAvailable == true`) và bổ sung widget test gọi `_camera.toggleFlash()`; không cần sửa `CaptureSource`/`SystemCaptureSource`.
- Lựa chọn: (A) Không thêm nút flash (đúng Figma `453:2216`, giữ gọn giao diện camera) / (B) Thêm nút bật/tắt flash trên góc trên camera.
- Giả định mặc định: (A) Không thêm nút flash.

Q3 [không chặn] Xác nhận mã Task ID `6.04-ocr-scan-redesign`: Trong `Product-and-Sprint-backlog-DrugTime.xlsx` ở `docs/`, mã `6.04` cũ là `PB33 · Simple Mode toggle`, trong khi danh sách Sprint 6 bạn giao ghi `6.04 · PB31 · Mobile: Redesign & complete Blister Pack Scan (OCR) & medication recognition result screens`. Bạn xác nhận dùng `6.04-ocr-scan-redesign` hay đổi sang `adhoc-20261126-ocr-scan-redesign` để tránh trùng mã với `PB33`?
- Ảnh hưởng: Quyết định tên thư mục `work/<task-id>/`, tên nhánh git (`feat/<task-id>`) và mã đối chiếu khi cập nhật `Test_Cases.xlsx`.
- Lựa chọn: (A) Giữ `6.04-ocr-scan-redesign` theo bảng Sprint 6 hiện hành bạn vừa giao / (B) Đổi sang `adhoc-20261126-ocr-scan-redesign`.
- Giả định mặc định: (A) Giữ `6.04-ocr-scan-redesign`.

## 9. Giả định

- Giữ nguyên cấu trúc 3 bước thêm thuốc (`Bước 1/3 · Quét vỏ` → `Bước 2/3 · Lịch uống` → `Bước 3/3 · Hoàn tất`) và điểm nối sang `AddMedicationScreen(scannedDrug: drug)`.
- Giữ nguyên cơ chế tự động xin quyền camera khi mở màn hình (không thêm nút `'Cho phép camera'` như bộ test hiện hành đã chốt), chỉ hiển thị `'Mở cài đặt'` khi `permanentlyDenied`.
- Giữ nguyên 2 câu thông điệp bảo mật khớp đúng Figma (`S07-O1` camera `453:2267`: `'Ảnh chỉ xử lý trên điện thoại của bạn'`; `S07-O2` sheet nhận diện `453:2524`: `'Ảnh chỉ xử lý trên máy, không gửi đi'`), nhãn nút `'Chụp lại'` và hướng dẫn `'Đặt tên thuốc vào trong khung'` để không phá vỡ test hồi quy hiện hành.
- Không thay đổi mã nguồn ở `backend` và `api_contract`.

## 10. Phát sinh

- **Kết quả `scope.py 6.04-ocr-scan-redesign --stage requirement`**: báo `CHẶN: 104 file ngoài phạm vi` (tất cả đều là file tồn đọng sẵn trên workspace trước khi bắt đầu task 6.04, không do phiên này tạo/sửa):
  - 100 file untracked trong thư mục `DrugTime_Pilot_4.01/` (dữ liệu tài liệu/script pilot 4.01).
  - 1 file untracked `execute_ducnt_plan/work/5.10-disclaimer-injection/01-requirement.md`.
  - 3 file modified/untracked trong submodule `backend` (đang ở nhánh `feat/5.10-disclaimer-injection`): `backend/src/drugtime/modules/ai_meal/adapters/inbound/schemas.py`, `backend/src/drugtime/modules/ai_meal/domain/model.py`, `backend/tests/unit/test_disclaimer_injection.py`.
  - Cần người dùng xác nhận hướng xử lý các file tồn đọng trên workspace (và nhánh `main` superproject đang phân kỳ 12/48 commit) trước khi chuyển sang giai đoạn `implement` để `scope.py` sạch.
- **Môi trường ổ đĩa**: phiên reviewer ghi nhận ổ `E:\temp` báo thiếu dung lượng (`errno = 112`) khi chạy biên dịch `.dill` của `flutter test`; cần kiểm tra/giải phóng dung lượng ổ `E:` trước giai đoạn `implement` để chạy được `flutter test`.

## 11. Size

- `size`: M
- Lý do: Chỉ ảnh hưởng 1 submodule (`frontend`), nhưng chạm nhiều file UI và test (> 3 file, > 50 dòng) đồng thời chạm vùng quy tắc an toàn dùng thuốc và dữ liệu tạm OCR (`QD-39`), nên không đủ điều kiện xếp size S.

## Bước tiếp theo

- Đang chờ: người dùng chốt Q1/Q2/Q3 (đều không chặn; phiên reviewer `3e2c9d0d-ffc3-4c37-b436-ba32311131a1` đã review vòng 2 kết luận ĐẠT) rồi duyệt giai đoạn `requirement`.
- Việc cần làm: Người dùng xác nhận Q1/Q2/Q3 và chạy `python .agents/scripts/gate.py approve 6.04-ocr-scan-redesign requirement` (hoặc yêu cầu đổi task ID trước nếu chọn Q3 = B).
- Cập nhật lần cuối: 2026-11-26 13:50, Antigravity
