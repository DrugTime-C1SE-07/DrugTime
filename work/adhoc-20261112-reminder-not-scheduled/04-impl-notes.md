---
task: adhoc-20261112-reminder-not-scheduled
stage: implement
owner: Ngọc Việt
started_at: 2026-11-12 22:30
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-13 16:26 +0700
content_hash: sha256:799e77ed366cf960
inputs:
  01-requirement.md: sha256:6b92750b479c1d4b
  03-plan.md: sha256:20d603a93ddf82f9
---

# adhoc-20261112-reminder-not-scheduled · Implement

## 1. Tiến độ

Theo `03-plan.md` bản sửa sau reopen (khảo sát trên frontend `origin/main` @ `f7c2efb4`).

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `flutter test test/core/notification/reminder_sync_coordinator_test.dart test/app/reminder_wiring_test.dart` trước khi sửa → **fail** biên dịch: thiếu `lib/core/notification/reminder_sync_coordinator.dart`, `ReminderSyncCoordinator` không phải type (đúng lý do: chưa có coordinator, app không có điểm gắn) | `evidence/implement-P1.log` |
| P2 | xong | `flutter test test/core/sync/api_schedule_remote_data_source_test.dart` → 4/4 pass | `evidence/implement-P2.log` |
| P3 | xong | `flutter test test/core/notification/reminder_sync_coordinator_test.dart` → 5/5 pass (gồm test hồi quy AC1) | `evidence/implement-P3.log` |
| P4 | xong | `flutter test test/features/medication/medication_controller_test.dart` → 6/6 pass | `evidence/implement-P4.log` |
| P5 | xong | `flutter analyze` 8 file của task → No issues found | `evidence/implement-P5.log` |
| P6 | xong | `flutter test test/app/reminder_wiring_test.dart test/core/notification/reminder_sync_coordinator_test.dart` → 6/6 pass (test hồi quy P1 giờ pass) | `evidence/implement-P6.log` |
| P7 | xong | `flutter test` toàn bộ → 1034 pass, 1 skip, 5 fail; cả 5 fail cũng fail trên `main` sạch (xem mục 3). `flutter analyze` → 3 info ở file có sẵn ngoài task | `evidence/implement-final-frontend.log`, `evidence/implement-analyze.log` |
| P8 | chưa làm (giai đoạn test) | Kiểm thủ công Android 14+ | `evidence/test-device-android14.md` |
| P9 | xong | Test hồi quy H1, M2, L1, M1 trước khi sửa → 7 fail: H1 `not contains <757667183>` (nhắc hoãn bị cancel), M2 vẫn lập lượt 2026-11-12T01:00Z đã ghi nhận, L1 `days_of_week` được nhận / `_TypeError` thay vì `ApiException`, M1 + L2 fail biên dịch (chưa có `NotificationPermissionPlatform`, `requestNotificationsPermission`). L2 không tách riêng được vì cùng file biên dịch lỗi | `evidence/implement-P9.log` |
| P10 | xong | `reminder_sync_coordinator_test` → 7/7 pass | `evidence/implement-P10.log` |
| P11 | xong | `api_schedule_remote_data_source_test` → 7/7 pass | `evidence/implement-P11.log` |
| P12 | xong | `notification_service_test` → 8/8 pass | `evidence/implement-P12.log` |
| P13 | xong | `reminder_wiring_test` → 2/2 pass (M1 thứ tự quyền; L2 sửa thuốc gọi lại `refresh`) | `evidence/implement-P13.log` |
| P14 | xong | `flutter test` toàn bộ → 1042 pass, 1 skip, 5 fail (đúng 5 test có sẵn trên `main`). `flutter analyze` → 3 info ở file có sẵn ngoài task. `scope.py --stage implement` → 11 file của task `[OK]` | `evidence/implement-final-frontend-r2.log`, `evidence/implement-analyze-r2.log`, `evidence/implement-scope-r2.log` |
| P15 | xong | `secure_storage_test` (mới) và 2 test mới trong `reminder_wiring_test` fail biên dịch đúng lý do: chưa có `markReminderPermissionsAsked`, chưa có tham số `shouldAskReminderPermissions` | `evidence/implement-P15.log` |
| P16 | xong | `SecureStorage.markReminderPermissionsAsked()` (khóa `reminder_permissions_asked`); `DrugTimeApp.shouldAskReminderPermissions`; `_activateReminders` tách `_shouldAskPermissions` + `_askReminderPermissions`, lỗi đọc cờ → không hỏi, vẫn `refresh`; `main.dart` truyền `secureStorage.markReminderPermissionsAsked`. 2 file test → 5/5 pass | `evidence/implement-P16.log` |
| P17 | xong | `flutter test` toàn bộ → 1045 pass, 1 skip, 5 fail; chạy lại 4 file fail → đúng 5 test có sẵn trên `main`. `flutter analyze` → 3 info cũ ngoài task. `scope.py` → 13 file của task `[OK]`, `[NGOÀI]` giống lần r2 (`frontend/admin/.test-build/**`, working tree superproject) | `evidence/implement-final-frontend-r3.log`, `evidence/implement-final-frontend-r3-failures.log`, `evidence/implement-scope-r3.log` |

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| frontend | `fix/adhoc-20261112-reminder-not-scheduled` | `mobile/lib/core/sync/api_schedule_remote_data_source.dart` (mới) |
| frontend | ″ | `mobile/lib/core/notification/reminder_sync_coordinator.dart` (mới) |
| frontend | ″ | `mobile/lib/main.dart` |
| frontend | ″ | `mobile/lib/app/app.dart` |
| frontend | ″ | `mobile/lib/features/medication/presentation/state/medication_controller.dart` |
| frontend | ″ | `mobile/test/core/sync/api_schedule_remote_data_source_test.dart` (mới) |
| frontend | ″ | `mobile/test/core/notification/reminder_sync_coordinator_test.dart` (mới) |
| frontend | ″ | `mobile/test/app/reminder_wiring_test.dart` (mới) |
| frontend | ″ | `mobile/test/features/medication/medication_controller_test.dart` |
| frontend | ″ | `mobile/lib/core/notification/notification_service.dart` (lần sửa sau review) |
| frontend | ″ | `mobile/test/core/notification/notification_service_test.dart` (lần sửa sau review) |
| frontend | ″ | `mobile/lib/core/storage/secure_storage.dart` (M3) |
| frontend | ″ | `mobile/test/core/storage/secure_storage_test.dart` (mới, M3) |

