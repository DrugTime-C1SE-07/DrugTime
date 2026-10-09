---
task: 2.07-fullscreen-reminder
title: Thông báo nhắc thuốc bật toàn màn hình trên màn hình khóa (Full-Screen Intent)
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-08 10:56 +0700
content_hash: sha256:541dbe91b87bef94
---

# 2.07-fullscreen-reminder · Thông báo nhắc thuốc bật toàn màn hình (Full-Screen Intent)

## 1. Mục tiêu

Khi đến giờ uống thuốc, DrugTime tự động bật màn hình và hiển thị giao diện nhắc nhở/xác nhận liều thuốc toàn màn hình ngay cả khi thiết bị đang khóa hoặc màn hình đang tắt (Full-Screen Intent trên Android). Đảm bảo tuân thủ nghiêm ngặt nguyên tắc bảo mật y tế NT-02 (không làm lộ danh tính bệnh nhân và tên thuốc trên màn hình khóa) bằng widget `LockscreenPrivacyGate` bọc ngoài màn hình nhắc thuốc, rơi về heads-up banner khi thiết bị đang mở khóa, và không làm hồi quy bất kỳ bài test tự động nào.

## 2. Phạm vi

### Trong phạm vi

- Cấu hình native Android:
  - Khai báo quyền `android.permission.USE_FULL_SCREEN_INTENT` trong `AndroidManifest.xml` (cần kiểm trên LG G7 xem quyền này có được cấp mặc định hay không).
  - Cấu hình `android:showWhenLocked="true"` và `android:turnScreenOn="true"` trên `<activity android:name=".MainActivity">`.
  - Thiết lập `setShowWhenLocked(true)` và `setTurnScreenOn(true)` trong `MainActivity.kt` cho Android 8.0+ (API 27+).
- Lên lịch thông báo Full-Screen qua `flutter_local_notifications` 17.2.4:
  - Bật cờ `fullScreenIntent: true` trong `AndroidNotificationDetails`.
  - Thiết lập kênh thông báo mức ưu tiên cao nhất (`Importance.max`, `Priority.high`), category `AndroidNotificationCategory.alarm`.
- Xử lý tương tác thông báo & Điều hướng ứng dụng:
  - Xử lý khởi động từ thông báo (`getNotificationAppLaunchDetails`) khi app đang tắt (cold start).
  - Lắng nghe sự kiện tương tác (`onDidReceiveNotificationResponse`) khi app đang chạy (foreground / background active).
  - Điều hướng tới màn hình xác nhận liều (`AppRoutes.doseReminder`) qua `rootNavigatorKey` được cung cấp từ ngoài widget tree.
- Tuân thủ quyền riêng tư NT-02 trên màn hình khóa qua `LockscreenPrivacyGate`:
  - Tiêu đề và nội dung thông báo hệ thống luôn ở dạng chung ("Đến giờ uống thuốc", "Vui lòng kiểm tra thuốc cần uống.").
  - **KHÔNG sửa `dose_reminder_screen.dart`**: Giữ nguyên implementation của dev.
  - Tạo widget mới `LockscreenPrivacyGate` bọc `DoseReminderScreen` tại `router.dart`.
  - Khi thiết bị đang bị khóa màn hình (Keyguard locked): `LockscreenPrivacyGate` hiển thị giao diện bảo vệ (Privacy Mask: chỉ hiện thông báo nhắc thuốc và nút "Mở khóa thiết bị để xem chi tiết / xác nhận", kèm nút nhanh "Đã uống cữ này"). Khi mở khóa thiết bị, widget lập tức hiển thị nội dung chi tiết bên trong.
- Fallback và giới hạn nền tảng:
  - Khi thiết bị đang mở khóa: kỳ vọng Android chỉ hiện heads-up notification (hành vi chuẩn của OS, không dùng hack can thiệp).
  - Kiểm tra quyền `USE_FULL_SCREEN_INTENT` trên Android 14+ (`requestFullScreenIntentPermission`); rơi về thông báo thường nếu bị từ chối.
