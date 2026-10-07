---
task: 2.07-notification-service
stage: plan
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-07 15:14 +0700
content_hash: sha256:ca783680b9ac92f2
inputs:
  01-requirement.md: sha256:4ae915828960be7d
---

# 2.07-notification-service · Kế hoạch triển khai (Plan)

## 1. Giải pháp kỹ thuật

### Phần (a): ID thông báo tất định và Payload

#### 1. Thuật toán băm FNV-1a 32-bit (Mask 31-bit)
- Chuỗi canonical: `"$medicationScheduleId:$epochSeconds"`
  - `epochSeconds = scheduledAt.millisecondsSinceEpoch ~/ 1000` (giây UTC từ 1970-01-01).
- Tham số FNV-1a:
  - Offset basis: `0x811c9dc5` (2166136261)
  - FNV prime: `0x01000193` (16777619)
  - Vòng lặp băm từng byte UTF-8: `hash = ((hash ^ byte) * prime) & 0xFFFFFFFF`.
  - Kết quả masked 31-bit: `hash = hash & 0x7FFFFFFF` để luôn thuộc khoảng `[0, 2^31 - 1]`.

#### 2. Vector kiểm tra sinh bằng Python độc lập
Script Python độc lập (tính epoch bằng `int(dt.timestamp())`, không gõ tay):
```python
from datetime import datetime, timezone

def fnv1a_31(schedule_id: int, dt: datetime) -> tuple[int, int, str]:
    epoch_seconds = int(dt.timestamp())
    canonical = f"{schedule_id}:{epoch_seconds}"
    h = 0x811c9dc5
    for b in canonical.encode("utf-8"):
        h = ((h ^ b) * 0x01000193) & 0xffffffff
    return epoch_seconds, h & 0x7fffffff, canonical

vectors = [
    (1, datetime(2026, 10, 7, 1, 0, 0, tzinfo=timezone.utc)),
    (2, datetime(2026, 10, 7, 1, 0, 0, tzinfo=timezone.utc)),
    (1, datetime(2026, 10, 7, 1, 0, 1, tzinfo=timezone.utc)),
    (102, datetime(2026, 10, 6, 17, 30, 0, tzinfo=timezone.utc)),
]

for sid, dt in vectors:
    epoch, nid, canon = fnv1a_31(sid, dt)
    print(f"schedule_id={sid}, dt={dt.strftime('%Y-%m-%dT%H:%M:%SZ')} -> epoch={epoch}, canon='{canon}' -> id={nid}")
```

Kết quả vector kiểm tra độc lập (khẳng định Python và Dart sinh ra cùng kết quả trên cùng đầu vào):
| STT | schedule_id | scheduledAt (UTC) | epoch_seconds | Canonical String | notification_id |
|:---:|:---:|---|:---:|:---:|:---:|
| 1 | 1 | `2026-10-07T01:00:00Z` | `1791334800` | `"1:1791334800"` | `277106154` |
| 2 | 2 | `2026-10-07T01:00:00Z` | `1791334800` | `"2:1791334800"` | `280090069` |
| 3 | 1 | `2026-10-07T01:00:01Z` | `1791334801` | `"1:1791334801"` | `293883773` |
| 4 | 102 | `2026-10-06T17:30:00Z` | `1791307800` | `"102:1791307800"` | `259718614` |

#### 3. Phân tích va chạm (Collision Analysis)
- Không gian ID: $M = 2^{31} = 2,147,483,648$.
- Công thức Birthday Problem: $P \approx 1 - e^{-\frac{n(n-1)}{2M}}$.
- Kết quả tính toán chính xác bằng Python:
  - Với $n = 64$ thông báo đồng thời:
    $$P \approx 9.3877 \times 10^{-7} \approx 9.4\times 10^{-7} \quad (\sim 0.000094\%)$$
  - Với $n = 500$ thông báo đồng thời:
    $$P \approx 5.8090 \times 10^{-5} \approx 5.8\times 10^{-5} \quad (\sim 0.0058\%)$$