Kết quả `python .agents/scripts/scope.py adhoc-20261112-reminder-not-scheduled --stage implement`: 9 file của task đều `[OK]`. Các dòng `[NGOÀI]` là thay đổi có sẵn không thuộc task: `frontend/admin/.test-build/**` (untracked, có từ trước khi bắt đầu) và working tree của superproject (nhánh `feat/5.06-admin-queue-api`, `.specify/`, `graphify-out/`...). Không xử lý vì không phải của task. Log: `evidence/implement-scope.log`

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| frontend | `cd frontend/mobile && flutter test` | 1034 / 5 / 1 | `evidence/implement-final-frontend.log` |
| frontend | `flutter test` 4 file chứa 5 test fail, chạy trên worktree tạm của `origin/main` @ `f7c2efb4` (chưa có thay đổi của task) | cùng 5 test fail | `evidence/implement-baseline-main-failures.log` |
| frontend | `cd frontend/mobile && flutter analyze` | 3 info (`edit_medication_screen.dart`, `reminder_edge_cases_test.dart` ×2), không file nào của task | `evidence/implement-analyze.log` |

5 test fail có sẵn trên `main` (không do task): `app_shell_test` AC16, AC20; `family_link_code_stability_test` mục 4; `family_tab_screen_test` "alert entry displays server unread count…"; `redeem_acceptance_test` AC2.

Test hồi quy: fail trước khi sửa (`evidence/implement-P1.log`), pass sau khi sửa (`evidence/implement-P6.log`).

## 3b. Bộ test case Excel (chỉ task size S)

Làm ở giai đoạn test.

## 4. Migration

Không có.

## 5. Ghi chú cho người review

Truy vết quy tắc → AC → test:

| Quy tắc | AC | Thực hiện | Test |
|---|---|---|---|
| QD-22 (lập trước 7 ngày; bổ sung khi mở app, sửa lịch) | AC1, AC3 | `ReminderSyncCoordinator.refresh` (horizon 7 ngày); gọi khi kích hoạt phiên (`app.dart` `_activateReminders`) và qua `MedicationController.onChanged` | `reminder_sync_coordinator_test` (hồi quy, xóa lịch → hủy nhắc), `reminder_wiring_test`, `medication_controller_test` |
| QD-33 (mất mạng vẫn nhắc cục bộ) | AC1 | Sync lỗi chỉ ghi log, vẫn lập nhắc từ store; kích hoạt nhắc không chờ `_online` | `reminder_sync_coordinator_test` "API fails" |
| QD-26 / NT-02 (màn hình khóa nội dung chung) | AC5 | Không đổi scheduler; test kiểm title mặc định, body không chứa tên thuốc | `reminder_sync_coordinator_test` (hồi quy) |
| Q1 (xin quyền FSI cùng lúc quyền thông báo) | AC4 | `requestFullScreenIntentPermission()` ở `_activateReminders`, chỉ lần đầu sau khi cài app (cờ `reminder_permissions_asked` trong `SecureStorage`, M3) | `reminder_wiring_test`, `secure_storage_test` |
| QD-20 (hoãn cữ) | AC2 | Không đổi (đã đúng trên `main`) | `reminder_notification_scheduler_test` hiện có, chạy lại trong P7 |

