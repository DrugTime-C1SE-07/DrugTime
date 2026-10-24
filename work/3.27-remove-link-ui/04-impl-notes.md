---
task: 3.27-remove-link-ui
stage: implement
owner: DrugTime Team
started_at: 2026-10-23 15:35
completed_at: 2026-10-23 15:52
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-23 15:57 +0700
content_hash: sha256:bf7d72957192be60
inputs:
  01-requirement.md: sha256:7b1b722a6068e75c
  03-plan.md: sha256:023a89daa93d8110
---

# 3.27-remove-link-ui · Implement

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `flutter test test/features/family_link/remote_caregiver_repository_test.dart` (22/22 pass) | `evidence/implement-P1.log` |
| P2 | xong | `flutter test test/features/family_link/caregivers_screen_test.dart` (15/15 pass) | `evidence/implement-P2.log` |
| P3 | xong | `flutter test test/core/storage/local_medication_store_test.dart` (2/2 pass) | `evidence/implement-P3.log` |
| P4 | xong | `flutter test test/features/family/family_alert_controller_test.dart` (6/6 pass) | `evidence/implement-P4.log` |
| P5 | xong | `flutter test test/features/family_link/linked_patients_controller_test.dart` (5/5 pass) | `evidence/implement-P5.log` |
| P6 | xong | `flutter test test/features/adherence/adherence_controller_test.dart` (5/5 pass) | `evidence/implement-P6.log` |
| P7 | xong | `flutter test ...` toàn bộ 5 test suite liên quan (49/49 pass 100%) | `evidence/implement-final-frontend.log` |

## 2. File đã thay đổi

| Submodule | Nhánh | File | Mô tả |
|---|---|---|---|
| `frontend` | `feat/3.27-remove-link-ui` | `mobile/lib/features/family_link/data/repositories/remote_caregiver_repository.dart` | Chuyển `revoke` sang gọi `DELETE /family/links/{id}` (HTTP 204) |
| `frontend` | `feat/3.27-remove-link-ui` | `mobile/lib/features/family_link/presentation/screens/caregivers_screen.dart` | Cập nhật nhãn "Gỡ liên kết", hộp thoại cảnh báo mất quyền, loading spinner và SnackBar |
| `frontend` | `feat/3.27-remove-link-ui` | `mobile/lib/core/storage/local_db/local_medication_store.dart` | Bổ sung `clearPatientData(patientId)` trong interface (kèm default impl) và `SqliteLocalMedicationStore` |
| `frontend` | `feat/3.27-remove-link-ui` | `mobile/lib/features/family/presentation/state/family_alert_controller.dart` | Bổ sung `removePatient(patientId)` dọn sạch alert của patient bị gỡ và reset detail nếu đang mở |
| `frontend` | `feat/3.27-remove-link-ui` | `mobile/lib/features/family_link/presentation/state/linked_patients_controller.dart` | Controller điều phối danh sách patient của Family Member, xử lý 403 và đồng bộ danh sách mới |
| `frontend` | `feat/3.27-remove-link-ui` | `mobile/lib/features/adherence/presentation/state/adherence_controller.dart` | Bổ sung hook `onPatientRevoked`, xóa RAM (`history = null`) khi gặp 403 denied |
| `frontend` | `feat/3.27-remove-link-ui` | `mobile/test/features/family_link/remote_caregiver_repository_test.dart` | Test `revoke` gửi đúng DELETE 204, xử lý mã lỗi |
| `frontend` | `feat/3.27-remove-link-ui` | `mobile/test/features/family_link/caregivers_screen_test.dart` | Widget test xác nhận dialog cảnh báo, hủy không gọi API, xác nhận gọi API, loading, reload khi lỗi |
| `frontend` | `feat/3.27-remove-link-ui` | `mobile/test/core/storage/local_medication_store_test.dart` | Test `clearPatientData` xóa schedules của đúng patient trong SQLite, cô lập bệnh nhân khác |
| `frontend` | `feat/3.27-remove-link-ui` | `mobile/test/features/family_link/linked_patients_controller_test.dart` | Test điều phối thu hồi quyền 403, đồng bộ danh sách mới, an toàn đồng thời và dọn alert |
| `frontend` | `feat/3.27-remove-link-ui` | `mobile/test/features/adherence/adherence_controller_test.dart` | Test 403 denied kích hoạt `onPatientRevoked` và xóa history |

