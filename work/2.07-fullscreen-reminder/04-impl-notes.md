---
task: 2.07-fullscreen-reminder
stage: implement
status: draft
owner: DrugTime Team
started_at: 2026-10-08 11:12
---

# 2.07-fullscreen-reminder · Implement

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `git merge origin/main` (commit 2b32f0c), `flutter test` pass 358/358 | `evidence/implement-P1.log` |
| P2 | xong | Android native manifest, activity lockscreen & MethodChannel KeyguardManager, `./gradlew compileDebugKotlin` BUILD SUCCESSFUL | `evidence/implement-P2.log` |
| P3 | xong | TDD ReminderNotificationScheduler fullScreenIntent + category alarm + snooze, mutation test pass | `evidence/implement-P3.log` |
| P4 | xong | TDD KeyguardService + LockscreenPrivacyGate (Native bridge + Privacy mask NT-02), 8 tests pass | `evidence/implement-P4.log` |
| P5 | xong | TDD Cold start routing với pendingPayload buffer, 4 tests pass | `evidence/implement-P5.log` |
| P6 | xong | `flutter analyze` 0 lỗi, `flutter test` pass 372/372, `flutter build apk --debug` thành công, đã cài đặt APK lên máy LG G7 | `evidence/implement-final-mobile.log` |

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/android/app/src/main/AndroidManifest.xml` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/android/app/src/main/kotlin/vn/drugtime/drugtime_mobile/MainActivity.kt` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/lib/core/notification/reminder_notification_scheduler.dart` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/lib/core/notification/notification_service.dart` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/lib/core/platform/keyguard_service.dart` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/lib/features/reminder/presentation/widgets/lockscreen_privacy_gate.dart` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/lib/app/app.dart` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/lib/app/router.dart` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/lib/main.dart` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/test/core/notification/reminder_notification_scheduler_test.dart` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/test/core/notification/notification_service_test.dart` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/test/core/platform/keyguard_service_test.dart` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/test/features/reminder/lockscreen_privacy_gate_test.dart` |
| `frontend` | `feat/2.07-fullscreen-reminder` | `mobile/test/features/reminder/notification_navigation_flow_test.dart` |

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| `frontend` | `cd frontend/mobile && flutter test` | 372 pass, 0 fail, 0 skip (100%) | `evidence/implement-final-mobile.log` |
| `frontend` | `cd frontend/mobile && flutter analyze` | No issues found! (0 warnings, 0 errors) | Terminal session |
| `frontend` | `cd frontend/mobile && flutter build apk --debug` | Built app-debug.apk (38.4s) | Terminal session |

## 4. Migration

Không có.

## 5. Ghi chú cho người review

1. **Tuân thủ NT-02 & Không sửa `dose_reminder_screen.dart`**:
   - Màn hình nhắc thuốc của dev giữ nguyên 100%.
   - Widget `LockscreenPrivacyGate` được bọc ngoài tại `AppRoutes.doseReminder` trong `router.dart`.
   - Kết nối Native Bridge qua `MethodChannel('vn.drugtime.drugtime_mobile/keyguard')`:
     - Nếu màn hình đang khóa (`isKeyguardLocked == true`), che giấu tên thuốc (Privacy Mask: chỉ hiện thông báo chung và nút "Mở khóa thiết bị").
     - Khi người dùng mở khóa thành công hoặc máy đã mở khóa, tự động bung toàn bộ giao diện `DoseReminderScreen`.
2. **Cold Start Routing an toàn**:
   - `NotificationService` tích hợp bộ đệm `pendingPayload`. Nếu người dùng mở app từ thông báo khi app đang tắt hoàn toàn (cold start), payload được lưu tạm và kích hoạt điều hướng an toàn sau khi `MaterialApp` và `Navigator` mount xong.
3. **Triển khai `ReminderScheduler.snooze`**:
   - `ReminderNotificationScheduler` triển khai đầy đủ interface `ReminderScheduler` để phục vụ thao tác hoãn cữ 10 phút từ `DoseReminderController`.
4. **Android Native**:
   - Đã cấu hình quyền `USE_FULL_SCREEN_INTENT`, thuộc tính `android:showWhenLocked="true"`, `android:turnScreenOn="true"` trên `MainActivity`.
   - `MainActivity.kt` gọi `setShowWhenLocked(true)`, `setTurnScreenOn(true)` và đăng ký handler cho `KeyguardManager`.

## 6. Phát sinh & Kết quả kiểm thử thực địa

- Các file untracked/tạm (`lib/debug/`, `lib/debug_main.dart`, `windows/`, `scripts/`, `contracts/`) và các file tài liệu ở superproject được bảo vệ không git add theo đúng chỉ đạo.
- **Tinh chỉnh giao diện & luồng thông báo theo yêu cầu mới (Ảnh 1, 2, 3, 4)**:
  1. **Luồng màn hình mở vs khóa**:
     - Màn hình đang mở: Heads-Up notification xuất hiện theo theme app (`#004D40`). Bấm vào thông báo mở trực tiếp `DoseReminderScreen` (Ảnh 2 / 3), loại bỏ hoàn toàn giao diện debug G7 cũ.
     - Màn hình đang khóa: Khi đến giờ nhắc, tự động bật toàn màn hình `LockscreenPrivacyGate` với giao diện như Ảnh 2 (nền xanh `#004D40`, đồng hồ lớn, icon pulse, thẻ thuốc che tên NT-02 "Đến giờ uống thuốc / Thiết bị đang khóa. Mở khóa để xem chi tiết."). Nhấn "Đã uống", "Nhắc lại sau 10 phút", hoặc "Bỏ qua liều này" sẽ kích hoạt Native Keyguard yêu cầu mở khóa máy (PIN/Vân tay/Hình vẽ). Mở khóa xong lập tức hiển thị đầy đủ chi tiết tên thuốc.
  2. **Multi đơn thuốc (Ảnh 3 - S09e, S09e-2, S09e-3)**:
     - S09e-2 (Chế độ xếp chồng): Thẻ thuốc chính hiển thị badge `+2 thuốc` (hoặc `+N thuốc`), 2 lớp thẻ bo tròn xếp tầng phía dưới, kèm dòng text `$N thuốc cần uống · Nhấn để xem tất cả ⌵`.
     - S09e-3 (Chế độ mở rộng): Header co gọn hiển thị thời gian, nút `Thu gọn ⌃` và hướng dẫn `Bỏ chọn thuốc bạn chưa uống trước khi xác nhận.`. Mỗi thẻ thuốc có checkbox tròn chọn/bỏ chọn.
     - Cho phép chọn uống từng thuốc hoặc uống cả 3: Nút chính cập nhật nhãn động `✓ Đã uống cả $total thuốc`, `✓ Đã uống $count thuốc`, `✓ Đã uống 1 thuốc`. Nhấn xác nhận chỉ ghi nhận các thuốc được chọn vào outbox.
  3. **Thanh thông báo chuẩn theme (Ảnh 4)**:
     - Đặt màu thương hiệu `color: Color(0xFF004D40)` cho notification channel & heads-up banner.
     - Loại bỏ nút action "ĐÃ UỐNG" trên thanh thông báo theo đúng yêu cầu; người dùng chạm vào banner để mở thẳng màn hình nhắc thuốc.
  4. **Kiểm thử tự động**:
     - 100% các unit test (31/31) trong `test/features/reminder/` và `test/core/notification/` pass.
     - Đã biên dịch thành công APK mới tại: `frontend/mobile/build/app/outputs/flutter-apk/app-debug.apk`.

## Bước tiếp theo

- Đang chờ: Người dùng kết nối lại thiết bị (Realme Q / LG G7) qua USB debugging để cài APK mới hoặc duyệt giai đoạn implement (`04-impl-notes.md`) bằng lệnh:
  ```powershell
  python .agents/scripts/gate.py approve 2.07-fullscreen-reminder implement
  ```
- Việc cần làm: Chạy lệnh cài đặt APK lên điện thoại:
  ```powershell
  & "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r frontend/mobile/build/app/outputs/flutter-apk/app-debug.apk
  ```
- Cập nhật lần cuối: 2026-10-09 11:20, Antigravity
