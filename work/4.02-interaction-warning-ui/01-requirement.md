---
task: 4.02-interaction-warning-ui
stage: requirement
status: draft
size: M
contract_change: no
owner: Duc1445
---

# 4.02 · Mobile: Warning Screen UI + Mandatory Disclaimer (PB24)

## 1. Mục tiêu và bối cảnh

- **Bối cảnh**: Trong quy trình thêm thuốc mới hoặc khi xem chi tiết danh sách đơn thuốc, ứng dụng DrugTime thực hiện đối soát tương tác thuốc–thuốc để cảnh báo người bệnh và người chăm sóc về các nguy cơ dược lý bất lợi.
- **Mục tiêu**: Xây dựng màn hình cảnh báo tương tác thuốc (`DrugInteractionWarningScreen`) trên ứng dụng di động Flutter với thiết kế trực quan, rõ ràng, tuân thủ nghiêm ngặt bất biến kiến trúc CD06 và tiêu chuẩn bảo đảm chất lượng QA.04.
- **Bất biến kiến trúc bắt buộc (CD06)**: Engine kiểm tra tương tác thuốc là tất định (rule-based), tuyệt đối không suy đoán hay khẳng định một đơn thuốc là "an toàn". Giao diện phải phản ánh chính xác 3 trạng thái kết quả.
- **Tiêu chuẩn bắt buộc (DoD & QA.04)**:
  1. **Mandatory Disclaimer**: Bắt buộc xuất hiện trên 100% màn hình cảnh báo, cố định ở chân màn hình (Bottom Banner/Card), tuyệt đối **không có nút đóng (X) hay ẩn đi được**.
     - Câu chữ chuẩn: *"Lưu ý: Thông tin cảnh báo tương tác thuốc chỉ mang tính chất tham khảo, không thay thế cho chỉ định hoặc tư vấn chuyên môn của bác sĩ/dược sĩ."*
  2. **Phân biệt rõ ràng 3 trạng thái kết quả**:
     - `có_tương_tác` (`hasInteractions`): Liệt kê danh sách tất cả các cặp xung đột (không dừng ở cặp đầu tiên), kèm badge mức độ nghiêm trọng (Chống chỉ định / Nghiêm trọng / Trung bình / Nhẹ) với màu sắc lâm sàng chuẩn, cơ chế và hướng dẫn xử trí.
     - `đã_kiểm_tra_không_thấy` (`noKnownInteractions`): Câu chữ bắt buộc: *"Không tìm thấy tương tác đã biết trong cơ sở dữ liệu hiện tại"* (TUYỆT ĐỐI KHÔNG ghi là "An toàn").
     - `chưa_đủ_dữ_liệu` (`insufficientData`): Hiển thị thông báo: *"Một số thuốc chưa có dữ liệu hoạt chất để kiểm tra tương tác, vui lòng tham khảo ý kiến bác sĩ hoặc dược sĩ."*

---

## 2. Tiêu chí chấp nhận (Acceptance Criteria)

- **AC1 (Mandatory Disclaimer Present)**: Trong 100% màn hình cảnh báo tương tác thuốc (bất kể trạng thái nào), thành phần `MandatoryDisclaimerCard` phải luôn hiển thị ở chân màn hình, không bị che khuất và tuyệt đối không có nút tắt/đóng (`close` button) hay thao tác vuốt để ẩn (`dismiss`).
- **AC2 (Mandatory Disclaimer Exact Text)**: Nội dung thông điệp miễn trừ trách nhiệm y tế phải khớp chính xác: *"Lưu ý: Thông tin cảnh báo tương tác thuốc chỉ mang tính chất tham khảo, không thay thế cho chỉ định hoặc tư vấn chuyên môn của bác sĩ/dược sĩ."*
- **AC3 (Has Interactions State)**: Khi có tương tác (`hasInteractions`), màn hình phải hiển thị toàn bộ các cặp xung đột thuốc (`DrugInteractionPair`), hiển thị rõ ràng tên 2 loại thuốc, mức độ nghiêm trọng (`Chống chỉ định`, `Nghiêm trọng`, `Trung bình`, `Nhẹ`) với badge màu sắc cảnh báo lâm sàng, cơ chế tương tác và khuyến cáo xử trí.
- **AC4 (No Known Interactions State - Invariant CD06)**: Khi không phát hiện tương tác (`noKnownInteractions`), màn hình phải hiển thị câu chữ nguyên văn: *"Không tìm thấy tương tác đã biết trong cơ sở dữ liệu hiện tại"*. Tuyệt đối không chứa từ "an toàn" (safe) trong toàn bộ giao diện của trạng thái này.
- **AC5 (Insufficient Data State)**: Khi chưa đủ dữ liệu hoạt chất (`insufficientData`), màn hình hiển thị cảnh báo: *"Một số thuốc chưa có dữ liệu hoạt chất để kiểm tra tương tác, vui lòng tham khảo ý kiến bác sĩ hoặc dược sĩ."*, đồng thời liệt kê các thuốc chưa có dữ liệu nếu có.
- **AC6 (Navigation & Actions)**: Đăng ký route `/interaction-warning` trong router của ứng dụng, hỗ trợ điều hướng với argument `DrugInteractionReport` hoặc `DrugInteractionWarningArgs`, cung cấp các nút hành động "Tôi đã hiểu và tiếp tục" và "Tham khảo ý kiến bác sĩ".

---

## 3. Phân loại và Phạm vi

- **Phân loại Task**: Size M.
  - Lý do: Task thuộc submodule `frontend`, không đổi API contract, nhưng liên quan trực tiếp đến cảnh báo an toàn dùng thuốc và bất biến kiến trúc CD06 (luật 3 trạng thái kết quả).
- **Submodule ảnh hưởng**: `frontend` (`frontend/mobile`).
- **File sẽ thay đổi**:

| Đường dẫn file | Mục đích thay đổi |
|---|---|
| `frontend/mobile/lib/features/interaction/domain/entities/drug_interaction_result.dart` | Định nghĩa entities `DrugInteractionPair`, `DrugInteractionReport`, các enums `InteractionSeverity` và `InteractionStatus` |
| `frontend/mobile/lib/features/interaction/presentation/widgets/mandatory_disclaimer_card.dart` | Component Disclaimer Card bắt buộc ở chân màn hình |
| `frontend/mobile/lib/features/interaction/presentation/widgets/interaction_pair_card.dart` | Card hiển thị từng cặp tương tác thuốc kèm badge mức độ |
| `frontend/mobile/lib/features/interaction/presentation/screens/drug_interaction_warning_screen.dart` | Màn hình chính xử lý 3 trạng thái tương tác thuốc |
| `frontend/mobile/lib/app/router.dart` | Đăng ký route `/interaction-warning` và route handler |
| `frontend/mobile/test/features/interaction/drug_interaction_warning_screen_test.dart` | Bộ widget tests kiểm thử 4 kịch bản nghiệm thu |
