---
task: 2.07-notification-service
title: ID thông báo tất định và khởi tạo NotificationService
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-07 15:06 +0700
content_hash: sha256:4ae915828960be7d
---

# 2.07-notification-service · ID thông báo tất định và khởi tạo NotificationService

## 1. Mục tiêu

Cung cấp cơ chế định danh thông báo nhắc thuốc tất định (`notificationIdFor`) trong không gian 31-bit nguyên dương cùng cơ chế tuần tự hóa `NotificationPayload`, và khởi tạo dịch vụ thông báo cục bộ `NotificationService.init` với múi giờ cố định `Asia/Ho_Chi_Minh` (UTC+7) trên Flutter. Chức năng phục vụ cho việc lên lịch nhắc thuốc offline, không phụ thuộc đồng hồ hệ thống hay múi giờ thiết bị, hỗ trợ action "Đã uống" sau này.

## 2. Phạm vi

### Trong phạm vi

- **Phần (a) ID thông báo tất định và Payload (Dart thuần, TDD):**
  - Hàm thuần `int notificationIdFor({required int medicationScheduleId, required DateTime scheduledAt})`.
  - Thuật toán băm FNV-1a 32-bit trên chuỗi chuẩn hóa `"$medicationScheduleId:$epochSeconds"`, giới hạn trong khoảng `[0, 2^31 - 1]`.
  - Chuẩn hóa `scheduledAt` về UTC và độ phân giải giây (`epochSeconds = scheduledAt.millisecondsSinceEpoch ~/ 1000`). Ném `ArgumentError` nếu `scheduledAt.isUtc == false`.
  - Phân tích xác suất va chạm và thiết kế hàm kiểm tra va chạm tập hợp `detectIdCollisions(occurrences)`. Khi phát hiện va chạm, ghi log lỗi rõ ràng và bỏ qua lượt thứ hai, tuyệt đối không tự ý đổi `scheduledAt` (để tránh lệch mốc giờ khi gọi `cancelOccurrence`).
  - Class `NotificationPayload` và các hàm `serialize()` / `tryParse()` để đóng gói và giải mã an toàn `medicationScheduleId` cùng `scheduledAt` (ISO-8601 UTC). Trả về lỗi có kiểm soát khi payload sai định dạng (không crash).
- **Phần (b) Khởi tạo NotificationService (`NotificationService.init`):**
  - Thêm 2 dependency `flutter_local_notifications: ^17.2.2` và `timezone: ^0.9.4` vào `pubspec.yaml`. Tuyệt đối KHÔNG thêm `flutter_timezone`.
  - Khởi tạo cơ sở dữ liệu múi giờ `tz.initializeTimeZones()` và cấu hình cố định `tz.getLocation('Asia/Ho_Chi_Minh')`. Cấm `tz.local` và không dùng `flutter_timezone`.
  - Cấu hình khởi tạo Android (`@mipmap/ic_launcher`, kênh thông báo quan trọng cao `drugtime_reminder_channel`) và iOS/Darwin (chưa tự xin quyền lúc init).
  - Nhận callback chuyển tiếp `onNotificationAction(NotificationPayload payload)` qua constructor khi người dùng tương tác thông báo.
  - Bọc plugin qua abstraction mỏng (`NotificationPlatform`) để test được không cần thiết bị thật.

### Ngoài phạm vi

