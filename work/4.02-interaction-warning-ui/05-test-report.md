---
task: 4.02-interaction-warning-ui
stage: test
status: ready_for_review
owner: Duc1445
---

# 4.02 · Báo cáo kiểm thử: Warning Screen UI + Mandatory Disclaimer (PB24)

## 1. Môi trường kiểm thử

- **Framework**: Flutter 3.47.6 • channel stable, Dart 3.13.5.
- **Hệ điều hành**: Windows 11.
- **Submodule**: `frontend/mobile`.
- **Nhánh**: `feat/4.02-interaction-warning-ui`.
- **Lệnh thực thi**:
  ```bash
  cd frontend/mobile && flutter test test/features/interaction/
  ```
- **File log bằng chứng thô**: [`work/4.02-interaction-warning-ui/evidence/test-interaction-warning-ui.log`](file:///e:/DrugTIme_main/work/4.02-interaction-warning-ui/evidence/test-interaction-warning-ui.log)

---

## 2. Kết quả kiểm thử tự động (Widget Tests)

Toàn bộ **5/5 test cases đều PASSED (100%)**:

```text
00:00 +0: Task 4.02 · Mobile Drug Interaction Warning Screen & Mandatory Disclaimer Test 1: MandatoryDisclaimerCard xuất hiện trên màn hình trong cả 3 trạng thái và không có nút đóng
00:00 +1: Task 4.02 · Mobile Drug Interaction Warning Screen & Mandatory Disclaimer Test 2: Trạng thái hasInteractions hiển thị đầy đủ tất cả các cặp thuốc xung đột và mức độ nghiêm trọng
00:01 +2: Task 4.02 · Mobile Drug Interaction Warning Screen & Mandatory Disclaimer Test 3: noKnownInteractions hiển thị câu chữ bắt buộc và tuyệt đối KHÔNG chứa từ "an toàn"
00:01 +3: Task 4.02 · Mobile Drug Interaction Warning Screen & Mandatory Disclaimer Test 4: insufficientData hiển thị thông báo khuyến cáo hỏi ý kiến bác sĩ/dược sĩ
00:01 +4: Task 4.02 · Mobile Drug Interaction Warning Screen & Mandatory Disclaimer Test 5: Đăng ký route AppRoutes.interactionWarning hoạt động chính xác với router
00:01 +5: All tests passed!
```

---

## 3. Chi tiết kiểm chứng từng tiêu chí nghiệm thu (Acceptance Criteria)

| STT | Kịch bản kiểm thử | Tiêu chí nghiệm thu (AC) | Kết quả | Ghi chú kiểm chứng |
|---|---|---|:---:|---|
| 1 | `MandatoryDisclaimerCard` xuất hiện trên 100% màn cảnh báo ở cả 3 trạng thái, cố định chân màn hình, không nút đóng | **AC1, AC2** | **PASS** | Kiểm tra `find.byType(MandatoryDisclaimerCard)` ở cả 3 trạng thái `hasInteractions`, `noKnownInteractions`, `insufficientData`. Khẳng định không có bất kỳ nút `IconButton` hoặc icon `Icons.close` nào trong card. Nội dung khớp nguyên văn. |
| 2 | Trạng thái `hasInteractions` liệt kê tất cả các cặp xung đột, mức độ nghiêm trọng, cơ chế và hướng dẫn xử trí | **AC3** | **PASS** | Kiểm tra với 3 cặp thuốc khác nhau (`Clopidogrel ⮂ Omeprazole`, `Metformin ⮂ Cimetidine`, `Paracetamol ⮂ Isoniazid`). Hiển thị đủ 3 `InteractionPairCard`, đúng badges (`Nghiêm trọng`, `Trung bình`, `Nhẹ`), và callbacks các nút bấm hoạt động chính xác. |
| 3 | Trạng thái `noKnownInteractions` hiển thị câu chữ bắt buộc và TUYỆT ĐỐI KHÔNG chứa từ "an toàn" (CD06) | **AC4** | **PASS** | Hiển thị nguyên văn *"Không tìm thấy tương tác đã biết trong cơ sở dữ liệu hiện tại"*. Duyệt toàn bộ cây widget qua `tester.widgetList<Text>` và khẳng định 0 widget nào chứa chuỗi "an toàn" hoặc "safe". |
| 4 | Trạng thái `insufficientData` hiển thị thông báo khuyến cáo hỏi ý kiến bác sĩ/dược sĩ | **AC5** | **PASS** | Hiển thị nguyên văn *"Một số thuốc chưa có dữ liệu hoạt chất để kiểm tra tương tác, vui lòng tham khảo ý kiến bác sĩ hoặc dược sĩ."*, đồng thời liệt kê đầy đủ các thuốc chưa có dữ liệu hoạt chất. |
| 5 | Điều hướng qua route `AppRoutes.interactionWarning` trong router của ứng dụng | **AC6** | **PASS** | Mở route `/interaction-warning` qua `Navigator.pushNamed`, giải nén `DrugInteractionReport` và render đúng màn hình cảnh báo. |

---

## 4. Kiểm tra chất lượng tĩnh (Static Analysis)

- Chạy `flutter analyze lib/features/interaction lib/app/router.dart test/features/interaction`:
  ```text
  Analyzing 3 items...
  No issues found! (ran in 55.9s)
  ```
- Không có bất kỳ lỗi cú pháp, cảnh báo deprecation hay cảnh báo format nào.
