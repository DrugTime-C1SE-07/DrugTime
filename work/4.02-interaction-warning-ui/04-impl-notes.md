---
task: 4.02-interaction-warning-ui
stage: implement
status: ready_for_review
size: M
owner: Duc1445
---

# 4.02 · Ghi chú triển khai: Warning Screen UI + Mandatory Disclaimer (PB24)

## 1. Tóm tắt giải pháp kỹ thuật

Đã hoàn thành toàn bộ các thành phần của Task 4.02 trong `frontend/mobile`, tuân thủ bất biến kiến trúc CD06 và tiêu chuẩn đảm bảo chất lượng QA.04:

1. **Data Models & Entities (`domain/entities/drug_interaction_result.dart`)**:
   - `InteractionSeverity`: 4 mức độ nghiêm trọng (`contraindicated`, `severe`, `moderate`, `mild`), gán kèm nhãn tiếng Việt (`Chống chỉ định`, `Nghiêm trọng`, `Trung bình`, `Nhẹ`), mã cấp (`CẤP 1` → `CẤP 4`), màu sắc badge và nền chuẩn theo Figma tokens (`AppColors.danger`, `AppColors.caution`, `AppColors.info`).
   - `InteractionStatus`: Enum phân loại chính xác 3 trạng thái của engine theo bất biến CD06 (`hasInteractions`, `noKnownInteractions`, `insufficientData`).
   - `DrugInteractionPair`: Entity mô tả một cặp thuốc xung đột (`firstDrugName`, `secondDrugName`, `severity`, `description`, `recommendation`, `referenceSource`).
   - `DrugInteractionReport`: Báo cáo kết quả tổng thể với danh sách các cặp tương tác, timestamp, `patientName`, `checkedMedications`, và danh sách các thuốc chưa có dữ liệu hoạt chất.

2. **Thành phần giao diện (UI Components - Bám sát Prototype Figma `page_127_Image556.png` & `page_130_Image562.png`)**:
   - `MandatoryDisclaimerCard` (`presentation/widgets/mandatory_disclaimer_card.dart`):
     - Hiển thị thông điệp miễn trừ trách nhiệm y tế chuẩn: *"Lưu ý: Thông tin cảnh báo tương tác thuốc chỉ mang tính chất tham khảo, không thay thế cho chỉ định hoặc tư vấn chuyên môn của bác sĩ/dược sĩ."*
     - Định dạng thẻ màu cam đào chuẩn Figma (`#FEEBD9`, viền `#FAD2B0`), tiêu đề in hoa `LƯU Ý Y TẾ BẮT BUỘC`, biểu tượng `Icons.health_and_safety_rounded`.
     - **Bất biến**: Cố định 100% ở chân màn hình, tuyệt đối không có nút đóng (X) hay thao tác ẩn.
   - `InteractionPairCard` (`presentation/widgets/interaction_pair_card.dart`):
     - Dải header phân loại nghiêm trọng chuẩn Figma: Dải băng màu đặc (`#BA1A1A` cho Chống chỉ định, `#DC2626` cho Nghiêm trọng, `#D97706` cho Trung bình, `#4B5563` cho Nhẹ) kèm icon và badge mức độ.
     - Khối hiển thị cặp thuốc dạng chip pill (`Color(0xFFF0F4FC)`) với icon thuốc và mũi tên hoán đổi.
     - Hộp cơ chế dược lực học & lâm sàng nổi bật (`#FDF2F2` / `#FEF9EE`) với biểu tượng `Icons.science_outlined`.
     - Hộp hướng dẫn xử trí lâm sàng (`#E8F6F4`) với biểu tượng `Icons.medical_services_outlined`.
     - Chú thích nguồn tham chiếu theo Quyết định 5948/QĐ-BYT & Dược thư Quốc gia Việt Nam.
   - `DrugInteractionWarningScreen` (`presentation/screens/drug_interaction_warning_screen.dart`):
     - Tích hợp **Patient Context Banner** (`#F0F4FC`) hiển thị tên người thân/bệnh nhân, icon xác thực bảo mật và nút chuyển chế độ "Chữ lớn" (`TT`).
     - Tích hợp Card **"Đã đối soát X hoạt chất"** với danh sách các thuốc dạng pill tags màu xanh ngọc (`#D2F3EE`).
     - Trạng thái `hasInteractions`: Prominent Warning Banner màu đỏ san hô (`#FDE8E8`), icon squircle đỏ cảnh báo, headline phát hiện tương tác, và trích dẫn pháp lý Quyết định 5948/QĐ-BYT.
     - Trạng thái `noKnownInteractions`: Tích hợp linh vật **DrugTime Mascot** (`AppAssets.mascotInteraction`), badge xác thực QĐ 5948/BYT, câu chữ bắt buộc *"Không tìm thấy tương tác đã biết trong cơ sở dữ liệu hiện tại"*, TUYỆT ĐỐI KHÔNG chứa từ "an toàn" (CD06).
     - Trạng thái `insufficientData`: Tích hợp linh vật **DrugTime Thinking Mascot** (`AppAssets.mascotThinking`), câu chữ bắt buộc *"Một số thuốc chưa có dữ liệu hoạt chất để kiểm tra tương tác, vui lòng tham khảo ý kiến bác sĩ hoặc dược sĩ."*, và danh sách thuốc thiếu dữ liệu.
     - Khối chân màn hình (`_buildBottomBar`): Cố định `MandatoryDisclaimerCard` cùng các nút hành động ("Tham khảo ý kiến bác sĩ" và "Tôi đã hiểu và tiếp tục").

3. **Routing / Navigation (`lib/app/router.dart`)**:
   - Khai báo route `AppRoutes.interactionWarning = '/interaction-warning'`.
   - Xử lý mở màn hình thông qua `DrugInteractionWarningArgs` hoặc trực tiếp bằng `DrugInteractionReport`.
   - Có màn hình fallback an toàn `_InvalidInteractionWarningRouteScreen` khi thiếu arguments.

---

## 2. Danh sách file thay đổi

| Submodule | File | Hành động | Mục đích |
|---|---|---|---|
| `frontend` | `mobile/lib/features/interaction/domain/entities/drug_interaction_result.dart` | Tạo mới | Khai báo các entities và enums cho kết quả tương tác thuốc |
| `frontend` | `mobile/lib/features/interaction/presentation/widgets/mandatory_disclaimer_card.dart` | Tạo mới | Widget disclaimer y tế bắt buộc |
| `frontend` | `mobile/lib/features/interaction/presentation/widgets/interaction_pair_card.dart` | Tạo mới | Widget card hiển thị cặp thuốc xung đột |
| `frontend` | `mobile/lib/features/interaction/presentation/screens/drug_interaction_warning_screen.dart` | Tạo mới | Màn hình chính cảnh báo tương tác thuốc theo 3 trạng thái |
| `frontend` | `mobile/lib/app/router.dart` | Chỉnh sửa | Đăng ký route `/interaction-warning` và route handler |
| `frontend` | `mobile/test/features/interaction/drug_interaction_warning_screen_test.dart` | Tạo mới | Bộ automated widget tests |
