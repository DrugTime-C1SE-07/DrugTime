---
task: adhoc-20261125-biometric-auth
stage: implement
owner: Ngọc Việt
started_at: 2026-11-25 17:00
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-25 19:16 +0700
content_hash: sha256:46445a019689d2d1
inputs:
  01-requirement.md: sha256:8b92aa54e07435ff
  03-plan.md: sha256:3ffb1d77cca7d71b
---

# adhoc-20261125-biometric-auth · Implement

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `flutter pub add local_auth` → `local_auth ^3.0.2` (android 2.3.0, darwin, platform_interface 1.1.0); `flutter analyze` không lỗi mới (xem P7) | `evidence/implement-P1.log` |
| P2 | xong | `flutter test test/core/security` → 11 pass (store 3, authenticator 8) | `evidence/implement-P2.log` |
| P3 | xong | `flutter test test/core/security test/core/platform` → 36 pass (gồm `app_lock_controller_test`) | `evidence/implement-P3-P4.log` |
| P4 | xong | Như P3; thêm lớp `AppLeavePlatform` riêng (xem Ghi chú 1) | `evidence/implement-P3-P4.log` |
| P5 | xong (build) | `flutter build apk --debug` → `√ Built build/app/outputs/flutter-apk/app-debug.apk`; hành vi trên máy thật chờ P11 | `evidence/implement-P5-P9-build-apk.log` |
| P6 | xong | `flutter test test/core/security` → 36 pass (gồm 7 test gate) | `evidence/implement-P6.log` |
| P7 | xong | `flutter analyze`: không issue nào ở file của task (14 issue cũ ở file khác) | `evidence/implement-P7-analyze.log` |
| P8 | xong | `flutter test test/features/profile/app_lock_settings_test.dart` → 5 pass | `evidence/implement-P8.log` |
| P9 | xong (cấu hình) | `NSFaceIDUsageDescription` thêm, plist parse OK; theme Android đổi sang AppCompat theo README `local_auth_android` (minSdk 24 ≤ Android 8); build APK OK. Prompt trên máy thật chờ P11 | `evidence/implement-P5-P9-build-apk.log` |
| P10 | xong (có lỗi cũ) | `flutter analyze`: 13 issue, không issue nào ở file của task. `flutter test`: 1818 pass, 2 skip, 15 fail; cả 15 fail giống hệt trên `main` sạch (442cb4e), không do task gây ra | `evidence/implement-final-frontend.log`, `evidence/implement-final-analyze.log`, `evidence/implement-baseline-main-failing.log` |
| P11 | chưa làm | Cần thiết bị thật iOS (Face ID) + Android (vân tay); kịch bản M1–M7 trong `03-plan.md` mục 5 | — |

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| frontend | `feat/adhoc-20261125-biometric-auth` | `mobile/pubspec.yaml`, `mobile/pubspec.lock` |
| frontend | `feat/adhoc-20261125-biometric-auth` | `mobile/lib/core/security/` (mới): `app_lock_settings_store.dart`, `device_authenticator.dart`, `app_lock_controller.dart`, `app_lock_gate.dart`, `app_lock_screen.dart`, `top_route_observer.dart` |
| frontend | `feat/adhoc-20261125-biometric-auth` | `mobile/lib/core/platform/keyguard_service.dart`, `mobile/lib/app/app.dart`, `mobile/lib/main.dart`, `mobile/lib/features/profile/presentation/screens/profile_settings_screen.dart` |
| frontend | `feat/adhoc-20261125-biometric-auth` | `mobile/android/app/src/main/kotlin/vn/drugtime/drugtime_mobile/MainActivity.kt`, `mobile/android/app/src/main/res/values/styles.xml`, `mobile/android/app/src/main/res/values-night/styles.xml`, `mobile/ios/Runner/Info.plist` |
| frontend | `feat/adhoc-20261125-biometric-auth` | Test: `mobile/test/core/security/` (5 file mới), `mobile/test/core/platform/keyguard_service_test.dart`, `mobile/test/features/profile/app_lock_settings_test.dart` |

Kết quả `python .agents/scripts/scope.py adhoc-20261125-biometric-auth --stage implement`: OK (mọi file `[OK]`; `docs/.../Test_Cases.xlsx` chưa sửa, làm ở giai đoạn test) — log: `evidence/implement-scope.log`

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| frontend | `cd frontend/mobile && flutter test` | 1818 pass / 2 skip / 15 fail (15 fail có sẵn trên `main`, xem dưới) | `evidence/implement-final-frontend.log` |
| frontend | 7 file fail chạy lại trên worktree sạch `main` 442cb4e | cùng 15 fail ở cùng test | `evidence/implement-baseline-main-failing.log` |
| frontend | Test của task: `test/core/security`, `test/core/platform`, `test/features/profile/app_lock_settings_test.dart` | 41 pass / 0 fail | `evidence/implement-P6.log`, `evidence/implement-P8.log` |