- **So sánh với phương án cấu trúc (Bit-packing):**
  - *Phương án cấu trúc:* Chia 31 bit thành `[Schedule ID: 11 bit] | [Day of year: 9 bit] | [Minute: 11 bit]`. Nhược điểm: Bị giới hạn cứng schedule ID tối đa là 2047, chu kỳ lặp sau 1 năm, code phức tạp.
  - *Phương án băm FNV-1a (được chọn):* Không giới hạn schedule ID hay năm, code cực ngắn (~15 dòng Dart thuần), phân phối đều, xác suất va chạm cực nhỏ (`~9.4e-7` với $n=64$).
- **Cơ chế xử lý khi va chạm:**
  - Cung cấp hàm `detectIdCollisions(Iterable<ReminderOccurrence> occurrences)`.
  - Khi phát hiện va chạm: **Ghi log lỗi rõ ràng và bỏ qua lượt thứ hai, giữ nguyên `scheduledAt` ban đầu**. Tuyệt đối không tự ý tịnh tiến 1 giây (vì việc đổi `scheduledAt` sẽ khiến hàm `cancelOccurrence` tính lại ID khác và không thể hủy thông báo chính xác).

#### 4. Cấu trúc Payload
- Model `NotificationPayload`:
  - `medicationScheduleId` (`int`)
  - `scheduledAt` (`DateTime`, UTC)
  - `serialize()`: Chuỗi JSON `{"schedule_id": 1, "scheduled_at": "2026-10-07T01:00:00.000Z"}`.
  - `tryParse(String? raw)`: Bắt mọi ngoại lệ định dạng, trả về `null` nếu chuỗi rác, thiếu trường, id không phải số, hoặc mốc giờ không phải UTC (an toàn, không crash app).

---

### Phần (b): Khởi tạo NotificationService

#### 1. Cấu hình gói và Múi giờ
- Thêm vào `pubspec.yaml`:
  - `flutter_local_notifications: ^17.2.2`
  - `timezone: ^0.9.4`
  - *(Lưu ý: Không thêm `flutter_timezone`; nhánh 2.24 từng thêm nhầm đã được gỡ bỏ sạch ở commit 4346605).*
- Khởi tạo timezone:
  - Gọi `tz.initializeTimeZones()` từ `package:timezone/data/latest_all.dart`.
  - Khởi tạo `final location = tz.getLocation('Asia/Ho_Chi_Minh')`. Tuyệt đối không dùng `tz.local`.

#### 2. Cấu hình nền tảng và Idempotency
- Khởi tạo Android: `AndroidInitializationSettings('@mipmap/ic_launcher')`.
- Kênh thông báo:
  - `AndroidNotificationChannel('drugtime_reminder_channel', 'Nhắc uống thuốc', description: 'Thông báo nhắc uống thuốc đúng giờ', importance: Importance.max)`.
- Khởi tạo iOS:
  - `DarwinInitializationSettings(requestAlertPermission: false, requestBadgePermission: false, requestSoundPermission: false)`.
- Abstraction phục vụ Unit Test:
  - Tạo `NotificationPlatform` abstract class bọc `FlutterLocalNotificationsPlugin`, tiêm `MockNotificationPlatform` trong unit test để kiểm tra khởi tạo mà không cần thiết bị thật.

---

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `mobile/pubspec.yaml` | Cần bổ sung `flutter_local_notifications: ^17.2.2` và `timezone: ^0.9.4`. |
| `mobile/lib/core/notification/reminder_occurrence_generator.dart` | Đã có `ReminderOccurrence` với `medicationScheduleId` và `scheduledAt` (UTC). |
| `mobile/android/app/build.gradle.kts` | Chưa cấu hình desugaring. Giữ nguyên cho SCRUM-61. |
| `mobile/android/app/src/main/AndroidManifest.xml` | Icon `@mipmap/ic_launcher`. Giữ nguyên cho SCRUM-61. |