Điểm cần xem:

- `main.dart`: bỏ khối quét lịch lúc khởi động (trước đây đọc bảng lịch luôn rỗng). Giờ lập nhắc khi phiên được kích hoạt (cả lúc mở app có phiên lưu sẵn), vì cần `patientId`.
- `app.dart`: dùng biến `_reminderUser` riêng, không gộp với `_tokenSession` (điều kiện FCM yêu cầu `_online` và `blocksRegistration`, không hợp với nhắc thuốc offline).
- `ReminderSyncCoordinator.clear()` chỉ hủy thông báo có payload nhắc thuốc (`NotificationPayload.tryParse` hợp lệ); thông báo người thân giữ nguyên. Gọi trong `beforeSignOut`.
- `onSessionExpired` không hủy nhắc: phiên hết hạn không có nghĩa người dùng đổi; đăng nhập lại sẽ `refresh`.
- `ApiScheduleRemoteDataSource` ném `ApiException` khi item sai định dạng thay vì bỏ qua, để không thay bảng lịch cục bộ bằng danh sách thiếu (`ScheduleSyncService` không ghi khi remote lỗi).
- M3: cờ được ghi ngay khi bắt đầu hỏi, trước khi người dùng trả lời. App bị tắt giữa chừng thì lần sau không hỏi lại; chấp nhận vì người dùng đã thấy hộp thoại. Cờ tính theo máy, đổi tài khoản không hỏi lại.
- Bộ test mới tái sử dụng `MockReminderNotificationPlatform` và `tokenSession` từ test hiện có.

## 6. Phát sinh

**PS4 — M1 dùng interface riêng thay vì thêm method vào `NotificationPlatform` (lệch cách làm ghi ở `03` mục 1b).** `03` ghi thêm `requestNotificationsPermission()` vào `NotificationPlatform` với thân mặc định để không phải sửa fake. Nhưng các fake dùng `implements NotificationPlatform` (không kế thừa thân mặc định), nên cách đó buộc sửa `test/core/notification/reminder_notification_scheduler_test.dart`, file không có trong bảng. Đã làm theo pattern `FamilyNotificationPlatform` có sẵn: interface `NotificationPermissionPlatform` riêng, `DefaultNotificationPlatform` cài đặt, `NotificationService.requestNotificationsPermission()` kiểm `is` rồi gọi, nền tảng không hỗ trợ thì trả `true`. Hành vi và test như plan; chỉ đổi chỗ khai báo, vẫn trong bảng file đã duyệt.

**PS5 — Lần chạy toàn bộ đầu tiên của P14 bị treo vì lỗi biên dịch do agent.** Bỏ phép ép kiểu ở `notification_service.dart` (tưởng biến local tự promote; Dart không promote sang interface không phải subtype). Đã khôi phục, chạy lại toàn bộ; log `implement-final-frontend-r2.log` là lần chạy sau khi sửa.

**PS1 — Phân tích ban đầu làm trên code cũ (đã xử lý).** `01`/`03` bản đầu khảo sát frontend ở `ec755c64` (nhánh `feat/4.15-ocr-manual-search`). `main` đã có commit `a3072bf0` gắn scheduler. Người dùng đã reopen và duyệt lại `plan` theo `main`; implement theo bản đó. `01` mục 3 vẫn ghi nguyên nhân gốc cũ (AC không đổi, không reopen). Bằng chứng: `evidence/implement-rebase-check.log`.

**PS2 — 5 test fail có sẵn trên `main`.** Ngoài phạm vi task; đề xuất mở task riêng.

**PS3 — Rủi ro hành vi xin quyền FSI.** Trên Android 14+, nếu người dùng từ chối, `requestFullScreenIntentPermission()` có thể mở lại màn cài đặt mỗi lần app khởi động với phiên sẵn có (code gọi một lần cho mỗi lần khởi động/đăng nhập, không ghi nhớ đã hỏi). Đã xử lý ở P15–P16 (plan mục 1c): chỉ hỏi lần đầu sau khi cài.

## Bước tiếp theo

- Đang chờ: người duyệt
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261112-reminder-not-scheduled implement`, rồi `gate.py reopen ... test`; giai đoạn test: chạy lại test liên quan, sửa kỳ vọng TC-REMIND-13 (lần đầu hỏi, mở lại không hỏi), thêm test case M3; rồi review lại. Chưa commit.
- Cập nhật lần cuối: 2026-11-13, Claude Code