- Tích hợp code mới từ `origin/main` (PR #24, #27, #28) vào nhánh `feat/2.07-fullscreen-reminder` qua `git merge origin/main`.

### Ngoài phạm vi

- Sửa đổi trực tiếp mã nguồn `dose_reminder_screen.dart` (đã được bọc ngoài bằng `LockscreenPrivacyGate`).
- Hack chiếm màn hình khi người dùng đang mở khóa sử dụng app khác (`SYSTEM_ALERT_WINDOW`, `draw over other apps`, hoặc `startActivity` nền cưỡng bức).
- Xử lý nền chuyên sâu (background headless engine / isolate) cho nút "Đã uống" khi app bị tắt hoàn toàn (thuộc phần 3 SCRUM-57).
- Nền tảng iOS (chưa có thiết bị iOS để kiểm thử).
- Thay đổi API contract backend (`contract_change: no`).

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `flutter_local_notifications-17.2.4` (pub cache) | `AndroidNotificationDetails` hỗ trợ tham số `fullScreenIntent: true` và `category: AndroidNotificationCategory.alarm`. Trên Android 14+, plugin cung cấp `requestFullScreenIntentPermission()` gọi native `NotificationManager.canUseFullScreenIntent()`. |
| Android Developer Docs (`Notification.Builder.setFullScreenIntent`) | Full-screen intent chỉ bật Activity khi màn hình tắt hoặc thiết bị đang khóa. Khi máy đang mở khóa, hệ điều hành tự động hạ xuống Heads-Up Notification để tránh gián đoạn người dùng. |
| Android Developer Docs (`setShowWhenLocked`, `setTurnScreenOn`) | Từ API 27+, Activity cần gọi `setShowWhenLocked(true)` và `setTurnScreenOn(true)` cùng manifest attribute tương ứng để hiển thị đè lên màn hình khóa và bật sáng màn hình. |
| `origin/main:mobile/lib/app/router.dart` | Đã có route `AppRoutes.doseReminder = '/reminders/dose'`, nhận `DoseReminderRouteArguments`. Bọc route này bằng `LockscreenPrivacyGate`. |
| `origin/main:mobile/lib/features/reminder/presentation/screens/dose_reminder_screen.dart` | Đã triển khai `DoseReminderScreen` đầy đủ với các nút xác nhận cữ thuốc, hoãn cữ (snooze), bỏ qua (skip). Giữ nguyên không sửa. |
| `mobile/lib/app/app.dart` & `main.dart` | `_navigatorKey` hiện là biến private bên trong `_DrugTimeAppState`. Cần chuyển thành `rootNavigatorKey` dùng chung để điều hướng từ ngoài widget tree. |
| `AGENTS.md` | Bất biến kiến trúc CD7 (múi giờ cố định `Asia/Ho_Chi_Minh`), NT-02 (không lộ tên thuốc/thông tin bệnh án trên màn hình khóa), phân loại rủi ro bảo mật dữ liệu y tế. |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `frontend` | Có | Thay đổi `mobile/android/`, `mobile/lib/core/notification/`, `mobile/lib/app/`, `mobile/lib/features/reminder/presentation/widgets/lockscreen_privacy_gate.dart`, `mobile/lib/main.dart` |
| `backend` | Không | Không thay đổi API hay cơ sở dữ liệu |
| `api_contract` | Không | Không thay đổi API contract |
| `tests` | Không | Không thay đổi E2E cross-service |
| `docs` | Không | Chưa cập nhật tài liệu chính thức |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: Toàn bộ thay đổi diễn ra ở tầng local notification và điều hướng native/Flutter trên client mobile. Không sửa request/response hay endpoint backend.
- Endpoint liên quan: Không có.

## 6. Vùng rủi ro và bất biến bị chạm

- **Quyền riêng tư dữ liệu sức khỏe (NT-02)**: Khi Activity bật lên trên màn hình khóa, không được làm lộ tên thuốc hoặc thông tin chẩn đoán y tế cho người ngoài nhìn thấy điện thoại khi chưa mở khóa. Giải quyết bằng `LockscreenPrivacyGate`.
- **Quyền `USE_FULL_SCREEN_INTENT` trên thiết bị thật LG G7**: Cần kiểm tra trên LG G7 xem ROM tùy biến Android 13 có cấp quyền này mặc định hay không.
- **Rủi ro chính sách Google Play Store**: Google Play thắt chặt việc sử dụng quyền `USE_FULL_SCREEN_INTENT` từ Android 14. Ứng dụng phải chuẩn bị giải trình tuân thủ điều trị (medical compliance alert) và có cơ chế fallback nếu quyền bị thu hồi.
- **Hành vi hệ điều hành khi máy mở khóa**: Phải tuân theo giới hạn chuẩn của Android (chỉ hiện heads-up), không lách luật bằng các quyền xâm nhập như `SYSTEM_ALERT_WINDOW`.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given thiết bị Android đang tắt màn hình hoặc đang khóa (lock screen), When đến giờ uống thuốc của một `ReminderOccurrence`, Then hệ điều hành tự động bật sáng màn hình và mở ứng dụng lên màn hình khóa với cờ `fullScreenIntent: true` | manual (LG G7) |
| AC2 | Given thiết bị đang mở khóa và người dùng đang ở ứng dụng khác, When thông báo nhắc thuốc kích hoạt, Then hệ điều hành chỉ hiển thị thông báo nổi đầu màn hình (Heads-Up Banner) kèm nút "Đã uống", không cưỡng bức chiếm toàn màn hình | manual (LG G7) |
| AC3 | Given người dùng đang mở trực tiếp ứng dụng DrugTime (foreground), When thông báo nhắc thuốc kích hoạt, Then ứng dụng tự động điều hướng thẳng vào màn hình nhắc liều thuốc `AppRoutes.doseReminder` (NT-11) | unit + widget |
| AC4 | Given ứng dụng đang bị tắt hoàn toàn (cold start) hoặc ở background, When người dùng bấm vào thông báo hoặc Heads-Up Banner, Then ứng dụng khởi động và mở đúng route `AppRoutes.doseReminder` với payload hợp lệ | unit + widget |
| AC5 | Given thông báo nhắc thuốc được gửi tới hệ thống Android, When kiểm tra thuộc tính notification, Then `fullScreenIntent` bằng `true`, `category` là `AndroidNotificationCategory.alarm`, tiêu đề và nội dung không chứa tên thuốc (NT-02) | unit |
| AC6 | Given thiết bị đang bị khóa màn hình (Keyguard locked), When màn hình nhắc thuốc bật lên, Then `LockscreenPrivacyGate` che giấu danh sách tên thuốc (Privacy Mask) và chỉ bung `DoseReminderScreen` đầy đủ sau khi người dùng mở khóa thiết bị | widget + manual |
| AC7 | Given thông báo mang payload bị rỗng hoặc định dạng JSON sai, When ứng dụng nhận sự kiện mở thông báo, Then ứng dụng bỏ qua an toàn, không bị crash (fail-safe) | unit |
| AC8 | Given quyền `USE_FULL_SCREEN_INTENT` bị thu hồi hoặc từ chối trên Android 14+, When lên lịch nhắc thuốc, Then hệ thống tự động rơi về thông báo nhắc nhở thông thường với độ ưu tiên cao | unit |
| AC9 | Given toàn bộ bộ test của `frontend/mobile` (gồm các test cũ từ 2.07, test mới từ `origin/main` sau khi merge, và các test mới của task này), When chạy `flutter test`, Then 100% test đều vượt qua (All tests passed, 0 fail), không có bất kỳ test nào bị hồi quy | unit |

## 8. Câu hỏi mở

Không có. (Người dùng đã chốt: Q1 chọn Phương án A với widget `LockscreenPrivacyGate` mới; Q2 chọn Phương án A merge `origin/main` vào nhánh `feat/2.07-fullscreen-reminder`).

## 9. Giả định & Quyết định đã chốt

- **Quyết định Q1**: Áp dụng Privacy Mask Mode. Không sửa `dose_reminder_screen.dart`, bọc ngoài bằng widget mới `LockscreenPrivacyGate`. Khi màn hình đang khóa, chỉ hiện thông báo chung và nút mở khóa / nút nhanh "Đã uống". Mở khóa xong mới hiện chi tiết thuốc.
- **Quyết định Q2**: Tích hợp mã nguồn bằng cách tạo nhánh `feat/2.07-fullscreen-reminder` từ `feat/2.07-notification-scheduling`, sau đó chạy `git merge origin/main`.
- **Cần kiểm trên LG**: Thiết bị thử nghiệm LG G7 ThinQ chạy Android 13 (API 33, ROM tùy biến TQ3A.230901.001) cần kiểm tra trực tiếp xem quyền `USE_FULL_SCREEN_INTENT` có được cấp mặc định khi cài đặt không.
- Múi giờ hệ thống luôn cố định là `Asia/Ho_Chi_Minh` (UTC+7) theo quyết định kiến trúc CD7.

## 10. Phát sinh

- `mobile/lib/main.dart` hiện tại chưa khởi tạo `NotificationService` và chưa chia sẻ `navigatorKey` ra ngoài. Cần cung cấp `rootNavigatorKey` cấp cao để phục vụ điều hướng thông báo.
- `mobile/lib/core/notification/reminder_scheduler.dart` trên `origin/main` đã được định nghĩa interface chuẩn `ReminderScheduler` với phương thức `snooze`. `ReminderNotificationScheduler` sẽ triển khai interface này.

## 11. Size

- `size`: M
- Lý do: Chạm đến cấu hình native Android (`AndroidManifest.xml`, `MainActivity.kt`), logic lên lịch notification nâng cao (`fullScreenIntent`), widget bảo vệ quyền riêng tư `LockscreenPrivacyGate` (NT-02), điều hướng router Flutter từ sự kiện native launch, và hợp nhất nhánh có xung đột nhỏ với `origin/main`.

## Bước tiếp theo

- Đang chờ: Người dùng duyệt requirement bằng lệnh trong terminal:
  ```powershell
  python .agents/scripts/gate.py approve 2.07-fullscreen-reminder requirement
  ```
- Việc cần làm: Sau khi người dùng duyệt requirement, tiến hành các bước theo `03-plan.md`.
- Cập nhật lần cuối: 2026-10-08 11:05, Antigravity
