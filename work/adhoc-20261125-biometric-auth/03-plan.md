---
task: adhoc-20261125-biometric-auth
stage: plan
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-25 16:59 +0700
content_hash: sha256:3ffb1d77cca7d71b
inputs:
  01-requirement.md: sha256:8b92aa54e07435ff
---

# adhoc-20261125-biometric-auth · Plan

## 1. Giải pháp

### Thành phần

Mọi thay đổi nằm trong `frontend/mobile`. Không đổi backend, contract, schema.

| Thành phần | Vai trò |
|---|---|
| `AppLockSettingsStore` (mới) | Lưu cờ bật/tắt khóa trong `flutter_secure_storage` qua `SecureStorage` (khóa `app_lock_enabled_v1`); có bản `Memory…` cho test, cùng pattern `AuthSessionStore`. |
| `DeviceAuthenticator` (mới) | Interface mỏng bọc `local_auth`: `isDeviceSupported()`, `authenticate(reason)` với `biometricOnly: false` (cho Face ID, vân tay, mã khóa màn hình). Cho phép mock trong test. |
| `AppLockController` (mới, `ChangeNotifier`) | Trạng thái `enabled`, `locked`, `obscured`. Hàm: `load()`, `enable()` (xác thực trước, rồi mới lưu), `disable()`, `unlock()`, `onLifecycle(state)`, `onSignedOut()`. Chống gọi `authenticate` chồng nhau (cờ `_authenticating`). |
| `AppLockGate` (mới, widget) | Gắn vào `MaterialApp.builder` (ngoài `AccountDeletionGate`). `Stack`: nội dung app, lớp che (khi `obscured`), màn khóa (khi `locked`). Màn khóa chặn mọi thao tác chạm và lệnh đọc màn hình bên dưới (`ExcludeSemantics`/`AbsorbPointer`). Cung cấp `AppLockScope` (InheritedNotifier) để màn Cài đặt đọc/đổi trạng thái. |
| `AppLockScreen` (mới) | Logo, câu "DrugTime đang khóa", nút "Mở khóa" (gọi lại `unlock`), nút "Đăng xuất". Tự gọi prompt một lần sau frame đầu tiên khi hiện. |
| `KeyguardPlatform` (sửa) | Thêm `consumeUserLeftApp()` và `setRecentsPrivacy(bool)` trên channel có sẵn `vn.drugtime.drugtime_mobile/keyguard`. |
| `MainActivity.kt` (sửa) | `FlutterActivity` → `FlutterFragmentActivity` (`local_auth` yêu cầu). Ghi cờ `userLeft = true` trong `onUserLeaveHint()` và trong `onPause()` khi `PowerManager.isInteractive == false` (tắt màn hình). Method `consumeUserLeftApp` trả cờ rồi reset. `setRecentsPrivacy` gọi `setRecentsScreenshotEnabled(!on)` trên API ≥ 33. |
| Cài đặt (sửa) | Dòng "Khóa ứng dụng" có `Switch` trong mục bảo mật của `ProfileSettingsScreen`. |

### Luồng

1. **Khởi động lạnh**: `main.dart` gọi `appLock.load()` song song với đọc phiên (trước `runApp`, trong lúc đang hiện `_SessionLoadingApp`). Nếu `enabled` và đã đăng nhập thì `locked = true`. Trong lúc chưa `load` xong, gate coi như `obscured` (fail-closed: không lộ nội dung).
2. **Rời app**: `didChangeAppLifecycleState` trong `_DrugTimeAppState` chuyển cho `appLock.onLifecycle`:
   - `inactive`/`hidden`/`paused` và `enabled`: `obscured = true` (lớp che cho ảnh app switcher trên iOS).
   - `paused` trên iOS: đặt `_pendingLock = true` (iOS chỉ `paused` khi app thực sự vào nền; hộp thoại Face ID, xin quyền, `UIImagePicker` chỉ gây `inactive`).
   - `resumed`: Android hỏi `consumeUserLeftApp()`; iOS dùng `_pendingLock`. Đúng thì `locked = true`, sai thì bỏ `obscured`.
