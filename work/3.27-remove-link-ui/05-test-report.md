---
task: 3.27-remove-link-ui
stage: test
owner: DrugTime Team
started_at: 2026-10-24 07:40
completed_at: 2026-10-24 07:45
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-24 08:01 +0700
content_hash: sha256:77d291a3a6ccbb9a
inputs:
  01-requirement.md: sha256:7b1b722a6068e75c
  03-plan.md: sha256:023a89daa93d8110
  04-impl-notes.md: sha256:bf7d72957192be60
---

# 3.27-remove-link-ui · Test tích hợp

## 1. Môi trường

- Flutter SDK: `C:\Users\Admin\develop\flutter\bin\flutter.bat` (Flutter 3.47.6, Dart 3.13.5).
- Nhánh `frontend`: `feat/3.27-remove-link-ui`.
- Nhánh `docs`: `feat/3.27-remove-link-ui`.
- Bảng test case tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Nội dung tiêu chí | Test tự động xác minh | Kết quả | Log bằng chứng |
|---|---|---|---|---|
| **AC1** | Patient xem danh sách người thân đã liên kết trên CaregiversScreen, mỗi người có nút "Gỡ liên kết" | `test/features/family_link/caregivers_screen_test.dart` | Pass | `evidence/implement-P2.log` |
| **AC2** | Nhấn "Gỡ liên kết" hiển thị dialog xác nhận cảnh báo mất quyền xem ngay lập tức; bấm "Hủy" không gọi API và giữ nguyên danh sách | `test/features/family_link/caregivers_screen_test.dart` | Pass | `evidence/implement-P2.log` |
| **AC3** | Xác nhận gỡ liên kết gọi đúng `DELETE /family/links/{id}` (204 No Content), gỡ khỏi UI và hiện SnackBar thành công | `test/features/family_link/remote_caregiver_repository_test.dart`, `caregivers_screen_test.dart` | Pass | `evidence/implement-P1.log`, `evidence/implement-P2.log` |
| **AC4** | Khi API thất bại: giữ nguyên danh sách, hiển thị thông báo lỗi và cho phép thử lại | `test/features/family_link/caregivers_screen_test.dart` | Pass | `evidence/implement-P2.log` |
| **AC5** | Ngăn bấm trùng lặp (loading spinner khi busy); xử lý an toàn khi liên kết đã bị gỡ từ trước (idempotent / reload) | `test/features/family_link/caregivers_screen_test.dart` | Pass | `evidence/implement-P2.log` |
| **AC6** | Family Member gặp 403 Forbidden: xóa Patient khỏi state cục bộ, dọn sạch SQLite cache (`clearPatientData`), xóa history trên RAM (`history = null`), và đồng bộ lại UI | `test/features/family_link/linked_patients_controller_test.dart`, `test/features/adherence/adherence_controller_test.dart` | Pass | `evidence/implement-P5.log`, `evidence/implement-P6.log` |
| **AC7** | Đồng bộ danh sách mới: tự động xác định các Patient bị gỡ, xóa khỏi state hiển thị và dọn sạch SQLite cache + alerts tương ứng | `test/features/family_link/linked_patients_controller_test.dart` | Pass | `evidence/implement-P5.log` |
| **AC8** | Độc lập dữ liệu giữa các bệnh nhân: gỡ Patient A không ảnh hưởng dữ liệu SQLite hay alerts của Patient B | `test/core/storage/local_medication_store_test.dart`, `test/features/family_link/linked_patients_controller_test.dart` | Pass | `evidence/implement-P3.log`, `evidence/implement-P5.log` |
| **AC9** | Xử lý an toàn khi nhiều request đồng thời cùng phát hiện quyền bị thu hồi hoặc gọi lặp lại: không crash, không race condition | `test/features/family_link/linked_patients_controller_test.dart` | Pass | `evidence/implement-P5.log` |

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Quy tắc | Test tự động | Kết quả |
|---|---|---|---|
| **Thu hồi quyền truy cập dữ liệu sức khỏe** | QD-29 | `test_linked_patients_controller_handles_revocation_403`, `test_adherence_controller_denied_clears_history_and_calls_hook` | Pass (SQLite cache & RAM history xóa ngay lập tức) |
| **Xác nhận gỡ liên kết rõ ràng** | QD-30 | `test_caregivers_screen_renders_remove_link_button`, `test_caregivers_screen_cancel_dialog_does_not_call_api`, `test_caregivers_screen_confirm_dialog_calls_revoke_and_shows_success` | Pass (Dialog cảnh báo rõ ràng, hủy không gọi API, xác nhận gọi DELETE 204) |
| **Fail-closed & không cache phân quyền** | CD2, CD4 | `test_adherence_controller_denied_clears_history_and_calls_hook`, `test_remote_caregiver_repository_revoke_delete_204` | Pass (403 denied kích hoạt xóa cache và khóa truy cập lập tức) |
| **Cách ly dữ liệu bệnh nhân** | Vùng rủi ro | `test_sqlite_local_medication_store_clear_patient_data`, `test_family_alert_controller_remove_patient` | Pass (Chỉ xóa bản ghi có `patient_user_id` khớp, không chạm bệnh nhân khác) |
| **An toàn đồng thời & Idempotent** | QA.03 | `test_linked_patients_controller_concurrent_revocation_safety`, `test_caregivers_screen_idempotent_revoke_reloads_list` | Pass (Khóa `_busy` và `_processingRevocations` chống race condition) |