Kết quả `python .agents/scripts/scope.py 3.27-remove-link-ui --stage implement`:
```
Phạm vi giai đoạn 'implement' của 3.27-remove-link-ui:
  [OK]        frontend/mobile/lib/core/storage/local_db/local_medication_store.dart
  [OK]        frontend/mobile/lib/features/adherence/presentation/state/adherence_controller.dart
  [OK]        frontend/mobile/lib/features/family/presentation/state/family_alert_controller.dart
  [OK]        frontend/mobile/lib/features/family_link/data/repositories/remote_caregiver_repository.dart
  [OK]        frontend/mobile/lib/features/family_link/presentation/screens/caregivers_screen.dart
  [OK]        frontend/mobile/lib/features/family_link/presentation/state/linked_patients_controller.dart
  [OK]        frontend/mobile/test/core/storage/local_medication_store_test.dart
  [OK]        frontend/mobile/test/features/adherence/adherence_controller_test.dart
  [OK]        frontend/mobile/test/features/family_link/caregivers_screen_test.dart
  [OK]        frontend/mobile/test/features/family_link/linked_patients_controller_test.dart
  [OK]        frontend/mobile/test/features/family_link/remote_caregiver_repository_test.dart
OK: mọi thay đổi nằm trong phạm vi.
```
Log chi tiết: `evidence/implement-scope.log`.

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| `frontend` | `flutter test test/features/family_link/remote_caregiver_repository_test.dart test/features/family_link/caregivers_screen_test.dart test/core/storage/local_medication_store_test.dart test/features/family_link/linked_patients_controller_test.dart test/features/adherence/adherence_controller_test.dart` | 49 passed, 0 failed, 0 skipped (100% pass) | `evidence/implement-final-frontend.log` |

## 3b. Bộ test case Excel (chỉ task size S)

Làm ở giai đoạn test (task size M).

## 4. Migration

Không có.

## 5. Ghi chú cho người review

- **API Base URL**: Sử dụng `_api.delete('/family/links/$linkId')` ánh xạ chính xác đến endpoint backend `DELETE /family/links/{id}` (trả về 204 No Content).
- **Tương thích ngược**: Interface `LocalMedicationStore` có default implementation `clearPatientData(String patientId) async {}` giúp mọi mock/fake store hiện có không bị lỗi biên dịch.
- **Tính cô lập**: Các thao tác xóa trong SQLite và `FamilyAlertController` luôn kèm `WHERE patient_user_id = ?` và `patientId == value`, bảo toàn tuyệt đối dữ liệu của bệnh nhân khác.
- **An toàn đồng thời**: `LinkedPatientsController` sử dụng tập hợp `_processingRevocations` để khóa và bảo vệ luồng thu hồi quyền khi nhiều request 403 cùng diễn ra đồng thời.
- **Flutter SDK**: Chạy bằng binary `C:\Users\Admin\develop\flutter\bin\flutter.bat`.

## 6. Phát sinh

Không có.

## Bước tiếp theo

- Đang chờ: Người duyệt xem xét kết quả giai đoạn `implement` và duyệt `04-impl-notes.md`.
- Việc cần làm: Người duyệt chạy lệnh duyệt trong terminal:
  ```bash
  python .agents/scripts/gate.py approve 3.27-remove-link-ui implement
  ```
- Cập nhật lần cuối: 2026-10-23 15:52 +0700, Antigravity
