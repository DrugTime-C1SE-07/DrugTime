---
task: 3.08-mobile-profile-form
stage: implement
status: draft
owner: Bao Nguyen
started_at: 2026-11-19 22:14 +0700
---

# 3.08-mobile-profile-form · Implement

## 1. Tiến độ

| Bước | Trạng thái | Kết quả | Bằng chứng |
|---|---|---|---|
| P1 Nối số liên hệ vào form | xong | Số điện thoại có thể nhập/chỉnh, được map thành `phone_number` cùng PUT `/profile`; chuỗi trống được bỏ khỏi request. Hiển thị lỗi `phone_change_unavailable` an toàn. | Đã đọc lại code nguồn; không chạy test theo yêu cầu người dùng. |
| P2 Lưu avatar theo tài khoản | xong | Preference dùng `flutter_secure_storage`, khóa theo user ID, chỉ đọc/ghi 6 asset cho phép; khôi phục khi session vào app, không xóa dữ liệu khi logout. Lỗi đọc/ghi có thông báo trong UI. | Đã đọc lại code nguồn; không chạy test theo yêu cầu người dùng. |
| P3 Vòng nền avatar | xong | Avatar có nền xanh nhạt và padding 6 px quanh vòng/ảnh bên trong; chữ cái giữ nguyên ở giữa vòng xanh đậm, không padding riêng. Form không có chiều cao/cân nặng. | Đã đọc lại code nguồn; không chạy test theo yêu cầu người dùng. |
| P4 Kiểm tra phạm vi | xong, có hạn chế metadata | Script trả OK, không báo file ngoài phạm vi; nhưng lại liệt kê file nguồn `[CHƯA SỬA]` do không đọc được git metadata submodule. | `evidence/implement-scope-phone-avatar.log` |

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| frontend | `feat/health-profile-UI` | `mobile/lib/app/app.dart`; `mobile/lib/features/profile/domain/entities/health_profile.dart`; `domain/entities/profile_failure.dart`; `domain/repositories/profile_avatar_preferences.dart`; `data/models/profile_api_mapper.dart`; `data/repositories/profile_preview_repository.dart`; `data/repositories/secure_profile_avatar_preferences.dart`; `presentation/state/profile_controller.dart`; `presentation/screens/personal_profile_screen.dart`; `presentation/widgets/avatar_picker_sheet.dart`; `presentation/widgets/profile_avatar.dart` |

Kết quả `python .agents/scripts/scope.py 3.08-mobile-profile-form --stage implement`: exit 0, không có file ngoài phạm vi; tuy vậy kết quả phát hiện thay đổi submodule không đáng tin cậy ở lượt này vì git không truy cập được `.git/modules/frontend` (`Permission denied`) và script đánh dấu các file vừa sửa `[CHƯA SỬA]`. Log: `evidence/implement-scope-phone-avatar.log`.

## 3. Kết quả test cuối

Không tạo/chạy test hoặc lint theo yêu cầu trực tiếp của người dùng. Các kết quả test trong `04` lịch sử trước đó không phải xác minh cho các thay đổi phone/avatar lần này.

## 4. Migration

Không có.

## 5. Ghi chú cho người review

- Phone là số liên hệ, không phải định danh đăng nhập. Form hiển thị dạng nội địa khi API trả E.164; khi lưu gửi chuỗi đã nhập. Backend hiện có xử lý chuẩn hóa/validation.
- Giá trị phone rỗng được bỏ khỏi request để giữ số đang lưu; không hỗ trợ xóa phone trong contract hiện tại.
- Avatar chỉ lưu local qua secure storage theo user ID; không gửi avatar tới backend. Asset đọc/ghi bị giới hạn trong danh sách 6 ảnh có sẵn.
- Khi đổi tài khoản, controller xóa state trong RAM rồi đọc preference của user mới. Thu hồi consent giữ avatar local nhưng xóa dữ liệu hồ sơ trong RAM.
- Scope script không nhận ra diff frontend do lỗi quyền đọc git metadata; cần môi trường có quyền đọc `.git/modules/frontend` để xác minh chính xác trạng thái submodule.

## 6. Phát sinh

- Không sửa backend hoặc API contract; API PUT `/profile` hiện đã hỗ trợ `phone_number`.
- Không chạy test/lint theo yêu cầu của người dùng.
- `git status` submodule lỗi `fatal: cannot chdir to '.git/modules/frontend': Permission denied`; scope script vẫn exit 0 nhưng báo file frontend `[CHƯA SỬA]`.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: người duyệt xem diff frontend (cần terminal có quyền đọc git metadata submodule) và chạy `python .agents/scripts/gate.py approve 3.08-mobile-profile-form implement`.
- Cập nhật lần cuối: 2026-11-19 22:14 +0700, Codex.