## 4. Toàn bộ bộ test

- Lệnh chạy:
  ```powershell
  cd frontend/mobile
  & "C:\Users\Admin\develop\flutter\bin\flutter.bat" test test/features/family_link/remote_caregiver_repository_test.dart test/features/family_link/caregivers_screen_test.dart test/core/storage/local_medication_store_test.dart test/features/family_link/linked_patients_controller_test.dart test/features/adherence/adherence_controller_test.dart
  ```
- Kết quả: **49 passed, 0 failed, 0 skipped** (100% pass, thời gian chạy ~4s).
- Phân tích tĩnh (`flutter analyze`): **0 issues found**.
- Log chi tiết: `evidence/implement-final-frontend.log`.
- `scope.py`:
  - Giai đoạn implement: `python .agents/scripts/scope.py 3.27-remove-link-ui --stage implement` -> `OK: mọi thay đổi nằm trong phạm vi` (log: `evidence/implement-scope.log`).
  - Giai đoạn test: Chỉnh sửa duy nhất file `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (vai trò `testcase-book` -> `[OK]`).

## 5. Bộ test case Excel

Thực hiện theo skill `wf-testcase`:
- Spec: `work/3.27-remove-link-ui/testcases.json`
- File task: `work/3.27-remove-link-ui/testcases.xlsx`
- File tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`
- Log merge: `evidence/testcase-xlsx.log`

| Chức năng (mã) | Sheet Name | Tổng | Pass | Fail | Pending | Ghi chú |
|---|---|---|---|---|---|---|
| **Quản lý người giám sát (CAREGIVER)** | `Người giám sát` | 36 | 35 | 0 | 1 | Cập nhật TC-CAREGIVER-24 theo UI mới và bổ sung TC-CAREGIVER-29 -> TC-CAREGIVER-36 phủ toàn bộ AC1–AC9. |

- **Test case Pending cần người chạy**:
  - `TC-CAREGIVER-28`: Bật/tắt chia sẻ và hủy liên kết thật trên hai thiết bị vật lý đồng thời (chạy kiểm thử thủ công trên thiết bị thật trước khi phát hành production).
- **Bug đã ghi vào Bug Report**: Không có (0 bug).

## 5b. Lỗi sản phẩm tìm thấy

Không có.

## 6. Test không ổn định hoặc bị skip

Không có.

## 7. Phát sinh

- `scope.py --stage test` đối chiếu toàn bộ working directory và commit trên nhánh task so với `origin/main`. Vì các file frontend của giai đoạn `implement` đang ở working tree và chưa commit (tuân thủ quy tắc không tự ý commit khi người dùng chưa yêu cầu), `scope.py --stage test` liệt kê chúng là `[NGOÀI]` do giai đoạn `test` chỉ quy định vùng `integration-test` và `testcase-book`. Toàn bộ 11 file frontend đã được xác thực `[OK]` 100% bằng `scope.py --stage implement`. File duy nhất được chỉnh sửa trong giai đoạn test là `Test_Cases.xlsx` (`testcase-book` - `[OK]`).

## Bước tiếp theo

- Đang chờ: Người duyệt xem xét và phê duyệt `05-test-report.md`.
- Việc cần làm: Người duyệt chạy lệnh duyệt trong terminal của mình:
  ```bash
  python .agents/scripts/gate.py approve 3.27-remove-link-ui test
  ```
- Cập nhật lần cuối: 2026-10-24 07:45 +0700, Antigravity
