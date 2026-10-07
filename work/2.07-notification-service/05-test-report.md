---
task: 2.07-notification-service
stage: test
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-07 15:48 +0700
content_hash: sha256:f6fe368a08eb7e68
inputs:
  01-requirement.md: sha256:4ae915828960be7d
  03-plan.md: sha256:ca783680b9ac92f2
  04-impl-notes.md: sha256:dd29809141a6be87
---

# 2.07-notification-service · Test tích hợp

## 1. Môi trường

- Lệnh chuẩn bị (reset DB, khởi động service): Không có (task thuần client-side logic tại submodule `frontend/mobile`, không phụ thuộc backend hay DB Supabase).
- Nhánh của vùng test: `feat/2.07-notification-service` trong submodule `frontend`.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Test | Kết quả |
|---|---|---|
| AC1 | `notificationIdFor returns deterministic IDs matching Python test vectors` | pass |
| AC2 | `notificationIdFor produces distinct IDs for different schedules or times` | pass |
| AC3 | `notificationIdFor produces IDs strictly in [0, 2^31 - 1] across 10000 random inputs` | pass |
| AC4 | `notificationIdFor throws ArgumentError for non-UTC scheduledAt` | pass |
| AC5 | `NotificationPayload round-trips valid data and returns null on corrupt data` | pass |
| AC6 | `detectIdCollisions detects colliding occurrences, logs warning and skips duplicate without shifting scheduledAt` | pass |
| AC7 | `NotificationService.init initializes Asia/Ho_Chi_Minh and configures notification channels` | pass |
| AC8 | `NotificationService.init is idempotent when called repeatedly` | pass |
| AC9 | `NotificationService forwards parsed NotificationPayload when action is received` | pass |
| AC10 | `Static check: notification code does not reference tz.local or DateTime.now` | pass |

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Test | Kết quả |
|---|---|---|
| Tất định thuật toán (AC1) | 4 test vector cố định độc lập bằng Python (khớp chính xác từng bit) | pass |
| An toàn không gian số nguyên (AC3) | 10.000 mẫu ngẫu nhiên không vượt quá khoảng `[0, 2^31 - 1]` | pass |
| Không lệch mốc giờ khi va chạm (AC6) | Giữ nguyên `scheduledAt` ban đầu, bỏ qua lượt thứ hai, ghi log cảnh báo | pass |
| Idempotency khởi tạo dịch vụ (AC8) | Gọi `NotificationService.init()` liên tiếp hoàn thành bình thường | pass |
| Bất biến múi giờ CD7 (AC7, AC10) | Timezone cố định `Asia/Ho_Chi_Minh`, cấm `tz.local`, `flutter_timezone`, `toLocal()`, `DateTime.now()` | pass |

## 4. Toàn bộ bộ test tích hợp

- Lệnh: `cd frontend/mobile && flutter test`
- Kết quả: 261 passed, 0 failed, 0 skipped (15 giây)
- Log: `evidence/test-integration.log`
- `scope.py --stage test`: Đã đối chiếu (code đã commit trong submodule `frontend`, không sửa file ngoài phạm vi)

## 5. Lỗi sản phẩm tìm thấy

Không có.

## 6. Test không ổn định hoặc bị skip

Không có.

## 7. Phát sinh

- Không có.

## Bước tiếp theo

- Đang chờ: Người duyệt phê duyệt `05-test-report.md`.
- Việc cần làm: Người dùng chạy `python .agents/scripts/gate.py approve 2.07-notification-service test` trong terminal.
- Cập nhật lần cuối: 2026-10-07 15:47, Antigravity
