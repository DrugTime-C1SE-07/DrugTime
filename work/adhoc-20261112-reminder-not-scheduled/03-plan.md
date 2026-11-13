---
task: adhoc-20261112-reminder-not-scheduled
stage: plan
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-13 16:20 +0700
content_hash: sha256:20d603a93ddf82f9
inputs:
  01-requirement.md: sha256:6b92750b479c1d4b
---

# adhoc-20261112-reminder-not-scheduled · Plan

> Bản sửa sau khi reopen (PS1 trong `04-impl-notes.md`): khảo sát lại trên frontend `origin/main` @ `f7c2efb4`, nhánh `fix/adhoc-20261112-reminder-not-scheduled`. Bản trước khảo sát nhầm trên `ec755c64` (nhánh `feat/4.15-ocr-manual-search`).

## 1. Giải pháp

Trên `main`, commit `a3072bf0` (task 2.07, 2.24) đã khởi tạo `ReminderNotificationScheduler`, dùng chung một `SqliteLocalMedicationStore`, truyền `reminderScheduler` và `localMedicationStore` vào app, và lúc khởi động quét `getActiveSchedules()` → `generateOccurrences(now, now+7d)` → `scheduleOccurrences` (`lib/main.dart:69-98`). Hoãn cữ và bấm thông báo đã có đường chạy.

**Nguyên nhân gốc trên `main`:** bảng lịch cục bộ không bao giờ được ghi. Không có lớp nào implement `ScheduleRemoteDataSource`; `ScheduleSyncService.syncSchedulesFromServer` và `LocalMedicationStore.replaceSchedules` không có nơi gọi trong `lib/`. Vì vậy `activeSchedules.isNotEmpty` (`main.dart:86`) luôn sai và không có nhắc nào được lên lịch.

**Thiếu thêm:** không xin quyền full-screen intent (AC4); chỉ lên lịch một lần lúc khởi động app, trước khi biết phiên đăng nhập, nên sửa thuốc không lên lịch lại (AC3); đăng xuất không hủy nhắc.

Luồng sau khi sửa:

```
kích hoạt phiên (đăng nhập / mở app có phiên, app.dart:180-194)
  → requestFullScreenIntentPermission()                     (Q1: cùng lúc xin quyền thông báo)
  → ReminderSyncCoordinator.refresh(session.userId)
sửa thuốc thành công (MedicationController._mutate)
  → ReminderSyncCoordinator.refresh(userId)

refresh(patientId):
  ScheduleSyncService.syncSchedulesFromServer(patientId)     (GET /patients/{id}/schedules, đi hết next_cursor)
    lỗi mạng/API → ghi log, dùng lịch cục bộ cũ (QD-33)
  LocalMedicationStore.getActiveSchedules(patientId)          (đã lọc reminder_enabled = 1, ended_at IS NULL)
  hủy mọi nhắc thuốc đang chờ (pending có payload nhắc thuốc)
  generateOccurrences(from: now, to: now + 7 ngày)            (QD-22)
  ReminderNotificationScheduler.scheduleOccurrences(...)      (fullScreenIntent: true, trần 64 trên iOS đã có)

đăng xuất (beforeSignOut) → ReminderSyncCoordinator.clear()
```

Thành phần:

- **Mới** `ApiScheduleRemoteDataSource` (`lib/core/sync/`): implement `ScheduleRemoteDataSource`, map `items[]` sang `LocalMedicationSchedule` (`medication.name/strength_text/dosage_form` → trường phẳng; `quantity_per_dose` số → chuỗi; `patientUserId` = `patientId`; `serverSyncedAt` = now UTC). Endpoint có sẵn trong contract và đã qua PEP ở backend.
- **Mới** `ReminderSyncCoordinator` (`lib/core/notification/`): ghép các bước trên; các lần `refresh` chạy tuần tự, không chồng nhau.
- **Sửa** `main.dart`: tạo `ScheduleSyncService` + coordinator, truyền coordinator vào `DrugTimeApp`; **bỏ** khối quét lúc khởi động `main.dart:82-98` (chuyển vào `refresh` khi kích hoạt phiên, để biết `patientId`); `beforeSignOut` gọi `clear()`.
- **Sửa** `app.dart`: nhận `reminderSyncCoordinator`; tại điểm kích hoạt phiên gọi xin quyền FSI + `refresh`; truyền `onChanged` vào `MedicationController` (`app.dart:265`).
- **Sửa** `MedicationController`: tham số tùy chọn `onChanged`, gọi sau `_mutate` thành công.

