---
task: adhoc-20261112-reminder-not-scheduled
title: Không có thông báo nhắc thuốc toàn màn hình
type: bug
severity: High
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-12 21:59 +0700
content_hash: sha256:6b92750b479c1d4b
---

# adhoc-20261112-reminder-not-scheduled · Không có thông báo nhắc thuốc toàn màn hình

## 1. Triệu chứng

- Mong đợi: tới giờ uống thuốc, app mobile (Android) hiện thông báo nhắc; khi máy khóa/tắt màn hình thì bật màn hình nhắc toàn màn hình (full-screen intent). Nguồn nghiệp vụ: `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` §6.1 — QD-21 (gom thuốc cùng giờ thành một thông báo, mở danh sách xác nhận từng thuốc), QD-22 (lập trước các nhắc gần nhất, bổ sung khi mở app/sửa lịch), QD-26 (màn hình khóa chỉ hiện nội dung chung), QD-20 (nhắc lại sau 10 phút). Tất cả trạng thái ✅.
- Thực tế: không có thông báo nhắc thuốc nào, kể cả dạng thường lẫn toàn màn hình.
- Môi trường: `frontend/mobile` (Flutter, Android), frontend HEAD `ec755c64`, `flutter_local_notifications ^17.2.2`.
- Thông báo lỗi / log: không có lỗi; app không bao giờ gọi API lên lịch thông báo.

## 2. Tái hiện

| Lệnh / thao tác | Kết quả | Log |
|---|---|---|
| Tìm mọi chỗ gọi `ReminderNotificationScheduler(`, `scheduleOccurrences(`, `requestFullScreenIntentPermission(` trong `lib/` | Chỉ có định nghĩa, không có nơi gọi | `evidence/requirement-repro.log` |
| Tìm `reminderScheduler` trong `lib/main.dart` | Không có | `evidence/requirement-repro.log` |
| Kiểm các nhánh `origin/feat/2.07-*` | Đều đã merge (0 commit chưa merge), không nhánh nào có phần gắn scheduler | `evidence/requirement-repro.log` |

Đây là tái hiện tĩnh (đọc mã nguồn). Chưa chạy trên thiết bị/emulator; xem Q2.

## 3. Nguyên nhân gốc

- Nguyên nhân gốc: `ReminderNotificationScheduler` (lớp lên lịch thông báo cục bộ, đã cấu hình `fullScreenIntent: true`) không được khởi tạo ở composition root và `scheduleOccurrences` không có nơi gọi. App không bao giờ đặt lịch thông báo nhắc.
- Chuỗi suy luận và bằng chứng:
  1. Cấu hình thông báo đúng: `frontend/mobile/lib/core/notification/reminder_notification_scheduler.dart:41-51` (`Importance.max`, `Priority.high`, `fullScreenIntent: true`, `category: alarm`). Manifest đủ quyền `USE_FULL_SCREEN_INTENT`, `SCHEDULE_EXACT_ALARM`, `showWhenLocked`, `turnScreenOn` (`android/app/src/main/AndroidManifest.xml:10,8,31-32`).
  2. `lib/main.dart:60-134` tạo `NotificationService` và truyền vào app nhưng không tạo `ReminderNotificationScheduler` và không truyền `reminderScheduler`.
  3. `lib/app/app.dart:428` vì vậy dùng `_FallbackReminderScheduler` (`app.dart:685`), trong đó `snooze()` rỗng.
  4. Không nơi nào trong `lib/` gọi `scheduleOccurrences(` → không có `zonedSchedule` nào chạy → không có thông báo.
- Nguyên nhân phụ (lộ ra sau khi sửa gốc): `NotificationService.requestFullScreenIntentPermission()` (`notification_service.dart:237`) không được gọi. Trên Android 14+, quyền full-screen intent mặc định tắt với app không phải đồng hồ/cuộc gọi, nên thông báo chỉ hiện dạng heads-up.

## 4. Phạm vi ảnh hưởng

- Chỗ khác có cùng mẫu lỗi: `_FallbackReminderScheduler.snooze()` rỗng → hoãn cữ (QD-20) cũng không đặt lại nhắc. Cần kiểm thêm: `ReminderOccurrenceGenerator` (sinh lượt nhắc từ lịch uống) có nơi gọi không; khôi phục nhắc sau `BOOT_COMPLETED` (NT-06, ⏳).
- Dữ liệu đã bị ảnh hưởng: không hỏng dữ liệu. Liều bị bỏ lỡ vì không được nhắc là ảnh hưởng nghiệp vụ, không cần sửa dữ liệu.
- Vùng rủi ro và bất biến bị chạm:
  - Ghi nhận liều và đồng bộ: nhắc mở màn xác nhận liều qua outbox; sửa không đổi logic outbox nhưng phải giữ idempotent.
  - Dữ liệu sức khỏe: lấy lịch uống qua Backend API sẵn có (đã đi qua PEP), không thêm endpoint.
  - Bất biến 7: múi giờ `Asia/Ho_Chi_Minh` — scheduler đã dùng `NotificationService.location`.
  - QD-26/NT-02: nội dung trên màn hình khóa không chứa tên thuốc (đã có `defaultTitle`/`defaultBody`).

