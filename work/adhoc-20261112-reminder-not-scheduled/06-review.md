---
task: adhoc-20261112-reminder-not-scheduled
stage: review
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-13 16:31 +0700
content_hash: sha256:0c757a672e875272
inputs:
  01-requirement.md: sha256:6b92750b479c1d4b
  03-plan.md: sha256:20d603a93ddf82f9
  04-impl-notes.md: sha256:799e77ed366cf960
  05-test-report.md: sha256:210e9f334c4b4697
---

# adhoc-20261112-reminder-not-scheduled · Review

## 1. Kết luận

**Đạt, kèm lưu ý.** Vòng 3 (2026-11-13) đã sửa M3 theo quyết định của người dùng: chỉ xin quyền ở lần đăng nhập đầu sau khi cài. Vòng 2 đã sửa H1, M1, M2, L1, L2. Không còn Critical/High/Medium. Còn 4 Low (L3–L6).

Lưu ý về tính độc lập: review này vẫn do cùng phiên agent đã implement thực hiện (Claude Code), không đạt yêu cầu "reviewer độc lập" của `wf-review`. Definition of Done vẫn cần ít nhất 1 thành viên khác approve PR.

Lưu ý về AC5: chưa được xác minh trên thiết bị (TC-REMIND-13…18 `Pending`). Nên chạy trước khi merge.

## 2. Phạm vi đã review

| Submodule | Lệnh diff |
|---|---|
| frontend | `git -C frontend diff origin/main -- mobile/lib mobile/test` (7 file sửa) và đọc trọn 6 file mới chưa track: `mobile/lib/core/notification/reminder_sync_coordinator.dart`, `mobile/lib/core/sync/api_schedule_remote_data_source.dart`, `mobile/test/app/reminder_wiring_test.dart`, `mobile/test/core/notification/reminder_sync_coordinator_test.dart`, `mobile/test/core/sync/api_schedule_remote_data_source_test.dart`, `mobile/test/core/storage/secure_storage_test.dart`. Vòng 3 đọc kỹ diff M3: `app.dart`, `main.dart`, `secure_storage.dart` |

Nhánh: `fix/adhoc-20261112-reminder-not-scheduled` @ `origin/main` `f7c2efb4` + thay đổi chưa commit.

Kết quả `scope.py --stage implement`: 13 file của task `[OK]` (`evidence/implement-scope-r3.log`). Các dòng `[NGOÀI]` là thay đổi có sẵn không thuộc task.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1–AC4 đạt ở mức code + test tự động; AC2 nay phủ cả kịch bản hoãn cữ rồi `refresh` (H1 đã sửa). AC5 chưa xác minh trên thiết bị |
| Phạm vi | Đúng bảng file `03` (bản sau reopen thứ ba, mục 1c). PS4 (interface riêng cho M1) là đổi chỗ khai báo trong file đã duyệt, đã ghi Phát sinh |
| Contract | Map đúng `GET /patients/{patient_id}/schedules`; pattern L1 bắt buộc `strength_text`/`dosage_form` có mặt, khớp `required` của contract (cho phép `null`) |
| Bất biến kiến trúc | (1) chỉ gọi Backend API; (4) mỗi `refresh` đọc lại API; (5) không đụng outbox/upsert liều; (7) giờ `Asia/Ho_Chi_Minh` — đạt |
| Bảo mật | Không secret; log không chứa token hay tên thuốc; nhắc dùng nội dung chung (QD-26) — đạt |
| Xử lý lỗi | Sync lỗi dùng lịch cục bộ (QD-33); lỗi xin quyền chỉ ghi log, không chặn lập nhắc; sai kiểu dữ liệu nay là `ApiException` (L1 đã sửa); lỗi đọc/ghi cờ M3 (`PlatformException` là `Exception`) được bắt → không hỏi, vẫn `refresh` |
| Hiệu năng | M2 gọi `hasDoseLog` cho từng lượt (tối đa vài trăm truy vấn SQLite tuần tự mỗi `refresh`) — chấp nhận được, ghi L4 |
| Chất lượng test | Có test hồi quy cho H1, M2, L1, M1, L2, M3 (đã hỏi → không xin quyền, vẫn `refresh`; cờ chỉ `true` lần đầu, giữ qua instance mới); khẳng định cụ thể (id bị cancel, ngày lập, thứ tự quyền); có đường lỗi |
| Dễ đọc và nhất quán | Theo pattern có sẵn (`FamilyNotificationPlatform`, `_queue`); comment giải thích phép ép kiểu cần thiết |
| Đối chiếu 04/05 với log trong `evidence/` | Khớp: P9 `+9 -7` (fail trước khi sửa), P10 `+7`, P11 `+7`, P12 `+8`, P13 `+2`, toàn bộ `+1042 ~1 -5` (5 fail có sẵn trên `main`), test giai đoạn test `+78`, analyze 3 info ngoài task. Vòng 3: P15 fail biên dịch đúng lý do, P16 `+5`, toàn bộ `+1045 ~1 -5` và chạy lại 4 file fail → đúng 5 test có sẵn (`implement-final-frontend-r3-failures.log`), test giai đoạn test `+81` (`test-integration-r3.log`). `testcase_xlsx.py validate`: 26 case, Pass 20 / Fail 0 / Pending 6; mọi Pass truy được tới log. PS5 (lần chạy treo do agent) được ghi trung thực |