File fail có sẵn: `test/app/adherence_demo_bootstrap_test.dart` (1), `test/features/drug_food_warning/food_warning_flow_test.dart` (2), `test/features/family_link/patient_switcher_home_entry_test.dart` (2), `test/features/interaction_check/interaction_flow_test.dart` (5), `test/features/medication/medication_screens_test.dart` (1), `test/features/profile/profile_layout_test.dart` (2), `test/shared/widgets/mascot/mascot_artwork_test.dart` (2).

## 3b. Bộ test case Excel (chỉ task size S)

Làm ở giai đoạn test.

## 4. Migration

Không có.

## 5. Ghi chú cho người review

Truy vết quyết định (`01` mục 9 → AC → test): Q1 tính năng tùy chọn, giữ phiên → AC2/AC4d/AC7 → `app_lock_controller_test` (enable/disable, sign out), `app_lock_settings_test`. Q3 khóa ngay → AC3/AC4/AC4b → `app_lock_controller_test` (cold start, lifecycle Android/iOS), `app_lock_gate_test`. Q4 Face ID/vân tay/mã khóa → AC1/AC5 → `device_authenticator_test` (`biometricOnly: false`), `app_lock_gate_test`. Q2 nhắc liều không cần mở khóa → AC8 → `app_lock_gate_test` (route `doseReminder` được miễn). Chống xem trộm → AC4c → `app_lock_gate_test` (lớp che), `setRecentsPrivacy`.

1. **Lệch nhỏ so với plan, P4**: thay vì thêm method vào `KeyguardPlatform`, thêm lớp `AppLeavePlatform`/`DefaultAppLeavePlatform` trong cùng file `keyguard_service.dart`, cùng channel. Lý do: hai fake `implements KeyguardPlatform` trong `test/features/reminder/*` sẽ không biên dịch nếu thêm method abstract, mà các file đó ngoài phạm vi.
2. **P7**: controller nghe đăng nhập qua `_onAuthChanged` có sẵn trong `app.dart` thay vì listener trong `main.dart`. `load()` gọi trong `_loadSession` sau `initSession()`, trước khi dựng `MaterialApp`, nên khởi động lạnh vào thẳng màn khóa. `main.dart` chỉ tạo controller.
3. **P9**: theme `LaunchTheme`/`NormalTheme` đổi sang `Theme.AppCompat.Light.NoActionBar` (sáng) và `Theme.AppCompat.NoActionBar` (tối), giữ `windowBackground`. Plan để điều kiện "chỉ khi cần"; README `local_auth_android` 2.3.0 ghi rõ bắt buộc để tránh crash trên Android ≤ 8, mà app có `minSdk = 24`. Cần xem lại màn splash trên máy thật.
4. `TopRouteObserver` ghi tên route ngay nhưng báo listener sau frame khi Navigator đang build (gate là cha của Navigator). `AppLockScreen` đọc lại điều kiện miễn khóa trước khi tự gọi prompt.
5. Fail-closed: chưa `load` xong thì che nội dung; `consumeUserLeftApp` lỗi thì khóa. Riêng việc đọc cờ từ Keychain/Keystore lỗi thì coi như tắt, để không chặn người dùng khỏi app khi storage hỏng.
6. Giới hạn đã biết: Android < 13 ảnh trong màn đa nhiệm có thể vẫn lộ; người dùng bấm Home ngay trong activity ngoài (chọn ảnh) thì quay lại không khóa; cuộc gọi đến không kích hoạt khóa.

## 6. Phát sinh

- 15 test có sẵn đang fail trên `main` (danh sách ở mục 3), không liên quan task. Đề xuất mở task/bug riêng.
- `MainActivity.setShowWhenLocked(true)` có từ trước, áp dụng cho mọi màn chứ không chỉ màn nhắc liều: khi app lock tắt, mở máy có thể thấy nội dung app trên màn hình khóa thiết bị. Khi app lock bật thì màn khóa của app che phần này. Ngoài phạm vi; đề xuất bug riêng để giới hạn cờ này cho màn nhắc liều.

## Bước tiếp theo

- Đang chờ: người dùng chạy P11 (kiểm tay M1–M7 trên iPhone có Face ID và máy Android có vân tay, ghi kết quả vào dòng P11), rồi người duyệt.
- Việc cần làm: sau P11, người duyệt chạy lệnh duyệt giai đoạn implement; sau đó agent làm `wf-test` (gồm `wf-testcase`).
- Cập nhật lần cuối: 2026-11-25, Claude Code
