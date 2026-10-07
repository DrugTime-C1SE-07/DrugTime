---
task: 2.07-notification-service
stage: review
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-07 15:52 +0700
content_hash: sha256:98d6e873a84b2948
inputs:
  01-requirement.md: sha256:4ae915828960be7d
  03-plan.md: sha256:ca783680b9ac92f2
  04-impl-notes.md: sha256:dd29809141a6be87
  05-test-report.md: sha256:f6fe368a08eb7e68
---

# 2.07-notification-service · Review

## 1. Kết luận

**Đạt**

## 2. Phạm vi đã review

| Submodule | Lệnh diff |
|---|---|
| `frontend` | `git -C frontend diff feat/2.07-reminder-occurrences...HEAD` (Commit [`461568a`](https://github.com/DrugTime-C1SE-07/DrugTime-frontend/commit/461568ab87194fd0f24181b67ef337e1b31793b6)) |

Kết quả `scope.py --stage implement`:
- Đúng 5 file trong phạm vi plan (+ file tự sinh `pubspec.lock`).
- Không chạm file native hay bất kỳ file nào ngoài phạm vi đã duyệt.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | **Đạt**: Đầy đủ AC1..AC10, khớp chính xác 4 test vector Python độc lập, range 31-bit, xử lý va chạm không làm lệch giờ, timezone Asia/Ho_Chi_Minh, payload fail-safe, init idempotent. |
| Phạm vi | **Đạt**: Chỉ thay đổi các file khai báo trong plan. |
| Contract | **Đạt**: Task thuần client, không thay đổi hợp đồng API backend. |
| Bất biến kiến trúc | **Đạt**: Tuân thủ tuyệt đối CD7 (cố định múi giờ `Asia/Ho_Chi_Minh` UTC+7). Không gọi `tz.local`, `toLocal()`, `DateTime.now()`, hay `timeZoneOffset`. |
| Bảo mật | **Đạt**: Không chứa secret, token, hay thông tin nhạy cảm. |
| Xử lý lỗi | **Đạt**: `NotificationPayload.tryParse` an toàn, không làm crash app với payload rác; `notificationIdFor` fail-fast với `ArgumentError` khi không phải UTC; `NotificationService.location` fail-fast với `StateError` khi chưa init. |
| Hiệu năng | **Đạt**: FNV-1a 32-bit thực thi $O(L)$ nhanh, nạp timezone 1 lần duy nhất, khởi tạo idempotent. |
| Chất lượng test | **Đạt**: 14 unit test mới rõ ràng, kiểm chứng đột biến đều bắt được lỗi, toàn bộ 261 test mobile pass. |
| Dễ đọc và nhất quán | **Đạt**: Code tinh gọn, chuẩn phong cách Dart, tài liệu doc tiếng Việt đầy đủ, có ponytail comment ghi nhận điểm mở rộng tương lai. |
| Đối chiếu 04/05 với log trong `evidence/` | **Đạt**: Toàn bộ kết quả đối chiếu khớp 100% với log thực thi (`implement-P1.log` đến `implement-P5.log`, `implement-final-mobile.log`, `test-integration.log`). |

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| - | - | Không có phát hiện (0 Critical, 0 High, 0 Medium, 0 Low) | - |

## 5. Mô tả PR

### Submodule `frontend` (`feat/2.07-notification-service` -> `main`)

```markdown
## Summary
Triển khai SCRUM-57 phần 1 (task 2.07):
- Thuật toán sinh Notification ID tất định (FNV-1a 32-bit masked 31-bit) từ `(medicationScheduleId, scheduledAt)`.
- Model `NotificationPayload` đóng gói và giải mã an toàn JSON payload gắn vào thông báo.
- Hàm `detectIdCollisions` phát hiện va chạm ID, ghi log lỗi và bỏ qua lượt trùng mà không thay đổi `scheduledAt`.
- Thêm dependency `flutter_local_notifications: ^17.2.2` và `timezone: ^0.9.4` (không thêm `flutter_timezone`).
- Lớp `NotificationService` và abstraction `NotificationPlatform` khởi tạo timezone `Asia/Ho_Chi_Minh`, tạo kênh thông báo Android `drugtime_reminder_channel` và chuyển tiếp action callback.

## Acceptance Criteria & Test Evidence
- AC1..AC6: Phủ bởi `mobile/test/core/notification/notification_id_test.dart` (khớp 4 vector Python độc lập, range 31-bit với 10k random samples, round-trip, collision handling).
- AC7..AC10: Phủ bởi `mobile/test/core/notification/notification_service_test.dart` (init channel, Asia/Ho_Chi_Minh, idempotency, callback action, static check cấm API cấm).
- Toàn bộ suite test mobile: 261 passed, 0 failed.

## Notes & Open Questions
- Tuân thủ CD7 (múi giờ cố định UTC+7).
- Hai câu hỏi trao đổi với Bao cho SCRUM-57 phần 2:
  1. Interface `ReminderScheduler` đang để `String scheduleId` trong khi DB/model dùng `int id`.
  2. `LocalMedicationStore.getActiveSchedules` đang lọc `ended_at IS NULL` ở SQL nên có thể sót lượt cuối của lịch có hẹn kết thúc tương lai.
```

### Superproject (PR bump con trỏ `frontend`)

```markdown
## Summary
Cập nhật con trỏ submodule `frontend` lên commit đã merge của nhánh `feat/2.07-notification-service` (SCRUM-57 phần 1: ID thông báo tất định và NotificationService.init).

## Thứ tự merge
1. Merge PR submodule `frontend`.
2. Merge PR bump submodule `frontend` trên superproject.
```

## 6. Ghi chú cho quy trình

- Quy trình TDD triển khai theo 2 pha (a) logic thuần Dart trước, (b) plugin và timezone sau diễn ra rất trơn tru, cô lập tốt các vùng thay đổi.

## Bước tiếp theo

- Đang chờ: Người duyệt xem xét và phê duyệt `06-review.md`.
- Việc cần làm: Người dùng chạy `python .agents/scripts/gate.py approve 2.07-notification-service review` trong terminal.
- Cập nhật lần cuối: 2026-10-07 15:50, Antigravity