3. **Mở khóa**: `unlock()` gọi `authenticate`; thành công thì `locked = obscured = false`; thất bại/hủy thì giữ màn khóa.
4. **Đăng xuất / 401**: controller nghe `AuthController`; khi `isAuthenticated` chuyển false thì `onSignedOut()` xóa cờ trong store, `enabled = locked = false`. Nút "Đăng xuất" trên màn khóa gọi `AuthController.signOut()`.
5. **Màn nhắc liều trên màn hình khóa** (Q2: không cần mở khóa): gate nhận một `ValueListenable<String?>` tên route trên cùng (từ `NavigatorObserver` mới gắn vào `navigatorObservers`). Nếu route trên cùng là `AppRoutes.doseReminder` thì gate không hiện màn khóa và không tự gọi prompt; khi route đó đóng, màn khóa hiện lại nếu vẫn `locked`. Hành động `actionTakeDose` trên thông báo (`reminder_notification_scheduler.dart:233`) không đi qua UI nên không bị ảnh hưởng.

### Vì sao dùng `onUserLeaveHint` thay cho danh sách ngoại lệ

Trên Android, app tự mở activity khác (chọn ảnh `image_picker`, xin quyền `permission_handler`, chọn nhạc chuông `ReminderSoundChannel`, `openAppSettings`) cũng gây `paused`. Cách 1 là bọc từng chỗ gọi (≥ 7 chỗ, dễ sót khi thêm tính năng). Cách 2 (chọn): `onUserLeaveHint` chỉ được gọi khi người dùng tự rời app (Home, Recents), cộng với kiểm tra tắt màn hình. Không phải sửa chỗ gọi nào, tính năng mới không cần biết đến app lock.

Bỏ phương án hẹn giờ (grace period vài giây) vì trái với yêu cầu "khóa ngay" đã chốt ở Q3.

### Đối chiếu bất biến

- Bất biến 1, 4: không đổi cách gọi API, không dùng Supabase key, không cache quyết định phân quyền.
- Bất biến 5 (ghi nhận liều): không chạm outbox/đồng bộ; app lock chỉ là lớp UI. Màn nhắc liều được miễn khóa (luồng 5).
- Bí mật: chỉ lưu cờ boolean; không log token hay kết quả xác thực.

### Quyết định nghiệp vụ áp dụng

Không áp dụng tài liệu nghiệp vụ trong `docs` (đã đối chiếu ở `01` mục 3: không có quyết định về sinh trắc/khóa ứng dụng). Truy vết theo quyết định của người dùng ghi ở `01` mục 9:

| Quy tắc (nguồn) | AC | Bước | Test |
|---|---|---|---|
| Q1: tính năng tùy chọn, giữ phiên | AC2, AC4d, AC7 | P3, P6, P8 | `app_lock_controller_test`, `app_lock_settings_test` |
| Q3: khóa ngay khi rời app / khóa màn hình | AC3, AC4, AC4b | P3, P4, P5, P7 | `app_lock_controller_test`, `app_lock_gate_test`, manual M1–M3 |
| Q4: Face ID / vân tay / mã khóa màn hình | AC1, AC5 | P2, P6, P8 | `device_authenticator_test`, `app_lock_gate_test` |
| Q2 (mặc định): nhắc liều không cần mở khóa | AC8 | P6, P7 | `app_lock_gate_test`, manual M5 |
| Chống xem trộm (app switcher) | AC4c | P4, P5, P6 | `app_lock_gate_test`, manual M4 |

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `frontend/mobile/lib/app/app.dart:225,441,957` | `_DrugTimeAppState` đã là `WidgetsBindingObserver`; `MaterialApp.builder` đang bọc `AccountDeletionScope/Gate`, `CaptureScope`; có `navigatorObservers`. Điểm gắn gate và lifecycle. |
| `frontend/mobile/lib/main.dart:74,77,189` | Tạo `SecureAuthSessionStore`, `AuthController`, rồi `runApp(DrugTimeApp(...))`; chỗ tạo và `load` controller. |
| `frontend/mobile/lib/features/auth/presentation/state/auth_controller.dart:243,263` | `handleUnauthorized()` và `signOut()` đều `notifyListeners`; nghe được để reset khóa. |
| `frontend/mobile/lib/features/auth/data/sources/auth_session_store.dart` | Pattern store: interface + `Secure…` + `Memory…`. |
| `frontend/mobile/lib/core/storage/secure_storage.dart` | `read/write/delete` theo key; dùng lại. |
| `frontend/mobile/lib/core/platform/keyguard_service.dart` | `KeyguardPlatform` + `DefaultKeyguardPlatform` qua MethodChannel, nuốt lỗi trả mặc định. Mở rộng tại đây. |
| `frontend/mobile/android/.../MainActivity.kt` | `FlutterActivity`, `setShowWhenLocked(true)` + `setTurnScreenOn(true)`: app hiện trên màn hình khóa (cho màn nhắc liều); có channel keyguard và `ReminderSoundChannel` dùng `startActivityForResult`. |
| `frontend/mobile/android/app/src/main/res/values/styles.xml` | Theme `@android:style/Theme.Light.NoTitleBar` (không phải AppCompat). |
| `frontend/mobile/lib/app/router.dart:289-300` | Route `doseReminder` bọc `LockscreenPrivacyGate`; tên route để miễn khóa. |
| `frontend/mobile/lib/core/notification/reminder_notification_scheduler.dart:233` | `actionTakeDose` xử lý qua callback thông báo, không qua màn hình. |
| `frontend/mobile/lib/features/profile/presentation/screens/profile_settings_screen.dart` | Dùng `ProfileFlowSection`/`ProfileFlowRow(trailing: Switch)`; nơi thêm công tắc. |
| Lệnh grep `request()|pickImage|openAppSettings|startActivityForResult` | 7+ chỗ mở activity ngoài; lý do chọn `onUserLeaveHint`. |
| `frontend/mobile/pubspec.yaml` | Chưa có `local_auth`; có `flutter_secure_storage`, `permission_handler`, `image_picker`, `camera`, `home_widget`. |
| `frontend/mobile/ios/Runner/Info.plist` | Chưa có `NSFaceIDUsageDescription`. |