Cách bị loại: giữ khối quét lúc khởi động và chỉ thêm sync trước nó — lúc đó chưa có phiên/`patientId`, và không phủ AC3 hay đăng xuất.

Bất biến: (1) chỉ gọi Backend API; (4) không cache phân quyền, mỗi `refresh` gọi lại API; (5) không đụng outbox hay upsert liều; (7) generator/scheduler cố định `Asia/Ho_Chi_Minh`. QD-26/NT-02: thông báo dùng `defaultTitle`/`defaultBody`, không tên thuốc.

### Quyết định nghiệp vụ áp dụng

Nguồn: `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` §6.1.

| Quy tắc | Trạng thái | AC | Bước | Test |
|---|---|---|---|---|
| QD-22: lập trước nhắc gần nhất, mục tiêu 7 ngày; bổ sung khi mở app, sửa lịch | ✅ | AC1, AC3 | P1, P3, P4, P6 | `reminder_sync_coordinator_test`, `medication_controller_test` |
| QD-21: gom thuốc cùng giờ, mở danh sách xác nhận từng thuốc | ✅ | AC5 | P8 | Thủ công (đã có ở `main`, không đổi) |
| QD-26 / NT-02: màn hình khóa chỉ nội dung chung | ✅ | AC5 | P8 | Thủ công; scheduler không đổi |
| QD-20: nhắc lại / hoãn cữ | ✅ | AC2 | P1, P7 | `reminder_notification_scheduler_test` hiện có (đã đúng trên `main`) |
| QD-33: mất mạng app vẫn nhắc cục bộ | ✅ | AC1 | P3 | `reminder_sync_coordinator_test` (API lỗi) |

### 1b. Sửa theo review (`06-review.md`, reopen ngày 2026-11-13)

Phạm vi lần sửa này: H1, M1, M2, L1, L2. **M3** (xin quyền FSI mỗi lần khởi động) để lại; đã sửa ở mục 1c.

- **H1 — giữ nhắc hoãn cữ khi `refresh`.** `refresh` chỉ hủy pending có `payload.scheduledAt >= now` (lượt tương lai, sẽ được sinh lại ngay sau đó). Pending có `scheduledAt < now` là nhắc hoãn cữ (scheduler giữ `scheduledAt` gốc trong payload, `reminder_notification_scheduler.dart:139-150`) nên giữ nguyên. `clear()` (đăng xuất) vẫn hủy mọi nhắc thuốc.
- **M1 — xin quyền thông báo độc lập với FCM.** Thêm `requestNotificationsPermission()` vào `NotificationPlatform` (mặc định `true` như `requestFullScreenIntentPermission`, để các fake hiện có không phải sửa), cài đặt ở `DefaultNotificationPlatform` qua `AndroidFlutterLocalNotificationsPlugin.requestNotificationsPermission()`, và hàm bọc ở `NotificationService`. `_activateReminders` gọi quyền thông báo trước, rồi quyền toàn màn hình (Q1: cùng lúc). Lỗi chỉ ghi log, không chặn lập nhắc.
- **M2 — không lập nhắc cho liều đã ghi nhận.** Sau `generateOccurrences`, bỏ lượt mà `LocalMedicationStore.hasDoseLog(medicationScheduleId, scheduledAt)` trả `true` (QD-21: hủy nhắc riêng liều đã xử lý).
- **L1 — lỗi kiểu dữ liệu thành `ApiException`.** `strength_text`, `dosage_form` kiểm bằng pattern (`String?`); `days_of_week` kiểm từng phần tử là `int`; sai kiểu thì ném `ApiException('Invalid schedule item')`.
- **L2 — test mức app cho sửa thuốc.** Widget test: phiên A đang hoạt động, gọi thao tác ghi thuốc qua `MedicationController` của app → `refresh('A')` được gọi lần nữa.