## 5. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| frontend | Có | Gắn scheduler, gọi lên lịch, xin quyền FSI trong `frontend/mobile` |
| backend | Không | Không đổi API |
| api_contract | Không | Không đổi contract |
| tests | Không | Test ở mức unit/widget trong `frontend/mobile/test` |
| docs | Không | — |

## 6. Hướng sửa đề xuất

| Hướng | Đánh đổi |
|---|---|
| A. Ở `main.dart` tạo `ReminderNotificationScheduler` và truyền vào `reminderScheduler`; gọi `scheduleOccurrences` (qua `ReminderOccurrenceGenerator`) khi mở app/đăng nhập và sau khi lịch uống thay đổi; xin quyền FSI một lần trên Android 14+ | Đúng QD-22, sửa cả snooze. Phải tìm điểm móc "lịch thay đổi" phù hợp |
| B. Chỉ lên lịch khi mở app | Diff nhỏ nhất, nhưng sửa lịch xong không có nhắc mới tới lần mở app sau → vi phạm QD-22 |

Đề xuất: A.

## 7. Thay đổi API contract

- `contract_change`: no
- Lý do: chỉ đổi phía client; dùng endpoint lịch uống sẵn có.

## 8. Tiêu chí chấp nhận (gồm test hồi quy)

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 (hồi quy) | Given app khởi động với patient có lịch uống trong tương lai, When khởi tạo xong composition root, Then `NotificationPlatform.zonedSchedule` được gọi cho mỗi lượt nhắc tương lai với `fullScreenIntent: true` và channel `drugtime_reminder_channel`. Phải fail trên code hiện tại | Unit/widget (fake `NotificationPlatform`) |
| AC2 (hồi quy) | Given app đang chạy, When patient hoãn cữ (snooze) trên màn nhắc, Then một nhắc mới được lên lịch ở `remindAt` (không dùng `_FallbackReminderScheduler`). Phải fail trên code hiện tại | Widget |
| AC3 | Given lịch uống bị thêm/sửa/xóa, When thao tác lưu thành công, Then nhắc cũ của lịch đó bị hủy và nhắc mới được lên lịch | Unit |
| AC4 | Given Android 14+ và chưa có quyền full-screen intent, When patient bật nhắc lần đầu, Then app gọi `requestFullScreenIntentPermission()` | Unit (fake platform) |
| AC5 | Given máy đang khóa, When tới giờ nhắc, Then thông báo hiện toàn màn hình, chỉ có nội dung chung (không tên thuốc), mở được màn xác nhận từng thuốc | Thủ công trên thiết bị Android 14+ |

## 9. Câu hỏi mở

- Q1: Thời điểm xin quyền full-screen intent? Mặc định của agent: xin ngay sau khi patient đăng nhập lần đầu, cùng lúc với quyền thông báo.
- Q2: Có thiết bị/emulator Android 14+ để chạy AC5 không? Mặc định: kiểm thủ công ở giai đoạn test, ghi kết quả vào evidence.

## 10. Giả định

- `ReminderOccurrenceGenerator` đã sinh lượt nhắc đúng (gom cùng giờ theo QD-21); sẽ xác minh ở giai đoạn plan.
- Khôi phục nhắc sau khởi động (NT-06) ngoài phạm vi; nó đang ⏳ trong tài liệu nghiệp vụ.

## 11. Phát sinh

- Superproject đang ở nhánh `feat/5.06-admin-queue-api` với thay đổi chưa commit. Nhánh task theo `wf-git` sẽ là `fix/adhoc-20261112-reminder-not-scheduled`; chưa tạo, chờ người dùng.

## 12. Size

- `size`: M
- Lý do: chạm vùng rủi ro "Ghi nhận liều và đồng bộ" (luồng nhắc → xác nhận liều), sửa nhiều file (`main.dart`, `app.dart`, điểm lưu lịch uống, test) → không được xếp S.

## Bước tiếp theo

- Đang chờ: người dùng trả lời Q1, Q2 và người duyệt
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261112-reminder-not-scheduled requirement`; sau đó agent làm giai đoạn plan (`wf-plan`)
- Cập nhật lần cuối: 2026-11-12, Claude Code