## 3. File sẽ thay đổi (ranh giới phạm vi)

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | `mobile/pubspec.yaml` | sửa | Thêm dependency `local_auth` |
| frontend | `mobile/pubspec.lock` | sửa | Khóa phiên bản do `flutter pub add` sinh |
| frontend | `mobile/lib/core/security/**` | thêm | `app_lock_settings_store.dart`, `device_authenticator.dart`, `app_lock_controller.dart`, `app_lock_gate.dart`, `app_lock_screen.dart`, `top_route_observer.dart` |
| frontend | `mobile/lib/core/platform/keyguard_service.dart` | sửa | Thêm `consumeUserLeftApp`, `setRecentsPrivacy` |
| frontend | `mobile/lib/app/app.dart` | sửa | Nhận `AppLockController`, gắn gate vào `builder`, observer route, chuyển lifecycle |
| frontend | `mobile/lib/main.dart` | sửa | Tạo và `load` `AppLockController`, truyền vào `DrugTimeApp` |
| frontend | `mobile/lib/features/profile/presentation/screens/profile_settings_screen.dart` | sửa | Dòng "Khóa ứng dụng" + `Switch` |
| frontend | `mobile/android/app/src/main/kotlin/vn/drugtime/drugtime_mobile/MainActivity.kt` | sửa | `FlutterFragmentActivity`, `onUserLeaveHint`, phát hiện tắt màn hình, `setRecentsScreenshotEnabled` |
| frontend | `mobile/android/app/src/main/res/values/styles.xml` | sửa | Chỉ khi P9 cho thấy `BiometricPrompt` cần theme AppCompat |
| frontend | `mobile/android/app/src/main/res/values-night/styles.xml` | sửa | Như trên, cho chế độ tối |
| frontend | `mobile/ios/Runner/Info.plist` | sửa | `NSFaceIDUsageDescription` tiếng Việt |
| frontend | `mobile/test/core/security/**` | thêm | Unit/widget test cho store, authenticator, controller, gate |
| frontend | `mobile/test/core/platform/keyguard_service_test.dart` | thêm | Test channel mới (mock MethodChannel) |
| frontend | `mobile/test/features/profile/app_lock_settings_test.dart` | thêm | Widget test công tắc trong Cài đặt |
| docs | `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` | sửa | Gộp test case qua `wf-testcase` ở cuối giai đoạn test |

## 4. Checklist

