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

2. **Thành phần giao diện (UI Components - Chuẩn hóa Clean UI/UX theo Prototype Figma `S06c` Node `401:107`)**:
   - `MandatoryDisclaimerCard` (`presentation/widgets/mandatory_disclaimer_card.dart`):
     - Hiển thị thông điệp miễn trừ trách nhiệm y tế chuẩn: *"Lưu ý: Thông tin cảnh báo tương tác thuốc chỉ mang tính chất tham khảo, không thay thế cho chỉ định hoặc tư vấn chuyên môn của bác sĩ/dược sĩ."*
     - Dải card màu hổ phách/vàng ấm nhẹ (`#FEF3E2`, viền `#FDE68A`), icon `Icons.shield_outlined` (`#D97706`), font size 11pt tinh gọn 1-2 dòng, giảm tối đa visual clutter.
     - **Bất biến**: Cố định 100% ở chân màn hình, tuyệt đối không có nút đóng (X) hay thao tác ẩn.
   - `InteractionPairCard` (`presentation/widgets/interaction_pair_card.dart`):
     - Phân cấp mức độ nguy cơ bằng icon tròn và badge màu tương ứng (`#DC2626` cho Chống chỉ định/Nghiêm trọng, `#D97706` cho Trung bình, `#16A34A` cho Nhẹ).
     - Khối hiển thị cặp thuốc dạng capsule nền trắng (`💊 Clopidogrel 75mg ⇄ 💊 Omeprazole 20mg`).
     - Tối ưu nhận thức trong 3 giây: 2 dòng bullet points cốt lõi (Nguy cơ + Khuyến nghị), loại bỏ các đoạn văn rườm rà.
   - `DrugInteractionWarningScreen` (`presentation/screens/drug_interaction_warning_screen.dart`):
     - Trạng thái `hasInteractions`: Hero alert card đỏ/hổ phách, headline số lượng tương tác, danh sách `InteractionPairCard`.
     - Trạng thái `noKnownInteractions`: Icon tròn xanh lá checkmark, badge chứng nhận QĐ 5948/BYT, câu chữ bắt buộc *"Không tìm thấy tương tác đã biết trong cơ sở dữ liệu hiện tại"*, TUYỆT ĐỐI KHÔNG chứa từ "an toàn" (CD06).
     - Trạng thái `insufficientData`: Icon tròn vàng hỏi chấm, câu chữ bắt buộc *"Một số thuốc chưa có dữ liệu hoạt chất để kiểm tra tương tác, vui lòng tham khảo ý kiến bác sĩ hoặc dược sĩ."*, và danh sách thuốc thiếu dữ liệu.
     - Card đơn thuốc đã đối soát và thông tin bệnh nhân tinh gọn, chỉ hiển thị khi có dữ liệu tường minh.
     - Khối chân màn hình (`_buildBottomBar`): Cố định `MandatoryDisclaimerCard` cùng các nút hành động ("Tham khảo ý kiến bác sĩ" 48px touch target và "Tôi đã hiểu và tiếp tục").

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
