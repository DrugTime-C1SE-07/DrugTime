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
   - `InteractionSeverity`: 4 mức độ nghiêm trọng (`contraindicated`, `severe`, `moderate`, `mild`), gán kèm nhãn tiếng Việt (`Chống chỉ định`, `Nghiêm trọng`, `Trung bình`, `Nhẹ`), màu sắc badge và nền chuẩn theo Figma tokens (`AppColors.danger`, `AppColors.caution`, `AppColors.info`).
   - `InteractionStatus`: Enum phân loại chính xác 3 trạng thái của engine theo bất biến CD06 (`hasInteractions`, `noKnownInteractions`, `insufficientData`).
   - `DrugInteractionPair`: Entity mô tả một cặp thuốc xung đột (`firstDrugName`, `secondDrugName`, `severity`, `description`, `recommendation`, `referenceSource`).
   - `DrugInteractionReport`: Báo cáo kết quả tổng thể với danh sách các cặp tương tác, timestamp, và danh sách các thuốc chưa có dữ liệu hoạt chất.

2. **Thành phần giao diện (UI Components)**:
   - `MandatoryDisclaimerCard` (`presentation/widgets/mandatory_disclaimer_card.dart`):
     - Hiển thị thông điệp miễn trừ trách nhiệm y tế chuẩn: *"Lưu ý: Thông tin cảnh báo tương tác thuốc chỉ mang tính chất tham khảo, không thay thế cho chỉ định hoặc tư vấn chuyên môn của bác sĩ/dược sĩ."*
     - Định dạng thẻ màu vàng cam nhạt (`AppColors.cautionBg`), biểu tượng `Icons.shield_outlined`.
     - **Bất biến**: Cố định 100% ở chân màn hình, tuyệt đối không có nút đóng (X) hay thao tác ẩn.
   - `InteractionPairCard` (`presentation/widgets/interaction_pair_card.dart`):
     - Hiển thị chi tiết từng cặp thuốc xung đột với badge mức độ nghiêm trọng nổi bật.
     - Trình bày cơ chế tương tác, hộp khuyến cáo xử trí lâm sàng nổi bật với biểu tượng y tế, và nguồn tham chiếu dược thư.
   - `DrugInteractionWarningScreen` (`presentation/screens/drug_interaction_warning_screen.dart`):
     - Màn hình chính xử lý State-driven UI cho 3 trạng thái kết quả.
     - Trạng thái `hasInteractions`: Hiển thị banner tổng số tương tác và danh sách toàn bộ các cặp xung đột (không ngắt ở cặp đầu tiên).
     - Trạng thái `noKnownInteractions`: Hiển thị icon tick kiểm tra, câu chữ bắt buộc *"Không tìm thấy tương tác đã biết trong cơ sở dữ liệu hiện tại"*, TUYỆT ĐỐI KHÔNG chứa từ "an toàn" (CD06).
     - Trạng thái `insufficientData`: Hiển thị biểu tượng trợ giúp, câu chữ bắt buộc *"Một số thuốc chưa có dữ liệu hoạt chất để kiểm tra tương tác, vui lòng tham khảo ý kiến bác sĩ hoặc dược sĩ."*, và danh sách các thuốc thiếu dữ liệu nếu có.
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