- Chưa lên lịch hoặc hủy thông báo thật (thuộc SCRUM-57 phần 2).
- Chưa cấu hình Android manifest (`POST_NOTIFICATIONS`, `SCHEDULE_EXACT_ALARM`, `RECEIVE_BOOT_COMPLETED`) và chưa bật desugaring trong `build.gradle.kts` (thuộc SCRUM-61).
- Chưa gọi `DoseOutbox.enqueue` hay xử lý logic ghi nhận liều khi bấm thông báo (thuộc SCRUM-57 phần 2 / Task 2.11).
- Không sửa `local_db.dart`, `sync_engine.dart`, `sqlite_dose_outbox.dart`, `features/dose_confirmation/**`.
- Không sửa `reminder_occurrence_generator.dart` (đã hoàn thành và commit ở commit `586cd90`).
- Không sửa `lib/core/contracts/reminder_scheduler.dart` hay `lib/core/notification/reminder_scheduler.dart`.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `frontend/mobile/pubspec.yaml` | Chưa có `flutter_local_notifications` và `timezone`. Ràng buộc SDK: `>=3.5.0 <4.0.0`. Flutter hiện tại: `3.47.6`, Dart: `3.13.5`. |
| Nhánh `feat/2.24-mobile-outbox` | Nhánh 2.24 từng kéo nhầm `flutter_local_notifications`, `timezone`, `flutter_timezone` vào PR #24; đã được gỡ bỏ hoàn toàn ở commit `4346605`. Task này chỉ thêm đúng 2 package cần thiết: `flutter_local_notifications: ^17.2.2` và `timezone: ^0.9.4`, không thêm `flutter_timezone`. |
| `frontend/mobile/lib/core/notification/reminder_occurrence_generator.dart` | Định nghĩa `ReminderOccurrence` với `medicationScheduleId` (int) và `scheduledAt` (DateTime UTC). |
| `frontend/mobile/lib/core/notification/notification_permission.dart` | File 0 byte, chưa có nội dung. |
| `frontend/mobile/android/app/build.gradle.kts` | Java 17, `minSdk = flutter.minSdkVersion` (21). Chưa cấu hình desugaring. Giữ nguyên, không sửa trong task này. |
| `frontend/mobile/android/app/src/main/AndroidManifest.xml` | Icon `@mipmap/ic_launcher`. Chưa khai báo quyền notification/alarm. Giữ nguyên cho SCRUM-61. |
| Tài liệu `flutter_local_notifications` (v17.2.x) | Android yêu cầu notification ID là số nguyên 32-bit (`int`). Phương thức `initialize` nhận `InitializationSettings` và callback `onDidReceiveNotificationResponse`. Hàm top-level `@pragma('vm:entry-point')` cần thiết cho background notification actions. |
| Tài liệu `timezone` (v0.9.x) | Cung cấp `initializeTimeZones()` và `getLocation('Asia/Ho_Chi_Minh')`. Có sẵn đầy đủ dữ liệu IANA tzdata cho Việt Nam. |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `frontend` | Có | Thêm 2 dependency vào `pubspec.yaml`, thêm 2 file code logic và 2 file test trong `mobile/`. |
| `backend` | Không | Logic thông báo hoàn toàn phía client. |
| `api_contract` | Không | Không đổi hợp đồng API. |
| `tests` | Không | Unit test thực thi bên trong submodule `frontend/mobile`. |
| `docs` | Không | Không thay đổi tài liệu dự án. |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: Không thêm, sửa, hay xóa endpoint nào giữa Backend và Client.
- Endpoint liên quan: Không có.

## 6. Vùng rủi ro và bất biến bị chạm

- Không chạm vùng rủi ro backend (không có PEP, access logs, DB schema migration).
- Bất biến kiến trúc CD7: Múi giờ cố định `Asia/Ho_Chi_Minh` (UTC+7). Tuyệt đối không dùng `tz.local`, không dùng `flutter_timezone`, không gọi `DateTime.now()` hay `toLocal()`.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given cùng một cặp `(medicationScheduleId, scheduledAt)`, When gọi `notificationIdFor` nhiều lần trên các môi trường chạy khác nhau, Then luôn trả về cùng một số nguyên (tất định), khớp đúng 4 test vector cố định được tính bằng Python độc lập:<br>1. (1, 2026-10-07T01:00:00Z, epoch 1791334800) → 277106154<br>2. (2, 2026-10-07T01:00:00Z, epoch 1791334800) → 280090069<br>3. (1, 2026-10-07T01:00:01Z, epoch 1791334801) → 293883773<br>4. (102, 2026-10-06T17:30:00Z, epoch 1791307800) → 259718614 | unit |
| AC2 | Given các đầu vào khác nhau (khác `medicationScheduleId` hoặc lệch 1 giây ở `scheduledAt`), When gọi `notificationIdFor`, Then trả về các ID khác nhau. | unit |
| AC3 | Given 10.000 cặp đầu vào ngẫu nhiên với seed cố định, When gọi `notificationIdFor`, Then mọi kết quả đều nằm trong khoảng `[0, 2^31 - 1]`. | unit |
| AC4 | Given tham số `scheduledAt` không phải UTC (`isUtc == false`), When gọi `notificationIdFor`, Then ném `ArgumentError`. | unit |
| AC5 | Given `NotificationPayload` hợp lệ, When gọi `serialize()` rồi `NotificationPayload.tryParse()`, Then khôi phục chính xác đối tượng ban đầu (round-trip). When chuỗi payload rác, rỗng, thiếu trường, id không phải int, hoặc thời gian không phải UTC, Then `tryParse` trả về `null` có kiểm soát (không throw/crash). | unit |
| AC6 | Given danh sách các lượt nhắc có 2 đầu vào bị trùng ID băm, When gọi `detectIdCollisions()`, Then phát hiện va chạm chính xác, ghi log cảnh báo và bỏ qua lượt thứ hai, giữ nguyên `scheduledAt` (không tịnh tiến mốc giờ). | unit |
| AC7 | Given `NotificationService.init()`, When khởi tạo, Then nạp dữ liệu timezone `Asia/Ho_Chi_Minh`, không gọi `tz.local`, và gọi plugin với cấu hình Android (icon `@mipmap/ic_launcher`, channel `drugtime_reminder_channel`) và Darwin (`requestAlertPermission: false`). | unit |
| AC8 | Given `NotificationService.init()`, When gọi khởi tạo 2 lần liên tiếp, Then hoàn thành bình thường không phát sinh lỗi (idempotent). | unit |
| AC9 | Given người dùng nhấn vào thông báo có payload hợp lệ, When plugin kích hoạt callback, Then `NotificationService` phân tích payload và chuyển tiếp đối tượng `NotificationPayload` cho handler đã đăng ký. | unit |
| AC10 | Given kiểm tra mã nguồn tĩnh qua grep, When quét toàn bộ code thông báo mới, Then không xuất hiện `tz.local`, `flutter_timezone`, `toLocal()`, hay `DateTime.now()`. | unit |