- [ ] P1 [frontend] Thêm `local_auth` bằng `flutter pub add local_auth` — file: `mobile/pubspec.yaml`, `mobile/pubspec.lock` — AC: AC1–AC5 — xong khi: `flutter pub get` thành công, `flutter analyze` không lỗi mới.
- [ ] P2 [frontend] Viết `AppLockSettingsStore` (Secure + Memory) và `DeviceAuthenticator` (LocalAuth + Fake) — file: `mobile/lib/core/security/app_lock_settings_store.dart`, `mobile/lib/core/security/device_authenticator.dart` — AC: AC1, AC10 — xong khi: test store đọc/ghi/xóa pass; `authenticate` truyền `biometricOnly: false`, `PlatformException` trả `false` thay vì ném.
- [ ] P3 [frontend] Viết `AppLockController` (load, enable, disable, unlock, onLifecycle, onSignedOut, chống prompt chồng) — file: `mobile/lib/core/security/app_lock_controller.dart` — AC: AC2, AC3, AC4, AC4b, AC4d, AC5, AC7 — xong khi: `app_lock_controller_test` pass đủ các nhánh ở mục 5.
- [ ] P4 [frontend] Mở rộng `KeyguardPlatform` với `consumeUserLeftApp()` (mặc định khi lỗi: `true` = khóa, fail-closed) và `setRecentsPrivacy(bool)` (lỗi thì bỏ qua) — file: `mobile/lib/core/platform/keyguard_service.dart` — AC: AC4, AC4c — xong khi: `keyguard_service_test` pass; các implement giả của `KeyguardPlatform` trong test cũ vẫn biên dịch (thêm method có thân mặc định nếu cần).
- [ ] P5 [frontend] Sửa `MainActivity`: kế thừa `FlutterFragmentActivity`; `onUserLeaveHint` đặt `userLeft = true`; `onPause` đặt `userLeft = true` khi `!PowerManager.isInteractive`; thêm hai method vào channel keyguard; `setRecentsPrivacy` gọi `setRecentsScreenshotEnabled(!on)` khi `SDK_INT >= 33` — file: `mobile/android/app/src/main/kotlin/vn/drugtime/drugtime_mobile/MainActivity.kt` — AC: AC4, AC4b, AC4c, AC9 — xong khi: `flutter build apk --debug` thành công; giữ nguyên `setShowWhenLocked`, `ReminderSoundChannel.onActivityResult`.
- [ ] P6 [frontend] Viết `TopRouteObserver`, `AppLockGate` (+ `AppLockScope`), `AppLockScreen`; miễn khóa khi route trên cùng là `AppRoutes.doseReminder`; fail-closed khi chưa `load` xong — file: `mobile/lib/core/security/top_route_observer.dart`, `mobile/lib/core/security/app_lock_gate.dart`, `mobile/lib/core/security/app_lock_screen.dart` — AC: AC3, AC4c, AC5, AC6, AC8 — xong khi: `app_lock_gate_test` pass; màn khóa có `Semantics` label tiếng Việt và chặn chạm xuống dưới.
- [ ] P7 [frontend] Nối vào app: `DrugTimeApp` nhận `appLockController` (tùy chọn, null thì không gate, để test cũ không đổi); `builder` bọc `AppLockGate` ngoài cùng; thêm observer vào `navigatorObservers`; `didChangeAppLifecycleState` gọi `onLifecycle`; `main.dart` tạo controller, `await load()`, nghe `AuthController` — file: `mobile/lib/app/app.dart`, `mobile/lib/main.dart` — AC: AC3, AC4, AC7, AC8 — xong khi: toàn bộ `flutter test` hiện có vẫn pass.
- [ ] P8 [frontend] Thêm dòng "Khóa ứng dụng" vào Cài đặt: đọc `AppLockScope`; thiết bị chưa đặt khóa màn hình thì `Switch` vô hiệu kèm dòng phụ "Hãy đặt khóa màn hình cho điện thoại trước"; bật thì gọi `enable()` — file: `mobile/lib/features/profile/presentation/screens/profile_settings_screen.dart` — AC: AC1, AC2 — xong khi: `app_lock_settings_test` pass.
- [ ] P9 [frontend] Cấu hình native: thêm `NSFaceIDUsageDescription` ("DrugTime dùng Face ID để mở khóa ứng dụng, bảo vệ thông tin sức khỏe của bạn."); chạy thử prompt trên Android; chỉ khi crash/không hiện thì đổi `LaunchTheme`/`NormalTheme` sang parent AppCompat tương ứng — file: `mobile/ios/Runner/Info.plist`, `mobile/android/app/src/main/res/values/styles.xml`, `mobile/android/app/src/main/res/values-night/styles.xml` — AC: AC9 — xong khi: prompt hiện đúng trên thiết bị thật Android và iOS (manual M1).
- [ ] P10 [frontend] Chạy `flutter analyze`, `flutter test`, lưu log vào `work/adhoc-20261125-biometric-auth/evidence/implement-flutter-test.log` — AC: tất cả — xong khi: không lỗi mới, mọi test pass.
- [ ] P11 [frontend] Kiểm tay trên thiết bị thật theo bảng manual M1–M7, ghi kết quả vào `04-impl-notes.md` — AC: AC3, AC4, AC4b, AC4c, AC8, AC9 — xong khi: mọi dòng có kết quả Pass/Fail kèm thiết bị, phiên bản OS.

