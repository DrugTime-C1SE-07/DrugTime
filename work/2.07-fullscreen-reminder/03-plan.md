---
task: 2.07-fullscreen-reminder
stage: plan
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-08 11:11 +0700
content_hash: sha256:73d73b0d362e5973
inputs:
  01-requirement.md: sha256:541dbe91b87bef94
---

# 2.07-fullscreen-reminder · Kế hoạch kỹ thuật (Plan)

## 1. Giải pháp

### 1.1. Luồng thông báo toàn màn hình (Full-Screen Intent)
```
[AlarmManager kích hoạt]
       │
       ▼
[ScheduledNotificationReceiver]
       │
       ▼ (Android OS đánh giá trạng thái màn hình & lockscreen)
       ├─────────────────────────────────┬─────────────────────────────────┐
       ▼ (Màn hình khóa / Màn hình tắt)   ▼ (Máy đang mở khóa)               ▼ (App đang mở foreground)
[Bật màn hình & hiển thị Activity]   [Heads-Up Banner ở đỉnh màn hình]   [Nhận sự kiện thông báo qua callback]
  - showWhenLocked = true               - Không chiếm màn hình             - Tự động push AppRoutes.doseReminder
  - turnScreenOn = true                 - Có nút "Đã uống"                (Tuân thủ NT-11)
  - LockscreenPrivacyGate bọc ngoài     - Bấm vào mở DoseReminderScreen
```