## 4. Phát hiện

Vòng 1 → vòng 2:

| Mã | Mức (vòng 1) | Trạng thái | Bằng chứng |
|---|---|---|---|
| H1 | High | Đã sửa | `reminder_sync_coordinator.dart` `_cancelPendingReminders(onlyFrom: now)`; test "refresh keeps a snoozed reminder…" |
| M1 | Medium | Đã sửa | `notification_service.dart` `NotificationPermissionPlatform`; `app.dart` `_activateReminders`; test thứ tự quyền |
| M2 | Medium | Đã sửa | Lọc `hasDoseLog`; test "refresh skips occurrences already recorded…" |
| M3 | Medium | Đã sửa (vòng 3) | `SecureStorage.markReminderPermissionsAsked`; `app.dart` `_shouldAskPermissions`; test "permissions already asked after install…", `secure_storage_test` |
| L1 | Low | Đã sửa | Pattern kiểu dữ liệu; 3 test sai kiểu |
| L2 | Low | Đã sửa | Test "a successful medication change refreshes reminders again" |

Phát hiện còn mở:

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| Low (L3) | `frontend/mobile/lib/app/app.dart` `_activateReminders` | `refresh` chạy sau khi các lời gọi xin quyền trả về; nếu màn cài đặt quyền toàn màn hình giữ người dùng lâu, việc lập nhắc bị trễ tương ứng | Cân nhắc chạy `refresh` song song với xin quyền; xác nhận ở TC-REMIND-13 |
| Low (L4) | `frontend/mobile/lib/core/notification/reminder_sync_coordinator.dart` vòng `hasDoseLog` | Một truy vấn SQLite cho mỗi lượt trong 7 ngày | Nếu chậm trên máy thật, đọc một lần các dose log trong khoảng `[now, now+7d]` |
| Low (L6) | `frontend/mobile/lib/core/storage/secure_storage.dart` `markReminderPermissionsAsked` | Cờ ghi trước khi người dùng trả lời và tính theo máy: từ chối, đổi tài khoản, hoặc tắt app giữa chừng thì không hỏi lại; quyền bị thu hồi sau này cũng không được nhắc. Android Auto Backup (manifest không tắt `allowBackup`) có thể khôi phục dữ liệu secure storage sang máy mới mà khóa Keystore không đi theo; khi đó đọc cờ lỗi → không hỏi (đã bắt lỗi, không crash) | Đúng quyết định người dùng. Ở task sau: thêm lối vào Cài đặt quyền trong app khi thiếu quyền; kiểm hành vi restore từ backup |
| Low (L5) | `reminder_sync_coordinator.dart` `_cancelPendingReminders(onlyFrom:)` | Nhắc hoãn cữ của lịch vừa bị xóa/ngưng trên server vẫn được giữ và sẽ hiện một lần | Chấp nhận (một lần, đúng giờ người dùng chọn); hoặc hủy nhắc hoãn khi `scheduleId` không còn trong lịch đang hoạt động |

Tổng còn mở: Critical 0 · High 0 · Medium 0 · Low 4.

## 5. Mô tả PR

Thứ tự merge theo `wf-git`: (1) PR frontend → merge; (2) PR superproject bump con trỏ `frontend` tới commit đã merge + artifact `work/adhoc-20261112-reminder-not-scheduled/`; (3) PR `docs` gộp bộ test case vào `Test_Cases.xlsx` khi `docs` sạch (có thể đi sau).

### PR 1 — `frontend` (`fix/adhoc-20261112-reminder-not-scheduled` → `main`)

**fix(mobile): schedule medication reminders from server schedules (adhoc-20261112-reminder-not-scheduled)**

