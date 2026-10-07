## Bối cảnh & Mục tiêu

Task 2.07 (SCRUM-57 phần 1): Triển khai thuật toán sinh Notification ID tất định và khởi tạo dịch vụ thông báo nhắc thuốc (`NotificationService.init`), làm nền tảng trước khi lên lịch và xử lý báo động chính xác (SCRUM-57 phần 2 / SCRUM-61).

## Thay đổi chính

- **`mobile/pubspec.yaml`**:
  - Thêm `flutter_local_notifications: ^17.2.2` và `timezone: ^0.9.4`.
  - Không thêm `flutter_timezone`.

- **`mobile/lib/core/notification/notification_id.dart`**:
  - `notificationIdFor(medicationScheduleId, scheduledAt)`: Thuật toán băm FNV-1a 32-bit masked 31-bit trên chuỗi canonical `"$medicationScheduleId:$epochSeconds"` (UTC). Trả về số nguyên an toàn trong `[0, 2^31 - 1]`. Ném `ArgumentError` nếu không phải UTC.
  - `NotificationPayload`: Đóng gói `medicationScheduleId` và `scheduledAt` (UTC). Các hàm `serialize()` và `tryParse(raw)` bắt lỗi an toàn (trả về `null` thay vì crash app nếu JSON rác, thiếu trường hoặc sai múi giờ).
  - `detectIdCollisions(occurrences)`: Phát hiện va chạm ID, ghi log lỗi rõ ràng và bỏ qua lượt trùng, giữ nguyên `scheduledAt` ban đầu (không tịnh tiến 1 giây).

- **`mobile/lib/core/notification/notification_service.dart`**:
  - Abstraction `NotificationPlatform` và cài đặt mặc định `DefaultNotificationPlatform` bọc `FlutterLocalNotificationsPlugin` phục vụ unit test độc lập không cần thiết bị.
  - `NotificationService.init()`: Cố định múi giờ `Asia/Ho_Chi_Minh` (UTC+7) qua `tz.getLocation('Asia/Ho_Chi_Minh')`. Cấu hình khởi tạo Android (`@mipmap/ic_launcher`), kênh thông báo `drugtime_reminder_channel` (độ ưu tiên tối đa), Darwin settings (`requestAlertPermission: false`), và đăng ký callback chuyển tiếp payload. Thực thi idempotent (gọi nhiều lần an toàn).

- **Kiểm thử unit & TDD (`mobile/test/core/notification/`)**:
  - `notification_id_test.dart`: 9 test phủ AC1..AC6 (khớp chính xác 4 test vector Python độc lập, 10.000 mẫu ngẫu nhiên trong range 31-bit, round-trip payload, collision detection).
  - `notification_service_test.dart`: 5 test phủ AC7..AC10 (cấu hình kênh, timezone, idempotency, callback action, và static check cấm API bị cấm).

## Kết quả kiểm thử

- **Unit test mới:** 14/14 test pass (+9 test `notification_id`, +5 test `notification_service`).
- **Hồi quy toàn bộ mobile:** 261/261 test pass (`flutter test` hoàn tất trong ~15 giây).
- **Phân tích tĩnh:** `flutter analyze` 0 lỗi/cảnh báo trong code mới (chỉ còn 1 cảnh báo cũ không liên quan tại contract).
- **Kiểm chứng đột biến:**
  - Phần (a): Đổi `_fnvOffsetBasis` từ `0x811c9dc5` thành `0x811c9dc6` làm AC1 & AC6 fail; hoàn tác thì xanh lại 9/9 pass.
  - Phần (b): Đổi timezone sang `Asia/Tokyo` làm AC7 fail; hoàn tác thì xanh lại 5/5 pass.

## Bất biến kiến trúc & Tuân thủ quy định

- **Bất biến CD7:** Múi giờ cố định `Asia/Ho_Chi_Minh` (UTC+7). Kiểm tra tĩnh xác nhận không xuất hiện `tz.local`, `flutter_timezone`, `toLocal()`, `DateTime.now()`, hay `timeZoneOffset`.
- Không chạm vào bất kỳ file native Android/iOS nào (`AndroidManifest.xml`, `build.gradle.kts`) hay các file thuộc task 2.24/SCRUM-60.

## Điểm cần trao đổi với Bao (cho SCRUM-57 phần 2)

1. **Kiểu dữ liệu `scheduleId`:** Interface `ReminderScheduler` trong `core/contracts/` đang nhận `String scheduleId`, trong khi DB và model `LocalMedicationSchedule` dùng `int id`. Đề xuất đổi contract sang `int` khi viết `NotificationService`.
2. **Truy vấn store:** `LocalMedicationStore.getActiveSchedules` hiện lọc `ended_at IS NULL` ở tầng SQLite, khiến các lịch có hẹn ngày kết thúc trong tương lai bị loại bỏ trước khi vào generator. Cần bổ sung query phù hợp ở task sau để không bị sót lượt nhắc cuối.

## Thứ tự Merge

1. Merge PR nhánh `feat/2.07-notification-service` vào `main` tại submodule `frontend`.
2. Bump con trỏ submodule `frontend` trên repo superproject.