### 1.2. Native Bridge cho Keyguard / Privacy Mask (Yêu cầu kỹ thuật 1)
- **Vấn đề**: Flutter thuần không có API native để nhận biết thiết bị đang khóa màn hình hay đã mở khóa.
- **Giải pháp Native Channel**:
  - Tạo `MethodChannel` tên `vn.drugtime.drugtime_mobile/keyguard` giữa Flutter và Android Native.
  - Phía Android ([MainActivity.kt](file:///e:/DrugTIme_main/frontend/mobile/android/app/src/main/kotlin/vn/drugtime/drugtime_mobile/MainActivity.kt)):
    - Gọi `KeyguardManager`:
      - `isKeyguardLocked`: Trả về `keyguardManager.isKeyguardLocked` (và `keyguardManager.isDeviceLocked` trên API 22+).
      - `requestDismissKeyguard`: Gọi `keyguardManager.requestKeyguardDismiss(...)` (API 26+) để kích hoạt màn hình nhập mã PIN / vân tay của Android.
  - Phía Flutter:
    - Tạo `KeyguardPlatform` abstraction (với `DefaultKeyguardPlatform` và `MockKeyguardPlatform`) giúp test unit 100% không phụ thuộc thiết bị.
    - Widget [LockscreenPrivacyGate](file:///e:/DrugTIme_main/frontend/mobile/lib/features/reminder/presentation/widgets/lockscreen_privacy_gate.dart):
      - Khi `isKeyguardLocked == true`: hiển thị Privacy Mask (chỉ hiện "Đến giờ uống thuốc", nút "Mở khóa để xem chi tiết / xác nhận").
      - Giới hạn bảo mật hệ thống: Android yêu cầu mở khóa trước khi thực hiện thao tác nhạy cảm trên màn hình khóa. Khi người dùng bấm nút xác nhận uống thuốc hoặc xem chi tiết, widget kích hoạt `requestDismissKeyguard()` để mở khóa máy trước khi thực hiện mutation dữ liệu dùng thuốc.
      - Khi `isKeyguardLocked == false`: bung toàn bộ giao diện `DoseReminderScreen` bên trong.

### 1.3. Cơ chế Cold Start Routing với `pendingPayload` (Yêu cầu kỹ thuật 2)
- **Vấn đề**: Khi app khởi động lạnh từ thông báo (cold start / terminated process), router và cây widget chưa được mount hoàn chỉnh. Nếu gọi điều hướng ngay lập tức sẽ bị mất sự kiện hoặc lỗi `Navigator operation requested with a context that does not include a Navigator`.
- **Giải pháp `pendingPayload`**:
  - Bổ sung `NotificationPayloadBuffer` (hoặc trường `pendingPayload` trong `NotificationService`):
    - Khi `main.dart` khởi động, gọi `getNotificationAppLaunchDetails()`. Nếu có notification launch payload, lưu vào `pendingPayload`.
    - Khi `MaterialApp` mount xong và `rootNavigatorKey.currentState != null`:
      Kiểm tra nếu có `pendingPayload`, rút ra và thực hiện điều hướng an toàn vào `AppRoutes.doseReminder`.
    - Lắng nghe sự kiện `onDidReceiveNotificationResponse` khi app đang chạy (foreground / background) để điều hướng tức thì.

### 1.4. Tích hợp mã nguồn từ `origin/main`
- Merge `origin/main` vào nhánh `feat/2.07-fullscreen-reminder`:
  - `build.gradle.kts`: Giữ desugaring `desugar_jdk_libs:2.1.4` từ `main`.
  - `pubspec.yaml`: Giữ `flutter_timezone: ^5.1.1` và `sqflite_common_ffi: ^2.3.3` từ `main`.
  - `reminder_scheduler.dart`: Đồng bộ interface `ReminderScheduler { Future<void> snooze(...); }` từ `main`.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `flutter_local_notifications-17.2.4` Java & Dart source | `AndroidNotificationDetails` hỗ trợ `fullScreenIntent: true` và `category: AndroidNotificationCategory.alarm`. Hàm `requestFullScreenIntentPermission()` xử lý trên Android 14+. |
| Android Developer Docs (`Notification.Builder.setFullScreenIntent`) | Full-screen intent chỉ bật Activity khi màn hình tắt hoặc thiết bị đang khóa. Khi máy đang mở khóa, hệ điều hành tự động hạ xuống Heads-Up Notification. |
| Android Developer Docs (`KeyguardManager`) | `keyguardManager.isKeyguardLocked` cung cấp trạng thái khóa; `requestKeyguardDismiss` cho phép ứng dụng yêu cầu mở khóa PIN/Pattern/biometric. |
| `origin/main:mobile/lib/app/router.dart` | Route `AppRoutes.doseReminder = '/reminders/dose'` đã sẵn sàng nhận `DoseReminderRouteArguments`. |
| `origin/main:mobile/lib/features/reminder/presentation/screens/dose_reminder_screen.dart` | Đã triển khai `DoseReminderScreen` đầy đủ. Giữ nguyên không sửa, bọc ngoài bằng `LockscreenPrivacyGate`. |
| `mobile/android/app/src/main/AndroidManifest.xml` | Đã có `SCHEDULE_EXACT_ALARM` và các receiver từ task 2.07. Cần thêm quyền `USE_FULL_SCREEN_INTENT` (cần kiểm trên LG) và thuộc tính lockscreen cho MainActivity. |

## 3. File sẽ thay đổi (ranh giới phạm vi)

<!-- scope.py đọc bảng này. Đường dẫn tính từ gốc submodule. -->

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| `frontend` | `mobile/android/app/src/main/AndroidManifest.xml` | Sửa | Khai báo `USE_FULL_SCREEN_INTENT`, `showWhenLocked`, `turnScreenOn` |
| `frontend` | `mobile/android/app/src/main/kotlin/vn/drugtime/drugtime_mobile/MainActivity.kt` | Sửa | `setShowWhenLocked`, `setTurnScreenOn`, và MethodChannel `KeyguardManager` |
| `frontend` | `mobile/android/app/build.gradle.kts` | Sửa | Đồng bộ desugaring `desugar_jdk_libs:2.1.4` từ `origin/main` |
| `frontend` | `mobile/pubspec.yaml` | Sửa | Đồng bộ các dependencies mới từ `origin/main` |
| `frontend` | `mobile/lib/core/notification/reminder_scheduler.dart` | Sửa | Đồng bộ interface từ `origin/main` và export scheduler |
| `frontend` | `mobile/lib/core/notification/reminder_notification_scheduler.dart` | Sửa | Thêm `fullScreenIntent: true`, category alarm, triển khai interface `snooze` |
| `frontend` | `mobile/lib/core/notification/notification_service.dart` | Sửa | Hỗ trợ launch details, pendingPayload buffer và request full-screen intent permission |
| `frontend` | `mobile/lib/core/platform/keyguard_service.dart` | Thêm | Abstraction Platform Channel giao tiếp với Android KeyguardManager |
| `frontend` | `mobile/lib/features/reminder/presentation/widgets/lockscreen_privacy_gate.dart` | Thêm | Widget bảo vệ quyền riêng tư NT-02 trên màn hình khóa qua KeyguardService |
| `frontend` | `mobile/lib/app/app.dart` | Sửa | Cung cấp `rootNavigatorKey` dùng chung cho MaterialApp và lắng nghe pendingPayload |
| `frontend` | `mobile/lib/app/router.dart` | Sửa | Bọc `DoseReminderScreen` bằng `LockscreenPrivacyGate` tại `AppRoutes.doseReminder` |
| `frontend` | `mobile/lib/main.dart` | Sửa | Khởi tạo NotificationService và xử lý notification launch khi khởi động |
| `frontend` | `mobile/test/core/notification/reminder_notification_scheduler_test.dart` | Sửa | Bổ sung test kiểm tra `fullScreenIntent: true` và category alarm |
| `frontend` | `mobile/test/core/platform/keyguard_service_test.dart` | Thêm | Test MethodChannel KeyguardService với mock platform |
| `frontend` | `mobile/test/features/reminder/lockscreen_privacy_gate_test.dart` | Thêm | Test widget `LockscreenPrivacyGate` ẩn/hiện tên thuốc theo trạng thái khóa máy |
| `frontend` | `mobile/test/features/reminder/notification_navigation_flow_test.dart` | Thêm | Test luồng điều hướng cold start với pendingPayload buffer |

*(Ghi chú: TUYỆT ĐỐI KHÔNG sửa `dose_reminder_screen.dart` theo yêu cầu).*

## 4. Checklist

- [ ] P1 [frontend] Tạo nhánh `feat/2.07-fullscreen-reminder` từ `feat/2.07-notification-scheduling`, chạy `git merge origin/main`, giải quyết xung đột `build.gradle.kts` (chọn desugar 2.1.4), `pubspec.yaml`, `reminder_scheduler.dart` — xong khi: merge commit hoàn tất và `flutter test` xanh.
- [ ] P2 [frontend] Cấu hình Android native (`AndroidManifest.xml`, `MainActivity.kt`) với quyền `USE_FULL_SCREEN_INTENT`, `showWhenLocked`, `turnScreenOn`, và MethodChannel `KeyguardManager` — AC: AC1 — xong khi: code biên dịch Android thành công.
- [ ] P3 [frontend] TDD cập nhật `ReminderNotificationScheduler`: Lên lịch với `fullScreenIntent: true`, category alarm, tiêu đề chung không lộ tên thuốc, triển khai `snooze` — file: `reminder_notification_scheduler.dart`, `reminder_notification_scheduler_test.dart` — AC: AC5, AC8 — xong khi: test đỏ rồi xanh, đột biến kiểm chứng.
- [ ] P4 [frontend] TDD tạo `KeyguardService` & `LockscreenPrivacyGate`: Giao tiếp Native Bridge, hiển thị Privacy Mask khi màn hình khóa (không lộ tên thuốc NT-02), bung chi tiết khi mở khóa, yêu cầu unlock trước khi mutate — file: `keyguard_service.dart`, `lockscreen_privacy_gate.dart`, `lockscreen_privacy_gate_test.dart` — AC: AC6 — xong khi: test đỏ rồi xanh.
- [ ] P5 [frontend] TDD tích hợp cold start routing với `pendingPayload` buffer: Lưu tạm payload khi khởi động lạnh, điều hướng an toàn khi router mount — file: `notification_service.dart`, `app.dart`, `main.dart`, `notification_navigation_flow_test.dart` — AC: AC3, AC4, AC7 — xong khi: unit test điều hướng vượt qua.
- [ ] P6 [frontend] Xác minh tổng thể: `flutter analyze`, `flutter test` (toàn bộ test pass, 0 fail, AC9), `dart format`, cài đặt lên thiết bị LG G7 bằng lệnh `flutter build apk --debug` rồi `flutter install -d LMG7103f11b938`, thực hiện `lg-test-checklist.md` — AC: AC9 — xong khi: toàn bộ pass và ghi log đầy đủ.

## 5. Test

### Unit & Widget

| Test dự kiến | AC | Submodule |
|---|---|---|
| Lên lịch thông báo có `fullScreenIntent == true` và `category == AndroidNotificationCategory.alarm` | AC5 | `frontend` |
| Tiêu đề và nội dung thông báo không chứa tên thuốc (NT-02) | AC5 | `frontend` |
| Native Bridge KeyguardService: Trả về trạng thái `isKeyguardLocked` từ platform | AC6 | `frontend` |
| Widget `LockscreenPrivacyGate` khi thiết bị khóa: chỉ hiện thông báo chung, che giấu tên thuốc | AC6 | `frontend` |
| Widget `LockscreenPrivacyGate` khi người dùng bấm xác nhận lúc máy khóa: kích hoạt request unlock | AC6 | `frontend` |
| Widget `LockscreenPrivacyGate` khi thiết bị mở khóa: hiển thị toàn bộ `DoseReminderScreen` bên trong | AC6 | `frontend` |
| Cold start routing: `pendingPayload` được lưu tạm và kích hoạt điều hướng khi Navigator sẵn sàng | AC4 | `frontend` |
| Payload rỗng hoặc sai format không làm app crash | AC7 | `frontend` |
| Fallback về thông báo thường khi không có quyền full screen intent | AC8 | `frontend` |
| Đột biến thủ công: tắt `fullScreenIntent`, test phải đỏ; hoàn tác | AC5 | `frontend` |

### Kiểm thử thủ công trên máy thật (LG G7 ThinQ, Android 13)

Lệnh cài đặt lên máy thử:
```powershell
cd frontend/mobile
flutter build apk --debug
flutter install -d LMG7103f11b938
```

| Kịch bản | AC / Kịch bản | Kết quả mong đợi |
|---|---|---|
| (A) Màn hình khóa | AC1, AC6 | Đến giờ: Màn hình bật sáng, hiển thị Activity đè lên lockscreen, `LockscreenPrivacyGate` che tên thuốc cho đến khi mở khóa |
| (B) Màn hình tắt | AC1 | Đến giờ: Màn hình tự động bật sáng và hiển thị Activity |
| (C) App bị vuốt tắt khỏi recents | AC1, AC4 | Đến giờ: Báo thức kích hoạt, cold start Activity đè khóa, `pendingPayload` đưa thẳng vào màn xác nhận |
| (D) Máy đang mở khóa, dùng app khác | AC2 | Đến giờ: Chỉ hiển thị Heads-Up Banner nổi ở đầu màn hình, không cưỡng bức chiếm toàn màn hình |
| (E) App đang mở trực tiếp (foreground) | AC3 | Đến giờ: Tự động chuyển thẳng vào màn hình xác nhận liều |

## 6. Migration

Không có.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| `superproject` | `feat/2.07-fullscreen-reminder` |
| `frontend` | `feat/2.07-fullscreen-reminder` |

## 8. Rủi ro

| Rủi ro | Mức độ | Cách giảm thiểu |
|---|---|---|
| Lộ tên thuốc trên màn hình khóa (vi phạm NT-02) | High | Đã xử lý bằng Native Bridge `KeyguardService` + `LockscreenPrivacyGate` |
| Mất sự kiện điều hướng khi Cold Start | Medium | Xử lý bằng cơ chế đệm `pendingPayload` cho đến khi `rootNavigatorKey` mount |
| Quyền `USE_FULL_SCREEN_INTENT` trên LG G7 (ROM TQ3A.230901.001) | Medium | Cần kiểm tra trên LG G7 xem quyền này có được cấp mặc định hay không qua lệnh `appops` |
| Google Play từ chối quyền `USE_FULL_SCREEN_INTENT` từ Android 14+ | Medium | Chuẩn bị văn bản giải trình tuân thủ điều trị (medical compliance alert); cài đặt fallback an toàn |

## 9. Câu hỏi mở

Không có (Q1 và Q2 đã được chốt).

## 10. Phát sinh

- Đã thống nhất bổ sung `KeyguardService` (Native Bridge) và `LockscreenPrivacyGate` để vừa thỏa mãn NT-02 vừa không cần can thiệp vào `dose_reminder_screen.dart` của dev.
- Thêm `pendingPayload` buffer để đảm bảo an toàn điều hướng khi cold start.

## Bước tiếp theo

- Đang chờ: Người dùng duyệt kế hoạch kỹ thuật (`03-plan.md`) bằng lệnh trong terminal:
  ```powershell
  python .agents/scripts/gate.py approve 2.07-fullscreen-reminder plan
  ```
- Việc cần làm: Sau khi người dùng duyệt plan, tiến hành P1 (tạo nhánh và merge `origin/main`).
- Cập nhật lần cuối: 2026-10-08 11:10, Antigravity