## 3. File sẽ thay đổi (ranh giới phạm vi)

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | `mobile/pubspec.yaml` | Sửa | Thêm 2 dependency `flutter_local_notifications: ^17.2.2` và `timezone: ^0.9.4` |
| frontend | `mobile/lib/core/notification/notification_id.dart` | Thêm | Hàm băm FNV-1a `notificationIdFor`, kiểm tra va chạm, model `NotificationPayload` |
| frontend | `mobile/lib/core/notification/notification_service.dart` | Thêm | Lớp `NotificationService`, interface `NotificationPlatform`, cấu hình timezone và kênh |
| frontend | `mobile/test/core/notification/notification_id_test.dart` | Thêm | Bộ test unit TDD cho phần (a): vector băm, range 31-bit, round-trip payload |
| frontend | `mobile/test/core/notification/notification_service_test.dart` | Thêm | Bộ test unit TDD cho phần (b): kiểm tra init, timezone, idempotency, callback |

## 4. Checklist

- [ ] P1 [frontend] Viết bộ test `mobile/test/core/notification/notification_id_test.dart` phủ AC1..AC6 (chạy test xác nhận đỏ)
- [ ] P2 [frontend] Cài đặt `mobile/lib/core/notification/notification_id.dart` cho đến khi toàn bộ test của P1 xanh
- [ ] P3 [frontend] Thêm `flutter_local_notifications: ^17.2.2` và `timezone: ^0.9.4` vào `mobile/pubspec.yaml`, chạy `flutter pub get`
- [ ] P4 [frontend] Viết bộ test `mobile/test/core/notification/notification_service_test.dart` phủ AC7..AC10 (chạy test xác nhận đỏ)
- [ ] P5 [frontend] Cài đặt `mobile/lib/core/notification/notification_service.dart` cho đến khi toàn bộ test của P4 xanh
- [ ] P6 [frontend] Kiểm tra hồi quy toàn bộ `flutter test` và `flutter analyze`; format code bằng `dart format`

## 5. Test

### Unit

| Test dự kiến | AC | Submodule |
|---|---|---|
| `notificationIdFor returns deterministic IDs matching Python test vectors` | AC1 | frontend |
| `notificationIdFor produces distinct IDs for different schedules or times` | AC2 | frontend |
| `notificationIdFor produces IDs strictly in [0, 2^31 - 1] across 10000 random inputs` | AC3 | frontend |
| `notificationIdFor throws ArgumentError for non-UTC scheduledAt` | AC4 | frontend |
| `NotificationPayload round-trips valid data and returns null on corrupt data` | AC5 | frontend |
| `detectIdCollisions detects colliding occurrences, logs warning and skips duplicate without shifting scheduledAt` | AC6 | frontend |
| `NotificationService.init initializes Asia/Ho_Chi_Minh and configures notification channels` | AC7 | frontend |
| `NotificationService.init is idempotent when called repeatedly` | AC8 | frontend |
| `NotificationService forwards parsed NotificationPayload when action is received` | AC9 | frontend |
| `Static check: notification code does not reference tz.local or DateTime.now` | AC10 | frontend |

### Tích hợp

Không có.

## 6. Migration

Không có.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| `frontend` | `feat/2.07-notification-service` |

## 8. Rủi ro

| Rủi ro | Mức độ | Cách giảm thiểu |
|---|---|---|
| Va chạm ID thông báo | Thấp | Xác suất `~9.4e-7` (với $n=64$). Hàm `detectIdCollisions` phát hiện va chạm, ghi log cảnh báo và bỏ qua lượt thứ hai mà không đổi `scheduledAt`. |
| Trôi múi giờ nếu dùng `tz.local` | Cao | Cố định `Asia/Ho_Chi_Minh` bằng `tz.getLocation('Asia/Ho_Chi_Minh')`, kiểm tra cấm `tz.local` qua test và grep. |

## 9. Câu hỏi mở

- Ghi nhận 2 câu hỏi trao đổi với Bao (kiểu `scheduleId` và query `getActiveSchedules` loại `ended_at IS NULL`).

## 10. Phát sinh

- Không có.

## Bước tiếp theo

- Đang chờ: Người duyệt phê duyệt `01-requirement.md`.
- Việc cần làm: Người dùng chạy `python .agents/scripts/gate.py approve 2.07-notification-service requirement` trong terminal.
- Cập nhật lần cuối: 2026-10-07 14:55, Antigravity