## 8. Câu hỏi mở

Q1 [không chặn] Vấn đề kiểu `scheduleId` trong `lib/core/contracts/reminder_scheduler.dart`:
- Ảnh hưởng: Interface `ReminderScheduler` đang để `String scheduleId`, trong khi DB và model dùng `int id`.
- Lựa chọn: Chờ Bao cập nhật contract sang `int` / Chuyển đổi tạm `int.parse` khi tích hợp ở SCRUM-57 phần 2.
- Giả định mặc định: Giữ nguyên `int` trong `notification_id.dart` và `NotificationService`; trao đổi với Bao ở phần 2.

Q2 [không chặn] Vấn đề `LocalMedicationStore.getActiveSchedules` lọc `ended_at IS NULL`:
- Ảnh hưởng: Loại bỏ các lịch có hẹn kết thúc tương lai trước khi lên lịch.
- Giả định mặc định: Không sửa store trong task này; trao đổi với Bao khi làm phần 2 để có query phù hợp.

Q3 [không chặn] Icon thông báo trên Android:
- Ảnh hưởng: Icon hiển thị ở thanh thông báo.
- Giả định mặc định: Sử dụng icon mặc định `@mipmap/ic_launcher` như đã định cấu hình trong AndroidManifest.

## 9. Giả định & Giới hạn

### Giả định
- Thuật toán băm FNV-1a 32-bit (mask `0x7FFFFFFF`) đảm bảo phân phối đều và độc lập hoàn toàn với seed ngẫu nhiên của Dart VM runtime.
- Xác suất va chạm trong không gian 31-bit: với $n = 64$ thông báo đồng thời là `~9.4e-7`; với $n = 500$ thông báo đồng thời là `~5.8e-5`.
- Khi phát hiện va chạm ID, cơ chế xử lý an toàn là ghi log cảnh báo và bỏ qua lượt thứ hai, giữ nguyên `scheduledAt` ban đầu để tránh làm sai lệch việc hủy lượt (`cancelOccurrence`).
- Múi giờ Việt Nam cố định UTC+7, location `Asia/Ho_Chi_Minh` luôn tồn tại trong cơ sở dữ liệu `timezone/data/latest_all.dart`.

### Giới hạn chưa kiểm chứng
- Chưa chạy trên thiết bị thật Android/iOS; các kiểm thử của `NotificationService` sử dụng mock/stub platform interface.
- Chưa kích hoạt quyền runtime thông báo (`POST_NOTIFICATIONS` trên Android 13+) và chưa cấu hình desugaring (thuộc SCRUM-61).

## 10. Phát sinh

- Không có.

## 11. Size

- `size`: M
- Lý do: Task thay đổi cấu hình `pubspec.yaml`, thêm 2 file mã nguồn (`notification_id.dart`, `notification_service.dart`) và 2 file test (`notification_id_test.dart`, `notification_service_test.dart`), tổng cộng 5 file, vượt quá tiêu chí size S (tối đa 3 file, 50 dòng). Kế hoạch thực hiện chi tiết được lưu tại `03-plan.md`.

## Bước tiếp theo

- Đang chờ: Người duyệt xem xét và phê duyệt artifact `01-requirement.md`.
- Việc cần làm: Người dùng chạy lệnh `python .agents/scripts/gate.py approve 2.07-notification-service requirement` trong terminal của mình để duyệt giai đoạn requirement.
- Cập nhật lần cuối: 2026-10-07 14:55, Antigravity