## 5. Test

### Unit

| Test dự kiến | AC | Submodule |
|---|---|---|
| `app_lock_settings_store_test`: mặc định tắt; ghi/đọc `true`; `clear` về tắt; giá trị hỏng coi như tắt | AC2, AC7, AC10 | frontend |
| `device_authenticator_test`: `authenticate` truyền `biometricOnly: false` và lý do tiếng Việt; `PlatformException` (NotEnrolled, LockedOut, NotAvailable) trả `false` | AC1, AC5 | frontend |
| `app_lock_controller_test` — enable: xác thực thành công thì lưu bật; thất bại/hủy thì giữ tắt, không ghi store | AC2 | frontend |
| `app_lock_controller_test` — load: bật + đã đăng nhập thì `locked`; tắt thì không | AC3 | frontend |
| `app_lock_controller_test` — lifecycle Android: `paused` → `resumed` với `consumeUserLeftApp = true` thì khóa; `= false` (chọn ảnh, xin quyền) thì không khóa, bỏ lớp che | AC4, AC4b | frontend |
| `app_lock_controller_test` — lifecycle iOS: `inactive` → `resumed` không khóa; `paused` → `resumed` khóa | AC4, AC4b | frontend |
| `app_lock_controller_test` — `inactive` khi bật thì `obscured = true`; khi tắt thì không | AC4c, AC4d | frontend |
| `app_lock_controller_test` — gọi `unlock` hai lần liên tiếp chỉ gọi `authenticate` một lần | AC4b | frontend |
| `app_lock_controller_test` — unlock thất bại giữ `locked`; thành công bỏ `locked`, `obscured` | AC5 | frontend |
| `app_lock_controller_test` — `onSignedOut` xóa store, `enabled = locked = false` | AC6, AC7 | frontend |
| `keyguard_service_test`: channel trả lỗi thì `consumeUserLeftApp` trả `true`; `setRecentsPrivacy` không ném | AC4, AC4c | frontend |
| `app_lock_gate_test`: `locked` thì hiện màn khóa, nội dung bên dưới không nhận chạm và không có trong semantics tree | AC3, AC5 | frontend |
| `app_lock_gate_test`: `obscured` thì hiện lớp che, không thấy text của màn bên dưới | AC4c | frontend |
| `app_lock_gate_test`: route trên cùng `doseReminder` thì không hiện màn khóa, không gọi `authenticate`; pop route thì màn khóa hiện lại | AC8 | frontend |
| `app_lock_gate_test`: bấm "Đăng xuất" gọi `signOut` và về màn Đăng nhập | AC6 | frontend |
| `app_lock_gate_test`: chưa `load` xong thì hiện lớp che | AC3 | frontend |
| `app_lock_settings_test`: thiết bị không hỗ trợ thì `Switch` vô hiệu kèm hướng dẫn; hỗ trợ thì bật → gọi `enable`; tắt → `disable` | AC1, AC2 | frontend |
| Bộ `flutter test` hiện có (đặc biệt `test/app/*`, `reminder_wiring_test`, `app_shell_test`) vẫn pass khi `appLockController` null | AC4d | frontend |

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| Không có test tích hợp backend | — | Task không chạm API/DB; không có kịch bản chất lượng nào trong `AGENTS.md` áp dụng. |
| M1: bật khóa, mở khóa bằng Face ID (iPhone) và vân tay (Android); hủy prompt rồi dùng mã khóa màn hình | AC2, AC5, AC9 | manual, thiết bị thật |
| M2: vuốt tắt app từ Recents rồi mở lại → màn khóa | AC3 | manual |
| M3: bấm Home / chuyển app / khóa màn hình rồi quay lại → màn khóa ngay | AC4 | manual |
| M4: mở màn đa nhiệm khi đang ở màn Lịch sử liều → ảnh thu nhỏ không lộ dữ liệu (Android 13+: ảnh trống; iOS: lớp che) | AC4c | manual; ghi rõ kết quả Android < 13 |
| M5: khóa màn hình, chờ nhắc liều hiện trên màn hình khóa → xác nhận liều được mà không cần mở app lock; đóng màn nhắc thì thấy màn khóa | AC8 | manual |
| M6: chụp đơn thuốc OCR, chọn ảnh thư viện, cấp quyền camera, chọn nhạc chuông → quay lại không bị khóa | AC4b | manual |
| M7: tắt công tắc → chuyển app quay lại không có màn khóa | AC4d | manual |