Tóm tắt:
- Nguyên nhân gốc: không có lớp nào tải lịch uống từ API về bảng lịch cục bộ (`ScheduleRemoteDataSource` không có implement, `ScheduleSyncService` không được gọi), nên khối quét lúc khởi động luôn đọc bảng rỗng và không lập nhắc nào.
- Thêm `ApiScheduleRemoteDataSource` (`GET /patients/{id}/schedules`, đi hết `next_cursor`, kiểm kiểu → `ApiException`).
- Thêm `ReminderSyncCoordinator`: đồng bộ lịch → hủy nhắc tương lai → sinh lượt 7 ngày, bỏ lượt đã có dose log → lập nhắc full-screen; giữ nhắc hoãn cữ; `clear()` khi đăng xuất. Lỗi mạng thì dùng lịch cục bộ.
- `main.dart`: nối coordinator, bỏ khối quét lúc khởi động, hủy nhắc khi đăng xuất.
- `app.dart`: khi phiên được kích hoạt, xin quyền thông báo rồi quyền toàn màn hình (chỉ lần đầu sau khi cài, cờ `reminder_permissions_asked` trong `SecureStorage`), sau đó `refresh`; sửa thuốc thành công thì `refresh` lại.
- `NotificationService.requestNotificationsPermission()` không phụ thuộc FCM.

AC và test:
- AC1: `reminder_sync_coordinator_test` (hồi quy), `api_schedule_remote_data_source_test`, `reminder_wiring_test`
- AC2: `reminder_sync_coordinator_test` "refresh keeps a snoozed reminder…", `reminder_notification_scheduler_test` nhóm snooze
- AC3: `reminder_sync_coordinator_test` (xóa lịch, liều đã ghi nhận), `medication_controller_test`, `reminder_wiring_test`
- AC4: `reminder_wiring_test` (thứ tự quyền, chỉ hỏi lần đầu), `notification_service_test`, `secure_storage_test`
- `flutter test`: 1045 pass, 1 skip, 5 fail có sẵn trên `main` (vùng người thân, không liên quan)

Test tay (Android 14+, TC-REMIND-13…18 trong `Test_Cases.xlsx` sheet "Nhắc uống thuốc"):
1. Cài mới, đăng nhập patient → hỏi quyền thông báo và mở cài đặt quyền toàn màn hình. Đóng hẳn rồi mở lại app → không hỏi lại.
2. Thêm lịch 2 phút sau, khóa máy → nhắc toàn màn hình, không có tên thuốc; bấm → danh sách xác nhận từng thuốc.
3. Hoãn cữ → nhắc lại đúng giờ; đóng/mở app trong lúc hoãn vẫn nhắc lại.
4. Đăng xuất → không còn nhắc.
5. Từ chối quyền toàn màn hình, mở lại app → không mở lại màn cài đặt (M3).

Rủi ro: từ chối quyền lần đầu thì app không hỏi lại, người dùng phải tự bật trong Cài đặt (L6); lập nhắc trễ trong lúc người dùng ở màn cài đặt (L3); nhắc mất sau khởi động lại máy cho tới khi mở app (NT-06, ngoài phạm vi).

### PR 2 — superproject (`fix/adhoc-20261112-reminder-not-scheduled` → `main`)

**chore: bump frontend to <sha-merge> (adhoc-20261112-reminder-not-scheduled)**

- Bump con trỏ `frontend` tới commit đã merge của PR 1.
- Thêm artifact `work/adhoc-20261112-reminder-not-scheduled/` (01–06, evidence, `testcases.json`, `testcases.xlsx`).
- Liên kết: PR 1 (frontend). Chỉ merge sau PR 1.

### PR 3 — `docs` (khi `docs` sạch)

**docs(testing): add REMIND test cases (adhoc-20261112-reminder-not-scheduled)**

- `python .agents/scripts/testcase_xlsx.py merge adhoc-20261112-reminder-not-scheduled` → thêm sheet "Nhắc uống thuốc" (26 case) vào `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`, dựng lại `Report`.
- Cập nhật kết quả TC-REMIND-13…18 sau khi chạy trên thiết bị.

## 6. Ghi chú cho quy trình

- `01`/`03` bản đầu khảo sát trên nhánh frontend không phải `main`. Đề xuất `wf-bug`/`wf-plan` ghi SHA và kiểm `merge-base --is-ancestor HEAD origin/<nhánh-gốc>` của submodule trước khi khảo sát.
- Plan vòng sửa giả định thân mặc định trong abstract class được kế thừa qua `implements` (sai trong Dart), phát hiện ở implement (PS4). Plan nên kiểm cách các fake hiện có cài đặt interface trước khi đề xuất đổi interface.
- Cả hai vòng review chạy cùng phiên với implement; skill khuyến nghị phiên/tool khác.
- `scope.py --stage test` báo `[NGOÀI]` cho chính file implement chưa commit; dễ gây hiểu nhầm.

## Bước tiếp theo

- Đang chờ: người duyệt (và người dùng chạy TC-REMIND-13…18)
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261112-reminder-not-scheduled review`; khi người dùng yêu cầu, commit và push theo `wf-git` rồi mở PR theo mục 5 (agent không tự mở PR hay merge)
- Cập nhật lần cuối: 2026-11-13, Claude Code
