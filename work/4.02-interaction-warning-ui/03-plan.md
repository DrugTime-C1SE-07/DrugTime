---
task: 4.02-interaction-warning-ui
stage: plan
status: ready_for_review
owner: Duc1445
---

# 4.02 · Kế hoạch kỹ thuật: Warning Screen UI + Mandatory Disclaimer (PB24)

## 1. Giải pháp kỹ thuật

1. **Entities & Enums (`domain/entities/drug_interaction_result.dart`)**:
   - `InteractionSeverity`: 4 cấp độ lâm sàng (`contraindicated`, `severe`, `moderate`, `mild`) tương ứng với nhãn tiếng Việt (`Chống chỉ định`, `Nghiêm trọng`, `Trung bình`, `Nhẹ`), màu sắc và nền theo token hệ thống.
   - `InteractionStatus`: Enum đại diện cho 3 trạng thái kết quả của engine tương tác theo CD06 (`hasInteractions`, `noKnownInteractions`, `insufficientData`).
   - `DrugInteractionPair`: Mô tả một cặp thuốc tương tác gồm tên 2 thuốc, mức độ, cơ chế, khuyến cáo xử trí và nguồn tham chiếu.
   - `DrugInteractionReport`: Chứa trạng thái tổng quát, danh sách tất cả các cặp tương tác, timestamp, và danh sách thuốc thiếu dữ liệu hoạt chất.

2. **Mandatory Disclaimer (`presentation/widgets/mandatory_disclaimer_card.dart`)**:
   - Component hiển thị dòng cảnh báo miễn trừ trách nhiệm y tế chuẩn: *"Lưu ý: Thông tin cảnh báo tương tác thuốc chỉ mang tính chất tham khảo, không thay thế cho chỉ định hoặc tư vấn chuyên môn của bác sĩ/dược sĩ."*
   - Cố định ở chân màn hình, xuất hiện trên 100% màn cảnh báo, TUYỆT ĐỐI không có nút tắt hay thao tác ẩn.

3. **Interaction Pair Card (`presentation/widgets/interaction_pair_card.dart`)**:
   - Component hiển thị cặp thuốc xung đột với badge mức độ nghiêm trọng, cơ chế tương tác, hộp hướng dẫn xử trí lâm sàng và nguồn trích dẫn.

4. **Màn hình cảnh báo (`presentation/screens/drug_interaction_warning_screen.dart`)**:
   - Nhận `DrugInteractionWarningArgs` (hoặc `DrugInteractionReport`).
   - Xử lý 3 trạng thái giao diện:
     - `hasInteractions`: Hiển thị danh sách tất cả các cặp xung đột, không dừng ở cặp đầu tiên.
     - `noKnownInteractions`: Hiển thị câu chữ bắt buộc *"Không tìm thấy tương tác đã biết trong cơ sở dữ liệu hiện tại"*, TUYỆT ĐỐI KHÔNG chứa từ "an toàn" (CD06).
     - `insufficientData`: Hiển thị câu chữ bắt buộc *"Một số thuốc chưa có dữ liệu hoạt chất để kiểm tra tương tác, vui lòng tham khảo ý kiến bác sĩ hoặc dược sĩ."*
   - Khối chân màn hình: `MandatoryDisclaimerCard` và các nút hành động ("Tham khảo ý kiến bác sĩ" và "Tôi đã hiểu và tiếp tục").

5. **Đăng ký Route (`lib/app/router.dart`)**:
   - Thêm `AppRoutes.interactionWarning = '/interaction-warning'`.
   - Kết nối `onGenerateRoute` và màn hình fallback an toàn `_InvalidInteractionWarningRouteScreen`.

---

## 2. Kế hoạch kiểm thử

- **Widget Tests (`test/features/interaction/drug_interaction_warning_screen_test.dart`)**:
  - Test 1: Đảm bảo `MandatoryDisclaimerCard` xuất hiện trên 100% màn hình ở cả 3 trạng thái và không có nút đóng.
  - Test 2: Kiểm tra trạng thái `hasInteractions` hiển thị đầy đủ tất cả các cặp thuốc xung đột và mức độ nghiêm trọng.
  - Test 3: Kiểm tra trạng thái `noKnownInteractions` hiển thị câu chữ bắt buộc và tuyệt đối không chứa từ "an toàn".
  - Test 4: Kiểm tra trạng thái `insufficientData` hiển thị thông báo khuyến cáo hỏi bác sĩ/dược sĩ.
  - Test 5: Kiểm tra điều hướng route `/interaction-warning`.

---

## 3. File sẽ thay đổi

| Submodule | Đường dẫn | Hành động | Mục đích |
|---|---|---|---|
| `frontend` | `mobile/lib/features/interaction/**` | Tạo mới | Domain entities, UI widgets và Warning Screen |
| `frontend` | `mobile/lib/app/router.dart` | Sửa | Đăng ký route `/interaction-warning` và route handler |
| `frontend` | `mobile/test/features/interaction/**` | Tạo mới | Bộ automated widget tests |