### 1c. Sửa M3 — chỉ xin quyền một lần sau khi cài (reopen lần 3, 2026-11-13)

Người dùng quyết định: chỉ xin quyền thông báo và toàn màn hình ở lần đăng nhập đầu tiên sau khi cài app; các lần mở app sau không hỏi lại.

- `SecureStorage` (đã có, `lib/core/storage/secure_storage.dart`) thêm `Future<bool> markReminderPermissionsAsked()`: đọc khóa `reminder_permissions_asked`; chưa có thì ghi `'1'` và trả `true`, có rồi thì trả `false`. Gỡ app thì Android xóa dữ liệu app nên cờ mất, cài lại sẽ hỏi lại một lần.
- `DrugTimeApp` nhận tham số tùy chọn `Future<bool> Function()? shouldAskReminderPermissions`. `_activateReminders` chỉ gọi hai hàm xin quyền khi hàm này trả `true` (không truyền thì giữ hành vi cũ: luôn hỏi). Lỗi đọc/ghi cờ chỉ ghi log và coi như không hỏi; `refresh(userId)` luôn chạy.
- `main.dart` truyền `secureStorage.markReminderPermissionsAsked`.
- Cờ tính theo máy, không theo tài khoản: đổi tài khoản không hỏi lại. Người dùng từ chối ở lần đầu thì phải tự bật trong Cài đặt Android (nút dẫn tới cài đặt nằm ngoài phạm vi).

Cách bị loại: lưu cờ trong bảng meta SQLite — phải đợi mở DB mã hóa và trộn cờ cấu hình máy vào dữ liệu thuốc; `shared_preferences` — thêm dependency trong khi `flutter_secure_storage` đã có.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `frontend/mobile/lib/main.dart:65-98, 146-150, 174-176` | Scheduler, store dùng chung, truyền vào app đã có; khối quét lúc khởi động đọc bảng lịch rỗng; `beforeSignOut` chưa hủy nhắc |
| `frontend/mobile/lib/core/sync/schedule_sync_service.dart` | `syncSchedulesFromServer({patientId})` → `replaceSchedules` + `setMeta`; không có implement data source, không nơi gọi |
| `frontend/mobile/test/core/sync/schedule_sync_service_test.dart` | Đã có test cho service; không cần sửa |
| `frontend/mobile/lib/core/storage/local_db/local_medication_store.dart:60,100-110` | `replaceSchedules`; `getActiveSchedules({String? patientId})` lọc `reminder_enabled = 1 AND ended_at IS NULL` |
| `frontend/mobile/lib/core/notification/reminder_notification_scheduler.dart:25-33,70,85,188,208` | `scheduleOccurrences` có trần 64 trên iOS; `cancelOccurrence`, `cancelAllForSchedule` |
| `frontend/mobile/lib/core/notification/notification_service.dart:36,146,238` | `pendingNotificationRequests`; `requestFullScreenIntentPermission` không nơi gọi |
| `frontend/mobile/lib/app/app.dart:180-194, 265-268, 349-372` | Điểm kích hoạt phiên; khởi tạo `MedicationController`; xử lý bấm thông báo dùng `localMedicationStore` |
| `frontend/mobile/lib/features/medication/presentation/state/medication_controller.dart` | Constructor có tham số tùy chọn `interactionCheckRepository`; `_mutate` là điểm chung sau add/update/setStopped/delete |
| `api_contract/openapi.json` `GET /patients/{patient_id}/schedules` | `items[]` đủ trường bắt buộc (`medication` gồm `id, name, active_ingredient, strength_text, dosage_form`), `next_cursor`; query `limit`, `cursor` |

