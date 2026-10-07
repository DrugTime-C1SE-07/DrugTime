---
task: 2.07-notification-service
stage: implement
owner: DrugTime Team
started_at: 2026-10-07 15:10
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-07 15:41 +0700
content_hash: sha256:dd29809141a6be87
inputs:
  01-requirement.md: sha256:4ae915828960be7d
  03-plan.md: sha256:ca783680b9ac92f2
---

# 2.07-notification-service · Implement

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `cd frontend/mobile; flutter test test/core/notification/notification_id_test.dart` (Red: Compilation failed do chưa có `notification_id.dart`) | `evidence/implement-P1.log` |
| P2 | xong | Cài đặt `notification_id.dart`, chạy 9 test mới pass. Kiểm chứng đột biến đổi `_fnvOffsetBasis` từ `0x811c9dc5` thành `0x811c9dc6` làm 2 test đỏ (AC1 & AC6), hoàn tác thì xanh lại 9/9 pass. | `evidence/implement-P2.log` |
| P3 | xong | Thêm `flutter_local_notifications: ^17.2.2` và `timezone: ^0.9.4` vào `pubspec.yaml`, chạy `dart pub get` thành công (7 dependencies resolved/downloaded). | `evidence/implement-P3.log` |
| P4 | xong | `cd frontend/mobile; flutter test test/core/notification/notification_service_test.dart` (Red: Compilation failed do chưa có `notification_service.dart`) | `evidence/implement-P4.log` |
| P5 | xong | Cài đặt `notification_service.dart`, chạy 5 test mới pass. Kiểm chứng đột biến đổi `Asia/Ho_Chi_Minh` thành `Asia/Tokyo` làm AC7 đỏ, hoàn tác thì xanh lại 5/5 pass. | `evidence/implement-P5.log` |
| P6 | xong | `dart format` (4 files), `flutter analyze` (0 lỗi/cảnh báo mới, chỉ còn 1 unused_import cũ tại contract), `flutter test` toàn bộ mobile suite: 261/261 tests passed (247 baseline + 14 test mới). | `evidence/implement-final-mobile.log` |

## 2. File đã thay đổi

| Submodule | Nhánh | File | Mô tả thay đổi |
|---|---|---|---|
| frontend | `feat/2.07-notification-service` | `mobile/pubspec.yaml` | Thêm `flutter_local_notifications: ^17.2.2` và `timezone: ^0.9.4` (không thêm `flutter_timezone`) |
| frontend | `feat/2.07-notification-service` | `mobile/lib/core/notification/notification_id.dart` | Cài đặt `notificationIdFor` (FNV-1a 32-bit masked 31-bit), `NotificationPayload` (`serialize`, `tryParse`), và `detectIdCollisions` |
| frontend | `feat/2.07-notification-service` | `mobile/lib/core/notification/notification_service.dart` | Cài đặt `NotificationPlatform`, `DefaultNotificationPlatform`, và `NotificationService.init` cấu hình timezone `Asia/Ho_Chi_Minh`, channel Android và callback payload |
| frontend | `feat/2.07-notification-service` | `mobile/test/core/notification/notification_id_test.dart` | Bộ test TDD cho AC1..AC6 (4 test vectors Python, range 31-bit với 10k random inputs, fail-safe payload, collision handling) |
| frontend | `feat/2.07-notification-service` | `mobile/test/core/notification/notification_service_test.dart` | Bộ test TDD cho AC7..AC10 (init timezone, idempotency, callback action, static check cấm forbidden APIs) |

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| frontend/mobile | `flutter test` | 261 passed, 0 failed, 0 skipped | `evidence/implement-final-mobile.log` |
| frontend/mobile | `flutter analyze` | 0 issues trong code mới (1 warning cũ ở contract) | - |

## 4. Migration

Không có.

## 5. Ghi chú cho người review

- Đúng 5 file trong phạm vi plan được tạo/sửa (+ file tự sinh `pubspec.lock`).
- Thuật toán băm FNV-1a 32-bit (mask 31-bit) khớp chính xác 4 test vector đã tính trước bằng Python:
  1. `(1, 2026-10-07T01:00:00Z)` → `277106154`
  2. `(2, 2026-10-07T01:00:00Z)` → `280090069`
  3. `(1, 2026-10-07T01:00:01Z)` → `293883773`
  4. `(102, 2026-10-06T17:30:00Z)` → `259718614`
- Xử lý va chạm `detectIdCollisions`: Ghi log lỗi rõ ràng, bỏ qua lượt thứ hai, giữ nguyên `scheduledAt` ban đầu (tuyệt đối không tịnh tiến 1 giây).
- Tuân thủ nghiêm ngặt bất biến kiến trúc CD7: Múi giờ cố định `Asia/Ho_Chi_Minh` (`tz.getLocation('Asia/Ho_Chi_Minh')`).
- Bộ test tĩnh AC10 xác nhận 100% không chứa các lệnh cấm: `tz.local`, `flutter_timezone`, `toLocal()`, `DateTime.now()`, `timeZoneOffset`. Không dùng `hashCode` cho notification ID.
- Không chạm vào bất kỳ file native Android/iOS nào (`AndroidManifest.xml`, `build.gradle.kts`) hay các file thuộc task 2.24/SCRUM-60.
- Hai câu hỏi trao đổi với Bao (chủ `local_medication_store.dart` và contract):
  1. Interface `ReminderScheduler` đang để `String scheduleId` trong khi DB và model dùng `int id`.
  2. `LocalMedicationStore.getActiveSchedules` đang lọc `ended_at IS NULL` ở SQL nên có thể sót lượt cuối của lịch có hẹn kết thúc tương lai.

## 6. Phát sinh

- Không có phát sinh ngoài ý muốn. Các file ngoài phạm vi mà `scope.py` liệt kê là các artifact tài liệu cũ và file build platform Windows có sẵn từ các phiên trước.

## Bước tiếp theo

- Đang chờ: Người duyệt kiểm tra kết quả implement và phê duyệt giai đoạn `implement`.
- Lệnh duyệt cho reviewer: `python .agents/scripts/gate.py approve 2.07-notification-service implement`
- Cập nhật lần cuối: 2026-10-07 15:28, Antigravity