## 6. Migration

Không có.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| superproject | `feat/adhoc-20261125-biometric-auth` |
| frontend | `feat/adhoc-20261125-biometric-auth` |
| docs | `feat/adhoc-20261125-biometric-auth` (chỉ khi gộp Test_Cases.xlsx) |

Hiện superproject đang ở nhánh `feat/5.09-meal-llm-cache` và `frontend`, `docs`, `api_contract` đang lệch con trỏ (doctor báo). Phải xử lý theo `wf-git` trước P1.

## 8. Rủi ro

| Rủi ro | Phát hiện / giảm thiểu |
|---|---|
| Đổi sang `FlutterFragmentActivity` làm hỏng `setShowWhenLocked`, `ReminderSoundChannel.onActivityResult`, camera/OCR, `home_widget` | Giữ nguyên các override; M5, M6 kiểm lại; chạy `reminder_wiring_test` và test capture. |
| `onUserLeaveHint` không được gọi khi có cuộc gọi đến hoặc thông báo full-screen của app khác che lên | Chấp nhận: người dùng không chủ động rời app. Ghi vào giới hạn đã biết. |
| Người dùng bấm Home ngay trong activity chọn ảnh/nhạc chuông (activity ngoài) → `onUserLeaveHint` gọi trên activity khác, app không khóa khi quay lại | Giới hạn đã biết, mức thấp; ghi vào `04`. |
| Prompt sinh trắc tự hiện đè lên màn nhắc liều trên màn hình khóa | Gate không tự gọi prompt khi route trên cùng là `doseReminder` (test ở mục 5). |
| Vòng lặp prompt: prompt gây `inactive`/`resumed` lại kích hoạt khóa | Chỉ khóa theo `consumeUserLeftApp`/`paused`, không theo `inactive`; cờ `_authenticating` chặn gọi chồng. |
| Android < 13 vẫn lộ ảnh trong màn đa nhiệm (Flutter không kịp vẽ lớp che) | Ghi rõ giới hạn; nếu không chấp nhận được thì task riêng dùng `FLAG_SECURE` (chặn cả chụp màn hình). |
| `consumeUserLeftApp` lỗi | Mặc định `true` (khóa) — an toàn hơn lộ dữ liệu. |
| Theme không phải AppCompat làm `BiometricPrompt` lỗi trên một số máy | P9 kiểm trên máy thật; chỉ đổi theme khi cần. |

## 9. Câu hỏi mở

Không có. Q2, Q5 của `01` theo giả định mặc định.

## 10. Phát sinh

- Doctor báo `frontend`, `docs`, `api_contract` lệch con trỏ superproject; cần xử lý trước khi tạo nhánh task.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: chạy `python .agents/scripts/gate.py approve adhoc-20261125-biometric-auth plan`; sau đó agent làm `wf-implement` từ P1 (tạo nhánh theo `wf-git` trước).
- Cập nhật lần cuối: 2026-11-25, Claude Code