## 3. File sẽ thay đổi (ranh giới phạm vi)

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | `mobile/lib/core/sync/api_schedule_remote_data_source.dart` | Thêm | Gọi `GET /patients/{id}/schedules`, phân trang, map sang `LocalMedicationSchedule` |
| frontend | `mobile/lib/core/notification/reminder_sync_coordinator.dart` | Thêm | Đồng bộ lịch → hủy cũ → sinh lượt → lên lịch; `clear()` khi đăng xuất |
| frontend | `mobile/lib/main.dart` | Sửa | Tạo sync service + coordinator, bỏ khối quét lúc khởi động, `clear()` khi đăng xuất |
| frontend | `mobile/lib/app/app.dart` | Sửa | Nhận coordinator; xin quyền FSI và `refresh` khi kích hoạt phiên; `onChanged` cho `MedicationController` |
| frontend | `mobile/lib/features/medication/presentation/state/medication_controller.dart` | Sửa | Tham số `onChanged` gọi sau khi ghi thành công |
| frontend | `mobile/test/core/sync/api_schedule_remote_data_source_test.dart` | Thêm | Unit test map và phân trang |
| frontend | `mobile/test/core/notification/reminder_sync_coordinator_test.dart` | Thêm | Test hồi quy AC1; AC3; API lỗi; `clear()` |
| frontend | `mobile/test/app/reminder_wiring_test.dart` | Thêm | Kích hoạt phiên gọi xin quyền FSI và `refresh` (AC4, AC1) |
| frontend | `mobile/test/features/medication/medication_controller_test.dart` | Sửa | `onChanged` gọi khi thành công, không gọi khi lỗi |
| frontend | `mobile/lib/core/notification/notification_service.dart` | Sửa | M1: `requestNotificationsPermission()` ở `NotificationPlatform`, `DefaultNotificationPlatform`, `NotificationService` |
| frontend | `mobile/test/core/notification/notification_service_test.dart` | Sửa | M1: `NotificationService.requestNotificationsPermission()` chuyển tiếp tới platform |
| frontend | `mobile/lib/core/storage/secure_storage.dart` | Sửa | M3: `markReminderPermissionsAsked()` |
| frontend | `mobile/test/core/storage/secure_storage_test.dart` | Thêm | M3: lần đầu `true`, lần sau `false` |

## 4. Checklist

- [ ] P1 [frontend] Viết test hồi quy: (a) `reminder_sync_coordinator_test` — "refresh với API trả 1 lịch tương lai thì `zonedSchedule` được gọi với `fullScreenIntent: true`, channel `drugtime_reminder_channel`"; (b) `reminder_wiring_test` — "kích hoạt phiên gọi `refresh(userId)` và `requestFullScreenIntentPermission`". Xác nhận fail trên code hiện tại (coordinator chưa có; app không gọi gì khi kích hoạt phiên) — file: `mobile/test/core/notification/reminder_sync_coordinator_test.dart`, `mobile/test/app/reminder_wiring_test.dart` — AC: AC1, AC4 — xong khi: hai file fail đúng lý do, log `evidence/implement-P1.log`
- [ ] P2 [frontend] Viết `ApiScheduleRemoteDataSource` + test: map đủ trường, `quantity_per_dose` số → chuỗi, `ended_at` null, đi hết `next_cursor`, lỗi API ném ra (không nuốt) — file: `mobile/lib/core/sync/api_schedule_remote_data_source.dart`, `mobile/test/core/sync/api_schedule_remote_data_source_test.dart` — AC: AC1 — xong khi: test pass, log `evidence/implement-P2.log`
- [ ] P3 [frontend] Viết `ReminderSyncCoordinator`: `refresh(patientId)` theo luồng mục 1, các lần gọi chạy tuần tự; sync lỗi thì ghi log và vẫn lên lịch từ dữ liệu cục bộ; `clear()` chỉ hủy pending có payload nhắc thuốc (không đụng thông báo family) — file: `mobile/lib/core/notification/reminder_sync_coordinator.dart` — AC: AC1, AC3 — xong khi: test P1(a) pass, thêm test AC3 (lịch bị xóa → nhắc cũ bị hủy), test API lỗi, test `clear()` pass; log `evidence/implement-P3.log`
- [ ] P4 [frontend] `MedicationController` nhận `onChanged`, gọi sau `_mutate` thành công — file: `mobile/lib/features/medication/presentation/state/medication_controller.dart`, `mobile/test/features/medication/medication_controller_test.dart` — AC: AC3 — xong khi: test gọi khi thành công, không gọi khi repository ném lỗi; log `evidence/implement-P4.log`
- [ ] P5 [frontend] `main.dart`: tạo `ScheduleSyncService(remoteDataSource: ApiScheduleRemoteDataSource(apiClient), localStore: localStore)` và `ReminderSyncCoordinator`; bỏ khối `main.dart:82-98`; truyền coordinator vào `DrugTimeApp`; `beforeSignOut` gọi `clear()` — file: `mobile/lib/main.dart` — AC: AC1 — xong khi: `flutter analyze` không lỗi mới, log `evidence/implement-P5.log`
- [ ] P6 [frontend] `app.dart`: nhận `reminderSyncCoordinator`; tại điểm kích hoạt phiên (`app.dart:180-194`) gọi `requestFullScreenIntentPermission()` và `refresh(session.userId)` (lỗi chỉ ghi log, không chặn đăng nhập); truyền `onChanged` vào `MedicationController` dùng `userId` của phiên hiện tại — file: `mobile/lib/app/app.dart` — AC: AC1, AC3, AC4 — xong khi: test P1(b) pass, log `evidence/implement-P6.log`
- [ ] P7 [frontend] Chạy toàn bộ `cd frontend/mobile && flutter test` và `flutter analyze` — AC: tất cả (gồm AC2 qua `reminder_notification_scheduler_test` hiện có) — xong khi: pass, log `evidence/implement-final-frontend.log`
- [ ] P8 [frontend] (giai đoạn test) Kiểm thủ công trên Android 14+: đăng nhập lần đầu → hỏi quyền thông báo và toàn màn hình; thêm lịch 2 phút sau; khóa máy → thông báo toàn màn hình không tên thuốc, bấm mở màn xác nhận từng thuốc; hoãn cữ; đăng xuất → nhắc bị hủy — AC: AC2, AC4, AC5 — xong khi: kết quả + ảnh chụp ở `evidence/test-device-android14.md`

Sửa theo review (sau reopen):

- [ ] P9 [frontend] Viết test hồi quy H1, M2, L1, M1, L2 và xác nhận fail trên code hiện tại: (H1) `reminder_sync_coordinator_test` "refresh keeps a snoozed reminder" — pending có payload `scheduledAt` quá khứ không bị cancel; `clear()` vẫn cancel nó; (M2) "refresh skips occurrences already recorded" — `hasDoseLog` true cho lượt đầu → lượt đó không được `zonedSchedule`; (L1) `api_schedule_remote_data_source_test` "throws ApiException on wrong field types" — `days_of_week: ['1']`, `strength_text: 5`; (M1) `reminder_wiring_test` kích hoạt phiên gọi `requestNotificationsPermission` 1 lần, trước `requestFullScreenIntentPermission`; (L2) `reminder_wiring_test` ghi thuốc qua app → `refresh('A')` gọi lần hai — file: `mobile/test/core/notification/reminder_sync_coordinator_test.dart`, `mobile/test/core/sync/api_schedule_remote_data_source_test.dart`, `mobile/test/app/reminder_wiring_test.dart` — AC: AC2, AC3, AC4, AC1 — xong khi: các test mới fail đúng lý do (L2 có thể pass ngay vì đường gọi đã có; ghi rõ), log `evidence/implement-P9.log`
- [ ] P10 [frontend] H1 + M2 trong coordinator: `refresh` chỉ hủy pending có `scheduledAt >= now`; lọc lượt đã `hasDoseLog` trước khi lập — file: `mobile/lib/core/notification/reminder_sync_coordinator.dart` — AC: AC2, AC3 — xong khi: toàn bộ `reminder_sync_coordinator_test` pass, log `evidence/implement-P10.log`
- [ ] P11 [frontend] L1 trong data source: kiểm kiểu `strength_text`, `dosage_form`, `days_of_week` → `ApiException` — file: `mobile/lib/core/sync/api_schedule_remote_data_source.dart` — AC: AC1 — xong khi: `api_schedule_remote_data_source_test` pass, log `evidence/implement-P11.log`
- [ ] P12 [frontend] M1: thêm `requestNotificationsPermission()` (platform mặc định `true`, Default gọi plugin Android, `NotificationService` chuyển tiếp) + test chuyển tiếp — file: `mobile/lib/core/notification/notification_service.dart`, `mobile/test/core/notification/notification_service_test.dart` — AC: AC4 — xong khi: `notification_service_test` pass, log `evidence/implement-P12.log`
- [ ] P13 [frontend] `_activateReminders` xin quyền thông báo rồi quyền toàn màn hình, lỗi từng bước chỉ ghi log — file: `mobile/lib/app/app.dart` — AC: AC4 — xong khi: `reminder_wiring_test` pass, log `evidence/implement-P13.log`
- [ ] P14 [frontend] Chạy lại toàn bộ `flutter test`, `flutter analyze`, `scope.py --stage implement` — AC: tất cả — xong khi: không có fail mới ngoài 5 fail có sẵn trên `main`, log `evidence/implement-final-frontend-r2.log`

Sửa M3 (sau reopen lần 3):

- [ ] P15 [frontend] Viết test hồi quy và xác nhận fail: `secure_storage_test` "markReminderPermissionsAsked true lần đầu, false lần sau"; `reminder_wiring_test` "shouldAskReminderPermissions false → không xin quyền nào nhưng vẫn refresh" — file: `mobile/test/core/storage/secure_storage_test.dart`, `mobile/test/app/reminder_wiring_test.dart` — AC: AC4 — xong khi: fail đúng lý do, log `evidence/implement-P15.log`
- [ ] P16 [frontend] Cài `markReminderPermissionsAsked`; `DrugTimeApp.shouldAskReminderPermissions` chặn hai lời xin quyền; `main.dart` truyền hàm — file: `mobile/lib/core/storage/secure_storage.dart`, `mobile/lib/app/app.dart`, `mobile/lib/main.dart` — AC: AC4 — xong khi: test P15 pass, log `evidence/implement-P16.log`
- [ ] P17 [frontend] Chạy lại toàn bộ `flutter test`, `flutter analyze`, `scope.py --stage implement` — AC: tất cả — xong khi: không có fail mới ngoài 5 fail có sẵn trên `main`, log `evidence/implement-final-frontend-r3.log`

## 5. Test

### Unit

| Test dự kiến | AC | Submodule |
|---|---|---|
| `reminder_sync_coordinator_test`: refresh lên lịch lượt tương lai với `fullScreenIntent: true` (hồi quy) | AC1 | frontend |
| `reminder_sync_coordinator_test`: lịch bị xóa/sửa trên server → nhắc cũ bị hủy, nhắc mới được lên lịch | AC3 | frontend |
| `reminder_sync_coordinator_test`: API lỗi → vẫn lên lịch từ dữ liệu cục bộ, không ném ra ngoài | AC1 | frontend |
| `reminder_sync_coordinator_test`: `clear()` chỉ hủy thông báo có payload nhắc thuốc | AC1 | frontend |
| `api_schedule_remote_data_source_test`: map trường, đi hết `next_cursor`, `ended_at` null, lỗi được ném ra | AC1 | frontend |
| `medication_controller_test`: `onChanged` gọi khi thành công, không gọi khi lỗi | AC3 | frontend |
| `reminder_wiring_test`: kích hoạt phiên gọi `requestFullScreenIntentPermission` và `refresh(userId)` (hồi quy) | AC1, AC4 | frontend |
| `reminder_notification_scheduler_test` (hiện có, chạy lại): hoãn cữ lên lịch ở `remindAt` | AC2 | frontend |
| `reminder_sync_coordinator_test`: refresh giữ nhắc hoãn cữ (pending `scheduledAt` quá khứ); `clear()` vẫn hủy (hồi quy H1) | AC2 | frontend |
| `reminder_sync_coordinator_test`: refresh không lập nhắc cho lượt đã có dose log (M2) | AC3 | frontend |
| `api_schedule_remote_data_source_test`: sai kiểu trường → `ApiException` (L1) | AC1 | frontend |
| `notification_service_test`: `requestNotificationsPermission` chuyển tiếp tới platform (M1) | AC4 | frontend |
| `reminder_wiring_test`: kích hoạt phiên xin quyền thông báo trước quyền toàn màn hình (M1); ghi thuốc qua app gọi lại `refresh` (L2) | AC4, AC3 | frontend |
| `secure_storage_test`: `markReminderPermissionsAsked` lần đầu `true`, lần sau `false` (M3) | AC4 | frontend |
| `reminder_wiring_test`: đã hỏi rồi → không xin quyền, vẫn `refresh` (M3) | AC4, AC1 | frontend |

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| Kiểm thủ công trên Android 14+ (P8) | AC2, AC4, AC5 | Full-screen intent và màn hình khóa không chạy được trong `flutter test` |
| Gửi lại cùng `client_uuid` → một bản ghi liều | Kịch bản chất lượng "Ghi nhận liều" | Không đổi code outbox; `sync_engine_test` hiện có chạy lại trong P7 |

## 6. Migration

Không có.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| superproject | `fix/adhoc-20261112-reminder-not-scheduled` |
| frontend | `fix/adhoc-20261112-reminder-not-scheduled` (đã tạo từ `origin/main` @ `f7c2efb4`) |

## 8. Rủi ro

- **Bỏ khối quét lúc khởi động**: nếu app mở không có mạng và phiên chưa kích hoạt (offline), nhắc chỉ được lên lịch khi điểm kích hoạt phiên chạy. Điểm này hiện yêu cầu `_online`; P6 gọi `refresh` ngay khi có phiên, không chờ `_online`, để offline vẫn lên lịch từ dữ liệu cục bộ (QD-33). Test P1(b) phủ trường hợp này.
- **Số lượng alarm trên Android**: 7 ngày × nhiều thuốc có thể chạm giới hạn alarm của hãng (~500). Generator đã gom theo `(scheduleId, scheduledAt)`; theo dõi ở P8.
- **Thiếu quyền exact alarm**: scheduler đã fallback inexact và ghi log; banner NT-07 (⏳) ngoài phạm vi.
- **Nhắc mất sau khởi động lại máy** (NT-06, ⏳): ngoài phạm vi; mở app sẽ `refresh` lại.
- **Thông báo của người dùng trước sót lại**: xử lý bằng `clear()` trong `beforeSignOut`.

## 9. Câu hỏi mở

Không có. Q1, Q2 ở `01` đã trả lời.

## 10. Phát sinh

- `01` mục 3 ghi nguyên nhân gốc "scheduler không được khởi tạo", không còn đúng trên `main` (xem mục 1). AC1–AC5 không đổi nên không reopen `01`; ghi nhận ở đây và ở PS1 của `04`.
- Superproject vẫn ở nhánh `feat/5.06-admin-queue-api` với thay đổi chưa commit của task khác; chưa chuyển nhánh superproject.

## Bước tiếp theo

- Đang chờ: người duyệt
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261112-reminder-not-scheduled plan`, rồi `gate.py reopen adhoc-20261112-reminder-not-scheduled implement`; sau đó agent implement P15–P17 (P1–P14 đã xong, xem `04-impl-notes.md`)
- Cập nhật lần cuối: 2026-11-13, Claude Code
